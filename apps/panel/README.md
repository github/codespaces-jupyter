# Panel privado

Aplicación Next.js independiente del bot de Telegram. Implementa un prototipo de panel de modelo con PostgreSQL, Drizzle ORM y Cloudflare Stream; los socios reciben enlaces firmados con un nivel de acceso.

## Requisitos

- Node.js 22
- pnpm 10
- Docker Compose
- Cuenta de Cloudflare con Stream y un token de API para crear subidas directas

## Desarrollo en el Codespace

```sh
cd apps/panel
pnpm install
cp .env.example .env.local
```

Edita `.env.local` en el Codespace. Genera un secreto privado con `openssl rand -base64 48`; úsalo como `AUTH_SECRET` y configura un valor distinto, largo y no reutilizado como `STUDIO_ACCESS_CODE`. Completa también `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_STREAM_TOKEN` y `CLOUDFLARE_CUSTOMER_CODE`. No pegues credenciales en el chat ni las subas a Git.

Para activar el chat del avatar y el creador de modelos, configura `VENICE_API_KEY` (también se acepta `VENICE_KEY`) y, opcionalmente, `VENICE_DEFAULT_CHAT_MODEL` y `VENICE_IMAGE_EDIT_MODEL` en `.env.local`; en producción, usa el gestor de secretos del host. La clave se envía desde el servidor a la API de Venice y nunca al navegador. El modelo de edición predeterminado es `firered-image-edit`; usa un modelo de edición compatible con `POST /image/edit` si cambias el valor.

Inicia PostgreSQL, crea las tablas y el modelo demo:

```sh
docker compose up -d
pnpm db:push
pnpm db:seed
```

El contenedor solo publica PostgreSQL en `127.0.0.1:5432` dentro del Codespace. `pnpm db:push` aplica el esquema Drizzle. Comprueba las cuatro tablas de aplicación:

```sh
docker compose exec postgres psql -U postgres -d postgres -c '\dt'
```

Arranca la app:

```sh
pnpm dev
```

Usa el puerto **3001** de la pestaña Ports; el puerto 3000 sigue reservado para el demo anterior. Abre la app en `https://<codespace>-3001.app.github.dev`, inicia sesión en `/login` con `STUDIO_ACCESS_CODE` y crea un enlace de socio. El enlace del socio incluye un token firmado con nivel Base, Plus o VIP, y vence a los 30 días.

La portada `/planes` y el estudio muestran los precios actualmente configurados en el bot: Base USD 15, Plus USD 30 y VIP USD 50, por 30 días, con los niveles de contenido que incluye cada uno. Son importes informativos en USD; este panel no tiene checkout, precios en ARS ni cobros automáticos. Si configuras `TELEGRAM_BOT_USERNAME`, se muestra un enlace al bot para continuar el flujo manual: `/planes`, comprobante y revisión por administración.

Los enlaces de socio incluyen una sala de avatar con chat de texto conectado a Venice, voz TTS del navegador y vista previa local de cámara/compartir pantalla. El historial del chat se guarda en PostgreSQL asociado al enlace de socio y se restaura al volver a la sala. `pnpm db:push` crea la tabla del chat. La vista previa no transmite cámara ni pantalla; videollamadas y transmisiones remotas requieren integrar un proveedor de tiempo real y no están habilitadas.

En `/studio/models`, el estudio puede crear un avatar desde una foto JPG/PNG/WebP autorizada de una persona adulta y una descripción, y luego generar decorados no explícitos desde la imagen resultante. Cada generación es una edición facturable de Venice. La foto original se envía para la generación inicial y no se guarda en la base; los resultados generados se guardan en PostgreSQL como base64. Aplica el esquema antes de usar esta función con `pnpm db:push`. La edición con referencia no garantiza identidad idéntica y no crea un embedding facial ni un vídeo animado/lip-sync.

## Conectar servidores MCP en VS Code

La configuración del workspace está en `.vscode/mcp.json` (raíz del repositorio). Al abrir esa carpeta en VS Code, los servidores Venice, GitHub y Hugging Face se pueden iniciar desde la vista **MCP Servers**; VS Code ejecuta el comando que figura en cada servidor. Para Venice se usa `npx -y @veniceai/mcp-server@0.3.0` y VS Code solicita `VENICE_API_KEY` como entrada secreta. No escribas la clave en `mcp.json`.

La conexión MCP es para las herramientas de VS Code; el chat de socios usa la API HTTPS de Venice desde Next.js. Son conexiones separadas: configura también `VENICE_API_KEY` en `.env.local` para desarrollo o en los secretos del despliegue. `Secyposbot/mcp.json` no es la configuración MCP que VS Code detecta automáticamente.

Mantén el puerto en **Private** para las pruebas normales. Para que Cloudflare pueda enviar webhooks al Codespace, la URL del webhook debe ser accesible públicamente; si habilitas temporalmente el puerto como Public, usa únicamente videos de prueba no sensibles, prueba el webhook firmado y vuelve a poner el puerto en Private. El `APP_BASE_URL` debe ser la URL HTTPS reenviada de Codespaces para que los enlaces compartidos apunten al host correcto.

## Cloudflare Stream

El panel crea una subida directa con `requireSignedURLs: false` y el navegador carga el archivo mediante TUS. Así se evita que el video pase por el servidor Next. Cloudflare asigna un UID primero; cuando se confirma la creación, PostgreSQL reserva atómicamente el número de catálogo y guarda el registro `subiendo`. Las cargas fallidas antes de crear el recurso no consumen correlativos.

Configura en Cloudflare Stream la notificación para:

```text
https://<host-publico>/api/webhooks/cloudflare
```

Guarda el secreto de firma entregado por Cloudflare como `CLOUDFLARE_STREAM_WEBHOOK_SECRET`. El webhook verifica `Webhook-Signature` (HMAC SHA-256 sobre el cuerpo intacto y el timestamp, con tolerancia de cinco minutos) antes de modificar el estado. Los estados `listo` y `error` se actualizan cuando llega la notificación.

## Límites de seguridad y funcionalidad

- El panel de modelo tiene una autenticación de código compartido para el prototipo; no es autenticación multiusuario y todavía no existen roles web de cliente, modelo y administrador.
- Los enlaces de socio están firmados y vencen, pero no hay gestión de pagos, suscripciones ni revocación individual de enlaces.
- La reproducción de Stream no está firmada. Quien obtenga el UID de un video puede acceder a su URL de reproducción aunque no tenga el enlace de socio. No uses contenido privado, identificable o sensible.
- Los webhooks sí comprueban la firma; el endpoint se puede exponer solo mientras sea necesario para las notificaciones.
- El panel registra una vista al cargar el reproductor. No registra eventos de venta reales; importes e ingresos permanecen en cero hasta integrar un proveedor de pagos.
- Esto no está listo para producción. Antes, implementa usuarios y roles reales, cuotas de inicio de sesión, reproducción firmada de Cloudflare, revocación y renovación de membresías, pagos con verificación del proveedor, auditoría y pruebas de autorización.

## Comandos

```sh
pnpm test
pnpm typecheck
pnpm lint
pnpm build
pnpm db:generate
pnpm db:push
pnpm db:seed
pnpm db:test-catalog
```

## Despliegue en Vercel

El proyecto puede importarse desde `apps/panel` como Root Directory. Configura una base Postgres administrada y los secretos únicamente en Environment Variables de Vercel. Usa la URL de producción como `APP_BASE_URL` y apunta el webhook de Cloudflare al host HTTPS desplegado. No conectes Vercel a la base efímera local del Codespace. La app aún no debe publicar material privado ni aceptar pagos reales.
