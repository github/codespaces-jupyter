import { config } from "dotenv";
import { randomUUID } from "node:crypto";
import { eq } from "drizzle-orm";

config({ path: ".env.local" });

async function main() {
  const { getDb, closeDb } = await import("../src/db");
  const { catalogSeq, model } = await import("../src/db/schema");
  const { proximoCatalogo } = await import("../src/lib/catalogo");
  const db = getDb();
  const handle = `catalog-test-${randomUUID()}`;
  const [testModel] = await db
    .insert(model)
    .values({ handle, nombre: "Catalog concurrency test" })
    .returning({ id: model.id });

  try {
    const results = await Promise.all(
      Array.from({ length: 20 }, () => proximoCatalogo(testModel.id)),
    );
    const sequences = results.map(({ seq }) => seq).sort((left, right) => left - right);
    const expected = Array.from({ length: 20 }, (_, index) => index + 1);
    if (
      sequences.some((sequence, index) => sequence !== expected[index]) ||
      new Set(results.map(({ no }) => no)).size !== 20
    ) {
      throw new Error("Las reservas concurrentes no fueron únicas y consecutivas.");
    }
    console.log("Correcto: 20 reservas paralelas produjeron 20 números únicos y consecutivos.");
  } finally {
    await db.delete(catalogSeq).where(eq(catalogSeq.modelId, testModel.id));
    await db.delete(model).where(eq(model.id, testModel.id));
    await closeDb();
  }
}

main().catch((error: unknown) => {
  console.error("Falló la prueba de concurrencia del catálogo:", error);
  process.exitCode = 1;
});
