import { and, desc, eq } from "drizzle-orm";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getDb } from "@/db";
import { contentAsset } from "@/db/schema";
import { verifyMemberToken } from "@/lib/auth";
import { currentModel, customerThumbnailUrl } from "@/lib/model";
import { canViewTier, isTier, type Tier } from "@/lib/tiers";

export const dynamic = "force-dynamic";

export default async function MemberPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const member = await verifyMemberToken(token);
  if (!member || !isTier(member.tier)) notFound();

  const studioModel = await currentModel();
  const assets = await getDb()
    .select({
      id: contentAsset.id,
      catalogNo: contentAsset.catalogNo,
      titulo: contentAsset.titulo,
      cfUid: contentAsset.cfUid,
      visibilityTier: contentAsset.visibilityTier,
    })
    .from(contentAsset)
    .where(
      and(
        eq(contentAsset.modelId, studioModel.id),
        eq(contentAsset.estado, "publicado"),
      ),
    )
    .orderBy(desc(contentAsset.creado));

  const visibleAssets = assets.filter(
    (asset): asset is typeof asset & { cfUid: string; visibilityTier: Tier } =>
      Boolean(asset.cfUid) &&
      isTier(asset.visibilityTier) &&
      canViewTier(member.tier, asset.visibilityTier),
  );

  return (
    <main className="shell">
      <header className="topbar">
        <Link className="brand" href="/">CATÁLOGO <span>PRIVADO</span></Link>
        <div className="top-actions">
          <Link className="button quiet" href="/planes">Planes premium</Link>
          <span className="pill ready">{member.tier.toUpperCase()}</span>
        </div>
      </header>
      <section className="member-header">
        <p className="eyebrow">CONTENIDO PARA SOCIOS</p>
        <h1>Hola, {member.nick}</h1>
        <p className="muted" style={{ fontSize: 13 }}>
          {studioModel.nombre} · Nivel {member.tier.toUpperCase()}
        </p>
        <Link className="button primary room-link" href={`/e/${encodeURIComponent(token)}/sala`}>
          Entrar a la sala del avatar
        </Link>
      </section>
      {visibleAssets.length === 0 ? (
        <div className="empty">Aún no hay contenido publicado para tu nivel.</div>
      ) : (
        <section className="member-grid">
          {visibleAssets.map((asset) => (
            <a
              className="member-card"
              key={asset.id}
              href={`/e/${encodeURIComponent(token)}/${encodeURIComponent(asset.catalogNo)}`}
            >
              <div
                role="img"
                aria-label={`Miniatura de ${asset.titulo}`}
                style={{
                  aspectRatio: "1",
                  backgroundColor: "#07080c",
                  backgroundImage: `url("${customerThumbnailUrl(asset.cfUid)}")`,
                  backgroundPosition: "center",
                  backgroundSize: "cover",
                }}
              />
              <div>
                <h2>{asset.titulo}</h2>
                <p>{asset.catalogNo}</p>
              </div>
            </a>
          ))}
        </section>
      )}
    </main>
  );
}
