import "server-only";
import { sql } from "drizzle-orm";
import { getDb } from "@/db";
import { catalogSeq } from "@/db/schema";

export async function proximoCatalogo(
  modelId: string,
): Promise<{ seq: number; no: string }> {
  const [fila] = await getDb()
    .insert(catalogSeq)
    .values({ modelId, ultimo: 1 })
    .onConflictDoUpdate({
      target: catalogSeq.modelId,
      set: { ultimo: sql`${catalogSeq.ultimo} + 1` },
    })
    .returning({ seq: catalogSeq.ultimo });

  if (!fila) {
    throw new Error("No se pudo reservar el número de catálogo.");
  }

  return { seq: fila.seq, no: `A-${String(fila.seq).padStart(4, "0")}` };
}
