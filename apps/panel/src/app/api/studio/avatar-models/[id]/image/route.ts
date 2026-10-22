import { NextRequest, NextResponse } from "next/server";
import { and, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { avatarModel, avatarScene } from "@/db/schema";
import { hasStudioSession } from "@/lib/auth";
import { currentModel } from "@/lib/model";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
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
  const sceneId = request.nextUrl.searchParams.get("scene");
  let imageData: string | undefined;
  let imageType: string | undefined;

  if (sceneId) {
    if (!/^[0-9a-f-]{36}$/i.test(sceneId)) {
      return NextResponse.json({ error: "Escena no válida." }, { status: 400 });
    }
    const [scene] = await getDb()
      .select({
        imageData: avatarScene.imageData,
        imageType: avatarScene.imageType,
      })
      .from(avatarScene)
      .innerJoin(avatarModel, eq(avatarScene.avatarModelId, avatarModel.id))
      .where(
        and(
          eq(avatarScene.id, sceneId),
          eq(avatarScene.avatarModelId, id),
          eq(avatarModel.studioModelId, studioModel.id),
        ),
      )
      .limit(1);
    imageData = scene?.imageData;
    imageType = scene?.imageType;
  } else {
    const [record] = await getDb()
      .select({
        imageData: avatarModel.imageData,
        imageType: avatarModel.imageType,
      })
      .from(avatarModel)
      .where(and(eq(avatarModel.id, id), eq(avatarModel.studioModelId, studioModel.id)))
      .limit(1);
    imageData = record?.imageData;
    imageType = record?.imageType;
  }

  if (!imageData || !imageType || !["image/png", "image/jpeg", "image/webp"].includes(imageType)) {
    return NextResponse.json({ error: "No se encontró la imagen." }, { status: 404 });
  }

  return new NextResponse(new Uint8Array(Buffer.from(imageData, "base64")), {
    headers: {
      "Content-Type": imageType,
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
