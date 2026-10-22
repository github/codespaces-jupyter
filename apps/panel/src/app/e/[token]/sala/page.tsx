import Link from "next/link";
import { notFound } from "next/navigation";
import { verifyMemberToken } from "@/lib/auth";
import { isTier } from "@/lib/tiers";
import { AvatarRoom } from "./room";

export const dynamic = "force-dynamic";

export default async function MemberRoomPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const member = await verifyMemberToken(token);
  if (!member || !isTier(member.tier)) notFound();

  return (
    <main className="shell">
      <header className="topbar">
        <Link className="brand" href={`/e/${encodeURIComponent(token)}`}>
          CATÁLOGO <span>PRIVADO</span>
        </Link>
        <span className="pill ready">{member.tier.toUpperCase()}</span>
      </header>
      <AvatarRoom token={token} nick={member.nick} />
    </main>
  );
}
