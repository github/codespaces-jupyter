import { NextResponse } from "next/server";
import { destroyStudioSession } from "@/lib/auth";

export async function POST() {
  await destroyStudioSession();
  return NextResponse.json({ ok: true });
}
