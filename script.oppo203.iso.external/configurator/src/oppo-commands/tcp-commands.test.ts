import { describe, expect, it } from "vitest";
import { OPPO_TCP_CATEGORY_LABELS, OPPO_TCP_COMMANDS } from "./tcp-commands";

describe("OPPO TCP command catalog", () => {
  it("is non-empty, all commands unique and well-formed", () => {
    expect(OPPO_TCP_COMMANDS.length).toBe(93);
    const cmds = OPPO_TCP_COMMANDS.map((c) => c.command);
    expect(new Set(cmds).size).toBe(cmds.length);
    expect(cmds.every((c) => c.startsWith("#") && c.length >= 4)).toBe(true);
  });

  it("every command's category has a display label", () => {
    for (const c of OPPO_TCP_COMMANDS) {
      expect(OPPO_TCP_CATEGORY_LABELS[c.category], c.command).toBeTruthy();
    }
  });

  it("status queries are read-only; control commands are flagged", () => {
    for (const c of OPPO_TCP_COMMANDS) {
      if (c.category === "query") expect(c.control, c.command).toBeFalsy();
      else expect(c.control, c.command).toBe(true);
    }
  });

  it("excludes the add-on's forbidden tokens", () => {
    const cmds = OPPO_TCP_COMMANDS.map((c) => c.command);
    for (const bad of ["#SIS", "#PGU", "#PGD"]) {
      expect(cmds.includes(bad), bad).toBe(false);
    }
  });

  it("includes the commands the add-on already drives", () => {
    const cmds = new Set(OPPO_TCP_COMMANDS.map((c) => c.command));
    for (const c of ["#PON", "#POF", "#EJT", "#PLA", "#STP", "#QPL", "#QFN", "#SVM 3"]) {
      expect(cmds.has(c), c).toBe(true);
    }
  });
});
