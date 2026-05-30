import type { PlayerBrand } from "./state";

export type BrandPosture = "stock" | "wake-rewrite" | "warning";
export type PlayerModelDef = { label: string; hw: string | null };
export type PlayerBrandDef = {
  id: PlayerBrand;
  name: string;
  ch: string;
  posture: BrandPosture;
  models: readonly PlayerModelDef[];
};

/**
 * Single source of truth for player brands: display metadata (name, logo char, posture), the
 * model labels shown in the picker, and the `oppo_hardware_model` enum value each model maps to
 * (verified against resources/settings.xml). Both the Step 3 brand picker and mapping.ts derive
 * from this — neither keeps its own copy, so a model added here can't silently fail to map.
 */
export const PLAYER_BRANDS: readonly PlayerBrandDef[] = [
  {
    id: "oppo",
    name: "OPPO",
    ch: "O",
    posture: "stock",
    models: [
      { label: "UDP-203", hw: "udp_203" },
      { label: "UDP-205", hw: "udp_205" },
    ],
  },
  {
    id: "chinoppo",
    name: "Chinoppo",
    ch: "C",
    posture: "wake-rewrite",
    models: [
      { label: "M9201", hw: "chinoppo_m9201" },
      { label: "M9203", hw: "chinoppo_m9203" },
      { label: "M9205 V1", hw: "chinoppo_m9205_v1" },
      { label: "M9205C", hw: "chinoppo_m9205c" },
      { label: "M9200", hw: "chinoppo_m9200" },
      { label: "M9205", hw: "chinoppo_m9205" },
      { label: "M9702", hw: "chinoppo_m9702" },
    ],
  },
  {
    id: "magnetar",
    name: "Magnetar",
    ch: "M",
    posture: "warning",
    models: [
      { label: "UDP800", hw: "magnetar_udp800" },
      { label: "UDP900", hw: "magnetar_udp900" },
    ],
  },
  {
    id: "reavon",
    name: "Reavon",
    ch: "R",
    posture: "warning",
    models: [
      { label: "UBR-X100", hw: "reavon_ubrx100" },
      { label: "UBR-X110", hw: "reavon_ubrx110" },
      { label: "UBR-X200", hw: "reavon_ubrx200" },
    ],
  },
  {
    id: "cineultra",
    name: "CineUltra",
    ch: "CU",
    posture: "wake-rewrite",
    models: [
      { label: "V203", hw: "cineultra_v203" },
      { label: "V204", hw: "cineultra_v204" },
    ],
  },
  {
    id: "ipuk",
    name: "iPUK",
    ch: "iP",
    posture: "wake-rewrite",
    models: [{ label: "UHD8592", hw: "ipuk_uhd8592" }],
  },
  {
    id: "giec",
    name: "Giec",
    ch: "G",
    posture: "wake-rewrite",
    models: [{ label: "BDP-G5300", hw: "giec_bdp_g5300" }],
  },
  {
    id: "other",
    name: "Other / clone",
    ch: "?",
    posture: "stock",
    models: [
      { label: "Conservative default", hw: "udp_203" },
      { label: "Chinoppo eject-to-wake", hw: "chinoppo_m9205" },
    ],
  },
];

export function brandDef(id: PlayerBrand | null): PlayerBrandDef | undefined {
  return PLAYER_BRANDS.find((b) => b.id === id);
}

/** The `oppo_hardware_model` enum value for a brand + model label, or null if unknown. */
export function hwModelFor(brand: PlayerBrand | null, modelLabel: string | null): string | null {
  if (!brand || !modelLabel) return null;
  return brandDef(brand)?.models.find((m) => m.label === modelLabel)?.hw ?? null;
}

/** True when the brand needs the eject-to-wake (#EJT) quirk handled before other commands. */
export function isWakeRewriteBrand(brand: PlayerBrand | null): boolean {
  return brandDef(brand)?.posture === "wake-rewrite";
}
