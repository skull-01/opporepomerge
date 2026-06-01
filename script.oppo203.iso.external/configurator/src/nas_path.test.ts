import { describe, expect, it } from "vitest";
import { deriveRewrite } from "./nas_path";

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
