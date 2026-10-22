"use client";

import { useEffect, useState, type FormEvent } from "react";
import Image from "next/image";
import { avatarScenePresets } from "@/lib/avatar-presets";

type ModelSummary = {
  id: string;
  name: string;
  description: string;
  creado: string;
};

type AvatarDetail = ModelSummary & {
  image: string;
};

type SceneSummary = {
  id: string;
  preset: string;
  creado: string;
};

type Scene = {
  id: string;
  preset: string;
  image: string;
  creado: string;
};

async function readResponse<T>(response: Response): Promise<T> {
  let result: T & { error?: string };
  try {
    result = (await response.json()) as T & { error?: string };
  } catch {
    throw new Error(`El servidor respondió con un formato no válido (HTTP ${response.status}).`);
  }
  if (!response.ok) {
    throw new Error(result.error || `La solicitud falló (HTTP ${response.status}).`);
  }
  return result;
}

async function compressPhoto(file: File): Promise<File> {
  const bitmap = await createImageBitmap(file);
  try {
    const scale = Math.min(1, 1280 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(bitmap.width * scale));
    canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Este navegador no pudo preparar la foto.");
    context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob(
        (output) => output ? resolve(output) : reject(new Error("No se pudo comprimir la foto.")),
        "image/jpeg",
        0.86,
      );
    });
    return new File([blob], "referencia.jpg", { type: "image/jpeg" });
  } finally {
    bitmap.close();
  }
}

export function AvatarModelStudio({ initialModels }: { initialModels: ModelSummary[] }) {
  const [models, setModels] = useState(initialModels);
  const [selectedId, setSelectedId] = useState("");
  const [detail, setDetail] = useState<AvatarDetail | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState("");
  const [consentConfirmed, setConsentConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [generatingScene, setGeneratingScene] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    if (initialModels[0]) void openModel(initialModels[0].id);
    // Load the newest server record on mount; the initial list only contains metadata.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function openModel(id: string) {
    setSelectedId(id);
    setStatus("");
    setError(false);
    try {
      const response = await fetch(`/api/studio/avatar-models/${encodeURIComponent(id)}`, {
        cache: "no-store",
      });
      const result = await readResponse<{ model: ModelSummary; scenes: SceneSummary[] }>(response);
      setDetail({
        ...result.model,
        image: `/api/studio/avatar-models/${encodeURIComponent(id)}/image`,
      });
      setScenes(result.scenes.map((scene) => ({
        ...scene,
        image: `/api/studio/avatar-models/${encodeURIComponent(id)}/image?scene=${encodeURIComponent(scene.id)}`,
      })));
    } catch (cause) {
      setDetail(null);
      setScenes([]);
      setError(true);
      setStatus(cause instanceof Error ? cause.message : "No se pudo cargar el modelo.");
    }
  }

  async function createModel(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!photo) {
      setError(true);
      setStatus("Selecciona una foto de referencia.");
      return;
    }
    setBusy(true);
    setError(false);
    setStatus("Preparando la foto. La generación puede tardar hasta dos minutos y consume saldo de Venice…");
    try {
      const compressed = await compressPhoto(photo);
      if (compressed.size > 6 * 1024 * 1024) {
        throw new Error("La foto comprimida supera el máximo de 6 MiB.");
      }
      const form = new FormData();
      form.set("name", name);
      form.set("description", description);
      form.set("consentConfirmed", String(consentConfirmed));
      form.set("photo", compressed);

      const response = await fetch("/api/studio/avatar-models", {
        method: "POST",
        body: form,
      });
      const result = await readResponse<{ model: ModelSummary }>(response);
      setModels((current) => [result.model, ...current]);
      setName("");
      setDescription("");
      setPhoto(null);
      setPhotoPreview("");
      setConsentConfirmed(false);
      await openModel(result.model.id);
      setStatus("Avatar creado. El archivo original no se guarda; solo se conserva el resultado generado.");
    } catch (cause) {
      setError(true);
      setStatus(cause instanceof Error ? cause.message : "No se pudo crear el avatar.");
    } finally {
      setBusy(false);
    }
  }

  async function generateScene(preset: string) {
    if (!selectedId || generatingScene) return;
    const presetLabel = avatarScenePresets.find((item) => item.id === preset)?.label || preset;
    if (!window.confirm(`Generar “${presetLabel}” consume saldo de Venice. ¿Continuar?`)) return;
    setGeneratingScene(preset);
    setStatus(`Generando escena. Esta operación consume saldo de Venice…`);
    setError(false);
    try {
      const response = await fetch(
        `/api/studio/avatar-models/${encodeURIComponent(selectedId)}/scenes`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ preset }),
        },
      );
      const result = await readResponse<{ scene: SceneSummary }>(response);
      setScenes((current) => [...current, {
        ...result.scene,
        image: `/api/studio/avatar-models/${encodeURIComponent(selectedId)}/image?scene=${encodeURIComponent(result.scene.id)}`,
      }]);
      setStatus("Decorado guardado.");
    } catch (cause) {
      setError(true);
      setStatus(cause instanceof Error ? cause.message : "No se pudo generar el decorado.");
    } finally {
      setGeneratingScene("");
    }
  }

  function selectPhoto(file: File | undefined) {
    setPhotoPreview("");
    setPhoto(null);
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type) || file.size > 6 * 1024 * 1024) {
      setError(true);
      setStatus("Selecciona una foto JPG, PNG o WebP de hasta 6 MiB.");
      return;
    }
    setError(false);
    setStatus("");
    setPhoto(file);
    setPhotoPreview(URL.createObjectURL(file));
  }

  useEffect(() => () => {
    if (photoPreview) URL.revokeObjectURL(photoPreview);
  }, [photoPreview]);

  return (
    <>
      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">CREADOR DE AVATAR</p>
            <h2>Crear desde una foto</h2>
            <p>Sube una referencia autorizada y describe el estilo del personaje.</p>
          </div>
        </div>
        <form className="avatar-create-form" onSubmit={createModel}>
          <label className="field">
            Nombre del modelo
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              maxLength={60}
              required
              placeholder="Ej. Luna"
            />
          </label>
          <label className="field">
            Descripción y dirección creativa
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              maxLength={500}
              required
              rows={3}
              placeholder="Ej. estilo elegante, pelo castaño ondulado, luz cálida y fondo de estudio."
            />
          </label>
          <label className="field avatar-photo-field">
            Foto de referencia · JPG, PNG o WebP, hasta 6 MiB
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(event) => selectPhoto(event.target.files?.[0])}
              required
            />
          </label>
          {photoPreview && (
            <Image
              className="avatar-photo-preview"
              src={photoPreview}
              alt="Vista previa de la foto seleccionada"
              width={1280}
              height={1280}
              unoptimized
            />
          )}
          <label className="avatar-consent">
            <input
              type="checkbox"
              checked={consentConfirmed}
              onChange={(event) => setConsentConfirmed(event.target.checked)}
              required
            />
            <span>Confirmo que la persona de la foto es adulta y autorizó su uso para crear este avatar.</span>
          </label>
          <button className="button primary" type="submit" disabled={busy || !consentConfirmed}>
            {busy ? "Creando avatar…" : "Crear avatar"}
          </button>
        </form>
        <p className={`status ${error ? "error" : ""}`} role={error ? "alert" : "status"}>
          {status || "La foto original solo se usa para esta generación; guardamos el avatar resultante en PostgreSQL."}
        </p>
      </section>

      {models.length > 0 && (
        <section className="avatar-workspace">
          <aside className="panel avatar-model-list">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">TUS MODELOS</p>
                <h2>Personajes creados</h2>
              </div>
            </div>
            <div className="avatar-model-buttons">
              {models.map((item) => (
                <button
                  className={`avatar-model-button ${selectedId === item.id ? "selected" : ""}`}
                  key={item.id}
                  type="button"
                  onClick={() => openModel(item.id)}
                >
                  <strong>{item.name}</strong>
                  <span>{new Date(item.creado).toLocaleDateString("es-AR")}</span>
                </button>
              ))}
            </div>
          </aside>

          <section className="panel avatar-detail">
            {detail ? (
              <>
                <div className="panel-heading">
                  <div>
                    <p className="eyebrow">IDENTIDAD DE REFERENCIA</p>
                    <h2>{detail.name}</h2>
                    <p>{detail.description}</p>
                  </div>
                </div>
                <Image
                  className="avatar-generated-image"
                  src={detail.image}
                  alt={`Avatar generado de ${detail.name}`}
                  width={1024}
                  height={1024}
                  unoptimized
                />

                <div className="scene-generator">
                  <div>
                    <p className="eyebrow">DECORADOS</p>
                    <p className="muted">Cada generación es una edición de imagen facturable.</p>
                  </div>
                  <div className="scene-preset-buttons">
                    {avatarScenePresets.map((preset) => {
                      const alreadyGenerated = scenes.some((scene) => scene.preset === preset.id);
                      return (
                        <button
                          className="button quiet"
                          disabled={Boolean(generatingScene) || alreadyGenerated}
                          key={preset.id}
                          type="button"
                          onClick={() => generateScene(preset.id)}
                        >
                          {generatingScene === preset.id
                            ? "Generando…"
                            : alreadyGenerated
                              ? `${preset.label} · listo`
                              : preset.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
                {scenes.length > 0 && (
                  <div className="avatar-scenes-grid">
                    {scenes.map((scene) => {
                      const preset = avatarScenePresets.find((item) => item.id === scene.preset);
                      return (
                        <figure key={scene.id}>
                          <Image
                            src={scene.image}
                            alt={`${detail.name} en ${preset?.label || scene.preset}`}
                            width={1024}
                            height={1536}
                            unoptimized
                          />
                          <figcaption>{preset?.label || scene.preset}</figcaption>
                        </figure>
                      );
                    })}
                  </div>
                )}
              </>
            ) : (
              <div className="empty">{status || "Selecciona un modelo para ver su avatar."}</div>
            )}
          </section>
        </section>
      )}
    </>
  );
}
