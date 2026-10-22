import { NextRequest, NextResponse } from "next/server";
import { and, eq, inArray } from "drizzle-orm";
import { getDb } from "@/db";
import { contentAsset } from "@/db/schema";
import { verifyCloudflareWebhook } from "@/lib/cloudflare-webhook";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const signature = request.headers.get("Webhook-Signature");
  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > 1_000_000) {
    return NextResponse.json({ error: "Webhook demasiado grande." }, { status: 413 });
  }

  const rawBody = await request.text();
  if (rawBody.length > 1_000_000) {
    return NextResponse.json({ error: "Webhook demasiado grande." }, { status: 413 });
  }
  try {
    if (!verifyCloudflareWebhook(rawBody, signature)) {
      return NextResponse.json({ error: "Firma de webhook no válida." }, { status: 401 });
    }
  } catch (error) {
    console.error("No está configurada la firma del webhook de Cloudflare:", error);
    return NextResponse.json({ error: "Webhook no configurado." }, { status: 503 });
  }

  let body: {
    uid?: unknown;
    duration?: unknown;
    readyToStream?: unknown;
    status?: { state?: unknown };
  };
  try {
    body = JSON.parse(rawBody) as typeof body;
  } catch {
    return NextResponse.json({ error: "JSON de webhook no válido." }, { status: 400 });
  }
  if (typeof body.uid !== "string" || body.uid.length > 128) {
    return NextResponse.json({ error: "UID de Stream no válido." }, { status: 400 });
  }

  if (body.status?.state === "ready" && body.readyToStream === true) {
    const duration =
      typeof body.duration === "number" && Number.isFinite(body.duration)
        ? Math.round(body.duration)
        : null;
    await getDb()
      .update(contentAsset)
      .set({ estado: "listo", duracionS: duration })
      .where(
        and(
          eq(contentAsset.cfUid, body.uid),
          inArray(contentAsset.estado, ["subiendo", "listo"]),
        ),
      );
  } else if (body.status?.state === "error") {
    await getDb()
      .update(contentAsset)
      .set({ estado: "error" })
      .where(
        and(
          eq(contentAsset.cfUid, body.uid),
          inArray(contentAsset.estado, ["subiendo", "listo"]),
        ),
      );
  }

  return NextResponse.json({ ok: true });
}
