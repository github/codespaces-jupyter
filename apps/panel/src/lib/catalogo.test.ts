import { createHmac } from "node:crypto";
import { describe, expect, it } from "vitest";
import { canViewTier } from "./tiers";
import { verifyWebhookSignature } from "./cloudflare-signature";
import { premiumPlans } from "./plans";

describe("niveles de acceso", () => {
  it("permite ver contenido del mismo nivel o inferior", () => {
    expect(canViewTier("base", "base")).toBe(true);
    expect(canViewTier("plus", "base")).toBe(true);
    expect(canViewTier("plus", "vip")).toBe(false);
    expect(canViewTier("vip", "vip")).toBe(true);
  });
});

describe("planes premium", () => {
  it("muestra los precios actuales del bot sin inventar importes ni ciclos", () => {
    expect(premiumPlans.map(({ code, priceUsd, days }) => ({ code, priceUsd, days }))).toEqual([
      { code: "base", priceUsd: 15, days: 30 },
      { code: "plus", priceUsd: 30, days: 30 },
      { code: "vip", priceUsd: 50, days: 30 },
    ]);
  });
});

describe("firma del webhook de Cloudflare", () => {
  it("acepta una firma válida y rechaza firmas alteradas o vencidas", () => {
    const secret = "test-webhook-secret";
    const now = 1_800_000_000;
    const body = JSON.stringify({ uid: "stream-id" });
    const signature = createHmac("sha256", secret)
      .update(`${now}.${body}`)
      .digest("hex");
    const header = `time=${now},sig1=${signature}`;

    expect(verifyWebhookSignature(body, header, secret, now)).toBe(true);
    expect(verifyWebhookSignature(`${body} `, header, secret, now)).toBe(false);
    expect(verifyWebhookSignature(body, header, secret, now + 301)).toBe(false);
    expect(verifyWebhookSignature(body, null, secret, now)).toBe(false);
  });
});
