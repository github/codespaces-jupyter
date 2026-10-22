import Link from "next/link";
import PlanCards from "./plan-cards";

export const metadata = {
  title: "Planes premium",
  description: "Compara los niveles Base, Plus y VIP del catálogo privado.",
};

export default function PlansPage() {
  return (
    <main className="shell">
      <header className="topbar">
        <Link className="brand" href="/">CATÁLOGO <span>PRIVADO</span></Link>
        <Link className="button quiet" href="/login">Panel de modelo</Link>
      </header>
      <section className="hero plans-hero">
        <p className="eyebrow">MEMBRESÍAS PREMIUM</p>
        <h1>Elige tu nivel,<br /><span>disfruta el catálogo.</span></h1>
        <p className="hero-copy">
          Los niveles superiores incluyen el contenido de los niveles anteriores. Cada plan dura 30 días.
        </p>
      </section>
      <PlanCards />
    </main>
  );
}
