import Link from "next/link";
import { premiumPlans } from "@/lib/plans";

export default function PlanCards() {
  const telegramUsername = process.env.TELEGRAM_BOT_USERNAME?.trim().replace(/^@/, "");
  const telegramUrl =
    telegramUsername && /^[A-Za-z0-9_]{5,32}$/.test(telegramUsername)
      ? `https://t.me/${telegramUsername}`
      : null;

  return (
    <>
      <div className="plans-grid">
        {premiumPlans.map((plan) => (
          <article
            className={`plan-card ${plan.featured ? "featured" : ""}`}
            key={plan.code}
          >
            <div className="plan-card-top">
              <div>
                <p className="eyebrow">MEMBRESÍA {plan.code.toUpperCase()}</p>
                <h2>{plan.name}</h2>
              </div>
              {plan.featured && <span className="pill ready">Más elegido</span>}
            </div>
            <p className="plan-tagline">{plan.tagline}</p>
            <p className="plan-price">
              <strong>USD {plan.priceUsd}</strong>
              <span>/ {plan.days} días</span>
            </p>
            <p className="plan-access-label">Incluye</p>
            <ul className="plan-access">
              {plan.access.map((item) => <li key={item}>{item}</li>)}
            </ul>
            <p className="plan-renewal">
              Vigencia de {plan.days} días. Renovación manual; no hay cobro automático.
            </p>
            {telegramUrl ? (
              <a
                className={`button ${plan.featured ? "primary" : ""} plan-button`}
                href={telegramUrl}
                target="_blank"
                rel="noreferrer"
              >
                Abrir bot y consultar /planes
              </a>
            ) : (
              <span className="plan-button-disabled">Pago online no disponible</span>
            )}
          </article>
        ))}
      </div>
      <aside className="notice plan-notice">
        <strong>Pago y activación.</strong> Estos son los importes USD que ya muestra el bot. El panel no acepta pagos: los importes en ARS todavía no están definidos y Mercado Pago no está conectado. En Telegram, consulta <code>/planes</code>, envía el comprobante y espera la revisión manual de administración. El acceso se activa únicamente después de aprobar el pago. No hay renovación automática.
      </aside>
      <div className="plan-contact">
        <span>¿Ya tienes tu enlace de socio?</span>
        <Link className="button quiet" href="/login">Acceso de socios</Link>
      </div>
    </>
  );
}
