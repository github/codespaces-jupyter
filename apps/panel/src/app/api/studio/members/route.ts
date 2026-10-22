import { NextRequest, NextResponse } from "next/server";
import { hasStudioSession, createMemberToken } from "@/lib/auth";
import { isTier } from "@/lib/tiers";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  if (!(await hasStudioSession())) {
    return NextResponse.json({ error: "No autorizado." }, { status: 401 });
  }

  let body: { nick?: unknown; tier?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "El cuerpo JSON no es válido." }, { status: 400 });
  }
  const nick = typeof body.nick === "string" ? body.nick.trim() : "";
  if (!nick || nick.length > 40 || !isTier(body.tier)) {
    return NextResponse.json(
      { error: "Indica un alias de hasta 40 caracteres y un nivel válido." },
      { status: 400 },
    );
  }

  const token = await createMemberToken(nick, body.tier);
  const baseUrl = process.env.APP_BASE_URL || new URL(request.url).origin;
  return NextResponse.json({ url: `${baseUrl}/e/${encodeURIComponent(token)}` });
}
