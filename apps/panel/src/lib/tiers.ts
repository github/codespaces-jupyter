export const tiers = ["base", "plus", "vip"] as const;
export type Tier = (typeof tiers)[number];

export function isTier(value: unknown): value is Tier {
  return typeof value === "string" && tiers.some((tier) => tier === value);
}

export function canViewTier(memberTier: Tier, assetTier: Tier): boolean {
  return tiers.indexOf(memberTier) >= tiers.indexOf(assetTier);
}
