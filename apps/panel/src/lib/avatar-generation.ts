import "server-only";

const maxGeneratedImageBytes = 12 * 1024 * 1024;

export type GeneratedImage = {
  data: string;
  mimeType: string;
};

export async function editAvatarImage(image: string, prompt: string): Promise<GeneratedImage> {
  const apiKey = process.env.VENICE_API_KEY?.trim() || process.env.VENICE_KEY?.trim();
  if (!apiKey) {
    throw new Error("Falta configurar VENICE_API_KEY (o VENICE_KEY) en el entorno del servidor.");
  }
  const model = process.env.VENICE_IMAGE_EDIT_MODEL?.trim() || "firered-image-edit";
  const response = await fetch("https://api.venice.ai/api/v1/image/edit", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      image,
      prompt,
      output_format: "webp",
      safe_mode: true,
    }),
    signal: AbortSignal.timeout(110_000),
    cache: "no-store",
  });

  if (!response.ok) {
    console.error(`Venice rechazó la edición de imagen (HTTP ${response.status}).`);
    if (response.status === 401 || response.status === 403) {
      throw new Error("Venice no autorizó la edición. Revisa la clave y los permisos de imagen.");
    }
    if (response.status === 402) {
      throw new Error("La cuenta de Venice no tiene saldo suficiente para generar la imagen.");
    }
    if (response.status === 429) {
      throw new Error("Venice está limitando las solicitudes. Espera un momento y vuelve a intentar.");
    }
    throw new Error("Venice no pudo generar la imagen. Revisa el modelo y vuelve a intentar.");
  }

  const mimeType = response.headers.get("content-type")?.split(";")[0]?.trim().toLowerCase();
  if (!mimeType || !["image/png", "image/jpeg", "image/webp"].includes(mimeType)) {
    throw new Error("Venice respondió con un formato de imagen no compatible.");
  }
  const bytes = Buffer.from(await response.arrayBuffer());
  if (bytes.length === 0 || bytes.length > maxGeneratedImageBytes) {
    throw new Error("La imagen generada está vacía o supera el tamaño permitido.");
  }
  return { data: bytes.toString("base64"), mimeType };
}
