import { NextRequest, NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { hasStudioSession } from "@/lib/auth";
import { proximoCatalogo } from "@/lib/catalogo";
import { contentAsset, model } from "@/db/schema";
import { getDb } from "@/db";
import { modelHandle, requiredEnv } from "@/lib/config";
import { isTier } from "@/lib/tiers";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  if (!(await hasStudioSession())) {
    return NextResponse.json({ error: "Inicia sesión para subir contenido." }, { status: 401 });
  }

  let body: { titulo?: unknown; visibilityTier?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "El cuerpo JSON no es válido." }, { status: 400 });
  }

  const titulo = typeof body.titulo === "string" ? body.titulo.trim() : "";
  const visibilityTier = body.visibilityTier ?? "base";
  if (!titulo || titulo.length > 120) {
    return NextResponse.json(
      { error: "El título es obligatorio y admite hasta 120 caracteres." },
      { status: 400 },
    );
  }
  if (!isTier(visibilityTier)) {
    return NextResponse.json({ error: "El nivel mínimo no es válido." }, { status: 400 });
  }

  try {
    const accountId = requiredEnv("CLOUDFLARE_ACCOUNT_ID");
    const apiToken = requiredEnv("CLOUDFLARE_STREAM_TOKEN");
    const [currentModel] = await getDb()
      .select({ id: model.id })
      .from(model)
      .where(eq(model.handle, modelHandle()))
      .limit(1);
    if (!currentModel) {
      return NextResponse.json(
        { error: "No existe el modelo. Ejecuta `pnpm db:seed`." },
        { status: 503 },
      );
    }

    const response = await fetch(
      `https://api.cloudflare.com/client/v4/accounts/${encodeURIComponent(accountId)}/stream/direct_upload`,
      {
        method: "POST",
        headers: {
          Authorization: ["Bearer", apiToken].join(" "),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          maxDurationSeconds: 7200,
          requireSignedURLs: false,
          meta: { name: titulo, modelId: currentModel.id },
        }),
        signal: AbortSignal.timeout(20_000),
        cache: "no-store",
      },
    );
    const cloudflare = (await response.json()) as {
      success?: boolean;
      errors?: Array<{ message?: string }>;
      result?: { uid?: string; uploadURL?: string };
    };
    const uid = cloudflare.result?.uid;
    const uploadURL = cloudflare.result?.uploadURL;
    if (!response.ok || !cloudflare.success || !uid || !uploadURL) {
      console.error("Cloudflare no pudo crear una subida directa:", cloudflare.errors);
      return NextResponse.json(
        { error: "Cloudflare no pudo crear la subida directa." },
        { status: 502 },
      );
    }

    const catalog = await proximoCatalogo(currentModel.id);
    const [asset] = await getDb()
      .insert(contentAsset)
      .values({
        modelId: currentModel.id,
        catalogSeq: catalog.seq,
        catalogNo: catalog.no,
        titulo,
        cfUid: uid,
        visibilityTier,
        estado: "subiendo",
      })
      .returning({ id: contentAsset.id });

    return NextResponse.json(
      { assetId: asset.id, catalogNo: catalog.no, uploadURL, uid },
      { status: 201 },
    );
  } catch (error) {
    console.error("No se pudo iniciar la subida a Stream:", error);
    return NextResponse.json(
      { error: "No se pudo iniciar la subida. Revisa la base de datos y la configuración de Cloudflare." },
      { status: 503 },
    );
  }
}
