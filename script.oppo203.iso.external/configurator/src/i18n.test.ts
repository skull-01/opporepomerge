import { beforeEach, describe, expect, it } from "vitest";
import { en, getLocale, setLocale, t, type MessageKey } from "./i18n";

beforeEach(() => setLocale("en"));

describe("i18n", () => {
  it("returns the English string for a known key", () => {
    expect(t("app.title")).toBe(en["app.title"]);
    expect(t("window.minimize")).toBe("Minimize");
    expect(t("window.close")).toBe("Close");
  });

  it("interpolates {name} placeholders from vars", () => {
    expect(t("app.versionLine", { name: "Configurator", version: "0.8.6" })).toBe(
      "Configurator-v0.8.6"
    );
  });

  it("falls back to the key itself for an unknown key (degrades visibly)", () => {
    expect(t("does.not.exist" as MessageKey)).toBe("does.not.exist");
  });

  it("defaults to the en locale", () => {
    expect(getLocale()).toBe("en");
  });

  it("every catalog value is a non-empty string", () => {
    for (const [key, value] of Object.entries(en)) {
      expect(value, key).toBeTypeOf("string");
      expect(value.length, key).toBeGreaterThan(0);
    }
  });
});
