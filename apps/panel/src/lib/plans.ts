import type { Tier } from "@/lib/tiers";

export type PremiumPlan = {
  code: Tier;
  name: string;
  priceUsd: number;
  days: number;
  tagline: string;
  access: string[];
  featured?: boolean;
};

export const premiumPlans: PremiumPlan[] = [
  {
    code: "base",
    name: "Base",
    priceUsd: 15,
    days: 30,
    tagline: "Acceso inicial al catálogo.",
    access: ["Publicaciones nivel Base"],
  },
  {
    code: "plus",
    name: "Plus",
    priceUsd: 30,
    days: 30,
    tagline: "Más contenido, un solo nivel.",
    access: ["Publicaciones Base", "Publicaciones Plus"],
    featured: true,
  },
  {
    code: "vip",
    name: "VIP",
    priceUsd: 50,
    days: 30,
    tagline: "Acceso a todos los niveles publicados.",
    access: ["Publicaciones Base", "Publicaciones Plus", "Publicaciones VIP"],
  },
];
