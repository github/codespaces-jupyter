import Link from "next/link";
import { redirect } from "next/navigation";
import { desc, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { avatarModel } from "@/db/schema";
import { hasStudioSession } from "@/lib/auth";
import { currentModel } from "@/lib/model";
import { AvatarModelStudio } from "./avatar-model-studio";

export const dynamic = "force-dynamic";

export default async function StudioModelsPage() {
  if (!(await hasStudioSession())) redirect("/login");

  const studioModel = await currentModel();
  const models = await getDb()
    .select({
      id: avatarModel.id,
      name: avatarModel.name,
      description: avatarModel.description,
      creado: avatarModel.creado,
    })
    .from(avatarModel)
    .where(eq(avatarModel.studioModelId, studioModel.id))
    .orderBy(desc(avatarModel.creado));

  return (
    <main className="shell">
      <header className="topbar">
        <Link className="brand" href="/studio">CATÁLOGO <span>STUDIO</span></Link>
        <Link className="button quiet" href="/studio">Volver al estudio</Link>
      </header>
      <section className="hero">
        <p className="eyebrow">CREACIÓN DE MODELOS</p>
        <h1>Tu foto, tu<br /><span>personaje.</span></h1>
        <p className="hero-copy">
          Crea un avatar desde una foto autorizada y genera decorados de referencia para su sala.
        </p>
      </section>
      <AvatarModelStudio
        initialModels={models.map((record) => ({
          ...record,
          creado: record.creado.toISOString(),
        }))}
      />
      <aside className="notice">
        <strong>Uso responsable.</strong> Sube solo imágenes de personas adultas que hayan autorizado
        este uso. La generación produce imágenes no explícitas; la foto original no se conserva.
        Venice edita la imagen de referencia, pero la semejanza exacta no está garantizada. Cada
        generación consume saldo de la cuenta configurada en Venice.
      </aside>
    </main>
  );
}
