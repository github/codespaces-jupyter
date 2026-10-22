import { config } from "dotenv";

config({ path: ".env.local" });

async function main() {
  const { closeDb, getDb } = await import("../src/db");
  const { model } = await import("../src/db/schema");
  const db = getDb();
  const handle = process.env.MODEL_HANDLE?.trim() || "demo";
  const name = process.env.MODEL_NAME?.trim() || "Modelo demo";

  try {
    const [record] = await db
      .insert(model)
      .values({ handle, nombre: name })
      .onConflictDoUpdate({
        target: model.handle,
        set: { nombre: name },
      })
      .returning({ id: model.id, handle: model.handle, nombre: model.nombre });

    if (!record) {
      throw new Error("No se pudo crear el modelo de prueba.");
    }

    console.log(`Modelo listo: ${record.nombre} (${record.handle}, ${record.id})`);
  } finally {
    await closeDb();
  }
}

main().catch((error: unknown) => {
  console.error("No se pudo crear el modelo de demostración:", error);
  process.exitCode = 1;
});
