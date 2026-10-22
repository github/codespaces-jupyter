import { and, eq } from "drizzle-orm";
import { notFound } from "next/navigation";
import { getDb } from "@/db";
import { contentAsset } from "@/db/schema";
import { verifyMemberToken } from "@/lib/auth";
import { customerStreamUrl, currentModel } from "@/lib/model";
import { canViewTier, isTier } from "@/lib/tiers";
import { ViewTracker } from "@/app/studio/studio-actions";

export const dynamic = "force-dynamic";

export default async function MemberVideoPage({
  params,
}: {
  params: Promise<{ token: string; cat: string }>;
}) {
  const { token, cat } = await params;
  const member = await verifyMemberToken(token);
  if (!member || !isTier(member.tier)) notFound();

  const studioModel = await currentModel();
  const [asset] = await getDb()
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
        eq(contentAsset.catalogNo, cat),
        eq(contentAsset.estado, "publicado"),
      ),
    )
    .limit(1);

  if (
    !asset?.cfUid ||
    !isTier(asset.visibilityTier) ||
    !canViewTier(member.tier, asset.visibilityTier)
  ) {
    notFound();
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href={`/e/${encodeURIComponent(token)}`}>
          CATÁLOGO <span>PRIVADO</span>
        </a>
        <span className="pill ready">{member.tier.toUpperCase()}</span>
      </header>
      <section style={{ paddingTop: 24 }}>
        <ViewTracker
          token={token}
          assetId={asset.id}
          src={customerStreamUrl(asset.cfUid)}
          title={asset.titulo}
        />
        <div className="player-title">
          <p className="eyebrow">{asset.catalogNo}</p>
          <h1>{asset.titulo}</h1>
          <p className="muted" style={{ fontSize: 12 }}>{studioModel.nombre}</p>
        </div>
      </section>
    </main>
  );
}
