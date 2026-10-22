import "server-only";
import { timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";
import { SignJWT, jwtVerify } from "jose";
import { nanoid } from "nanoid";
import { requiredEnv } from "@/lib/config";
import { isTier, type Tier } from "@/lib/tiers";

const cookieName = "panel_session";
const sessionDurationSeconds = 8 * 60 * 60;

function secretKey(): Uint8Array {
  const secret = requiredEnv("AUTH_SECRET");
  if (secret.length < 32) {
    throw new Error("AUTH_SECRET debe tener al menos 32 caracteres.");
  }
  return new TextEncoder().encode(secret);
}

function constantTimeEqual(input: string, expected: string): boolean {
  const inputBytes = Buffer.from(input);
  const expectedBytes = Buffer.from(expected);
  return inputBytes.length === expectedBytes.length &&
    timingSafeEqual(inputBytes, expectedBytes);
}

export async function verifyStudioCode(input: string): Promise<boolean> {
  const expected = requiredEnv("STUDIO_ACCESS_CODE");
  return constantTimeEqual(input, expected);
}

export async function createStudioSession(): Promise<void> {
  const token = await new SignJWT({ role: "model" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(`${sessionDurationSeconds}s`)
    .sign(secretKey());

  const cookieStore = await cookies();
  cookieStore.set(cookieName, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: sessionDurationSeconds,
  });
}

export async function destroyStudioSession(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(cookieName);
}

export async function hasStudioSession(): Promise<boolean> {
  const token = (await cookies()).get(cookieName)?.value;
  if (!token) return false;
  const key = secretKey();
  try {
    const { payload } = await jwtVerify(token, key, {
      algorithms: ["HS256"],
    });
    return payload.role === "model";
  } catch {
    return false;
  }
}

export async function createMemberToken(
  nick: string,
  tier: Tier,
): Promise<string> {
  return new SignJWT({ nick, tier, purpose: "member" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setJti(nanoid(12))
    .setExpirationTime("30d")
    .sign(secretKey());
}

export async function verifyMemberToken(
  token: string,
): Promise<{ nick: string; tier: Tier } | null> {
  const key = secretKey();
  try {
    const { payload } = await jwtVerify(token, key, {
      algorithms: ["HS256"],
    });
    if (
      payload.purpose !== "member" ||
      typeof payload.nick !== "string" ||
      !payload.nick ||
      !isTier(payload.tier)
    ) {
      return null;
    }
    return { nick: payload.nick, tier: payload.tier };
  } catch {
    return null;
  }
}
