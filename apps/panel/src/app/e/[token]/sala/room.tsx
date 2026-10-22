"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export function AvatarRoom({ token, nick }: { token: string; nick: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [status, setStatus] = useState("");
  const [mediaError, setMediaError] = useState("");
  const [camera, setCamera] = useState<MediaStream | null>(null);
  const [screen, setScreen] = useState<MediaStream | null>(null);
  const [previewMode, setPreviewMode] = useState<"camera" | "screen" | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const chatRef = useRef<HTMLDivElement>(null);
  const activeStreamsRef = useRef<MediaStream[]>([]);
  const speechSupported =
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    "SpeechSynthesisUtterance" in window;

  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();
    };
  }, []);

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  useEffect(() => {
    const controller = new AbortController();
    async function loadHistory() {
      setStatus("");
      try {
        const response = await fetch("/api/member/chat", {
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal,
        });
        let result: { error?: string; messages?: ChatMessage[] };
        try {
          result = (await response.json()) as typeof result;
        } catch {
          throw new Error(`El servidor respondió con un formato no válido (HTTP ${response.status}).`);
        }
        if (!response.ok || !Array.isArray(result.messages)) {
          throw new Error(result.error || "No se pudo cargar el historial del chat.");
        }
        setMessages(result.messages.length ? result.messages : [{
          role: "assistant",
          content: `Hola ${nick}. Soy tu avatar de conversación. ¿Sobre qué te gustaría charlar?`,
        }]);
      } catch (cause) {
        if (!controller.signal.aborted) {
          setStatus(cause instanceof Error ? cause.message : "No se pudo cargar el historial del chat.");
        }
      } finally {
        if (!controller.signal.aborted) setLoadingHistory(false);
      }
    }
    void loadHistory();
    return () => controller.abort();
  }, [nick, token]);

  useEffect(() => {
    const video = videoRef.current;
    const stream = previewMode === "screen" ? screen : previewMode === "camera" ? camera : null;
    activeStreamsRef.current = [camera, screen].filter(
      (mediaStream): mediaStream is MediaStream => mediaStream !== null,
    );
    if (video) video.srcObject = stream;
  }, [camera, previewMode, screen]);

  useEffect(() => () => {
    activeStreamsRef.current.forEach((stream) => {
      stream.getTracks().forEach((track) => track.stop());
    });
  }, []);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = draft.trim();
    if (!content || sending || loadingHistory) return;

    const nextMessages = [...messages, { role: "user" as const, content }];
    setMessages(nextMessages);
    setDraft("");
    setSending(true);
    setStatus("");
    try {
      const response = await fetch("/api/member/chat", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content }),
      });
      let result: { error?: string; reply?: string };
      try {
        result = (await response.json()) as typeof result;
      } catch {
        throw new Error(`El servidor respondió con un formato no válido (HTTP ${response.status}).`);
      }
      if (!response.ok || typeof result.reply !== "string") {
        throw new Error(result.error || "No se pudo obtener una respuesta.");
      }
      const reply = result.reply;
      setMessages((current) => [...current, { role: "assistant", content: reply }]);
    } catch (cause) {
      setMessages((current) => current.slice(0, -1));
      setDraft(content);
      setStatus(cause instanceof Error ? cause.message : "No se pudo conectar con el avatar.");
    } finally {
      setSending(false);
    }
  }

  function speakLastReply() {
    const lastReply = [...messages].reverse().find((message) => message.role === "assistant");
    if (!lastReply || !speechSupported) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(lastReply.content));
  }

  async function toggleCamera() {
    setMediaError("");
    if (camera) {
      camera.getTracks().forEach((track) => track.stop());
      setCamera(null);
      if (previewMode === "camera") setPreviewMode(screen ? "screen" : null);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      setCamera(stream);
      setPreviewMode("camera");
    } catch {
      setMediaError("No se pudo abrir la cámara. Revisa los permisos del navegador y la conexión HTTPS.");
    }
  }

  async function toggleScreen() {
    setMediaError("");
    if (screen) {
      screen.getTracks().forEach((track) => track.stop());
      setScreen(null);
      if (previewMode === "screen") setPreviewMode(camera ? "camera" : null);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
      stream.getVideoTracks()[0]?.addEventListener("ended", () => {
        setScreen(null);
        setPreviewMode((mode) => (mode === "screen" ? (camera ? "camera" : null) : mode));
      }, { once: true });
      setScreen(stream);
      setPreviewMode("screen");
    } catch {
      setMediaError("No se compartió la pantalla. Puedes volver a intentarlo cuando quieras.");
    }
  }

  return (
    <section className="room">
      <div className="room-heading">
        <div>
          <p className="eyebrow">ESPACIO INTERACTIVO</p>
          <h1>Sala del avatar</h1>
          <p className="muted">Hola, {nick}. Conversa por texto o escucha las respuestas.</p>
        </div>
        <span className="pill ready">CHAT CON IA</span>
      </div>

      <div className="room-layout">
        <section className="avatar-panel" aria-label="Avatar y herramientas de llamada">
          <div className="avatar-stage">
            <div className="avatar-orbit" aria-hidden="true">
              <div className="avatar-face">
                <span className="avatar-eye avatar-eye-left" />
                <span className="avatar-eye avatar-eye-right" />
                <span className="avatar-smile" />
              </div>
            </div>
            <p className="avatar-name">Avatar de conversación</p>
            <p className="avatar-caption">Asistente de IA · voz del navegador</p>
          </div>

          <div className="media-preview">
            {previewMode ? (
              <video ref={videoRef} autoPlay muted playsInline aria-label="Vista previa local" />
            ) : (
              <div className="media-placeholder">
                <span aria-hidden="true">◉</span>
                <p>La cámara y la pantalla solo se muestran en tu navegador.</p>
              </div>
            )}
          </div>

          <div className="media-controls">
            <button className="button quiet" type="button" onClick={toggleCamera}>
              {camera ? "Apagar cámara" : "Probar cámara"}
            </button>
            <button className="button quiet" type="button" onClick={toggleScreen}>
              {screen ? "Detener pantalla" : "Compartir pantalla"}
            </button>
          </div>
          {mediaError && <p className="status error" role="alert">{mediaError}</p>}

          <div className="realtime-notice">
            <strong>Llamadas y directo</strong>
            <p>
              La vista previa no transmite video a otras personas. Para habilitar
              videollamadas y directos reales hace falta configurar un servicio de
              tiempo real y su señalización.
            </p>
            <div className="realtime-actions">
              <button className="button" type="button" disabled title="Pendiente de integrar un proveedor de tiempo real">
                Videollamada · pendiente
              </button>
              <button className="button" type="button" disabled title="Pendiente de integrar un proveedor de streaming">
                Transmisión · pendiente
              </button>
            </div>
          </div>
        </section>

        <section className="chat-panel" aria-label="Chat con el avatar">
          <div className="chat-heading">
            <div>
              <h2>Chat escrito</h2>
              <p>Las respuestas se generan con el modelo configurado en el servidor.</p>
            </div>
            <button
              className="button quiet"
              type="button"
              onClick={speakLastReply}
              disabled={!speechSupported}
              title={speechSupported ? "Escuchar la última respuesta" : "Este navegador no tiene voz TTS"}
            >
              Escuchar respuesta
            </button>
          </div>
          <div className="chat-messages" ref={chatRef} aria-live="polite">
            {loadingHistory && <p className="chat-typing" role="status">Cargando conversación…</p>}
            {messages.map((message, index) => (
              <article className={`chat-message ${message.role}`} key={`${index}-${message.role}`}>
                <span>{message.role === "assistant" ? "Avatar" : "Tú"}</span>
                <p>{message.content}</p>
              </article>
            ))}
            {sending && <p className="chat-typing" role="status">El avatar está pensando…</p>}
          </div>
          <form className="chat-form" onSubmit={sendMessage}>
            <label className="sr-only" htmlFor="avatar-message">Escribe tu mensaje</label>
            <textarea
              id="avatar-message"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              maxLength={1200}
              placeholder="Escribe un mensaje…"
              rows={2}
              required
            />
            <button className="button primary" type="submit" disabled={sending || loadingHistory || !draft.trim()}>
              {sending ? "Enviando…" : "Enviar"}
            </button>
          </form>
          {status && <p className="status error" role="alert">{status}</p>}
          <p className="chat-footnote">
            No compartas datos sensibles. Las respuestas se procesan con el proveedor de IA configurado.
          </p>
        </section>
      </div>
    </section>
  );
}
