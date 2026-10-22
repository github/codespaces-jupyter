import { NextRequest, NextResponse } from "next/server";
import { and, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { avatarModel, avatarScene } from "@/db/schema";
import { hasStudioSession } from "@/lib/auth";
import { editAvatarImage } from "@/lib/avatar-generation";
import { avatarScenePreset } from "@/lib/avatar-presets";
import { currentModel } from "@/lib/model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ id: string }> },
) {
  if (!(await hasStudioSession())) {
    return NextResponse.json({ error: "Inicia sesión para generar una escena." }, { status: 401 });
  }

  const { id } = await context.params;
  if (!/^[0-9a-f-]{36}$/i.test(id)) {
    return NextResponse.json({ error: "Modelo no válido." }, { status: 400 });
  }

  let body: { preset?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "El cuerpo JSON no es válido." }, { status: 400 });
  }
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return NextResponse.json({ error: "El cuerpo JSON no es válido." }, { status: 400 });
  }
  const preset = typeof body.preset === "string" ? avatarScenePreset(body.preset) : null;
  if (!preset) {
    return NextResponse.json({ error: "Selecciona una escena disponible." }, { status: 400 });
  }

  const studioModel = await currentModel();
  const [record] = await getDb()
    .select({
      id: avatarModel.id,
      imageData: avatarModel.imageData,
      description: avatarModel.description,
    })
    .from(avatarModel)
    .where(and(eq(avatarModel.id, id), eq(avatarModel.studioModelId, studioModel.id)))
    .limit(1);
  if (!record) {
    return NextResponse.json({ error: "No se encontró el modelo." }, { status: 404 });
  }
  const [existingScene] = await getDb()
    .select({ id: avatarScene.id })
    .from(avatarScene)
    .where(and(eq(avatarScene.avatarModelId, record.id), eq(avatarScene.preset, preset.id)))
    .limit(1);
  if (existingScene) {
    return NextResponse.json(
      { error: "Este decorado ya fue generado para el modelo." },
      { status: 409 },
    );
  }

  let generated;
  try {
    generated = await editAvatarImage(
      record.imageData,
      [
        "Edit this portrait into a tasteful, photorealistic lifestyle scene featuring the same adult person.",
        "Preserve recognizable facial identity, hairstyle, skin tone, and overall appearance from the reference. Show one person only.",
        `Scene: ${preset.prompt}.`,
        `Character description: ${record.description}`,
        "Keep the person fully clothed in modest, appropriate everyday clothing. Non-sexual, no nudity, no lingerie, no suggestive pose.",
        "Natural proportions, realistic hands, soft cinematic lighting, no text, no logos, no watermark.",
      ].join(" "),
    );
  } catch (error) {
    console.error("No se pudo generar una escena para el avatar:", error);
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : "No se pudo generar la escena. Revisa la conexión con Venice.",
      },
      { status: error instanceof Error && error.message.includes("VENICE_API_KEY") ? 503 : 502 },
    );
  }

  const [created] = await getDb()
    .insert(avatarScene)
    .values({
      avatarModelId: record.id,
      preset: preset.id,
      imageData: generated.data,
      imageType: generated.mimeType,
    })
    .returning({
      id: avatarScene.id,
      preset: avatarScene.preset,
      creado: avatarScene.creado,
    });

  return NextResponse.json({
    scene: {
      ...created,
      image: `/api/studio/avatar-models/${record.id}/image?scene=${created.id}`,
    },
  }, { status: 201 });
}
