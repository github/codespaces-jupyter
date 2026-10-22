import { NextRequest, NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { avatarModel } from "@/db/schema";
import { hasStudioSession } from "@/lib/auth";
import { editAvatarImage } from "@/lib/avatar-generation";
import { currentModel } from "@/lib/model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const maxReferenceBytes = 6 * 1024 * 1024;
const maxRequestBytes = maxReferenceBytes + 32_000;

export async function GET() {
  if (!(await hasStudioSession())) {
    return NextResponse.json({ error: "No autorizado." }, { status: 401 });
  }

  const studioModel = await currentModel();
  const records = await getDb()
    .select({
      id: avatarModel.id,
      name: avatarModel.name,
      description: avatarModel.description,
      creado: avatarModel.creado,
    })
    .from(avatarModel)
    .where(eq(avatarModel.studioModelId, studioModel.id))
    .orderBy(desc(avatarModel.creado));

  return NextResponse.json({ models: records });
}

export async function POST(request: NextRequest) {
  if (!(await hasStudioSession())) {
    return NextResponse.json({ error: "Inicia sesión para crear un modelo." }, { status: 401 });
  }

  const contentLength = Number(request.headers.get("content-length") || 0);
  if (!Number.isSafeInteger(contentLength) || contentLength <= 0) {
    return NextResponse.json({ error: "La solicitud debe incluir el tamaño de la foto." }, { status: 411 });
  }
  if (contentLength > maxRequestBytes) {
    return NextResponse.json({ error: "La foto supera el tamaño permitido de 6 MiB." }, { status: 413 });
  }

  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    return NextResponse.json({ error: "No se pudo leer el formulario de creación." }, { status: 400 });
  }

  const name = typeof form.get("name") === "string" ? String(form.get("name")).trim() : "";
  const description =
    typeof form.get("description") === "string" ? String(form.get("description")).trim() : "";
  const consentConfirmed = form.get("consentConfirmed") === "true";
  const photo = form.get("photo");

  if (!name || name.length > 60 || !description || description.length > 500) {
    return NextResponse.json(
      { error: "El nombre es obligatorio (hasta 60 caracteres) y la descripción admite hasta 500." },
      { status: 400 },
    );
  }
  if (!consentConfirmed) {
    return NextResponse.json(
      { error: "Confirma que la persona es adulta y autorizó el uso de su foto." },
      { status: 400 },
    );
  }
  if (
    !(photo instanceof File) ||
    !["image/jpeg", "image/png", "image/webp"].includes(photo.type) ||
    photo.size === 0 ||
    photo.size > maxReferenceBytes
  ) {
    return NextResponse.json(
      { error: "Sube una foto JPG, PNG o WebP de hasta 6 MiB." },
      { status: 400 },
    );
  }

  const studioModel = await currentModel();
  const sourceImage = Buffer.from(await photo.arrayBuffer()).toString("base64");
  let generated;
  try {
    generated = await editAvatarImage(
      sourceImage,
      [
        "Create a polished, photorealistic, fully clothed profile portrait of the same adult person in the reference image.",
        "Preserve the person's recognizable facial features, hairstyle, skin tone, and overall identity. Do not add another person.",
        `Creative direction: ${description}`,
        "Use natural skin texture, tasteful styling, a simple softly lit studio background, and a friendly neutral expression.",
        "Non-sexual, no nudity, no lingerie, no suggestive pose, no text, no logos, no watermark.",
      ].join(" "),
    );
  } catch (error) {
    console.error("No se pudo generar el avatar con Venice:", error);
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : "No se pudo generar el avatar. Revisa la conexión con Venice.",
      },
      { status: error instanceof Error && error.message.includes("VENICE_API_KEY") ? 503 : 502 },
    );
  }

  const [created] = await getDb()
    .insert(avatarModel)
    .values({
      studioModelId: studioModel.id,
      name,
      description,
      imageData: generated.data,
      imageType: generated.mimeType,
    })
    .returning({
      id: avatarModel.id,
      name: avatarModel.name,
      description: avatarModel.description,
      creado: avatarModel.creado,
    });

  return NextResponse.json({ model: created }, { status: 201 });
}
