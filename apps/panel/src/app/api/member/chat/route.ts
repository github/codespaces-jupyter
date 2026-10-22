import { createHash } from "node:crypto";
import { desc, eq } from "drizzle-orm";
import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/db";
import { memberChatMessage } from "@/db/schema";
import { verifyMemberToken } from "@/lib/auth";

export const dynamic = "force-dynamic";

const maxBodyBytes = 16 * 1024;
const maxMessageLength = 1200;
const maxContextMessages = 12;
const maxHistoryMessages = 100;

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

function getTokenHash(token: string): string {
  return createHash("sha256").update(token).digest("hex");
}

async function authorizedMember(request: NextRequest) {
  const authorization = request.headers.get("authorization") || "";
  const match = /^Bearer (.+)$/.exec(authorization);
  if (!match || match[1].length > 4096) return null;

  const member = await verifyMemberToken(match[1]);
  return member ? { tokenHash: getTokenHash(match[1]) } : null;
}

function isChatMessage(value: unknown): value is ChatMessage {
  if (!value || typeof value !== "object") return false;
  const message = value as Record<string, unknown>;
  return (
    (message.role === "user" || message.role === "assistant") &&
    typeof message.content === "string" &&
    message.content.trim().length > 0
  );
}

function isUserMessage(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0 && value.length <= maxMessageLength;
}

export async function GET(request: NextRequest) {
  const authorized = await authorizedMember(request);
  if (!authorized) {
    return NextResponse.json({ error: "El enlace de socio venció o no es válido." }, { status: 401 });
  }

  const records = await getDb()
    .select({
      role: memberChatMessage.role,
      content: memberChatMessage.content,
    })
    .from(memberChatMessage)
    .where(eq(memberChatMessage.tokenHash, authorized.tokenHash))
    .orderBy(desc(memberChatMessage.creado), desc(memberChatMessage.id))
    .limit(maxHistoryMessages);

  return NextResponse.json({
    messages: records.reverse().filter(isChatMessage).map(({ role, content }) => ({ role, content })),
  });
}

export async function POST(request: NextRequest) {
  const origin = request.headers.get("origin");
  if (origin && origin !== request.nextUrl.origin) {
    return NextResponse.json({ error: "Origen de solicitud no válido." }, { status: 403 });
  }

  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > maxBodyBytes) {
    return NextResponse.json({ error: "El mensaje es demasiado grande." }, { status: 413 });
  }

  let rawBody: string;
  try {
    rawBody = await request.text();
  } catch {
    return NextResponse.json({ error: "No se pudo leer la solicitud." }, { status: 400 });
  }
  if (Buffer.byteLength(rawBody, "utf8") > maxBodyBytes) {
    return NextResponse.json({ error: "El mensaje es demasiado grande." }, { status: 413 });
  }

  let parsedBody: unknown;
  try {
    parsedBody = JSON.parse(rawBody) as unknown;
  } catch {
    return NextResponse.json({ error: "El cuerpo JSON no es válido." }, { status: 400 });
  }
  if (
    !parsedBody ||
    typeof parsedBody !== "object" ||
    Array.isArray(parsedBody) ||
    !isUserMessage((parsedBody as { message?: unknown }).message)
  ) {
    return NextResponse.json({ error: "El mensaje no es válido." }, { status: 400 });
  }
  const message = (parsedBody as { message: string }).message.trim();

  const authorized = await authorizedMember(request);
  if (!authorized) {
    return NextResponse.json({ error: "El enlace de socio venció o no es válido." }, { status: 401 });
  }

  const apiKey = process.env.VENICE_API_KEY?.trim() || process.env.VENICE_KEY?.trim();
  if (!apiKey) {
    return NextResponse.json(
      { error: "Chat de IA sin configurar: falta VENICE_API_KEY (o VENICE_KEY) en el entorno del servidor." },
      { status: 503 },
    );
  }

  const model =
    process.env.VENICE_DEFAULT_CHAT_MODEL?.trim() ||
    process.env.VENICE_MODEL?.trim() ||
    "llama-3.3-70b";
  const history = await getDb()
    .select({
      role: memberChatMessage.role,
      content: memberChatMessage.content,
    })
    .from(memberChatMessage)
    .where(eq(memberChatMessage.tokenHash, authorized.tokenHash))
    .orderBy(desc(memberChatMessage.creado), desc(memberChatMessage.id))
    .limit(maxContextMessages - 1);
  const context = history.reverse().filter(isChatMessage);

  let response: Response;
  try {
    response = await fetch("https://api.venice.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        max_tokens: 500,
        messages: [
          {
            role: "system",
            content:
              "Eres un avatar conversacional amable y respetuoso. Responde en el idioma del usuario, de forma clara y breve. No afirmes ser una persona real ni un profesional de salud.",
          },
          ...context,
          { role: "user", content: message },
        ],
      }),
      signal: AbortSignal.timeout(30_000),
      cache: "no-store",
    });
  } catch {
    console.error("No se pudo contactar a Venice para el chat del avatar.");
    return NextResponse.json({ error: "El servicio del avatar no está disponible ahora." }, { status: 502 });
  }

  if (!response.ok) {
    console.error(`Venice rechazó el chat del avatar (HTTP ${response.status}).`);
    return NextResponse.json(
      { error: "El servicio del avatar rechazó la solicitud. Revisa el modelo y la configuración del servidor." },
      { status: response.status === 429 ? 429 : 502 },
    );
  }

  let result: {
    choices?: Array<{ message?: { content?: unknown } }>;
  };
  try {
    result = (await response.json()) as typeof result;
  } catch {
    console.error("Venice devolvió una respuesta JSON no válida para el chat del avatar.");
    return NextResponse.json({ error: "El servicio devolvió una respuesta no válida." }, { status: 502 });
  }
  const reply = result.choices?.[0]?.message?.content;
  if (typeof reply !== "string" || !reply.trim()) {
    console.error("Venice devolvió una respuesta vacía para el chat del avatar.");
    return NextResponse.json({ error: "El servicio no devolvió una respuesta de texto." }, { status: 502 });
  }

  await getDb().transaction(async (transaction) => {
    await transaction.insert(memberChatMessage).values([
      { tokenHash: authorized.tokenHash, role: "user", content: message },
      { tokenHash: authorized.tokenHash, role: "assistant", content: reply.trim() },
    ]);
  });

  return NextResponse.json({ reply: reply.trim() });
}
