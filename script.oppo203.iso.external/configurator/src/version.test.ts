// @vitest-environment node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The configurator version is pinned in three files that must agree, or a
 * `tauri build` produces mismatched crate / installer / artifact versions.
 * This is the configurator-scale analogue of the add-on's sync_version guard.
 */
function read(rel: string): string {
  return readFileSync(new URL(rel, import.meta.url), "utf8");
}

describe("configurator version consistency", () => {
  it("package.json, Cargo.toml, and tauri.conf.json declare the same version", () => {
    const pkg = JSON.parse(read("../package.json")).version as string;
    const tauri = JSON.parse(read("../src-tauri/tauri.conf.json")).version as string;
    const cargo = read("../src-tauri/Cargo.toml").match(/^version\s*=\s*"([^"]+)"/m)?.[1];

    expect(pkg).toBeTruthy();
    expect(tauri).toBe(pkg);
    expect(cargo).toBe(pkg);
  });
});
