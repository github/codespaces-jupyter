import { NextRequest, NextResponse } from "next/server";
import { createStudioSession, verifyStudioCode } from "@/lib/auth";

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as { code?: unknown };
    if (typeof body.code !== "string" || body.code.length > 256) {
      return NextResponse.json({ error: "Código no válido." }, { status: 400 });
    }
    if (!(await verifyStudioCode(body.code))) {
      return NextResponse.json({ error: "Código incorrecto." }, { status: 401 });
    }
    await createStudioSession();
    return NextResponse.json({ ok: true });
  } catch (error) {
    console.error("No se pudo iniciar sesión en el panel:", error);
    return NextResponse.json(
      { error: "No se pudo iniciar sesión. Revisa la configuración del servidor." },
      { status: 503 },
    );
  }
}
