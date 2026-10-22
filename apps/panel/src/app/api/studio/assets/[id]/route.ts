import { NextRequest, NextResponse } from "next/server";
import { and, eq, inArray } from "drizzle-orm";
import { getDb } from "@/db";
import { contentAsset, model } from "@/db/schema";
import { hasStudioSession } from "@/lib/auth";
import { modelHandle } from "@/lib/config";
import { isTier } from "@/lib/tiers";

export const dynamic = "force-dynamic";

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ id: string }> },
) {
  if (!(await hasStudioSession())) {
    return NextResponse.json({ error: "No autorizado." }, { status: 401 });
  }

  const { id } = await context.params;
  if (!/^[0-9a-f-]{36}$/i.test(id)) {
    return NextResponse.json({ error: "Artículo no válido." }, { status: 400 });
  }

  let body: { titulo?: unknown; visibilityTier?: unknown; estado?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "El cuerpo JSON no es válido." }, { status: 400 });
  }
  const titulo = typeof body.titulo === "string" ? body.titulo.trim() : "";
  if (
    !titulo ||
    titulo.length > 120 ||
    !isTier(body.visibilityTier) ||
    !["borrador", "publicado"].includes(String(body.estado))
  ) {
    return NextResponse.json({ error: "Completa el título, nivel y estado válidos." }, { status: 400 });
  }

  const [currentModel] = await getDb()
    .select({ id: model.id })
    .from(model)
    .where(eq(model.handle, modelHandle()))
    .limit(1);
  if (!currentModel) {
    return NextResponse.json({ error: "No existe el modelo configurado." }, { status: 503 });
  }

  const [asset] = await getDb()
    .select({ estado: contentAsset.estado })
    .from(contentAsset)
    .where(and(eq(contentAsset.id, id), eq(contentAsset.modelId, currentModel.id)))
    .limit(1);
  if (!asset) {
    return NextResponse.json({ error: "Artículo no encontrado." }, { status: 404 });
  }
  if (!["listo", "publicado"].includes(asset.estado)) {
    return NextResponse.json(
      { error: "El artículo solo se puede publicar cuando Stream terminó de procesarlo." },
      { status: 409 },
    );
  }

  const estado = body.estado === "publicado" ? "publicado" : "borrador";
  await getDb()
    .update(contentAsset)
    .set({ titulo, visibilityTier: body.visibilityTier, estado })
    .where(
      and(
        eq(contentAsset.id, id),
        eq(contentAsset.modelId, currentModel.id),
        inArray(contentAsset.estado, ["listo", "publicado"]),
      ),
    );
  return NextResponse.json({ ok: true });
}
