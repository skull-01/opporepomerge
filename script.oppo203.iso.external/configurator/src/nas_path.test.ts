import { describe, expect, it } from "vitest";
import { deriveRewrite, parseOppoPlayingPath } from "./nas_path";

describe("deriveRewrite", () => {
  it("derives the prefix rewrite from matching Kodi and OPPO paths (SMB)", () => {
    expect(deriveRewrite("smb://192.168.1.10/Movies/Film.iso", "MyPC/Movies/Film.iso")).toEqual({
      from: "smb://192.168.1.10/",
      to: "MyPC/",
    });
  });

  it("works for an NFS source", () => {
    expect(
      deriveRewrite("nfs://10.0.0.5/volume1/Movies/Film.iso", "MyNFS/Movies/Film.iso"),
    ).toEqual({ from: "nfs://10.0.0.5/volume1/", to: "MyNFS/" });
  });

  it("returns null when the paths share no trailing segment", () => {
    expect(deriveRewrite("smb://nas/A/x.iso", "MyPC/B/y.iso")).toBeNull();
  });

  it("returns null when the paths are identical (no rewrite needed)", () => {
    expect(deriveRewrite("smb://nas/x.iso", "smb://nas/x.iso")).toBeNull();
  });

  it("returns null on empty input", () => {
    expect(deriveRewrite("", "MyPC/x.iso")).toBeNull();
    expect(deriveRewrite("smb://nas/x.iso", "  ")).toBeNull();
  });

  it("matches a single shared filename segment", () => {
    expect(deriveRewrite("smb://nas/share/Film.iso", "Disc/Film.iso")).toEqual({
      from: "smb://nas/share/",
      to: "Disc/",
    });
  });
});

describe("parseOppoPlayingPath", () => {
  it("pulls a path field from a flat payload", () => {
    expect(parseOppoPlayingPath('{"path":"MyPC/Movies/Film.iso","state":"play"}')).toBe(
      "MyPC/Movies/Film.iso",
    );
  });

  it("finds a nested file field", () => {
    expect(parseOppoPlayingPath('{"info":{"file":"Disc/x.iso"}}')).toBe("Disc/x.iso");
  });

  it("returns null when nothing path-like is present", () => {
    expect(parseOppoPlayingPath('{"state":"stop","elapsed":0}')).toBeNull();
  });

  it("returns null on a non-JSON body", () => {
    expect(parseOppoPlayingPath("<html>error</html>")).toBeNull();
  });
});
