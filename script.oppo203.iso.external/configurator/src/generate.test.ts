import { describe, expect, it } from "vitest";
import {
  buildDiscFolderRuleXml,
  buildKeymapXml,
  buildPlayercorefactoryXml,
  buildTransferFiles,
  KEYMAP_FILENAME,
  kodiTargetForPlatform,
  parseDiscFolders,
} from "./generate";

describe("kodiTargetForPlatform", () => {
  it("derives CoreELEC paths", () => {
    const t = kodiTargetForPlatform("coreelec");
    expect(t.pythonPath).toBe("/usr/bin/python3");
    expect(t.externalPlayerScript).toBe(
      "/storage/.kodi/addons/script.oppo203.iso.external/resources/lib/external_player.py",
    );
    expect(t.addonDataDir).toBe(
      "/storage/.kodi/userdata/addon_data/script.oppo203.iso.external",
    );
  });

  it("uses backslash paths on Windows", () => {
    const t = kodiTargetForPlatform("windows");
    expect(t.addonDataDir).toBe(
      "%APPDATA%\\Kodi\\userdata\\addon_data\\script.oppo203.iso.external",
    );
  });

  it("honors a custom python path", () => {
    expect(kodiTargetForPlatform("coreelec", "/opt/py/python3").pythonPath).toBe("/opt/py/python3");
  });
});

describe("buildPlayercorefactoryXml", () => {
  const target = kodiTargetForPlatform("coreelec");

  it("embeds the external player with the target paths in <args>", () => {
    const xml = buildPlayercorefactoryXml(target);
    expect(xml).toContain('<player name="Oppo203ISO" type="ExternalPlayer"');
    expect(xml).toContain("<filename>/usr/bin/python3</filename>");
    expect(xml).toContain(
      '"/storage/.kodi/addons/script.oppo203.iso.external/resources/lib/external_player.py" --addon-data "/storage/.kodi/userdata/addon_data/script.oppo203.iso.external" --file "{1}"',
    );
  });

  it("includes the 4K iso rule and disc-folder rules by default", () => {
    const xml = buildPlayercorefactoryXml(target);
    expect(xml).toContain(
      '<rule filetypes="iso" filename=".*(4K|4k|UHD|uhd|2160p|2160P).*" player="Oppo203ISO"/>',
    );
    expect(xml).toContain('filetypes="bdmv"');
    expect(xml).toContain('filetypes="mpls"');
  });

  it("omits disc-folder rules when disabled", () => {
    const xml = buildPlayercorefactoryXml(target, false);
    expect(xml).not.toContain('filetypes="bdmv"');
    expect(xml).toContain('filetypes="iso"');
  });

  it("escapes XML metacharacters in paths", () => {
    const xml = buildPlayercorefactoryXml({
      pythonPath: "py&",
      externalPlayerScript: "a<b",
      addonDataDir: 'c"d',
    });
    expect(xml).toContain("py&amp;");
    expect(xml).toContain("a&lt;b");
    expect(xml).toContain("c&quot;d");
  });
});

describe("disc-folder routing rules (B / playercorefactory)", () => {
  const target = kodiTargetForPlatform("coreelec");

  it("parseDiscFolders splits, trims, and drops blanks", () => {
    expect(parseDiscFolders("  a/b \n\n c/d \n")).toEqual(["a/b", "c/d"]);
    expect(parseDiscFolders("")).toEqual([]);
    expect(parseDiscFolders(null)).toEqual([]);
  });

  it("emits tag-independent iso/bdmv/mpls rules per folder, regex-escaped + forward-slashed", () => {
    const xml = buildDiscFolderRuleXml([
      "smb://192.168.1.177/Super3Share/01Movies/01-4kDisc",
      "\\\\nas\\Discs\\",
    ]);
    expect(xml).toContain(
      '<rule filetypes="iso" filename=".*smb://192\\.168\\.1\\.177/Super3Share/01Movies/01-4kDisc.*" player="Oppo203ISO"/>',
    );
    expect(xml).toContain('filetypes="bdmv" filename=".*smb://192\\.168\\.1\\.177');
    expect(xml).toContain('filetypes="mpls" filename=".*smb://192\\.168\\.1\\.177');
    // UNC normalized to forward slashes, trailing slash dropped
    expect(xml).toContain(".*//nas/Discs.*");
    // no 4K/UHD tag required for folder routing
    expect(xml).not.toContain("2160p");
  });

  it("includes folder rules alongside the 4K rule in the full document", () => {
    const xml = buildPlayercorefactoryXml(target, true, ["smb://nas/Movies/Discs"]);
    expect(xml).toContain(".*smb://nas/Movies/Discs.*");
    expect(xml).toContain('filename=".*(4K|4k|UHD|uhd|2160p|2160P).*"');
  });

  it("is a no-op (byte-identical) when no folders are configured", () => {
    expect(buildPlayercorefactoryXml(target, true, [])).toBe(buildPlayercorefactoryXml(target));
    expect(buildDiscFolderRuleXml([])).toBe("");
    expect(buildDiscFolderRuleXml(["   "])).toBe("");
  });

  it("buildTransferFiles threads folders into the playercorefactory", () => {
    const files = buildTransferFiles(target, true, ["smb://nas/X/Discs"]);
    expect(files["playercorefactory.xml"]).toContain(".*smb://nas/X/Discs.*");
  });
});

describe("buildKeymapXml", () => {
  it("maps remote + keyboard keys to the oppo_key script", () => {
    const xml = buildKeymapXml();
    expect(xml).toContain("<keymap>");
    expect(xml).toContain("<FullscreenVideo>");
    expect(xml).toContain("RunScript(script.oppo203.iso.external,oppo_key,select)");
    expect(xml).toContain("RunScript(script.oppo203.iso.external,oppo_key,popup_menu)");
  });
});

describe("buildTransferFiles", () => {
  it("returns the two files keyed by userdata-relative path", () => {
    const files = buildTransferFiles(kodiTargetForPlatform("coreelec"));
    expect(Object.keys(files).sort()).toEqual(["keymaps/oppo203iso.xml", "playercorefactory.xml"]);
    expect(KEYMAP_FILENAME).toBe("oppo203iso.xml");
  });
});
