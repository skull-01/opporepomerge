// @vitest-environment node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * `src-tauri/installer.nsi` is a VENDORED copy of Tauri's NSIS installer
 * template, edited to suppress the built-in reinstall page (see
 * `src-tauri/installer-hooks.nsh`). It must track the `@tauri-apps/cli`
 * version that actually builds the installer — a silent CLI bump would render
 * against a diverged template. This guard fails the build until the template
 * is consciously re-vendored and its version stamp updated.
 */
function read(rel: string): string {
  return readFileSync(new URL(rel, import.meta.url), "utf8");
}

describe("vendored NSIS template", () => {
  it("version stamp matches the resolved @tauri-apps/cli", () => {
    const stamped = read("../src-tauri/installer.nsi").match(
      /oppo-nsis-template-version:\s*(\S+)/,
    )?.[1];

    const lock = JSON.parse(read("../package-lock.json"));
    const cliVersion = lock.packages?.["node_modules/@tauri-apps/cli"]?.version as string;

    expect(stamped, "template carries a version stamp").toBeTruthy();
    expect(cliVersion, "@tauri-apps/cli resolved in lockfile").toBeTruthy();
    expect(stamped).toBe(cliVersion);
  });

  it("tauri.conf.json points nsis.template at the vendored file", () => {
    const conf = JSON.parse(read("../src-tauri/tauri.conf.json"));
    expect(conf.bundle?.windows?.nsis?.template).toBe("installer.nsi");
  });
});
