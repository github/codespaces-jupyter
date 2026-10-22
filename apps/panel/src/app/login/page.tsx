import { redirect } from "next/navigation";
import Link from "next/link";
import { hasStudioSession } from "@/lib/auth";
import LoginForm from "./login-form";

export const dynamic = "force-dynamic";

export default async function LoginPage() {
  if (await hasStudioSession()) redirect("/studio");

  return (
    <main className="shell">
      <header className="topbar">
        <Link className="brand" href="/">CATÁLOGO <span>PRIVADO</span></Link>
        <span className="muted" style={{ fontSize: 11 }}>Acceso protegido</span>
      </header>
      <div className="login-wrap">
        <section className="login-card">
          <p className="eyebrow">PANEL DE MODELO</p>
          <h1>Inicia sesión</h1>
          <p className="muted" style={{ fontSize: 13, lineHeight: 1.6 }}>
            Introduce el código privado configurado para este entorno.
          </p>
          <LoginForm />
        </section>
      </div>
    </main>
  );
}
