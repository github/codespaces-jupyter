import { NextRequest, NextResponse } from "next/server";
import { and, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { assetEvent, contentAsset } from "@/db/schema";
import { verifyMemberToken } from "@/lib/auth";
import { canViewTier, isTier } from "@/lib/tiers";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  let body: { token?: unknown; assetId?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "El cuerpo JSON no es válido." }, { status: 400 });
  }
  if (
    typeof body.token !== "string" ||
    body.token.length > 4096 ||
    typeof body.assetId !== "string" ||
    !/^[0-9a-f-]{36}$/i.test(body.assetId)
  ) {
    return NextResponse.json({ error: "Solicitud no válida." }, { status: 400 });
  }
  const member = await verifyMemberToken(body.token);
  if (!member || !isTier(member.tier)) {
    return NextResponse.json({ error: "El enlace venció o no es válido." }, { status: 401 });
  }

  const [asset] = await getDb()
    .select({
      id: contentAsset.id,
      modelId: contentAsset.modelId,
      visibilityTier: contentAsset.visibilityTier,
    })
    .from(contentAsset)
    .where(
      and(
        eq(contentAsset.id, body.assetId),
        eq(contentAsset.estado, "publicado"),
      ),
    )
    .limit(1);
  if (!asset || !isTier(asset.visibilityTier) || !canViewTier(member.tier, asset.visibilityTier)) {
    return NextResponse.json({ error: "Contenido no disponible para este nivel." }, { status: 404 });
  }

  await getDb().insert(assetEvent).values({
    assetId: asset.id,
    modelId: asset.modelId,
    nick: member.nick,
    tipo: "vista",
  });
  return NextResponse.json({ ok: true }, { status: 201 });
}
