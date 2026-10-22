"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Upload } from "tus-js-client";
import { isTier, type Tier } from "@/lib/tiers";

export function UploadForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [tier, setTier] = useState<Tier>("base");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError(true);
      setStatus("Selecciona un video.");
      return;
    }
    const allowedExtension = /\.(mp4|mov|m4v|webm)$/i.test(file.name);
    if (!allowedExtension || file.size === 0 || file.size > 500 * 1024 * 1024) {
      setError(true);
      setStatus("Selecciona MP4, MOV, M4V o WebM de hasta 500 MiB.");
      return;
    }
    setBusy(true);
    setError(false);
    setStatus("Reservando número de catálogo…");
    try {
      const response = await fetch("/api/studio/assets/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ titulo: title, visibilityTier: tier }),
      });
      const result = (await response.json()) as {
        error?: string;
        catalogNo?: string;
        uploadURL?: string;
        assetId?: string;
      };
      if (!response.ok || !result.uploadURL || !result.assetId || !result.catalogNo) {
        throw new Error(result.error || "No se pudo iniciar la carga.");
      }

      const uploadURL = result.uploadURL;
      setStatus(`Número ${result.catalogNo} reservado. Subiendo a Cloudflare Stream…`);
      await new Promise<void>((resolve, reject) => {
        const upload = new Upload(file, {
          uploadUrl: uploadURL,
          metadata: { name: title, filetype: file.type || "application/octet-stream" },
          retryDelays: [0, 1000, 3000, 5000],
          onProgress(bytesUploaded, bytesTotal) {
            const percent = Math.round((bytesUploaded / bytesTotal) * 100);
            setStatus(`Subiendo ${result.catalogNo} a Cloudflare Stream… ${percent}%`);
          },
          onError(uploadError) {
            reject(uploadError);
          },
          onSuccess() {
            resolve();
          },
        });
        upload.start();
      });

      setStatus(`Carga completada (${result.catalogNo}). Esperando el procesamiento de Cloudflare…`);
      setTitle("");
      setFile(null);
      const input = document.querySelector<HTMLInputElement>("#video-file");
      if (input) input.value = "";
      router.refresh();
    } catch (cause) {
      setError(true);
      setStatus(
        cause instanceof Error
          ? cause.message
          : "La carga falló; el número reservado no se reutiliza.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit}>
      <div className="upload-grid">
        <label className="field">
          Título
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            maxLength={120}
            required
            placeholder="Ej. Sesión de verano"
          />
        </label>
        <label className="field">
          Nivel mínimo
          <select value={tier} onChange={(event) => setTier(event.target.value as Tier)}>
            <option value="base">Base</option>
            <option value="plus">Plus</option>
            <option value="vip">VIP</option>
          </select>
        </label>
        <label className="field file-field">
          Video · MP4, MOV o WebM
          <input
            id="video-file"
            type="file"
            accept="video/mp4,video/quicktime,video/webm,.mp4,.mov,.m4v,.webm"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            required
          />
        </label>
        <button className="button primary" type="submit" disabled={busy}>
          {busy ? "Subiendo…" : "Reservar y subir"}
        </button>
      </div>
      <p className={`status ${error ? "error" : ""}`} role="status" aria-live="polite">
        {status}
      </p>
    </form>
  );
}

export function AssetEditor({
  asset,
}: {
  asset: {
    id: string;
    titulo: string;
    visibilityTier: string;
    estado: string;
  };
}) {
  const router = useRouter();
  const [title, setTitle] = useState(asset.titulo);
  const [tier, setTier] = useState<Tier>(
    isTier(asset.visibilityTier) ? asset.visibilityTier : "base",
  );
  const [state, setState] = useState(asset.estado === "publicado" ? "publicado" : "borrador");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch(`/api/studio/assets/${asset.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ titulo: title, visibilityTier: tier, estado: state }),
      });
      const result = (await response.json()) as { error?: string };
      if (!response.ok) throw new Error(result.error || "No se pudo guardar.");
      setMessage("Guardado");
      router.refresh();
    } catch (cause) {
      setMessage(cause instanceof Error ? cause.message : "No se pudo guardar.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="inline-edit">
      <input
        aria-label="Título"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        maxLength={120}
      />
      <select
        aria-label="Nivel mínimo"
        value={tier}
        onChange={(event) => setTier(event.target.value as Tier)}
      >
        <option value="base">Base</option>
        <option value="plus">Plus</option>
        <option value="vip">VIP</option>
      </select>
      <select
        aria-label="Publicación"
        value={state}
        onChange={(event) => setState(event.target.value)}
      >
        <option value="borrador">Borrador</option>
        <option value="publicado">Publicado</option>
      </select>
      <button className="button" type="button" onClick={save} disabled={busy}>
        {busy ? "…" : "Guardar"}
      </button>
      {message && <span className="muted" style={{ fontSize: 10 }}>{message}</span>}
    </div>
  );
}

export function MemberInviteForm() {
  const [nick, setNick] = useState("");
  const [tier, setTier] = useState<Tier>("base");
  const [url, setUrl] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    setUrl("");
    try {
      const response = await fetch("/api/studio/members", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nick, tier }),
      });
      const result = (await response.json()) as { url?: string; error?: string };
      if (!response.ok || !result.url) throw new Error(result.error || "No se pudo crear el enlace.");
      setUrl(result.url);
      setMessage("Enlace personal · caduca en 30 días");
    } catch (cause) {
      setMessage(cause instanceof Error ? cause.message : "No se pudo crear el enlace.");
    } finally {
      setBusy(false);
    }
  }

  async function copyLink() {
    await navigator.clipboard.writeText(url);
    setMessage("Enlace copiado");
  }

  return (
    <>
      <form className="invite-form" onSubmit={submit}>
        <label className="field">
          Alias del socio
          <input
            value={nick}
            onChange={(event) => setNick(event.target.value)}
            maxLength={40}
            required
            placeholder="Ej. Socio 001"
          />
        </label>
        <label className="field">
          Nivel
          <select value={tier} onChange={(event) => setTier(event.target.value as Tier)}>
            <option value="base">Base</option>
            <option value="plus">Plus</option>
            <option value="vip">VIP</option>
          </select>
        </label>
        <button className="button primary" type="submit" disabled={busy}>
          {busy ? "Creando…" : "Crear enlace"}
        </button>
      </form>
      {message && <p className="status" role="status">{message}</p>}
      {url && (
        <div className="invite-result">
          <input aria-label="Enlace del socio" readOnly value={url} />
          <button className="button" type="button" onClick={copyLink}>Copiar enlace</button>
        </div>
      )}
    </>
  );
}

export function LogoutButton() {
  const router = useRouter();

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.replace("/login");
    router.refresh();
  }

  return <button className="button quiet" type="button" onClick={logout}>Cerrar sesión</button>;
}

export function ViewTracker({
  token,
  assetId,
  src,
  title,
}: {
  token: string;
  assetId: string;
  src: string;
  title: string;
}) {
  const [sent, setSent] = useState(false);
  const [message, setMessage] = useState("");

  async function track() {
    if (sent) return;
    setSent(true);
    try {
      const response = await fetch("/api/assets/view", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, assetId }),
      });
      if (!response.ok) setMessage("No se pudo registrar esta vista.");
    } catch {
      setMessage("No se pudo registrar esta vista.");
    }
  }

  return (
    <div>
      <iframe
        className="player-frame"
        src={src}
        title={title}
        onLoad={track}
        referrerPolicy="no-referrer"
        allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture"
        allowFullScreen
      />
      {message && <p className="status error" role="status">{message}</p>}
    </div>
  );
}
