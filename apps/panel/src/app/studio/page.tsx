import { desc, eq, sql } from "drizzle-orm";
import Link from "next/link";
import { redirect } from "next/navigation";
import { getDb } from "@/db";
import { assetEvent, contentAsset } from "@/db/schema";
import { hasStudioSession } from "@/lib/auth";
import { currentModel } from "@/lib/model";
import PlanCards from "@/app/planes/plan-cards";
import {
  AssetEditor,
  LogoutButton,
  MemberInviteForm,
  UploadForm,
} from "./studio-actions";

export const dynamic = "force-dynamic";

export default async function StudioPage() {
  if (!(await hasStudioSession())) redirect("/login");

  const studioModel = await currentModel();
  const assets = await getDb()
    .select({
      id: contentAsset.id,
      catalogNo: contentAsset.catalogNo,
      titulo: contentAsset.titulo,
      visibilityTier: contentAsset.visibilityTier,
      estado: contentAsset.estado,
      precioMicro: contentAsset.precioMicro,
      creado: contentAsset.creado,
      vistas: sql<number>`count(*) filter (where ${assetEvent.tipo} = 'vista')`.mapWith(Number),
      unicos: sql<number>`count(distinct ${assetEvent.nick}) filter (where ${assetEvent.tipo} = 'vista')`.mapWith(Number),
      ventas: sql<number>`count(*) filter (where ${assetEvent.tipo} = 'venta')`.mapWith(Number),
      ingresos: sql<number>`coalesce(sum(${assetEvent.montoMicro}) filter (where ${assetEvent.tipo} = 'venta'), 0)`.mapWith(Number),
    })
    .from(contentAsset)
    .leftJoin(assetEvent, eq(assetEvent.assetId, contentAsset.id))
    .where(eq(contentAsset.modelId, studioModel.id))
    .groupBy(contentAsset.id)
    .orderBy(desc(contentAsset.creado));

  const views = assets.reduce((total, asset) => total + asset.vistas, 0);
  const sales = assets.reduce((total, asset) => total + asset.ventas, 0);
  const revenueMicro = assets.reduce((total, asset) => total + asset.ingresos, 0);

  return (
    <main className="shell">
      <header className="topbar">
        <Link className="brand" href="/">CATÁLOGO <span>STUDIO</span></Link>
        <div className="top-actions">
          <span className="muted" style={{ fontSize: 11 }}>{studioModel.nombre}</span>
          <Link className="button quiet" href="/studio/models">Crear modelo</Link>
          <LogoutButton />
        </div>
      </header>

      <section className="hero">
        <p className="eyebrow">ESPACIO DE MODELO · {studioModel.handle}</p>
        <h1>Tu catálogo,<br /><span>bajo control.</span></h1>
        <p className="hero-copy">
          Sube videos directamente a Cloudflare Stream, publica por nivel y comparte accesos personales con tus socios.
        </p>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">01 — CATÁLOGO</p>
            <h2>Subir un video</h2>
            <p>El número correlativo queda reservado antes de iniciar la carga.</p>
          </div>
        </div>
        <UploadForm />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">02 — RENDIMIENTO</p>
            <h2>Resumen del catálogo</h2>
          </div>
          <div className="top-actions muted" style={{ fontSize: 11 }}>
            <span>{assets.length} artículos</span>
            <span>·</span>
            <span>{views} vistas</span>
            <span>·</span>
            <span>{sales} ventas</span>
            <span>·</span>
            <span>${(revenueMicro / 1_000_000).toFixed(2)}</span>
          </div>
        </div>
        {assets.length === 0 ? (
          <div className="empty">Todavía no hay artículos. Sube el primer video para reservar A-0001.</div>
        ) : (
          <div className="asset-table-wrap">
            <table className="asset-table">
              <thead>
                <tr>
                  <th>Catálogo</th>
                  <th>Artículo</th>
                  <th>Estado</th>
                  <th>Vistas</th>
                  <th>Únicos</th>
                  <th>Ventas</th>
                  <th>Ingresos</th>
                  <th>Conv.</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset) => {
                  const conversion = asset.unicos
                    ? Math.round((asset.ventas / asset.unicos) * 100)
                    : 0;
                  const editable = ["listo", "publicado"].includes(asset.estado);
                  return (
                    <tr key={asset.id}>
                      <td className="catalog-no">{asset.catalogNo}</td>
                      <td>
                        {editable ? (
                          <AssetEditor asset={asset} />
                        ) : (
                          <span>{asset.titulo}</span>
                        )}
                      </td>
                      <td>
                        <span className={`pill ${asset.estado === "listo" || asset.estado === "publicado" ? "ready" : asset.estado === "error" ? "error" : ""}`}>
                          {asset.estado}
                        </span>
                      </td>
                      <td>{asset.vistas}</td>
                      <td>{asset.unicos}</td>
                      <td>{asset.ventas}</td>
                      <td>${(asset.ingresos / 1_000_000).toFixed(2)}</td>
                      <td>{asset.unicos ? `${conversion}%` : "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">03 — ACCESO DE SOCIOS</p>
            <h2>Crear un enlace personal</h2>
            <p>El enlace lleva un nivel firmado y caduca a los 30 días.</p>
          </div>
        </div>
        <MemberInviteForm />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">04 — PLANES PREMIUM</p>
            <h2>Información de membresías</h2>
            <p>Precios actuales del bot, vigencia y alcance de cada nivel.</p>
          </div>
        </div>
        <PlanCards />
      </section>

      <aside className="notice">
        <strong>Prototipo con videos reales.</strong> Los enlaces de Cloudflare están sin firma de reproducción para que el reproductor funcione sin claves adicionales; cualquier persona que obtenga el UID del video podría verlo. Usa solo videos de prueba no sensibles y mantén el puerto del Codespace en modo Private. No es un servicio listo para producción.
      </aside>
    </main>
  );
}
