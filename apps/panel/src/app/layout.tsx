import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Panel privado",
  description: "Catálogo privado y panel de rendimiento.",
  referrer: "no-referrer",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
