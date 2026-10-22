import "server-only";
import { requiredEnv } from "@/lib/config";
import { verifyWebhookSignature } from "@/lib/cloudflare-signature";

export function verifyCloudflareWebhook(
  rawBody: string,
  signatureHeader: string | null,
): boolean {
  return verifyWebhookSignature(
    rawBody,
    signatureHeader,
    requiredEnv("CLOUDFLARE_STREAM_WEBHOOK_SECRET"),
  );
}
