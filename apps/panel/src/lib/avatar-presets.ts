export const avatarScenePresets = [
  { id: "studio", label: "Estudio", prompt: "a clean photography studio with a soft neutral backdrop and professional softbox lighting" },
  { id: "cafe", label: "Cafetería", prompt: "a bright modern café with warm wood, a window seat, and soft morning light" },
  { id: "gym", label: "Gimnasio", prompt: "a contemporary fitness studio with exercise equipment in the background, fully clothed athletic wear" },
  { id: "kitchen", label: "Cocina", prompt: "a tasteful modern home kitchen with natural daylight and a calm lifestyle atmosphere" },
  { id: "rooftop", label: "Terraza", prompt: "an elegant rooftop terrace at golden hour with a softly blurred city skyline" },
  { id: "office", label: "Estudio de trabajo", prompt: "a cozy home office with bookshelves, a desk, and warm practical lighting" },
] as const;

export type AvatarScenePresetId = (typeof avatarScenePresets)[number]["id"];

export function avatarScenePreset(id: string) {
  return avatarScenePresets.find((preset) => preset.id === id) ?? null;
}
