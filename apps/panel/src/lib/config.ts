import "server-only";

export function requiredEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Falta configurar ${name} en apps/panel/.env.local.`);
  return value;
}

export function modelHandle(): string {
  return process.env.MODEL_HANDLE?.trim() || "demo";
}
