import "server-only";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { model } from "@/db/schema";
import { modelHandle, requiredEnv } from "@/lib/config";

export async function currentModel() {
  const [record] = await getDb()
    .select()
    .from(model)
    .where(eq(model.handle, modelHandle()))
    .limit(1);

  if (!record) {
    throw new Error(
      "No existe el modelo configurado. Ejecuta `pnpm db:seed` para crearlo.",
    );
  }
  return record;
}

export function customerStreamUrl(uid: string): string {
  const customerCode = requiredEnv("CLOUDFLARE_CUSTOMER_CODE");
  return `https://customer-${customerCode}.cloudflarestream.com/${encodeURIComponent(uid)}/iframe`;
}

export function customerThumbnailUrl(uid: string): string {
  const customerCode = requiredEnv("CLOUDFLARE_CUSTOMER_CODE");
  return `https://customer-${customerCode}.cloudflarestream.com/${encodeURIComponent(uid)}/thumbnails/thumbnail.jpg`;
}
