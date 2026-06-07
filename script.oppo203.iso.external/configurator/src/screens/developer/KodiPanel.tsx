import { useState } from "react";
import { invoke } from "../../ipc";
import { fileReadPlan } from "../../dashboard_status";
import { ADDON_DATA_SETTINGS_REL, parseSettingsXml } from "../../settings_xml";
import { sanitizeSettings } from "../../settings_diff";
import { addonsDirForPlatform } from "../../generate";
import type { AddonSettings } from "../../mapping";
import type { DevPanelProps } from "./types";
import { PingRow } from "./devControls";

const ADDON_ID = "script.oppo203.iso.external";
// Add-on ids the dev tools recognise: the v2 OppoKodiBridge service add-on and the v1 add-on.
const ACCEPTED_ADDON_IDS = ["service.oppokodibridge", ADDON_ID];

type KodiHost = { ip: string; version: string | null };

/** Pull version="..." off the first <addon> element of an addon.xml string (mirrors the Rust parse). */
function parseAddonVersion(xml: string): string | null {
  return /<addon\b[^>]*\bversion="([^"]+)"/.exec(xml)?.[1] ?? null;
}

/**
 * Kodi developer tools: installed-vs-bundled add-on version, a live settings table, and the
 * box operations that shorten test cycles — register-without-restart, remote restart, and
 * upload-any-version. The box operations run over SSH to the configured Kodi box; the restart and
 * the zip upload (which overwrites the installed add-on) are confirm-gated. All box I/O is
 * hardware-pending.
 */
export function KodiPanel({ state, set }: DevPanelProps) {
  const addonsDir = addonsDirForPlatform(state.kodiPlatform ?? "coreelec");

  const [scanBase, setScanBase] = useState("");
  const [scanning, setScanning] = useState(false);
  const [boxes, setBoxes] = useState<KodiHost[]>([]);
  const [scanMsg, setScanMsg] = useState<string | null>(null);
  const [bundled, setBundled] = useState<string | null>(null);
  const [installed, setInstalled] = useState<string | null>(null);
  const [versErr, setVersErr] = useState<string | null>(null);
  const [settings, setSettings] = useState<AddonSettings | null>(null);
  const [settingsErr, setSettingsErr] = useState<string | null>(null);
  const [zipPath, setZipPath] = useState("");
  const [confirm, setConfirm] = useState<null | "restart" | "upload">(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [zipValid, setZipValid] = useState<boolean | null>(null);
  const [zipReason, setZipReason] = useState("");
  const [zipVersion, setZipVersion] = useState<string | null>(null);
  const [zipSig, setZipSig] = useState<string>("");
  const [zipAddonId, setZipAddonId] = useState<string | null>(null);
  const [installedId, setInstalledId] = useState<string | null>(null);

  async function scanForBoxes() {
    setScanning(true);
    setScanMsg(null);
    try {
      const found = await invoke<KodiHost[]>("scan_kodi_hosts", { baseIp: scanBase.trim() || undefined });
      setBoxes(found);
      setScanMsg(
        found.length ? `Found ${found.length} Kodi box(es).` : "No Kodi boxes answered on :8080."
      );
    } catch (e) {
      setBoxes([]);
      setScanMsg(`Scan failed: ${String(e)}`);
    } finally {
      setScanning(false);
    }
  }

  async function refreshVersions() {
    setBusy(true);
    setVersErr(null);
    try {
      const b = await invoke<{ version: string }>("bundled_addon_info");
      setBundled(b.version);
    } catch (e) {
      setBundled(null);
      setVersErr(`Bundled version: ${String(e)}`);
    }
    try {
      let foundId: string | null = null;
      let foundVer: string | null = null;
      for (const id of ACCEPTED_ADDON_IDS) {
        const xml = await invoke<string | null>("read_ssh_file", {
          host: state.kodiIp,
          user: state.sshUser,
          userdataPath: addonsDir,
          rel: `${id}/addon.xml`,
        });
        if (xml) {
          foundId = id;
          foundVer = parseAddonVersion(xml) ?? "unknown";
          break;
        }
      }
      setInstalledId(foundId);
      setInstalled(foundVer ?? "not installed");
    } catch (e) {
      setInstalled(null);
      setInstalledId(null);
      setVersErr(`Installed version (SSH): ${String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  async function readSettings() {
    setBusy(true);
    setSettingsErr(null);
    setSettings(null);
    const plan = fileReadPlan(state, ADDON_DATA_SETTINGS_REL);
    if (!plan.supported) {
      setSettingsErr(plan.note);
      setBusy(false);
      return;
    }
    try {
      const raw = await invoke<string | null>(plan.command, plan.args);
      if (raw == null) setSettingsErr("No settings.xml on the box yet.");
      else setSettings(sanitizeSettings(parseSettingsXml(raw)));
    } catch (e) {
      setSettingsErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function register() {
    setBusy(true);
    setActionMsg(null);
    try {
      const ok = await invoke<boolean>("kodi_set_addon_enabled", {
        host: state.kodiIp,
        user: state.sshUser,
        addonId: zipAddonId ?? installedId ?? undefined,
      });
      setActionMsg(ok ? "Add-on enabled via Kodi JSON-RPC (no restart)." : "Kodi did not confirm the enable — try a restart.");
    } catch (e) {
      setActionMsg(`Register failed: ${String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  async function restart() {
    setConfirm(null);
    setBusy(true);
    setActionMsg(null);
    try {
      await invoke("kodi_restart", { host: state.kodiIp, user: state.sshUser });
      setActionMsg("Restart command sent (systemctl restart kodi).");
    } catch (e) {
      setActionMsg(`Restart failed: ${String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  async function validateZip(path: string) {
    const p = path.trim();
    if (!p) {
      setZipValid(null);
      setZipReason("");
      setZipVersion(null);
      setZipSig("");
      setZipAddonId(null);
      return;
    }
    try {
      const r = await invoke<{ valid: boolean; version: string | null; reason: string; signature_state: string; addon_id: string | null }>("validate_addon_zip", { path: p });
      setZipValid(r.valid);
      setZipReason(r.reason);
      setZipVersion(r.version);
      setZipSig(r.signature_state);
      setZipAddonId(r.addon_id);
    } catch (e) {
      setZipValid(false);
      setZipReason(String(e));
      setZipVersion(null);
      setZipSig("");
      setZipAddonId(null);
    }
  }

  async function browse() {
    try {
      const picked = await invoke<string | null>("pick_addon_zip");
      if (picked) {
        setZipPath(picked);
        await validateZip(picked);
      }
    } catch (e) {
      setZipValid(false);
      setZipReason(`Browse failed: ${String(e)}`);
    }
  }

  async function upload() {
    setConfirm(null);
    const p = zipPath.trim();
    if (!p) {
      setActionMsg("Enter the path to an add-on .zip first.");
      return;
    }
    setBusy(true);
    setActionMsg(null);
    try {
      const rep = await invoke<{ version: string; target: string; backed_up?: string | null; addon_id: string }>(
        "install_addon_zip",
        { host: state.kodiIp, user: state.sshUser, addonsPath: addonsDir, zipPath: p }
      );
      let msg = `Uploaded add-on ${rep.addon_id} ${rep.version} to ${rep.target}.`;
      if (rep.backed_up) msg += ` Backed up the previous copy to ${rep.backed_up}.`;
      try {
        const ok = await invoke<boolean>("kodi_set_addon_enabled", {
          host: state.kodiIp,
          user: state.sshUser,
          addonId: rep.addon_id,
        });
        msg += ok ? " Enabled it via Kodi (no restart)." : " Enable it in Kodi → Add-ons, or restart.";
      } catch {
        msg += " Couldn't auto-enable — restart Kodi or enable it in Add-ons.";
      }
      setActionMsg(msg);
    } catch (e) {
      setActionMsg(`Upload failed: ${String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  const settingsRows = settings ? Object.entries(settings) : [];

  return (
    <div className="stack-lg">
      <section className="card">
        <h3 style={{ marginTop: 0 }}>Kodi box</h3>
        <div className="field" style={{ maxWidth: 280 }}>
          <label className="field-label" htmlFor="dev-kodi-ip">Kodi box IP</label>
          <input id="dev-kodi-ip" className="input" value={state.kodiIp} placeholder="192.168.1.x" spellCheck={false} onChange={(e) => set({ kodiIp: e.target.value })} />
          <span className="field-hint">Used by every action on this panel — version, settings, the SSH box ops, and the Ping below.</span>
        </div>
        <PingRow label="Kodi box" host={state.kodiIp} port={8080} />

        <h4 className="dev-subhead" style={{ marginTop: 16 }}>Don't know the IP? Scan the subnet</h4>
        <div className="row wrap" style={{ alignItems: "flex-end", gap: 12 }}>
          <div className="field" style={{ maxWidth: 280 }}>
            <label className="field-label" htmlFor="dev-kodi-scanbase">
              Base IP (optional — defaults to this host's subnet)
            </label>
            <input id="dev-kodi-scanbase" className="input" value={scanBase} placeholder="192.168.1.0" spellCheck={false} onChange={(e) => setScanBase(e.target.value)} />
          </div>
          <button className="btn" disabled={scanning} onClick={() => void scanForBoxes()}>
            {scanning ? "Scanning…" : "Scan network"}
          </button>
        </div>
        <span className="field-hint">Probes :8080 across the /24 and confirms each hit via Kodi JSON-RPC (yields the version).</span>
        {boxes.length > 0 && (
          <div className="model-list" style={{ marginTop: 12 }}>
            {boxes.map((b) => (
              <button
                key={b.ip}
                className="model-row"
                onClick={() => { set({ kodiIp: b.ip }); setScanMsg(`Kodi IP set to ${b.ip}.`); }}
                style={{ background: "none", border: "none", font: "inherit", textAlign: "left", cursor: "pointer", width: "100%" }}
              >
                <span className="mono">{b.ip}</span>
                <span className="model-row-meta">{b.version ? `Kodi ${b.version}` : "Kodi (version n/a)"}</span>
              </button>
            ))}
          </div>
        )}
        {scanMsg && <p className="field-hint" style={{ marginBottom: 0 }} role="status">{scanMsg}</p>}
      </section>

      <section className="card">
        <div className="row-between" style={{ marginBottom: 10 }}>
          <h3 style={{ margin: 0 }}>Add-on version</h3>
          <button className="btn ghost sm" disabled={busy} onClick={() => void refreshVersions()}>
            Refresh
          </button>
        </div>
        <div className="row wrap" style={{ gap: 18 }}>
          <div>
            <div className="field-label">Bundled (configurator)</div>
            <div className="mono">{bundled ?? "—"}</div>
          </div>
          <div>
            <div className="field-label">Installed (on the box)</div>
            <div className="mono">
              {installed ?? "—"}
              {installedId && installed && installed !== "not installed" ? ` (${installedId})` : ""}
            </div>
          </div>
          {bundled && installed && installed !== "not installed" && installed !== "unknown" && installedId === ADDON_ID && (
            <span className={`chip ${bundled === installed ? "success" : "warn"}`}>
              {bundled === installed ? "match" : "differ"}
            </span>
          )}
        </div>
        <span className="field-hint">Installed version is read over SSH from the installed add-on's addon.xml under {addonsDir} (OppoKodiBridge or the v1 add-on).</span>
        {versErr && (
          <p className="danger-text" style={{ marginBottom: 0 }} role="status">
            {versErr}
          </p>
        )}
      </section>

      <section className="card">
        <div className="row-between" style={{ marginBottom: 10 }}>
          <h3 style={{ margin: 0 }}>Add-on settings</h3>
          <button className="btn ghost sm" disabled={busy} onClick={() => void readSettings()}>
            Read settings
          </button>
        </div>
        {settingsErr && (
          <p className="danger-text" style={{ marginTop: 0 }} role="status">
            {settingsErr}
          </p>
        )}
        {settings && (
          <div className="dev-transcript" role="table" aria-label="Add-on settings">
            {settingsRows.length === 0 ? (
              <div className="dev-tline dev-info">(no settings)</div>
            ) : (
              settingsRows.map(([k, v]) => (
                <div key={k} className="dev-tline">
                  <span className="muted">{k}</span> = {String(v)}
                </div>
              ))
            )}
          </div>
        )}
        {settings && (
          <span className="field-hint">{settingsRows.length} settings — secrets masked.</span>
        )}
      </section>

      <section className="card">
        <h3 style={{ marginTop: 0 }}>Box operations (SSH)</h3>
        <div className="callout info" style={{ marginBottom: 12 }}>
          <span className="callout-icon">i</span>
          <div className="callout-body">
            These run over SSH to the Kodi box (<span className="mono">{state.sshUser}@{state.kodiIp}</span>).
          </div>
        </div>

        <div className="row wrap" style={{ gap: 10, marginBottom: 14 }}>
          <button className="btn" disabled={busy} onClick={() => void register()}>
            Register add-on (no restart)
          </button>
          {confirm === "restart" ? (
            <span className="row" style={{ gap: 6 }}>
              <button className="btn danger" disabled={busy} onClick={() => void restart()}>
                Confirm restart
              </button>
              <button className="btn ghost" onClick={() => setConfirm(null)}>
                Cancel
              </button>
            </span>
          ) : (
            <button className="btn outline" disabled={busy} onClick={() => setConfirm("restart")}>
              Restart Kodi…
            </button>
          )}
        </div>

        <div className="field">
          <label className="field-label" htmlFor="dev-kodi-zip">
            Upload add-on .zip (any version)
          </label>
          <div className="row" style={{ gap: 6 }}>
            <input
              id="dev-kodi-zip"
              className="input mono"
              placeholder="C:\path\to\script.oppo203.iso.external-x.y.z.zip"
              value={zipPath}
              spellCheck={false}
              onChange={(e) => {
                setZipPath(e.target.value);
                setZipValid(null);
                setZipReason("");
                setZipVersion(null);
                setZipSig("");
                setZipAddonId(null);
              }}
              onBlur={() => void validateZip(zipPath)}
            />
            <button className="btn outline" onClick={() => void browse()}>
              Browse…
            </button>
          </div>
          <span className="field-hint">
            Deploys this .zip to the box over SSH (backing up the current copy) and re-registers it
            without a restart. It must be a valid OppoKodiAddon — Upload stays disabled otherwise.
          </span>
          {zipValid !== null && (
            <p className={zipValid ? "success-text" : "danger-text"} style={{ marginBottom: 0 }} role="status">
              {zipValid
                ? `✓ Valid add-on${zipAddonId ? ` ${zipAddonId}` : ""}${zipVersion ? ` v${zipVersion}` : ""}${zipSig === "signed" ? " — build tag verified ✓" : zipSig === "unsigned" ? " — no build tag (older build)" : ""}`
                : `✗ ${zipReason}`}
            </p>
          )}
          <div className="row" style={{ gap: 6, marginTop: 8 }}>
            {confirm === "upload" ? (
              <>
                <button className="btn danger" disabled={busy} onClick={() => void upload()}>
                  Confirm upload + replace
                </button>
                <button className="btn ghost" onClick={() => setConfirm(null)}>
                  Cancel
                </button>
              </>
            ) : (
              <button className="btn" disabled={busy || zipValid !== true} onClick={() => setConfirm("upload")}>
                Upload + register…
              </button>
            )}
          </div>
        </div>

        {actionMsg && (
          <p style={{ marginBottom: 0 }} role="status">
            {actionMsg}
          </p>
        )}
      </section>
    </div>
  );
}
