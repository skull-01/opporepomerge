// @vitest-environment node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

// The AVR DB ships in two copies: the bundled offline fallback that avrdb.ts imports
// (configurator/src/avr-db/avr-models.json) and the canonical, remotely-refreshable copy
// (docs/configurator/avr-db/avr-models.json). build/gen_avr_db.py writes both, but nothing
// enforced that they stay in step -- and since the loader only ever imports the bundled copy,
// a hand-edit to one could ship undetected drift. This guard pins them identical and pins the
// structural invariants avrdb.ts and Step 6 rely on.

function read(rel: string): string {
  return readFileSync(new URL(rel, import.meta.url), "utf8");
}

const SRC_REL = "./avr-db/avr-models.json";
const DOCS_REL = "../../docs/configurator/avr-db/avr-models.json";

describe("avr-models.json: bundled and docs copies stay in lockstep", () => {
  const srcRaw = read(SRC_REL);
  const docsRaw = read(DOCS_REL);

  it("are byte-for-byte identical", () => {
    expect(docsRaw).toBe(srcRaw);
  });

  it("parse to deep-equal objects", () => {
    expect(JSON.parse(docsRaw)).toEqual(JSON.parse(srcRaw));
  });
});

type AvrLineup = { id: string };
type AvrModel = { id: string; lineup: string };

describe("avr-models.json: schema invariants", () => {
  const db = JSON.parse(read(SRC_REL)) as {
    schema_version: number;
    db_version: string;
    lineups: AvrLineup[];
    models: AvrModel[];
  };

  it("declares schema_version 2", () => {
    expect(db.schema_version).toBe(2);
  });

  it("carries a non-empty db_version string", () => {
    expect(typeof db.db_version).toBe("string");
    expect(db.db_version.length).toBeGreaterThan(0);
  });

  it("has non-empty lineups and models", () => {
    expect(db.lineups.length).toBeGreaterThan(0);
    expect(db.models.length).toBeGreaterThan(0);
  });

  it("has unique lineup ids", () => {
    const ids = db.lineups.map((l) => l.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("has unique model ids", () => {
    const ids = db.models.map((m) => m.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("every model references an existing lineup", () => {
    const lineupIds = new Set(db.lineups.map((l) => l.id));
    const orphans = db.models.filter((m) => !lineupIds.has(m.lineup)).map((m) => m.id);
    expect(orphans).toEqual([]);
  });
});
