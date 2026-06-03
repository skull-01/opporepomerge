import { describe, expect, it } from "vitest";
import { OPPO_HTTP_CATEGORY_LABELS, OPPO_HTTP_COMMANDS } from "./http-commands";

describe("OPPO HTTP command catalog", () => {
  it("has the full contributed endpoint set, all unique and well-formed", () => {
    expect(OPPO_HTTP_COMMANDS.length).toBe(61);
    const eps = OPPO_HTTP_COMMANDS.map((c) => c.endpoint);
    expect(new Set(eps).size).toBe(eps.length);
    expect(eps.every((e) => e.startsWith("/") && e.length > 1)).toBe(true);
  });

  it("every command's category has a display label", () => {
    for (const c of OPPO_HTTP_COMMANDS) {
      expect(OPPO_HTTP_CATEGORY_LABELS[c.category], c.endpoint).toBeTruthy();
    }
  });

  it("credential-bearing (sensitive) endpoints are state-changing and need params", () => {
    const sensitive = OPPO_HTTP_COMMANDS.filter((c) => c.sensitive);
    for (const c of sensitive) {
      expect(c.control, c.endpoint).toBe(true);
      expect(c.needsParams, c.endpoint).toBe(true);
    }
    expect(sensitive.map((c) => c.endpoint).sort()).toEqual(["/loginNfsServer", "/loginSambaWithID"]);
  });

  it("includes the endpoints the wizard already uses", () => {
    const eps = new Set(OPPO_HTTP_COMMANDS.map((c) => c.endpoint));
    for (const e of ["/playnormalfile", "/getmovieplayinfo", "/signin", "/checkfolderhasBDMV"]) {
      expect(eps.has(e), e).toBe(true);
    }
  });
});
