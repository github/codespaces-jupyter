import { NextRequest, NextResponse } from "next/server";
import { and, asc, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { avatarModel, avatarScene } from "@/db/schema";
import { hasStudioSession } from "@/lib/auth";
import { currentModel } from "@/lib/model";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ id: string }> },
) {
  if (!(await hasStudioSession())) {
    return NextResponse.json({ error: "No autorizado." }, { status: 401 });
  }

  const { id } = await context.params;
  if (!/^[0-9a-f-]{36}$/i.test(id)) {
    return NextResponse.json({ error: "Modelo no válido." }, { status: 400 });
  }
  const studioModel = await currentModel();
  const [record] = await getDb()
    .select({
      id: avatarModel.id,
      name: avatarModel.name,
      description: avatarModel.description,
      creado: avatarModel.creado,
    })
    .from(avatarModel)
    .where(and(eq(avatarModel.id, id), eq(avatarModel.studioModelId, studioModel.id)))
    .limit(1);
  if (!record) {
    return NextResponse.json({ error: "No se encontró el modelo." }, { status: 404 });
  }

  const scenes = await getDb()
    .select({
      id: avatarScene.id,
      preset: avatarScene.preset,
      creado: avatarScene.creado,
    })
    .from(avatarScene)
    .where(eq(avatarScene.avatarModelId, record.id))
    .orderBy(asc(avatarScene.creado));

  return NextResponse.json({
    model: {
      id: record.id,
      name: record.name,
      description: record.description,
      image: `/api/studio/avatar-models/${record.id}/image`,
      creado: record.creado,
    },
    scenes: scenes.map((scene) => ({
      id: scene.id,
      preset: scene.preset,
      image: `/api/studio/avatar-models/${record.id}/image?scene=${scene.id}`,
      creado: scene.creado,
    })),
  });
}
