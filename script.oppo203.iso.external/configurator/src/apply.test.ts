// @vitest-environment happy-dom
import { describe, expect, it } from "vitest";
import { buildApplyFileSet } from "./apply";
import { INITIAL_STATE, type WizardState } from "./state";

function makeState(patch: Partial<WizardState>): WizardState {
  return { ...INITIAL_STATE, ...patch };
}

describe("buildApplyFileSet", () => {
  it("includes playercorefactory, keymap, and settings.xml keyed by userdata path", () => {
    const files = buildApplyFileSet(
      makeState({ playerBrand: "oppo", playerModel: "UDP-203" }),
      null,
    );
    expect(Object.keys(files).sort()).toEqual([
      "addon_data/script.oppo203.iso.external/settings.xml",
      "keymaps/oppo203iso.xml",
      "playercorefactory.xml",
    ]);
    expect(files["playercorefactory.xml"]).toContain('name="Oppo203ISO"');
    expect(files["addon_data/script.oppo203.iso.external/settings.xml"]).toContain(
      'id="oppo_hardware_model"',
    );
  });

  it("merges into an existing playercorefactory, keeping the user's player", () => {
    const existing =
      '<playercorefactory><players>' +
      '<player name="MPV"><filename>mpv</filename></player>' +
      '</players></playercorefactory>';
    const files = buildApplyFileSet(makeState({}), existing);
    expect(files["playercorefactory.xml"]).toContain('name="MPV"');
    expect(files["playercorefactory.xml"]).toContain('name="Oppo203ISO"');
  });

  it("merges into an existing settings.xml, preserving settings we do not own", () => {
    const existingSettings =
      '<settings version="2"><setting id="addon_language">de_DE</setting></settings>';
    const files = buildApplyFileSet(
      makeState({ playerBrand: "oppo", playerModel: "UDP-203" }),
      null,
      existingSettings,
    );
    const settings = files["addon_data/script.oppo203.iso.external/settings.xml"];
    expect(settings).toContain('id="addon_language">de_DE');
    expect(settings).toContain('id="oppo_hardware_model"');
  });
});
