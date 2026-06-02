use serde_json::Value;
use std::collections::BTreeMap;
use std::fs;
use std::io::{Read, Write};
use std::net::{TcpStream, ToSocketAddrs, UdpSocket};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tauri::{Emitter, Manager};

#[tauri::command]
fn load_wizard_state(app: tauri::AppHandle) -> Result<Option<Value>, String> {
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    let path = dir.join("state.json");
    if !path.exists() {
        return Ok(None);
    }
    let raw = fs::read_to_string(&path).map_err(|e| e.to_string())?;
    let value: Value = serde_json::from_str(&raw).map_err(|e| e.to_string())?;
    Ok(Some(value))
}

#[tauri::command]
fn save_wizard_state(app: tauri::AppHandle, state: Value) -> Result<(), String> {
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join("state.json");
    let pretty = serde_json::to_string_pretty(&state).map_err(|e| e.to_string())?;
    fs::write(&path, pretty).map_err(|e| e.to_string())?;
    Ok(())
}

/// Resolve a caller-supplied relative path under the app data dir, rejecting anything that
/// could escape it (absolute paths, or `..`/root components). The dashboard's own callers pass
/// fixed names, but validating keeps a stray value from ever reading or writing outside appdata.
fn safe_app_rel(rel: &str) -> Result<std::path::PathBuf, String> {
    let p = std::path::Path::new(rel);
    if p.is_absolute() {
        return Err("path must be relative".into());
    }
    for comp in p.components() {
        if !matches!(comp, std::path::Component::Normal(_)) {
            return Err("path must not contain '..' or root components".into());
        }
    }
    Ok(p.to_path_buf())
}

/// Read a JSON document the dashboard previously stored under the app data dir, or `None` when
/// it has never been written. Mirrors `load_wizard_state` but for arbitrary dashboard files.
#[tauri::command]
fn read_app_json(app: tauri::AppHandle, rel: String) -> Result<Option<Value>, String> {
    let rel = safe_app_rel(&rel)?;
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    let path = dir.join(rel);
    if !path.exists() {
        return Ok(None);
    }
    let raw = fs::read_to_string(&path).map_err(|e| e.to_string())?;
    let value: Value = serde_json::from_str(&raw).map_err(|e| e.to_string())?;
    Ok(Some(value))
}

/// Persist a JSON document under the app data dir (creating parent dirs), pretty-printed for a
/// human-readable, diff-friendly file. Mirrors `save_wizard_state` but for arbitrary dashboard files.
#[tauri::command]
fn write_app_json(app: tauri::AppHandle, rel: String, value: Value) -> Result<(), String> {
    let rel = safe_app_rel(&rel)?;
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    let path = dir.join(rel);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    let pretty = serde_json::to_string_pretty(&value).map_err(|e| e.to_string())?;
    fs::write(&path, pretty).map_err(|e| e.to_string())?;
    Ok(())
}

/// Write the generated files (keyed by path relative to Kodi userdata/) into the app's
/// data dir under `generated/`, mirroring the userdata layout. Returns the output dir.
#[tauri::command]
fn generate_files(
    app: tauri::AppHandle,
    files: BTreeMap<String, String>,
) -> Result<String, String> {
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    let out = dir.join("generated");
    for (rel, contents) in &files {
        let path = out.join(rel);
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        fs::write(&path, contents).map_err(|e| e.to_string())?;
    }
    Ok(out.to_string_lossy().into_owned())
}

/// Reveal a path in the OS file manager (Windows Explorer). Best-effort.
#[tauri::command]
fn reveal_path(path: String) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        // Only reveal a real, existing absolute path -- never hand Explorer an arbitrary string
        // (it can interpret URLs / shell targets). Reject relative / non-existent inputs.
        let p = std::path::Path::new(&path);
        if !p.is_absolute() || !p.exists() {
            return Err(format!(
                "reveal_path requires an existing absolute path: {path}"
            ));
        }
        std::process::Command::new("explorer")
            .arg(&path)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    #[cfg(not(target_os = "windows"))]
    {
        let _ = &path;
    }
    Ok(())
}

#[derive(serde::Serialize)]
struct DeployReport {
    written: Vec<String>,
    backed_up: Vec<String>,
}

fn backup_suffix() -> String {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
        .to_string()
}

/// Validate an SSH host or username so ssh can't misread it as an option (a leading '-' such
/// as `-oProxyCommand=...`) and so it can't carry shell metacharacters. Allows only the
/// characters that appear in real hostnames/IPs and usernames.
fn validate_ssh_component(label: &str, v: &str) -> Result<(), String> {
    if v.is_empty() {
        return Err(format!("ssh {label} is empty"));
    }
    if v.starts_with('-') {
        return Err(format!("ssh {label} '{v}' may not start with '-'"));
    }
    if let Some(c) = v
        .chars()
        .find(|&c| !(c.is_ascii_alphanumeric() || matches!(c, '.' | ':' | '_' | '-')))
    {
        return Err(format!(
            "ssh {label} '{v}' contains an invalid character '{c}'"
        ));
    }
    Ok(())
}

fn validate_ssh_target(host: &str, user: &str) -> Result<(), String> {
    validate_ssh_component("host", host)?;
    validate_ssh_component("user", user)
}

/// Read a file under the given Kodi userdata directory (local or SMB UNC path), if present.
#[tauri::command]
fn read_userdata_file(userdata_path: String, rel: String) -> Result<Option<String>, String> {
    let path = std::path::Path::new(&userdata_path).join(&rel);
    if !path.exists() {
        return Ok(None);
    }
    fs::read_to_string(&path)
        .map(Some)
        .map_err(|e| e.to_string())
}

/// Deploy files (keyed by path relative to userdata/) into a Kodi userdata directory,
/// backing up any existing file to a timestamped .bak first. Works for a local path or an
/// SMB UNC path on Windows.
#[tauri::command]
fn deploy_to_userdata(
    userdata_path: String,
    files: BTreeMap<String, String>,
) -> Result<DeployReport, String> {
    let base = std::path::PathBuf::from(&userdata_path);
    // (target, Option<bak>) for each file already swapped in, so a later failure can roll the
    // whole set back instead of leaving a half-applied config (e.g. new settings.xml + old keymap).
    let mut applied: Vec<(std::path::PathBuf, Option<String>)> = Vec::new();
    for (rel, contents) in &files {
        let target = base.join(rel);
        if let Err(e) = deploy_one_file(&target, contents, &mut applied) {
            rollback_deploy(&applied);
            return Err(e);
        }
    }
    Ok(DeployReport {
        written: applied
            .iter()
            .map(|(t, _)| t.to_string_lossy().into_owned())
            .collect(),
        backed_up: applied.iter().filter_map(|(_, b)| b.clone()).collect(),
    })
}

/// Write one file into place (backup, then temp-write + swap so an interrupted write can't leave
/// a truncated target) and record it in `applied` for a possible rollback.
fn deploy_one_file(
    target: &std::path::Path,
    contents: &str,
    applied: &mut Vec<(std::path::PathBuf, Option<String>)>,
) -> Result<(), String> {
    if let Some(parent) = target.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    let bak = if target.exists() {
        let bak = format!("{}.{}.bak", target.to_string_lossy(), backup_suffix());
        fs::copy(target, &bak).map_err(|e| e.to_string())?;
        Some(bak)
    } else {
        None
    };
    let tmp = std::path::PathBuf::from(format!("{}.oppocfg-tmp", target.to_string_lossy()));
    fs::write(&tmp, contents).map_err(|e| e.to_string())?;
    if target.exists() {
        fs::remove_file(target).map_err(|e| e.to_string())?;
    }
    fs::rename(&tmp, target).map_err(|e| e.to_string())?;
    applied.push((target.to_path_buf(), bak));
    Ok(())
}

/// Best-effort rollback: restore each already-applied target from its `.bak`, or remove a
/// newly-created file that had no prior version. Reverse order so the set undoes cleanly.
fn rollback_deploy(applied: &[(std::path::PathBuf, Option<String>)]) {
    for (target, bak) in applied.iter().rev() {
        match bak {
            Some(b) => {
                let _ = fs::copy(b, target);
            }
            None => {
                let _ = fs::remove_file(target);
            }
        }
    }
}

/// Verify a Kodi userdata directory is writable by creating and removing a temp file.
#[tauri::command]
fn smb_test_write(userdata_path: String) -> Result<(), String> {
    let base = std::path::PathBuf::from(&userdata_path);
    fs::create_dir_all(&base).map_err(|e| e.to_string())?;
    let probe = base.join(".oppo203-configurator-write-test");
    fs::write(&probe, b"ok").map_err(|e| e.to_string())?;
    fs::remove_file(&probe).map_err(|e| e.to_string())?;
    Ok(())
}

// ============================================================
// Reset all configurations: remove the add-on + the deployed files from the box, per tier.
// ============================================================
//
// The configurator deploys exactly four things to a Kodi box: the add-on folder under addons/,
// and (under userdata/) playercorefactory.xml, keymaps/oppo203iso.xml, and the addon_data/<id>
// directory (settings.xml + status JSON). Reset removes ONLY those fixed, code-constructed paths
// -- never the userdata/addons root or any free-form path -- mirroring the deploy commands' two
// transports (SSH for tier A, a filesystem path for tier B/SMB).

const RESET_ADDON_ID: &str = "script.oppo203.iso.external";

/// The four box paths the configurator owns, given the userdata and addons directories: the
/// add-on folder, then the three userdata artifacts. Used by the tier B / local reset and the
/// path-construction test; the SSH reset mirrors the same four paths as remote strings.
fn box_reset_targets(userdata: &Path, addons: &Path) -> Vec<PathBuf> {
    vec![
        addons.join(RESET_ADDON_ID),
        userdata.join("playercorefactory.xml"),
        userdata.join("keymaps").join("oppo203iso.xml"),
        userdata.join("addon_data").join(RESET_ADDON_ID),
    ]
}

/// Remove each path that exists (dir or file), returning the ones actually removed. A missing
/// path is skipped, so the operation is idempotent.
fn remove_existing_paths(targets: &[PathBuf]) -> Result<Vec<String>, String> {
    let mut removed = Vec::new();
    for t in targets {
        if t.is_dir() {
            fs::remove_dir_all(t).map_err(|e| e.to_string())?;
            removed.push(t.to_string_lossy().into_owned());
        } else if t.exists() {
            fs::remove_file(t).map_err(|e| e.to_string())?;
            removed.push(t.to_string_lossy().into_owned());
        }
    }
    Ok(removed)
}

/// One step of a reset, streamed to the UI as a `reset-progress` event so the user sees what the
/// action is doing instead of a frozen "Resetting…". `status` is one of running/done/failed.
#[derive(serde::Serialize, Clone)]
struct ResetProgress {
    step: String,
    label: String,
    status: String,
    detail: Option<String>,
}

fn emit_reset(app: &tauri::AppHandle, step: &str, label: &str, status: &str, detail: Option<String>) {
    let _ = app.emit(
        "reset-progress",
        ResetProgress {
            step: step.to_string(),
            label: label.to_string(),
            status: status.to_string(),
            detail,
        },
    );
}

/// Host of a Windows UNC path (`\\host\share\...`), for a fast reachability pre-probe. None for a
/// local/drive path — those have no network device to be unreachable, so they can't hang on it.
fn unc_host(path: &str) -> Option<String> {
    let rest = path.strip_prefix(r"\\").or_else(|| path.strip_prefix("//"))?;
    let host = rest.split(['\\', '/']).next().unwrap_or("");
    if host.is_empty() {
        None
    } else {
        Some(host.to_string())
    }
}

/// Tier B / local: delete the add-on + deployed userdata files from a filesystem path (a local
/// Kodi dir or an SMB UNC). Removes only the four owned paths; the userdata/addons roots survive.
/// A dead SMB share would otherwise block each fs op on the UNC for tens of seconds, so an SMB
/// target is reachability-probed (port 445) first and fails fast; local/drive paths skip the probe.
#[tauri::command]
fn reset_box_userdata(
    app: tauri::AppHandle,
    userdata_path: String,
    addons_path: String,
) -> Result<Vec<String>, String> {
    if let Some(host) = unc_host(&userdata_path) {
        emit_reset(&app, "box", "Checking the Kodi share is reachable…", "running", None);
        if let Err(e) = connect_timeout(&host, 445, 2500) {
            emit_reset(&app, "box", "Kodi share is unreachable", "failed", Some(e.clone()));
            return Err(format!(
                "Kodi share \\\\{host} is unreachable (SMB port 445 — powered off or on another network): {e}"
            ));
        }
    }
    let targets = box_reset_targets(&PathBuf::from(&userdata_path), &PathBuf::from(&addons_path));
    let mut removed = Vec::new();
    for t in &targets {
        let name = t.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
        emit_reset(&app, "box", &format!("Removing {name}…"), "running", None);
        removed.extend(remove_existing_paths(std::slice::from_ref(t))?);
    }
    emit_reset(&app, "box", "Removed the add-on and config from the Kodi share", "done", None);
    Ok(removed)
}

/// Tier A: delete the add-on + deployed userdata files over SSH, then a best-effort Kodi restart
/// so the removed add-on drops out of the running instance. Returns the paths that existed and
/// were removed. Non-interactive -- requires SSH key auth. Only the four owned paths are touched.
#[tauri::command]
fn reset_box_ssh(
    app: tauri::AppHandle,
    host: String,
    user: String,
    userdata_path: String,
    addons_path: String,
    restart: bool,
) -> Result<Vec<String>, String> {
    validate_ssh_target(&host, &user)?;
    // Fast reachability pre-probe: an unreachable box would otherwise grind through five sequential
    // ssh ConnectTimeout=8 calls (~40s) with the UI frozen. Bail in ~2.5s with a clear message so
    // the caller can skip the box and still reset local state.
    emit_reset(&app, "box", "Checking the Kodi box is reachable…", "running", None);
    if let Err(e) = connect_timeout(&host, 22, 2500) {
        emit_reset(&app, "box", "Kodi box is unreachable", "failed", Some(e.clone()));
        return Err(format!(
            "Kodi box {host}:22 is unreachable over SSH (powered off or on another network): {e}"
        ));
    }
    let target = format!("{user}@{host}");
    let ud = userdata_path.trim_end_matches('/');
    let ad = addons_path.trim_end_matches('/');
    let remotes = [
        format!("{ad}/{RESET_ADDON_ID}"),
        format!("{ud}/playercorefactory.xml"),
        format!("{ud}/keymaps/oppo203iso.xml"),
        format!("{ud}/addon_data/{RESET_ADDON_ID}"),
    ];
    let mut removed = Vec::new();
    for r in &remotes {
        let name = r.rsplit('/').next().unwrap_or(r.as_str());
        emit_reset(&app, "box", &format!("Removing {name}…"), "running", None);
        let script =
            format!("if [ -e '{r}' ]; then rm -rf '{r}' && printf 'REMOVED'; else printf 'ABSENT'; fi");
        if run_ssh_capture(&target, &script)?.trim() == "REMOVED" {
            removed.push(r.clone());
        }
    }
    if restart {
        emit_reset(&app, "box", "Restarting Kodi…", "running", None);
        let _ = run_ssh(&target, "systemctl restart kodi");
    }
    emit_reset(&app, "box", "Removed the add-on and config from the Kodi box", "done", None);
    Ok(removed)
}

/// Reset the configurator itself to first-run: remove the persisted wizard session (state.json),
/// the dashboard memory (dashboard/), and any locally-generated files (generated/) under the app
/// data dir. The next launch starts at the first wizard screen.
#[tauri::command]
fn reset_app_data(app: tauri::AppHandle) -> Result<Vec<String>, String> {
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    let targets: Vec<PathBuf> = ["state.json", "dashboard", "generated"]
        .iter()
        .map(|n| dir.join(n))
        .collect();
    remove_existing_paths(&targets)
}

#[derive(serde::Serialize)]
struct DiagnosticsEnv {
    os: String,
    arch: String,
    configurator_version: String,
}

/// Host OS/arch + the configurator's own version, for the diagnostics-export header. No secrets.
#[tauri::command]
fn diagnostics_env() -> DiagnosticsEnv {
    DiagnosticsEnv {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        configurator_version: env!("CARGO_PKG_VERSION").to_string(),
    }
}

/// Persist the (already-redacted) diagnostics JSON the frontend built to a fixed file under the
/// app-data dir, returning its absolute path so the user can attach it to a bug report. Overwrites
/// the previous export. Redaction is the frontend's job; this only writes bytes.
#[tauri::command]
fn write_diagnostics(app: tauri::AppHandle, contents: String) -> Result<String, String> {
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join("oppo203-configurator-diagnostics.json");
    fs::write(&path, contents).map_err(|e| e.to_string())?;
    Ok(path.to_string_lossy().into_owned())
}

// ============================================================
// Test-ISO copy to the media share (Phase 4.2 self-test; D-2 = user supplies the ISO)
// ============================================================
//
// The OPPO self-test needs a UHD-tagged file on the SAME media share Kodi and the player both
// read. D-2 (locked): the operator supplies the master disc/ISO, so this is placeholder wiring --
// it copies a user-CHOSEN source file to a user-chosen destination (a local path or an SMB UNC,
// the same transport `deploy_to_userdata` uses on Windows), streaming it in chunks and emitting a
// `copy-progress` event per chunk so the UI can show a progress bar for a multi-GB transfer. No
// master ISO is bundled or downloaded. The real transfer + share visibility are hardware-pending.

/// 1 MiB copy chunk -- big enough to keep a network share busy, small enough that progress events
/// stay responsive on a multi-GB file.
const COPY_CHUNK_BYTES: usize = 1024 * 1024;

#[derive(serde::Serialize, Clone)]
struct CopyProgress {
    bytes_copied: u64,
    total: u64,
    percent: u8,
}

#[derive(serde::Serialize)]
struct CopyReport {
    dest: String,
    bytes_copied: u64,
}

/// Integer percent (0..=100) of `copied`/`total`, saturating. A zero-byte total reads as complete
/// (100) rather than dividing by zero, so an empty source still drives the bar to done.
fn copy_progress_percent(copied: u64, total: u64) -> u8 {
    if total == 0 {
        return 100;
    }
    let pct = (copied as u128 * 100 / total as u128).min(100);
    pct as u8
}

/// Validate the copy source and destination before opening anything: both must be non-empty and the
/// destination must not be a bare directory path (we need a file name to write). Pure, so the UI's
/// guardrails are unit-tested without touching the filesystem.
fn validate_copy_paths(source: &str, dest: &str) -> Result<(), String> {
    if source.trim().is_empty() {
        return Err("source path is empty".to_string());
    }
    if dest.trim().is_empty() {
        return Err("destination path is empty".to_string());
    }
    let ends_with_sep = dest.ends_with('/') || dest.ends_with('\\');
    if ends_with_sep {
        return Err("destination must include a file name, not just a folder".to_string());
    }
    Ok(())
}

/// Copy a user-chosen source file to a destination (local path or SMB UNC) in 1 MiB chunks,
/// emitting a `copy-progress` event (bytesCopied/total/percent) per chunk. Writes to a sibling
/// temp file then renames it into place, so an interrupted copy can't leave a half-written target
/// in the library. Placeholder wiring for the Phase 4 self-test (D-2: the operator supplies the
/// ISO); the real multi-GB transfer over a share is hardware-pending.
#[tauri::command]
fn copy_to_share(
    app: tauri::AppHandle,
    source_path: String,
    dest_path: String,
) -> Result<CopyReport, String> {
    validate_copy_paths(&source_path, &dest_path)?;
    let src = PathBuf::from(&source_path);
    let dest = PathBuf::from(&dest_path);

    let mut reader =
        fs::File::open(&src).map_err(|e| format!("cannot open source '{}': {e}", src.display()))?;
    let total = reader.metadata().map(|m| m.len()).unwrap_or(0);

    if let Some(parent) = dest.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
    }
    let tmp = PathBuf::from(format!("{}.oppocfg-copy-tmp", dest.to_string_lossy()));
    let mut writer = fs::File::create(&tmp)
        .map_err(|e| format!("cannot create destination '{}': {e}", tmp.display()))?;

    let mut buf = vec![0u8; COPY_CHUNK_BYTES];
    let mut copied: u64 = 0;
    // Emit a 0% frame up front so the bar appears immediately, before the first chunk lands.
    let _ = app.emit(
        "copy-progress",
        CopyProgress {
            bytes_copied: 0,
            total,
            percent: copy_progress_percent(0, total),
        },
    );
    loop {
        let n = match reader.read(&mut buf) {
            Ok(0) => break,
            Ok(n) => n,
            Err(e) => {
                let _ = fs::remove_file(&tmp);
                return Err(format!("read error after {copied} bytes: {e}"));
            }
        };
        if let Err(e) = writer.write_all(&buf[..n]) {
            let _ = fs::remove_file(&tmp);
            return Err(format!("write error after {copied} bytes: {e}"));
        }
        copied += n as u64;
        let _ = app.emit(
            "copy-progress",
            CopyProgress {
                bytes_copied: copied,
                total,
                percent: copy_progress_percent(copied, total),
            },
        );
    }
    writer.flush().map_err(|e| e.to_string())?;
    drop(writer);

    if dest.exists() {
        fs::remove_file(&dest).map_err(|e| e.to_string())?;
    }
    fs::rename(&tmp, &dest).map_err(|e| e.to_string())?;

    Ok(CopyReport {
        dest: dest.to_string_lossy().into_owned(),
        bytes_copied: copied,
    })
}

fn connect_timeout(host: &str, port: u16, timeout_ms: u64) -> Result<TcpStream, String> {
    let mut last = String::from("no address resolved");
    for addr in (host, port).to_socket_addrs().map_err(|e| e.to_string())? {
        match TcpStream::connect_timeout(&addr, Duration::from_millis(timeout_ms)) {
            Ok(s) => return Ok(s),
            Err(e) => last = e.to_string(),
        }
    }
    Err(last)
}

/// True if a TCP connection to host:port succeeds within the timeout.
#[tauri::command]
fn tcp_probe(host: String, port: u16, timeout_ms: Option<u64>) -> bool {
    connect_timeout(&host, port, timeout_ms.unwrap_or(1500)).is_ok()
}

#[derive(serde::Serialize)]
struct PortResult {
    port: u16,
    open: bool,
}

/// Probe several ports on a host, reporting which accept a TCP connection.
#[tauri::command]
fn tv_port_probe(host: String, ports: Vec<u16>, timeout_ms: Option<u64>) -> Vec<PortResult> {
    let t = timeout_ms.unwrap_or(1200);
    ports
        .into_iter()
        .map(|port| PortResult {
            port,
            open: connect_timeout(&host, port, t).is_ok(),
        })
        .collect()
}

/// One raw frame on the OPPO IP-control wire, emitted to the developer debug panel as a
/// `debug-wire` event. Only the OPPO control path emits these -- the bytes are protocol frames
/// (#QVM / @UPL ...) with no secrets. Deploy/SSH payloads carry the generated settings.xml
/// (Sony PSK / SmartThings token) and are deliberately never emitted: the panel's key-based
/// redactor cannot sanitize a raw byte stream.
#[derive(serde::Serialize, Clone)]
struct WireEvent {
    direction: &'static str,
    label: &'static str,
    host: String,
    port: u16,
    hex: String,
    text: String,
    len: usize,
}

/// Space-separated lowercase hex of each byte ("23 51 56 4d 0d" for the bytes of `#QVM\r`).
fn to_hex(bytes: &[u8]) -> String {
    bytes
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect::<Vec<_>>()
        .join(" ")
}

/// Emit one wire frame to the debug panel. Best-effort -- a failed emit never breaks the command.
fn emit_wire(app: &tauri::AppHandle, direction: &'static str, host: &str, port: u16, bytes: &[u8]) {
    let _ = app.emit(
        "debug-wire",
        WireEvent {
            direction,
            label: "oppo_query",
            host: host.to_string(),
            port,
            hex: to_hex(bytes),
            text: String::from_utf8_lossy(bytes).into_owned(),
            len: bytes.len(),
        },
    );
}

/// Send an OPPO IP-control query (default #QPW on port 23) and return the raw reply.
/// Mirrors resources/lib/oppo/oppo_control.py (CR-terminated; reply form "@CODE OK VALUE").
#[tauri::command]
fn oppo_query(
    app: tauri::AppHandle,
    host: String,
    port: Option<u16>,
    command: Option<String>,
    timeout_ms: Option<u64>,
) -> Result<String, String> {
    let port = port.unwrap_or(23);
    let ms = timeout_ms.unwrap_or(3000);
    let timeout = Duration::from_millis(ms);
    let mut stream = connect_timeout(&host, port, ms)?;
    stream
        .set_read_timeout(Some(timeout))
        .map_err(|e| e.to_string())?;
    stream
        .set_write_timeout(Some(timeout))
        .map_err(|e| e.to_string())?;
    let mut cmd = command.unwrap_or_else(|| "#QPW".to_string());
    if !cmd.ends_with('\r') {
        cmd.push('\r');
    }
    emit_wire(&app, "sent", &host, port, cmd.as_bytes());
    stream
        .write_all(cmd.as_bytes())
        .map_err(|e| e.to_string())?;
    // OPPO replies are CR-terminated; a single read() can return a partial or echoed frame.
    // Accumulate until we see the CR terminator, the peer closes, or the read times out.
    let mut data: Vec<u8> = Vec::new();
    let mut chunk = [0u8; 256];
    loop {
        match stream.read(&mut chunk) {
            Ok(0) => break,
            Ok(n) => {
                data.extend_from_slice(&chunk[..n]);
                if data.contains(&b'\r') || data.len() > 4096 {
                    break;
                }
            }
            Err(ref e)
                if e.kind() == std::io::ErrorKind::WouldBlock
                    || e.kind() == std::io::ErrorKind::TimedOut =>
            {
                break
            }
            Err(e) => return Err(e.to_string()),
        }
    }
    emit_wire(&app, "recv", &host, port, &data);
    Ok(String::from_utf8_lossy(&data).trim().to_string())
}

/// Map a power action to its OPPO IP-control token (Phase 4 self-test power-cycle). `#POF` powers
/// off, `#PON` powers on stock OPPO, `#EJT` wakes clones that lack `#PON` (hardware_presets.py).
fn oppo_power_token(action: &str) -> Result<&'static str, String> {
    match action.trim().to_ascii_lowercase().as_str() {
        "off" | "power_off" => Ok("#POF"),
        "on" | "power_on" => Ok("#PON"),
        "eject" | "wake" => Ok("#EJT"),
        other => Err(format!(
            "unknown OPPO power action '{other}' (expected off/on/eject)"
        )),
    }
}

/// Power the OPPO off/on (or wake a clone via eject) over IP control, for the Phase 4 self-test
/// power-cycle. Delegates to oppo_query so it shares the CR-terminated send + wire transcript.
/// Best-effort + hardware-pending.
#[tauri::command]
fn oppo_power(
    app: tauri::AppHandle,
    host: String,
    port: Option<u16>,
    action: String,
    timeout_ms: Option<u64>,
) -> Result<String, String> {
    let token = oppo_power_token(&action)?;
    oppo_query(app, host, port, Some(token.to_string()), timeout_ms)
}

fn ssh_base_args(target: &str) -> Vec<String> {
    vec![
        "-o".into(),
        "BatchMode=yes".into(),
        "-o".into(),
        "StrictHostKeyChecking=accept-new".into(),
        "-o".into(),
        "ConnectTimeout=8".into(),
        // Bound a hung connection (box unreachable mid-command) at ~15s instead of forever.
        "-o".into(),
        "ServerAliveInterval=5".into(),
        "-o".into(),
        "ServerAliveCountMax=3".into(),
        target.to_string(),
    ]
}

fn run_ssh(target: &str, remote_cmd: &str) -> Result<(), String> {
    let out = std::process::Command::new("ssh")
        .args(ssh_base_args(target))
        .arg(remote_cmd)
        .output()
        .map_err(|e| format!("could not launch ssh (is the OpenSSH client installed?): {e}"))?;
    if out.status.success() {
        Ok(())
    } else {
        Err(String::from_utf8_lossy(&out.stderr).trim().to_string())
    }
}

fn run_ssh_capture(target: &str, remote_cmd: &str) -> Result<String, String> {
    let out = std::process::Command::new("ssh")
        .args(ssh_base_args(target))
        .arg(remote_cmd)
        .output()
        .map_err(|e| format!("could not launch ssh (is the OpenSSH client installed?): {e}"))?;
    if out.status.success() {
        Ok(String::from_utf8_lossy(&out.stdout).into_owned())
    } else {
        Err(String::from_utf8_lossy(&out.stderr).trim().to_string())
    }
}

fn run_ssh_stdin(target: &str, remote_cmd: &str, data: &[u8]) -> Result<String, String> {
    let mut child = std::process::Command::new("ssh")
        .args(ssh_base_args(target))
        .arg(remote_cmd)
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| format!("could not launch ssh (is the OpenSSH client installed?): {e}"))?;
    child
        .stdin
        .as_mut()
        .ok_or_else(|| "ssh stdin unavailable".to_string())?
        .write_all(data)
        .map_err(|e| e.to_string())?;
    let out = child.wait_with_output().map_err(|e| e.to_string())?;
    if out.status.success() {
        Ok(String::from_utf8_lossy(&out.stdout).into_owned())
    } else {
        Err(String::from_utf8_lossy(&out.stderr).trim().to_string())
    }
}

/// Verify SSH reachability + key auth to the Kodi box (non-interactive; key auth only).
#[tauri::command]
fn ssh_test(host: String, user: String) -> Result<(), String> {
    validate_ssh_target(&host, &user)?;
    run_ssh(&format!("{user}@{host}"), "echo ok")
}

/// Read a file under the Kodi userdata dir over SSH, if present (None when absent).
#[tauri::command]
fn read_ssh_file(
    host: String,
    user: String,
    userdata_path: String,
    rel: String,
) -> Result<Option<String>, String> {
    validate_ssh_target(&host, &user)?;
    let target = format!("{user}@{host}");
    let base = userdata_path.trim_end_matches('/');
    let remote = format!("{base}/{rel}");
    let script =
        format!("if [ -f '{remote}' ]; then cat '{remote}'; else printf '__OPPOCFG_ABSENT__'; fi");
    let out = run_ssh_capture(&target, &script)?;
    if out == "__OPPOCFG_ABSENT__" {
        Ok(None)
    } else {
        Ok(Some(out))
    }
}

/// Tier A: write the files into the Kodi userdata dir over SSH (backing up any existing file
/// remotely first and aborting the write if that backup fails), then optionally restart Kodi.
/// Non-interactive — requires SSH key auth.
#[tauri::command]
fn deploy_ssh(
    host: String,
    user: String,
    userdata_path: String,
    files: BTreeMap<String, String>,
    restart: bool,
) -> Result<DeployReport, String> {
    validate_ssh_target(&host, &user)?;
    let target = format!("{user}@{host}");
    let base = userdata_path.trim_end_matches('/');
    // (remote, Option<bak>) for each file already written, so a later failure rolls the whole set
    // back (restore from .bak / remove new files) instead of leaving a half-applied remote config.
    let mut applied: Vec<(String, Option<String>)> = Vec::new();
    for (rel, contents) in &files {
        let remote = format!("{base}/{rel}");
        let parent = remote.rsplit_once('/').map(|(p, _)| p).unwrap_or(".");
        let bak = format!("{remote}.{}.bak", backup_suffix());
        // Back up an existing file before overwriting; '&&' chaining ABORTS the write if the
        // backup fails, and the echoed marker lets us report (and roll back to) the real .bak path.
        let script = format!(
            "mkdir -p '{parent}' && if [ -f '{remote}' ]; then cp -p '{remote}' '{bak}' && printf 'BAK:%s\\n' '{bak}'; fi && cat > '{remote}'"
        );
        match run_ssh_stdin(&target, &script, contents.as_bytes()) {
            Ok(stdout) => {
                let bak_path = stdout
                    .lines()
                    .find(|l| l.starts_with("BAK:"))
                    .map(|l| l.trim_start_matches("BAK:").to_string());
                applied.push((remote, bak_path));
            }
            Err(e) => {
                rollback_deploy_ssh(&target, &applied);
                return Err(e);
            }
        }
    }
    if restart {
        run_ssh(&target, "systemctl restart kodi")?;
    }
    Ok(DeployReport {
        written: applied.iter().map(|(r, _)| r.clone()).collect(),
        backed_up: applied.iter().filter_map(|(_, b)| b.clone()).collect(),
    })
}

/// Best-effort remote rollback: restore each already-written file from its `.bak`, or remove a
/// newly-created file that had no prior version. Reverse order so the set undoes cleanly.
fn rollback_deploy_ssh(target: &str, applied: &[(String, Option<String>)]) {
    for (remote, bak) in applied.iter().rev() {
        let script = match bak {
            Some(b) => format!("cp -p '{b}' '{remote}'"),
            None => format!("rm -f '{remote}'"),
        };
        let _ = run_ssh(target, &script);
    }
}

// ============================================================
// Kodi "what is playing" probe (Phase 1b NAS-path capture; area:configurator, issue #173)
// ============================================================
//
// Reads the exact path Kodi is currently playing, over the existing SSH channel, so the
// configurator can learn the Kodi-visible side of the http_handoff path rewrite
// (`oppo_http_path_from`). Primary: Kodi JSON-RPC on the box (its web server need only listen
// on localhost); fallback: the most recent "OpenFile" entry in kodi.log. The OPPO-visible side
// is captured separately (`#QFN` / `/getmovieplayinfo`); see D-4 / Phase 1b in docs/BUILD_PLAN.md.

const KODI_ACTIVE_PLAYERS_BODY: &str =
    r#"{"jsonrpc":"2.0","id":1,"method":"Player.GetActivePlayers"}"#;

fn kodi_jsonrpc_cmd(body: &str) -> String {
    format!(
        "curl -s --max-time 8 -H 'content-type: application/json' http://localhost:8080/jsonrpc -d '{body}'"
    )
}

fn kodi_get_item_body(player_id: i64) -> String {
    format!(
        r#"{{"jsonrpc":"2.0","id":1,"method":"Player.GetItem","params":{{"playerid":{player_id},"properties":["file"]}}}}"#
    )
}

/// First active player id from a `Player.GetActivePlayers` reply (None when nothing is playing).
fn parse_kodi_active_player_id(json: &str) -> Option<i64> {
    let v: serde_json::Value = serde_json::from_str(json).ok()?;
    v.get("result")?
        .as_array()?
        .iter()
        .find_map(|p| p.get("playerid").and_then(serde_json::Value::as_i64))
}

/// The `file` of the playing item from a `Player.GetItem` reply (None when absent/empty).
fn parse_kodi_player_file(json: &str) -> Option<String> {
    let v: serde_json::Value = serde_json::from_str(json).ok()?;
    let file = v.get("result")?.get("item")?.get("file")?.as_str()?.trim();
    (!file.is_empty()).then(|| file.to_string())
}

/// Fallback: the path from the most recent "OpenFile"/"Opening" line in a kodi.log tail.
fn parse_kodi_log_file(text: &str) -> Option<String> {
    let mut found = None;
    for line in text.lines() {
        for marker in ["OpenFile: ", "Opening: ", "Opening stream: "] {
            if let Some(idx) = line.find(marker) {
                let rest = line[idx + marker.len()..]
                    .trim()
                    .trim_matches(|c| c == '"' || c == '\'');
                if !rest.is_empty() {
                    found = Some(rest.to_string());
                }
            }
        }
    }
    found
}

/// Read the path Kodi is currently playing, over SSH. Primary: Kodi JSON-RPC on the box
/// (`Player.GetActivePlayers` -> `Player.GetItem{file}`); fallback: the last "OpenFile" line in
/// `~/.kodi/temp/kodi.log`. Returns None when nothing resolvable is playing.
#[tauri::command]
fn kodi_now_playing(host: String, user: String) -> Result<Option<String>, String> {
    validate_ssh_target(&host, &user)?;
    let target = format!("{user}@{host}");
    if let Ok(players) = run_ssh_capture(&target, &kodi_jsonrpc_cmd(KODI_ACTIVE_PLAYERS_BODY)) {
        if let Some(pid) = parse_kodi_active_player_id(&players) {
            if let Ok(item) = run_ssh_capture(&target, &kodi_jsonrpc_cmd(&kodi_get_item_body(pid)))
            {
                if let Some(file) = parse_kodi_player_file(&item) {
                    return Ok(Some(file));
                }
            }
        }
    }
    // Fallback: most recent opened file from the Kodi log (constant path -> no shell injection).
    if let Ok(tail) = run_ssh_capture(&target, "tail -n 400 ~/.kodi/temp/kodi.log 2>/dev/null") {
        if let Some(file) = parse_kodi_log_file(&tail) {
            return Ok(Some(file));
        }
    }
    Ok(None)
}

// ============================================================
// OPPO HTTP play (Phase 1b verify-by-playing; ported from oppo_control.py:346-445)
// ============================================================
//
// The undocumented OPPO community HTTP "app" API on port 436: a 6-byte 0x55 UDP broadcast
// "activate" wakes the API, /signin opens a session, and /playnormalfile?payload=<urlencoded
// JSON> starts a network file. Ported as raw HTTP/1.0 over TCP (the tv_switch_roku shape) so the
// verify step can fire a play and then confirm real playback via SVM3 @UPL PLAY. The handshake
// and payload are undocumented -> verified on a real OPPO, not in-session.

const OPPO_HTTP_PORT: u16 = 436;

/// Percent-encode every byte that is not RFC3986-unreserved (matches Python's
/// urllib.parse.quote(s, safe="")), so a JSON payload survives as one query value.
fn percent_encode(s: &str) -> String {
    let mut out = String::with_capacity(s.len() * 3);
    for &b in s.as_bytes() {
        if b.is_ascii_alphanumeric() || matches!(b, b'-' | b'_' | b'.' | b'~') {
            out.push(b as char);
        } else {
            out.push_str(&format!("%{b:02X}"));
        }
    }
    out
}

/// The /playnormalfile JSON payload (json_payload mode), matching `_build_json_payload`.
fn oppo_play_payload(oppo_path: &str) -> String {
    serde_json::json!({
        "path": oppo_path,
        "index": 0,
        "type": 1,
        "appDeviceType": 2,
        "extraNetPath": "",
        "playMode": 0
    })
    .to_string()
}

/// Raw HTTP/1.0 GET for an OPPO app-API endpoint + already-built query string.
fn oppo_http_request(host: &str, endpoint: &str, query: &str) -> String {
    format!(
        "GET {endpoint}?{query} HTTP/1.0\r\nHost: {host}:{OPPO_HTTP_PORT}\r\nConnection: close\r\n\r\n"
    )
}

fn oppo_signin_request(host: &str) -> String {
    oppo_http_request(
        host,
        "/signin",
        &percent_encode(r#"{"user":"","password":""}"#),
    )
}

fn oppo_play_request(host: &str, oppo_path: &str) -> String {
    let query = format!("payload={}", percent_encode(&oppo_play_payload(oppo_path)));
    oppo_http_request(host, "/playnormalfile", &query)
}

/// Send a raw request to the OPPO app API and return whatever it sends back (best-effort read).
fn oppo_http_exchange(host: &str, request: &str, timeout_ms: u64) -> Result<String, String> {
    let mut stream = connect_timeout(host, OPPO_HTTP_PORT, timeout_ms)?;
    let t = Duration::from_millis(timeout_ms);
    stream
        .set_read_timeout(Some(t))
        .map_err(|e| e.to_string())?;
    stream
        .set_write_timeout(Some(t))
        .map_err(|e| e.to_string())?;
    stream
        .write_all(request.as_bytes())
        .map_err(|e| e.to_string())?;
    // Cap the read so a chatty/hostile peer on :436 cannot grow this unboundedly.
    let mut resp = Vec::new();
    let _ = (&mut stream).take(65536).read_to_end(&mut resp);
    Ok(String::from_utf8_lossy(&resp).into_owned())
}

/// Fire a network-file play on the OPPO over the undocumented HTTP app API
/// (activate broadcast -> /signin -> /playnormalfile). `oppo_path` is the OPPO-visible path
/// (already rewritten via oppo_http_path_from/to). Phase 1b verify-by-playing calls this, then
/// confirms real playback via SVM3 @UPL PLAY. Best-effort + hardware-pending.
#[tauri::command]
fn oppo_http_play(host: String, oppo_path: String) -> Result<String, String> {
    validate_ssh_component("host", &host)?;
    if oppo_path.trim().is_empty() {
        return Err("oppo_path is empty".to_string());
    }
    // 1) activate: a 6-byte 0x55 UDP broadcast wakes the HTTP API (non-fatal).
    if let Ok(sock) = UdpSocket::bind("0.0.0.0:0") {
        let _ = sock.set_broadcast(true);
        let _ = sock.send_to(&[0x55u8; 6], ("255.255.255.255", OPPO_HTTP_PORT));
    }
    // 2) signin: open a session (non-fatal -- some firmware needs it, some doesn't).
    let _ = oppo_http_exchange(&host, &oppo_signin_request(&host), 5000);
    // 3) play.
    oppo_http_exchange(&host, &oppo_play_request(&host, &oppo_path), 10000)
}

/// Raw HTTP/1.0 GET for the OPPO /getmovieplayinfo now-playing endpoint (no query).
fn oppo_info_request(host: &str) -> String {
    format!("GET /getmovieplayinfo HTTP/1.0\r\nHost: {host}:{OPPO_HTTP_PORT}\r\nConnection: close\r\n\r\n")
}

/// Best-effort read of the OPPO's /getmovieplayinfo (undocumented now-playing). Returns the
/// response body for the UI to parse; the payload shape is unverified -> hardware-pending.
#[tauri::command]
fn oppo_playback_info(host: String) -> Result<String, String> {
    validate_ssh_component("host", &host)?;
    let raw = oppo_http_exchange(&host, &oppo_info_request(&host), 5000)?;
    Ok(raw
        .split_once("\r\n\r\n")
        .map(|(_, body)| body.to_string())
        .unwrap_or(raw))
}

// ============================================================
// Add-on install — bundle the Kodi add-on inside the configurator and lay it down
// ============================================================
//
// The configurator bundles the add-on ZIP as a Tauri resource (resource_dir()/addon/<id>.zip).
// `bundled_addon_info` reads the version Kodi will see; `install_addon` lays the add-on into the
// Kodi `addons/` directory over the same transports as the config deploy (SSH / local-or-SMB), or
// copies the ZIP for a manual "Install from zip file". The on-box install (SSH unzip, Kodi restart,
// the add-on actually loading) is software-verified only -- not hardware-tested.

const ADDON_ID: &str = "script.oppo203.iso.external";

/// Pull the `version="..."` off the first `<addon ...>` element of an addon.xml string.
fn parse_addon_version(xml: &str) -> Option<String> {
    let start = xml.find("<addon")?;
    let rest = &xml[start..];
    let key = rest.find("version=\"")?;
    let after = &rest[key + "version=\"".len()..];
    let end = after.find('"')?;
    Some(after[..end].to_string())
}

/// Read the bundled add-on's declared version from the `addon.xml` inside the ZIP.
fn read_addon_version_from_zip(zip_path: &Path) -> Result<String, String> {
    let file = fs::File::open(zip_path)
        .map_err(|e| format!("bundled add-on not found at {}: {e}", zip_path.display()))?;
    let mut zip = zip::ZipArchive::new(file).map_err(|e| e.to_string())?;
    for i in 0..zip.len() {
        let mut entry = zip.by_index(i).map_err(|e| e.to_string())?;
        if entry.name().ends_with("addon.xml") {
            let mut xml = String::new();
            entry.read_to_string(&mut xml).map_err(|e| e.to_string())?;
            if let Some(v) = parse_addon_version(&xml) {
                return Ok(v);
            }
        }
    }
    Err("addon.xml with a version attribute not found in the bundle".into())
}

/// Extract every file in `zip_path` into `dest`, preserving the archive's relative layout (the
/// add-on ZIP carries a top-level `script.oppo203.iso.external/` folder). Returns the file count.
/// `enclosed_name` rejects absolute / `..` members (zip-slip), so a hostile archive can't escape.
fn extract_zip_into(zip_path: &Path, dest: &Path) -> Result<usize, String> {
    let file = fs::File::open(zip_path).map_err(|e| e.to_string())?;
    let mut zip = zip::ZipArchive::new(file).map_err(|e| e.to_string())?;
    let mut written = 0usize;
    for i in 0..zip.len() {
        let mut entry = zip.by_index(i).map_err(|e| e.to_string())?;
        let rel = match entry.enclosed_name() {
            Some(p) => p.to_path_buf(),
            None => continue,
        };
        let out = dest.join(&rel);
        if entry.is_dir() {
            fs::create_dir_all(&out).map_err(|e| e.to_string())?;
            continue;
        }
        if let Some(parent) = out.parent() {
            fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let mut buf = Vec::with_capacity(entry.size() as usize);
        entry.read_to_end(&mut buf).map_err(|e| e.to_string())?;
        fs::write(&out, &buf).map_err(|e| e.to_string())?;
        written += 1;
    }
    Ok(written)
}

#[derive(serde::Serialize)]
struct BundledAddonInfo {
    addon_id: String,
    version: String,
    path: String,
}

fn bundled_addon_zip(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let dir = app.path().resource_dir().map_err(|e| e.to_string())?;
    Ok(dir.join("addon").join(format!("{ADDON_ID}.zip")))
}

/// Report the add-on version the bundle would install (read from the bundled ZIP's addon.xml).
#[tauri::command]
fn bundled_addon_info(app: tauri::AppHandle) -> Result<BundledAddonInfo, String> {
    let zip = bundled_addon_zip(&app)?;
    let version = read_addon_version_from_zip(&zip)?;
    Ok(BundledAddonInfo {
        addon_id: ADDON_ID.to_string(),
        version,
        path: zip.to_string_lossy().into_owned(),
    })
}

#[derive(serde::Serialize)]
struct InstallReport {
    addon_id: String,
    version: String,
    files: usize,
    target: String,
    backed_up: Option<String>,
}

/// Lay the bundled add-on into a Kodi `addons/` directory.
///
/// `tier` "A" installs over SSH (push the ZIP, expand it on the box with `python3 -m zipfile`,
/// backing up any existing copy first; optional Kodi restart). "B" extracts the bundle directly
/// into a local or SMB-mounted `addons_path`. "C" copies the ZIP there for a manual "Install from
/// zip file". SSH/box behaviour is software-verified only -- not hardware-tested.
#[tauri::command]
fn install_addon(
    app: tauri::AppHandle,
    tier: String,
    host: Option<String>,
    user: Option<String>,
    addons_path: String,
    restart: bool,
) -> Result<InstallReport, String> {
    let zip = bundled_addon_zip(&app)?;
    let version = read_addon_version_from_zip(&zip)?;

    match tier.as_str() {
        "A" => {
            let host = host.ok_or("ssh host required for tier A")?;
            let user = user.ok_or("ssh user required for tier A")?;
            validate_ssh_target(&host, &user)?;
            let ssh_target = format!("{user}@{host}");
            let base = addons_path.trim_end_matches('/');
            let remote_dir = format!("{base}/{ADDON_ID}");
            let remote_zip = format!("{base}/.{ADDON_ID}.oppocfg.zip");
            let stamp = backup_suffix();
            let bytes = fs::read(&zip).map_err(|e| e.to_string())?;
            // Push the ZIP bytes, then expand on the box. `python3 -m zipfile` is present wherever
            // the add-on runs; fall back to `unzip`. Back up an existing install first.
            run_ssh_stdin(
                &ssh_target,
                &format!("mkdir -p '{base}' && cat > '{remote_zip}'"),
                &bytes,
            )?;
            let script = format!(
                "if [ -d '{remote_dir}' ]; then mv '{remote_dir}' '{remote_dir}.{stamp}.bak' && printf 'BAK:%s\\n' '{remote_dir}.{stamp}.bak'; fi && (python3 -m zipfile -e '{remote_zip}' '{base}/' || unzip -oq '{remote_zip}' -d '{base}/') && rm -f '{remote_zip}'"
            );
            let out = run_ssh_capture(&ssh_target, &script)?;
            let backed_up = out
                .lines()
                .find(|l| l.starts_with("BAK:"))
                .map(|l| l.trim_start_matches("BAK:").to_string());
            if restart {
                run_ssh(&ssh_target, "systemctl restart kodi")?;
            }
            Ok(InstallReport {
                addon_id: ADDON_ID.to_string(),
                version,
                files: 0,
                target: remote_dir,
                backed_up,
            })
        }
        "B" => {
            let dest = PathBuf::from(&addons_path);
            let addon_dir = dest.join(ADDON_ID);
            let mut backed_up = None;
            if addon_dir.exists() {
                let bak = format!("{}.{}.bak", addon_dir.to_string_lossy(), backup_suffix());
                fs::rename(&addon_dir, &bak).map_err(|e| e.to_string())?;
                backed_up = Some(bak);
            }
            let files = extract_zip_into(&zip, &dest)?;
            Ok(InstallReport {
                addon_id: ADDON_ID.to_string(),
                version,
                files,
                target: addon_dir.to_string_lossy().into_owned(),
                backed_up,
            })
        }
        "C" => {
            let dest = PathBuf::from(&addons_path);
            fs::create_dir_all(&dest).map_err(|e| e.to_string())?;
            let out = dest.join(format!("{ADDON_ID}.zip"));
            fs::copy(&zip, &out).map_err(|e| e.to_string())?;
            Ok(InstallReport {
                addon_id: ADDON_ID.to_string(),
                version,
                files: 1,
                target: out.to_string_lossy().into_owned(),
                backed_up: None,
            })
        }
        other => Err(format!("unknown install tier '{other}'")),
    }
}

/// Build the Kodi JSON-RPC body that enables the add-on (`Addons.SetAddonEnabled`).
fn kodi_enable_body(addon_id: &str) -> String {
    format!(
        r#"{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{addon_id}","enabled":true}}}}"#
    )
}

/// True when Kodi acknowledged the enable with `"result":"OK"`.
fn kodi_enable_ok(reply: &str) -> bool {
    reply.replace(' ', "").contains(r#""result":"OK""#)
}

/// Enable the installed add-on via Kodi JSON-RPC over SSH, so a freshly-dropped add-on doesn't
/// sit disabled (D-3). Returns true on Kodi's `"result":"OK"`; the caller falls back to a manual
/// Kodi restart on false/Err. Hardware-pending.
#[tauri::command]
fn kodi_set_addon_enabled(host: String, user: String) -> Result<bool, String> {
    validate_ssh_target(&host, &user)?;
    let target = format!("{user}@{host}");
    let cmd = kodi_jsonrpc_cmd(&kodi_enable_body(ADDON_ID));
    Ok(kodi_enable_ok(&run_ssh_capture(&target, &cmd)?))
}

// ============================================================
// Live OPPO verbose-mode monitor (dashboard live stream)
// ============================================================
//
// A persistent background thread holds one TCP connection to the OPPO, switches it to verbose
// mode 3 (`#SVM 3`), and streams each @UPL / @UTC / status push line to the webview as an
// "oppo-live" event. Mirrors resources/lib/oppo/playback_monitor_svm3.py: it remembers the
// prior verbose mode (`#QVM`) and restores it on stop. The OPPO treats verbose mode as a
// device-global setting, so only one subscriber should drive it at a time -- the DUAL-SUBSCRIBER
// gate is enforced on the frontend (it refuses to start while the add-on reports an active
// session). Not hardware-validated.

#[derive(serde::Serialize, Clone)]
struct LiveFrame {
    seq: u64,
    kind: String,
    raw: String,
}

struct LiveHandle {
    token: u64,
    stop: Arc<AtomicBool>,
    join: Option<std::thread::JoinHandle<()>>,
}

#[derive(Default)]
struct LiveMonitor(Mutex<Option<LiveHandle>>, std::sync::atomic::AtomicU64);

/// Classify an OPPO verbose push line by its leading code, for frontend coloring.
fn classify_frame(line: &str) -> &'static str {
    if line.starts_with("@UPL") {
        "upl"
    } else if line.starts_with("@UTC") {
        "utc"
    } else if line.starts_with('@') {
        "status"
    } else {
        "raw"
    }
}

/// Parse a `#QVM` reply ("@QVM OK 2") into the current verbose mode 0..3, or None on an error /
/// unparseable reply. Mirrors parseOppoVerboseMode in configurator/src/probes.ts.
fn parse_verbose_mode(reply: &str) -> Option<u8> {
    let upper = reply.to_ascii_uppercase();
    if upper.split_whitespace().any(|t| t == "ER") {
        return None;
    }
    for tok in upper.split_whitespace().rev() {
        if let Ok(n) = tok.parse::<u8>() {
            if n <= 3 {
                return Some(n);
            }
        }
    }
    None
}

fn write_cmd(stream: &mut TcpStream, cmd: &str) -> Result<(), String> {
    let mut s = cmd.to_string();
    if !s.ends_with('\r') {
        s.push('\r');
    }
    stream.write_all(s.as_bytes()).map_err(|e| e.to_string())
}

/// Read whatever is available (up to a couple of reads / the CR terminator) for a handshake
/// reply, honoring the stream's read timeout. Best-effort: a timeout just yields what we have.
fn read_brief(stream: &mut TcpStream) -> String {
    let mut data: Vec<u8> = Vec::new();
    let mut chunk = [0u8; 256];
    for _ in 0..2 {
        match stream.read(&mut chunk) {
            Ok(0) => break,
            Ok(n) => {
                data.extend_from_slice(&chunk[..n]);
                if data.contains(&b'\r') {
                    break;
                }
            }
            Err(_) => break,
        }
    }
    String::from_utf8_lossy(&data).trim().to_string()
}

fn emit_frame(app: &tauri::AppHandle, seq: u64, kind: &str, raw: String) {
    let _ = app.emit(
        "oppo-live",
        LiveFrame {
            seq,
            kind: kind.to_string(),
            raw,
        },
    );
}

fn run_live_loop(
    app: tauri::AppHandle,
    mut stream: TcpStream,
    prior: Option<u8>,
    stop: Arc<AtomicBool>,
) {
    let mut seq: u64 = 0;
    let mut buf: Vec<u8> = Vec::new();
    let mut chunk = [0u8; 512];
    emit_frame(
        &app,
        seq,
        "info",
        match prior {
            Some(n) => format!("verbose mode 3 enabled (prior mode {n})"),
            None => "verbose mode 3 enabled (prior mode unknown)".to_string(),
        },
    );
    seq += 1;
    while !stop.load(Ordering::SeqCst) {
        match stream.read(&mut chunk) {
            Ok(0) => {
                emit_frame(&app, seq, "info", "connection closed by player".to_string());
                break;
            }
            Ok(n) => {
                buf.extend_from_slice(&chunk[..n]);
                while let Some(i) = buf.iter().position(|&b| b == b'\r' || b == b'\n') {
                    let line: Vec<u8> = buf.drain(..=i).collect();
                    let text = String::from_utf8_lossy(&line).trim().to_string();
                    if text.is_empty() {
                        continue;
                    }
                    emit_frame(&app, seq, classify_frame(&text), text);
                    seq += 1;
                }
            }
            Err(ref e)
                if e.kind() == std::io::ErrorKind::WouldBlock
                    || e.kind() == std::io::ErrorKind::TimedOut =>
            {
                // idle tick; the loop re-checks the stop flag
            }
            Err(e) => {
                emit_frame(&app, seq, "error", format!("read error: {e}"));
                break;
            }
        }
    }
    // Restore the prior verbose mode (only if we learned it), then close.
    if let Some(n) = prior {
        let _ = write_cmd(&mut stream, &format!("#SVM {n}"));
        emit_frame(&app, seq, "info", format!("restored verbose mode {n}"));
    }
    let _ = stream.shutdown(std::net::Shutdown::Both);
}

/// Open a verbose-mode-3 stream to the player and emit each push line as an "oppo-live" event.
/// The frontend gates this so it never runs while the add-on owns a playback session.
#[tauri::command]
fn start_oppo_live_monitor(
    app: tauri::AppHandle,
    monitor: tauri::State<'_, LiveMonitor>,
    host: String,
    port: Option<u16>,
) -> Result<u64, String> {
    let port = port.unwrap_or(23);
    // Recover from a poisoned lock (a one-off panic must not wedge the monitor permanently).
    let mut guard = monitor.0.lock().unwrap_or_else(|p| p.into_inner());
    if guard.is_some() {
        return Err("live monitor already running".into());
    }
    let mut stream = connect_timeout(&host, port, 3000)?;
    stream
        .set_read_timeout(Some(Duration::from_millis(500)))
        .map_err(|e| e.to_string())?;
    stream
        .set_write_timeout(Some(Duration::from_millis(3000)))
        .map_err(|e| e.to_string())?;
    write_cmd(&mut stream, "#QVM")?;
    let prior = parse_verbose_mode(&read_brief(&mut stream));
    write_cmd(&mut stream, "#SVM 3")?;
    let _ = read_brief(&mut stream); // drain the #SVM ack
    let stop = Arc::new(AtomicBool::new(false));
    let stop_thread = stop.clone();
    let join = std::thread::spawn(move || run_live_loop(app, stream, prior, stop_thread));
    // Owner token: only the subscriber that started the stream (matching token) may stop it.
    let token = monitor.1.fetch_add(1, Ordering::SeqCst) + 1;
    *guard = Some(LiveHandle {
        token,
        stop,
        join: Some(join),
    });
    Ok(token)
}

/// Stop the live monitor (signals the thread, waits for it to restore verbose mode + close).
#[tauri::command]
fn stop_oppo_live_monitor(
    monitor: tauri::State<'_, LiveMonitor>,
    token: Option<u64>,
) -> Result<(), String> {
    let mut guard = monitor.0.lock().unwrap_or_else(|p| p.into_inner());
    // Only the owner (matching token) may stop the stream, so a sibling screen's unmount cannot
    // cancel another subscriber's live stream. A None / non-matching token is a no-op.
    let owns = matches!((token, guard.as_ref()), (Some(t), Some(h)) if h.token == t);
    if !owns {
        return Ok(());
    }
    let handle = guard.take();
    drop(guard);
    if let Some(mut h) = handle {
        h.stop.store(true, Ordering::SeqCst);
        if let Some(j) = h.join.take() {
            let _ = j.join();
        }
    }
    Ok(())
}

/// Build the raw HTTP request for one Roku ECP keypress (e.g. an input key like "InputHDMI1").
/// Mirrors resources/lib/tv/tv_roku_ecp_control.py (POST /keypress/<key> on :8060). The key is
/// validated alphanumeric so it cannot inject a different request path.
fn roku_keypress_request(host: &str, key: &str) -> Result<String, String> {
    if key.is_empty() || !key.chars().all(|c| c.is_ascii_alphanumeric()) {
        return Err(format!(
            "invalid Roku key '{key}' (expected an alphanumeric ECP key like InputHDMI1)"
        ));
    }
    Ok(format!(
        "POST /keypress/{key} HTTP/1.0\r\nHost: {host}:8060\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
    ))
}

/// Switch a Roku TV input by sending one ECP keypress to host:8060, mirroring the add-on's
/// tv_roku_ecp_control.send_keypress. Returns the HTTP status line on a 200. Software-verified
/// only -- not hardware-tested against a real Roku TV.
#[tauri::command]
fn tv_switch_roku(host: String, key: String, timeout_ms: Option<u64>) -> Result<String, String> {
    let request = roku_keypress_request(&host, &key)?;
    let ms = timeout_ms.unwrap_or(3000);
    let timeout = Duration::from_millis(ms);
    let mut stream = connect_timeout(&host, 8060, ms)?;
    stream
        .set_read_timeout(Some(timeout))
        .map_err(|e| e.to_string())?;
    stream
        .set_write_timeout(Some(timeout))
        .map_err(|e| e.to_string())?;
    stream
        .write_all(request.as_bytes())
        .map_err(|e| e.to_string())?;
    let mut data: Vec<u8> = Vec::new();
    let mut chunk = [0u8; 512];
    loop {
        match stream.read(&mut chunk) {
            Ok(0) => break,
            Ok(n) => {
                data.extend_from_slice(&chunk[..n]);
                if data.contains(&b'\n') || data.len() > 4096 {
                    break;
                }
            }
            Err(ref e)
                if e.kind() == std::io::ErrorKind::WouldBlock
                    || e.kind() == std::io::ErrorKind::TimedOut =>
            {
                break
            }
            Err(e) => return Err(e.to_string()),
        }
    }
    let text = String::from_utf8_lossy(&data);
    let status = text.lines().next().unwrap_or("").trim().to_string();
    if status.contains("200") {
        Ok(status)
    } else if status.is_empty() {
        Err("no response from the Roku TV (is the IP correct and ECP enabled?)".into())
    } else {
        Err(format!("Roku TV returned: {status}"))
    }
}

// ============================================================
// AVR input switching (Phase 3.1) -- per-brand builders + best-effort fire
// ============================================================
//
// Mirrors the add-on's AVR drivers (resources/lib/avr/): Denon/Marantz telnet `SI<input>` on :23,
// Onkyo/Integra/Pioneer eISCP `!1SLI<hh>` framed on :60128, Yamaha MusicCast/YXC HTTP `setInput`
// on :80, and the experimental Sony Audio Control API JSON-RPC `setPlayContent` POST. The builders
// are pure (unit-tested against the add-on's wire format); the fire commands open one short-lived
// socket like tv_switch_roku and are best-effort -- hardware-pending, not validated in-session.

const DENON_PORT: u16 = 23;
const EISCP_PORT: u16 = 60128;
const YAMAHA_PORT: u16 = 80;
const SONY_AUDIO_PORT: u16 = 80;

/// Build a Denon/Marantz input-select command (`SI<INPUT>`), validating like the add-on's
/// VALID_DENON_INPUT_RE (`^[A-Za-z0-9_/-]{1,32}$`, upper-cased). The wire frame appends CR.
fn denon_input_command(input: &str) -> Result<String, String> {
    let text = input.trim().to_ascii_uppercase();
    let n = text.chars().count();
    let ok = (1..=32).contains(&n)
        && text
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || matches!(c, '_' | '/' | '-'));
    if !ok {
        return Err(format!("invalid Denon/Marantz input '{input}'"));
    }
    Ok(format!("SI{text}"))
}

/// Build an Onkyo/Pioneer eISCP input-select payload (`!1SLI<HH>`) from a 2-hex-digit code.
fn eiscp_input_payload(code: &str) -> Result<String, String> {
    let text = code.trim().to_ascii_uppercase();
    if text.len() != 2 || !text.chars().all(|c| c.is_ascii_hexdigit()) {
        return Err(format!(
            "invalid eISCP input '{code}' (expected 2 hex digits)"
        ));
    }
    Ok(format!("!1SLI{text}"))
}

/// Frame an eISCP payload: `ISCP` magic + big-endian header/data sizes + version, the payload
/// terminated with CR. Mirrors build_eiscp_frame in avr_onkyo_eiscp.py.
fn eiscp_frame(payload: &str) -> Vec<u8> {
    let body = format!("{payload}\r");
    let body_bytes = body.as_bytes();
    let mut frame = Vec::with_capacity(16 + body_bytes.len());
    frame.extend_from_slice(b"ISCP");
    frame.extend_from_slice(&16u32.to_be_bytes());
    frame.extend_from_slice(&(body_bytes.len() as u32).to_be_bytes());
    frame.extend_from_slice(&[1, 0, 0, 0]);
    frame.extend_from_slice(body_bytes);
    frame
}

/// Build the Yamaha MusicCast/YXC `setInput` path+query for a validated input
/// (`^[A-Za-z0-9_/-]{1,64}$`). Fired as a raw HTTP GET.
fn yamaha_input_path(input: &str) -> Result<String, String> {
    let text = input.trim();
    let n = text.chars().count();
    let ok = (1..=64).contains(&n)
        && text
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || matches!(c, '_' | '/' | '-'));
    if !ok {
        return Err(format!("invalid Yamaha input '{input}'"));
    }
    Ok(format!(
        "/YamahaExtendedControl/v1/main/setInput?input={}",
        percent_encode(text)
    ))
}

/// Compact, key-sorted Sony Audio Control API JSON-RPC body (matches build_sony_audio_payload:
/// serde_json's default Map is a BTreeMap, so keys serialize sorted like Python's sort_keys=True).
fn sony_audio_payload(method: &str, params: serde_json::Value) -> String {
    serde_json::json!({"method": method, "params": params, "id": 1, "version": "1.0"}).to_string()
}

/// The Sony Audio Control API `setPlayContent` body for an input URI.
fn sony_audio_set_input_payload(uri: &str) -> String {
    sony_audio_payload("setPlayContent", serde_json::json!([{"uri": uri}]))
}

/// Raw HTTP/1.0 GET request for host:port + an absolute path/query.
fn http_get_request(host: &str, port: u16, path_query: &str) -> String {
    format!("GET {path_query} HTTP/1.0\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n")
}

/// Raw HTTP/1.0 JSON POST request. `extra_headers` (each `Name: value\r\n`) is inserted verbatim.
fn json_post_request(host: &str, port: u16, path: &str, body: &str, extra_headers: &str) -> String {
    format!(
        "POST {path} HTTP/1.0\r\nHost: {host}:{port}\r\nContent-Type: application/json; charset=UTF-8\r\nContent-Length: {len}\r\n{extra_headers}Connection: close\r\n\r\n{body}",
        len = body.len()
    )
}

/// Interpret a device reply: HTTP 2xx (or a non-HTTP raw echo) is Ok, other HTTP codes are Err.
fn device_response_ok(resp: &str) -> Result<String, String> {
    let first = resp.lines().next().unwrap_or("").trim().to_string();
    if first.is_empty() {
        return Err("no response from the device".to_string());
    }
    match first
        .split_whitespace()
        .nth(1)
        .and_then(|c| c.parse::<u16>().ok())
    {
        Some(c) if (200..300).contains(&c) => Ok(first),
        Some(_) => Err(format!("device returned: {first}")),
        None => Ok(first),
    }
}

/// First non-empty reply line, or a "sent" note when the device stays silent (Denon/eISCP often do).
fn first_line_or_sent(resp: &str) -> String {
    let line = resp
        .lines()
        .map(str::trim)
        .find(|l| !l.is_empty())
        .unwrap_or("");
    if line.is_empty() {
        "command sent (no response)".to_string()
    } else {
        line.to_string()
    }
}

/// Open one short-lived TCP connection, send `payload`, and return the device's reply (best-effort,
/// lossy UTF-8). Shared by the Denon/eISCP (raw) and Yamaha/Sony (HTTP) fire commands.
fn socket_exchange(
    host: &str,
    port: u16,
    payload: &[u8],
    timeout_ms: u64,
) -> Result<String, String> {
    let mut stream = connect_timeout(host, port, timeout_ms)?;
    let t = Duration::from_millis(timeout_ms);
    stream
        .set_read_timeout(Some(t))
        .map_err(|e| e.to_string())?;
    stream
        .set_write_timeout(Some(t))
        .map_err(|e| e.to_string())?;
    stream.write_all(payload).map_err(|e| e.to_string())?;
    let mut resp = Vec::new();
    let mut chunk = [0u8; 1024];
    loop {
        match stream.read(&mut chunk) {
            Ok(0) => break,
            Ok(n) => {
                resp.extend_from_slice(&chunk[..n]);
                if resp.len() >= 8192 {
                    break;
                }
            }
            Err(_) => break,
        }
    }
    Ok(String::from_utf8_lossy(&resp).into_owned())
}

/// Switch a Denon/Marantz receiver to an input over telnet (:23), mirroring send_denon_command.
/// Best-effort + hardware-pending.
#[tauri::command]
fn avr_switch_denon(
    host: String,
    input: String,
    port: Option<u16>,
    timeout_ms: Option<u64>,
) -> Result<String, String> {
    validate_ssh_component("host", &host)?;
    let command = denon_input_command(&input)?;
    let resp = socket_exchange(
        &host,
        port.unwrap_or(DENON_PORT),
        format!("{command}\r").as_bytes(),
        timeout_ms.unwrap_or(4000),
    )?;
    Ok(first_line_or_sent(&resp))
}

/// Switch an Onkyo/Integra/Pioneer receiver to an input over eISCP (:60128). Best-effort +
/// hardware-pending. Pioneer shares the protocol -- the brand label lives configurator-side.
#[tauri::command]
fn avr_switch_eiscp(
    host: String,
    input_code: String,
    port: Option<u16>,
    timeout_ms: Option<u64>,
) -> Result<String, String> {
    validate_ssh_component("host", &host)?;
    let frame = eiscp_frame(&eiscp_input_payload(&input_code)?);
    let resp = socket_exchange(
        &host,
        port.unwrap_or(EISCP_PORT),
        &frame,
        timeout_ms.unwrap_or(4000),
    )?;
    Ok(first_line_or_sent(&resp))
}

/// Switch a Yamaha MusicCast/YXC receiver to an input over HTTP (:80). Best-effort +
/// hardware-pending.
#[tauri::command]
fn avr_switch_yamaha(
    host: String,
    input: String,
    port: Option<u16>,
    timeout_ms: Option<u64>,
) -> Result<String, String> {
    validate_ssh_component("host", &host)?;
    let p = port.unwrap_or(YAMAHA_PORT);
    let request = http_get_request(&host, p, &yamaha_input_path(&input)?);
    let resp = socket_exchange(&host, p, request.as_bytes(), timeout_ms.unwrap_or(5000))?;
    device_response_ok(&resp)
}

/// Switch a Sony AV receiver to an input via the experimental Audio Control API (`setPlayContent`
/// POST). Best-effort + hardware-pending.
#[tauri::command]
fn avr_switch_sony_audio(
    host: String,
    input_uri: String,
    api_path: Option<String>,
    psk: Option<String>,
    timeout_ms: Option<u64>,
) -> Result<String, String> {
    validate_ssh_component("host", &host)?;
    if input_uri.trim().is_empty() {
        return Err("input_uri is empty".to_string());
    }
    let path = api_path
        .map(|p| p.trim().to_string())
        .filter(|p| !p.is_empty())
        .unwrap_or_else(|| "/sony/audio".to_string());
    if !path.starts_with('/') || path.contains("..") || path.contains('\r') || path.contains('\n') {
        return Err(format!("invalid Sony Audio API path '{path}'"));
    }
    let extra = match psk.as_deref().map(str::trim).filter(|s| !s.is_empty()) {
        Some(p) => format!("X-Auth-PSK: {p}\r\n"),
        None => String::new(),
    };
    let body = sony_audio_set_input_payload(input_uri.trim());
    let request = json_post_request(&host, SONY_AUDIO_PORT, &path, &body, &extra);
    let resp = socket_exchange(
        &host,
        SONY_AUDIO_PORT,
        request.as_bytes(),
        timeout_ms.unwrap_or(5000),
    )?;
    device_response_ok(&resp)
}

// ============================================================
// TV input switching (Phase 3.1) -- per-backend builders + fire
// ============================================================
//
// Mirrors resources/lib/tv/. Sony Bravia switches directly over its REST API (X-Auth-PSK
// setPlayContent). The command-based backends (adb / lg / samsung / custom) run on the Kodi box
// over the existing SSH channel exactly as the add-on's tv_control does on-device. SmartThings
// builds its cloud request for display/confirmation -- HTTPS firing is out of scope (no TLS crate).
// Builders are unit-tested; the fire commands are best-effort + hardware-pending.

const SONY_BRAVIA_PORT: u16 = 80;

/// The Sony Bravia `setPlayContent` body selecting an HDMI port (`extInput:hdmi?port=N`).
fn sony_bravia_set_input_body(port: u32) -> String {
    serde_json::json!({
        "method": "setPlayContent",
        "version": "1.0",
        "id": 1,
        "params": [{"uri": format!("extInput:hdmi?port={port}")}]
    })
    .to_string()
}

/// Switch a Sony Bravia TV to an HDMI port over its REST API (POST /sony/avContent, X-Auth-PSK),
/// mirroring _sony_set_hdmi in tv_control.py. Best-effort + hardware-pending.
#[tauri::command]
fn tv_switch_sony_bravia(
    host: String,
    psk: String,
    port: u32,
    timeout_ms: Option<u64>,
) -> Result<String, String> {
    validate_ssh_component("host", &host)?;
    if psk.trim().is_empty() {
        return Err("Sony Bravia PSK is required".to_string());
    }
    let body = sony_bravia_set_input_body(port);
    let extra = format!("X-Auth-PSK: {}\r\n", psk.trim());
    let request = json_post_request(&host, SONY_BRAVIA_PORT, "/sony/avContent", &body, &extra);
    let resp = socket_exchange(
        &host,
        SONY_BRAVIA_PORT,
        request.as_bytes(),
        timeout_ms.unwrap_or(5000),
    )?;
    device_response_ok(&resp)
}

/// Substitute `{tv_ip}` into a user-configured TV command template (lg / samsung / custom),
/// mirroring tv_control._run_external's `command.format(tv_ip=...)`.
fn format_external_command(template: &str, tv_ip: &str) -> Result<String, String> {
    let cmd = template.trim();
    if cmd.is_empty() {
        return Err("TV command is empty".to_string());
    }
    Ok(cmd.replace("{tv_ip}", tv_ip))
}

/// Build the on-box adb shell line that selects a TV input, mirroring tv_adb_control: connect, then
/// `adb -s host:port shell <command>`. Run on the Kodi box over SSH, where adb lives.
fn adb_switch_command_line(
    adb_path: &str,
    host: &str,
    port: u16,
    command: &str,
) -> Result<String, String> {
    let cmd = command.trim();
    if cmd.is_empty() {
        return Err("adb shell command is empty".to_string());
    }
    let adb = adb_path.trim();
    let adb = if adb.is_empty() { "adb" } else { adb };
    Ok(format!(
        "{adb} connect {host}:{port} >/dev/null 2>&1; {adb} -s {host}:{port} shell {cmd}"
    ))
}

/// Switch an LG / Samsung / custom TV input by running its configured command on the Kodi box over
/// SSH (the add-on runs the same command on-device). Best-effort + hardware-pending.
#[tauri::command]
fn tv_switch_external(
    ssh_host: String,
    ssh_user: String,
    template: String,
    tv_ip: String,
) -> Result<String, String> {
    validate_ssh_target(&ssh_host, &ssh_user)?;
    let command = format_external_command(&template, &tv_ip)?;
    let out = run_ssh_capture(&format!("{ssh_user}@{ssh_host}"), &command)?;
    Ok(first_line_or_sent(&out))
}

/// Switch a TV input via adb run on the Kodi box over SSH (adb connect + `adb shell <command>`).
/// Best-effort + hardware-pending.
#[tauri::command]
fn tv_switch_adb(
    ssh_host: String,
    ssh_user: String,
    adb_path: String,
    tv_host: String,
    tv_port: u16,
    adb_command: String,
) -> Result<String, String> {
    validate_ssh_target(&ssh_host, &ssh_user)?;
    validate_ssh_component("tv_host", &tv_host)?;
    let command = adb_switch_command_line(&adb_path, &tv_host, tv_port, &adb_command)?;
    let out = run_ssh_capture(&format!("{ssh_user}@{ssh_host}"), &command)?;
    Ok(first_line_or_sent(&out))
}

/// The SmartThings cloud `commands` URL for a device id (`/devices/<id>/commands`).
fn smartthings_command_url(device_id: &str) -> String {
    format!(
        "https://api.smartthings.com/v1/devices/{}/commands",
        percent_encode(device_id)
    )
}

/// The SmartThings `setInputSource` command body for a media input id, mirroring
/// _build_command_payload in tv_smartthings_control.py.
fn smartthings_set_input_body(input_id: &str) -> String {
    serde_json::json!({
        "commands": [{
            "component": "main",
            "capability": "mediaInputSource",
            "command": "setInputSource",
            "arguments": [input_id]
        }]
    })
    .to_string()
}

#[derive(serde::Serialize)]
struct SmartThingsRequest {
    url: String,
    body: String,
}

/// Build the SmartThings input-switch request (URL + JSON body) for the UI to display/confirm. The
/// add-on fires this on-device over HTTPS with the user's bearer token; the configurator constructs
/// it here (HTTPS firing is out of scope -- no TLS crate) so the operator can verify it.
#[tauri::command]
fn smartthings_switch_request(
    device_id: String,
    input_id: String,
) -> Result<SmartThingsRequest, String> {
    if device_id.trim().is_empty() {
        return Err("SmartThings device id is required".to_string());
    }
    if input_id.trim().is_empty() {
        return Err("SmartThings input id is required".to_string());
    }
    Ok(SmartThingsRequest {
        url: smartthings_command_url(device_id.trim()),
        body: smartthings_set_input_body(input_id.trim()),
    })
}

#[cfg(test)]
mod tests {
    use super::{
        adb_switch_command_line, box_reset_targets, classify_frame, copy_progress_percent,
        denon_input_command,
        device_response_ok, eiscp_frame, eiscp_input_payload, extract_zip_into, first_line_or_sent,
        format_external_command, http_get_request, json_post_request, kodi_enable_body,
        kodi_enable_ok, kodi_get_item_body, oppo_info_request, oppo_play_payload,
        oppo_play_request, oppo_power_token, oppo_signin_request, parse_addon_version,
        parse_kodi_active_player_id, parse_kodi_log_file, parse_kodi_player_file,
        parse_verbose_mode, percent_encode, remove_existing_paths, roku_keypress_request,
        safe_app_rel,
        smartthings_command_url, smartthings_set_input_body, sony_audio_set_input_payload,
        sony_bravia_set_input_body, to_hex, unc_host, validate_copy_paths, yamaha_input_path,
    };

    #[test]
    fn oppo_power_token_maps_actions() {
        assert_eq!(oppo_power_token("off").unwrap(), "#POF");
        assert_eq!(oppo_power_token("Power_On").unwrap(), "#PON");
        assert_eq!(oppo_power_token(" eject ").unwrap(), "#EJT");
        assert!(oppo_power_token("explode").is_err());
    }

    #[test]
    fn copy_progress_percent_is_saturating_and_zero_safe() {
        assert_eq!(copy_progress_percent(0, 100), 0);
        assert_eq!(copy_progress_percent(50, 100), 50);
        assert_eq!(copy_progress_percent(100, 100), 100);
        // never exceeds 100 even if copied somehow overshoots.
        assert_eq!(copy_progress_percent(150, 100), 100);
        // a zero-byte total reads as complete, not a divide-by-zero.
        assert_eq!(copy_progress_percent(0, 0), 100);
        // large (multi-GB) totals don't overflow the intermediate product.
        assert_eq!(copy_progress_percent(8_000_000_000, 16_000_000_000), 50);
    }

    #[test]
    fn validate_copy_paths_requires_both_and_a_file_name() {
        assert!(validate_copy_paths("C:/src/test.iso", "\\\\nas\\Movies\\test.iso").is_ok());
        assert!(validate_copy_paths("  ", "\\\\nas\\Movies\\test.iso").is_err());
        assert!(validate_copy_paths("C:/src/test.iso", "   ").is_err());
        // a bare directory destination (trailing separator) is rejected -- we need a file name.
        assert!(validate_copy_paths("C:/src/test.iso", "\\\\nas\\Movies\\").is_err());
        assert!(validate_copy_paths("C:/src/test.iso", "/mnt/share/").is_err());
    }

    #[test]
    fn sony_bravia_body_selects_hdmi_port() {
        let body = sony_bravia_set_input_body(2);
        assert!(body.contains(r#""method":"setPlayContent""#));
        assert!(body.contains(r#""uri":"extInput:hdmi?port=2""#));
    }

    #[test]
    fn format_external_command_substitutes_tv_ip() {
        assert_eq!(
            format_external_command("curl http://{tv_ip}/x", "10.0.0.8").unwrap(),
            "curl http://10.0.0.8/x"
        );
        assert!(format_external_command("   ", "10.0.0.8").is_err());
    }

    #[test]
    fn adb_switch_command_line_connects_then_shells() {
        let line = adb_switch_command_line("adb", "10.0.0.7", 5555, "input keyevent KEYCODE_HOME")
            .unwrap();
        assert!(line.contains("adb connect 10.0.0.7:5555"));
        assert!(line.contains("adb -s 10.0.0.7:5555 shell input keyevent KEYCODE_HOME"));
        assert!(adb_switch_command_line("adb", "10.0.0.7", 5555, "  ").is_err());
        // empty adb path falls back to `adb`.
        assert!(adb_switch_command_line("", "10.0.0.7", 5555, "x")
            .unwrap()
            .starts_with("adb connect"));
    }

    #[test]
    fn smartthings_request_targets_device_commands() {
        assert_eq!(
            smartthings_command_url("dev-1"),
            "https://api.smartthings.com/v1/devices/dev-1/commands"
        );
        let body = smartthings_set_input_body("HDMI1");
        assert!(body.contains(r#""command":"setInputSource""#));
        assert!(body.contains(r#""capability":"mediaInputSource""#));
        assert!(body.contains(r#""HDMI1""#));
    }

    #[test]
    fn denon_input_command_builds_si_and_upper_cases() {
        assert_eq!(denon_input_command("bd").unwrap(), "SIBD");
        assert_eq!(denon_input_command(" Game ").unwrap(), "SIGAME");
    }

    #[test]
    fn denon_input_command_rejects_junk() {
        assert!(denon_input_command("").is_err());
        assert!(denon_input_command("BD;rm").is_err());
        assert!(denon_input_command(&"X".repeat(33)).is_err());
    }

    #[test]
    fn eiscp_input_payload_requires_two_hex_digits() {
        assert_eq!(eiscp_input_payload("23").unwrap(), "!1SLI23");
        assert_eq!(eiscp_input_payload("0a").unwrap(), "!1SLI0A");
        assert!(eiscp_input_payload("2").is_err());
        assert!(eiscp_input_payload("ZZ").is_err());
        assert!(eiscp_input_payload("233").is_err());
    }

    #[test]
    fn eiscp_frame_has_iscp_magic_and_sizes() {
        let frame = eiscp_frame("!1SLI23");
        assert_eq!(&frame[0..4], b"ISCP");
        assert_eq!(&frame[4..8], &16u32.to_be_bytes());
        // payload is the command plus a trailing CR.
        assert_eq!(&frame[8..12], &8u32.to_be_bytes());
        assert_eq!(frame[12], 1);
        assert_eq!(&frame[16..], b"!1SLI23\r");
    }

    #[test]
    fn yamaha_input_path_targets_set_input() {
        assert_eq!(
            yamaha_input_path("hdmi1").unwrap(),
            "/YamahaExtendedControl/v1/main/setInput?input=hdmi1"
        );
        assert!(yamaha_input_path("").is_err());
        assert!(yamaha_input_path("bad input").is_err());
    }

    #[test]
    fn sony_audio_payload_is_compact_and_key_sorted() {
        let body = sony_audio_set_input_payload("extInput:hdmi?port=1");
        assert!(body.contains(r#""method":"setPlayContent""#));
        assert!(body.contains(r#""uri":"extInput:hdmi?port=1""#));
        // sort_keys: id precedes method precedes params precedes version, with no spaces.
        assert!(body.starts_with(r#"{"id":1,"method":"#));
        assert!(!body.contains(", "));
    }

    #[test]
    fn json_post_request_sets_content_length() {
        let body = "{\"a\":1}";
        let req = json_post_request("10.0.0.5", 80, "/sony/audio", body, "X-Auth-PSK: k\r\n");
        assert!(req.starts_with("POST /sony/audio HTTP/1.0\r\n"));
        assert!(req.contains(&format!("Content-Length: {}\r\n", body.len())));
        assert!(req.contains("X-Auth-PSK: k\r\n"));
        assert!(req.ends_with(body));
    }

    #[test]
    fn http_get_request_is_well_formed() {
        let req = http_get_request("10.0.0.6", 80, "/x?y=1");
        assert!(req.starts_with("GET /x?y=1 HTTP/1.0\r\n"));
        assert!(req.contains("Host: 10.0.0.6:80\r\n"));
    }

    #[test]
    fn device_response_ok_reads_http_status() {
        assert!(device_response_ok("HTTP/1.1 200 OK\r\n\r\n{}").is_ok());
        assert!(device_response_ok("HTTP/1.0 403 Forbidden\r\n").is_err());
        assert!(device_response_ok("").is_err());
        // a non-HTTP raw echo (e.g. a Denon ack) is treated as a reply, not an error.
        assert!(device_response_ok("SIBD").is_ok());
    }

    #[test]
    fn first_line_or_sent_handles_silence() {
        assert_eq!(first_line_or_sent("  \n SIBD \n"), "SIBD");
        assert_eq!(first_line_or_sent("   "), "command sent (no response)");
    }

    #[test]
    fn kodi_enable_body_targets_set_addon_enabled() {
        let b = kodi_enable_body("script.oppo203.iso.external");
        assert!(b.contains(r#""method":"Addons.SetAddonEnabled""#));
        assert!(b.contains(r#""addonid":"script.oppo203.iso.external""#));
        assert!(b.contains(r#""enabled":true"#));
    }

    #[test]
    fn kodi_enable_ok_reads_result_ok() {
        assert!(kodi_enable_ok(r#"{"id":1,"jsonrpc":"2.0","result":"OK"}"#));
        assert!(kodi_enable_ok(r#"{"result": "OK"}"#));
        assert!(!kodi_enable_ok(r#"{"error":{"code":-32602}}"#));
        assert!(!kodi_enable_ok("not json"));
    }

    #[test]
    fn classifies_verbose_frames() {
        assert_eq!(classify_frame("@UPL PLAY"), "upl");
        assert_eq!(classify_frame("@UTC 0 0 T 00:00:01"), "utc");
        assert_eq!(classify_frame("@UPW ON"), "status");
        assert_eq!(classify_frame("garbage"), "raw");
    }

    #[test]
    fn parses_verbose_mode_reply() {
        assert_eq!(parse_verbose_mode("@QVM OK 2"), Some(2));
        assert_eq!(parse_verbose_mode("@QVM OK 0"), Some(0));
        assert_eq!(parse_verbose_mode("@QVM ER"), None);
        assert_eq!(parse_verbose_mode("nonsense"), None);
    }

    #[test]
    fn to_hex_empty() {
        assert_eq!(to_hex(&[]), "");
    }

    #[test]
    fn to_hex_ascii_command_with_cr() {
        assert_eq!(to_hex(b"#QVM\r"), "23 51 56 4d 0d");
    }

    #[test]
    fn to_hex_non_utf8_bytes() {
        assert_eq!(to_hex(&[0xff, 0x00, 0x1b]), "ff 00 1b");
    }

    #[test]
    fn parses_addon_version_attribute() {
        assert_eq!(
            parse_addon_version(r#"<addon id="x" version="2.9.14" name="y">"#),
            Some("2.9.14".to_string())
        );
        assert_eq!(
            parse_addon_version("<addon\n  version=\"1.0.0-exp\">"),
            Some("1.0.0-exp".to_string())
        );
        assert_eq!(parse_addon_version("<nope/>"), None);
    }

    #[test]
    fn extract_zip_into_lays_down_files_and_dirs() {
        use std::io::Write as _;
        let tmp = std::env::temp_dir().join(format!("oppocfg-ztest-{}", super::backup_suffix()));
        std::fs::create_dir_all(&tmp).unwrap();
        let zip_path = tmp.join("a.zip");
        {
            let f = std::fs::File::create(&zip_path).unwrap();
            let mut zw = zip::ZipWriter::new(f);
            let opts = zip::write::SimpleFileOptions::default()
                .compression_method(zip::CompressionMethod::Stored);
            zw.start_file("script.oppo203.iso.external/addon.xml", opts)
                .unwrap();
            zw.write_all(b"<addon version=\"9.9.9\"/>").unwrap();
            zw.start_file("script.oppo203.iso.external/resources/lib/x.py", opts)
                .unwrap();
            zw.write_all(b"print(1)").unwrap();
            zw.finish().unwrap();
        }
        let dest = tmp.join("out");
        let n = extract_zip_into(&zip_path, &dest).unwrap();
        assert_eq!(n, 2);
        assert!(dest.join("script.oppo203.iso.external/addon.xml").is_file());
        assert!(dest
            .join("script.oppo203.iso.external/resources/lib/x.py")
            .is_file());
        let _ = std::fs::remove_dir_all(&tmp);
    }

    #[test]
    fn roku_keypress_request_builds_a_valid_post_for_an_input_key() {
        let req = roku_keypress_request("10.0.1.55", "InputHDMI1").unwrap();
        assert!(req.starts_with("POST /keypress/InputHDMI1 HTTP/1.0\r\n"));
        assert!(req.contains("Host: 10.0.1.55:8060\r\n"));
        assert!(req.ends_with("\r\n\r\n"));
    }

    #[test]
    fn roku_keypress_request_rejects_path_injection_and_junk() {
        assert!(roku_keypress_request("10.0.1.55", "../launch/dev").is_err());
        assert!(roku_keypress_request("10.0.1.55", "Input HDMI1").is_err());
        assert!(roku_keypress_request("10.0.1.55", "").is_err());
    }

    #[test]
    fn kodi_get_item_body_pins_playerid_and_file_property() {
        let body = kodi_get_item_body(1);
        assert!(body.contains(r#""method":"Player.GetItem""#));
        assert!(body.contains(r#""playerid":1"#));
        assert!(body.contains(r#""properties":["file"]"#));
    }

    #[test]
    fn parses_active_player_id() {
        assert_eq!(
            parse_kodi_active_player_id(r#"{"result":[{"playerid":1,"type":"video"}]}"#),
            Some(1)
        );
        assert_eq!(parse_kodi_active_player_id(r#"{"result":[]}"#), None);
        assert_eq!(
            parse_kodi_active_player_id(r#"{"result":[{"type":"video"}]}"#),
            None
        );
        assert_eq!(parse_kodi_active_player_id("not json"), None);
    }

    #[test]
    fn parses_player_file_path() {
        assert_eq!(
            parse_kodi_player_file(
                r#"{"result":{"item":{"file":"smb://nas/Movies/Film.iso","label":"Film"}}}"#
            ),
            Some("smb://nas/Movies/Film.iso".to_string())
        );
        assert_eq!(
            parse_kodi_player_file(r#"{"result":{"item":{"label":"x"}}}"#),
            None
        );
        assert_eq!(
            parse_kodi_player_file(r#"{"result":{"item":{"file":"  "}}}"#),
            None
        );
        assert_eq!(parse_kodi_player_file("nonsense"), None);
    }

    #[test]
    fn parses_last_opened_file_from_log() {
        let log = "2026-06-01 11:59 T:1 info <general>: VideoPlayer::OpenFile: nfs://10.0.0.5/v1/Old.mkv\n2026-06-01 12:00 T:1 info <general>: CVideoPlayer::OpenFile: smb://nas/Movies/Film.iso\n2026-06-01 12:00 T:1 debug <general>: something else";
        assert_eq!(
            parse_kodi_log_file(log),
            Some("smb://nas/Movies/Film.iso".to_string())
        );
        assert_eq!(parse_kodi_log_file("no markers here"), None);
    }

    #[test]
    fn percent_encode_matches_quote_safe_empty() {
        assert_eq!(percent_encode("abcABC123-_.~"), "abcABC123-_.~");
        assert_eq!(percent_encode("a b/c"), "a%20b%2Fc");
        assert_eq!(percent_encode("{\"k\":\"v\"}"), "%7B%22k%22%3A%22v%22%7D");
    }

    #[test]
    fn oppo_play_payload_has_the_spec_fields() {
        let p = oppo_play_payload("smb://nas/Movies/Film.iso");
        assert!(p.contains(r#""path":"smb://nas/Movies/Film.iso""#));
        assert!(p.contains(r#""index":0"#));
        assert!(p.contains(r#""type":1"#));
        assert!(p.contains(r#""appDeviceType":2"#));
        assert!(p.contains(r#""extraNetPath":"""#));
        assert!(p.contains(r#""playMode":0"#));
    }

    #[test]
    fn oppo_play_request_is_a_playnormalfile_get() {
        let req = oppo_play_request("10.0.0.9", "smb://nas/x.iso");
        assert!(req.starts_with("GET /playnormalfile?payload=%7B"));
        assert!(req.contains("HTTP/1.0\r\n"));
        assert!(req.contains("Host: 10.0.0.9:436\r\n"));
        assert!(req.ends_with("\r\n\r\n"));
    }

    #[test]
    fn oppo_signin_request_targets_signin() {
        let req = oppo_signin_request("10.0.0.9");
        assert!(req.starts_with("GET /signin?%7B"));
        assert!(req.contains("Host: 10.0.0.9:436\r\n"));
    }

    #[test]
    fn oppo_info_request_targets_getmovieplayinfo() {
        let req = oppo_info_request("10.0.0.9");
        assert!(req.starts_with("GET /getmovieplayinfo HTTP/1.0\r\n"));
        assert!(req.contains("Host: 10.0.0.9:436\r\n"));
        assert!(req.ends_with("\r\n\r\n"));
    }

    #[test]
    fn safe_app_rel_accepts_nested_names() {
        assert_eq!(
            safe_app_rel("dashboard/session-log.json").unwrap(),
            std::path::Path::new("dashboard/session-log.json")
        );
    }

    #[test]
    fn safe_app_rel_rejects_parent_traversal() {
        assert!(safe_app_rel("dashboard/../../etc/passwd").is_err());
        assert!(safe_app_rel("../state.json").is_err());
    }

    #[test]
    fn safe_app_rel_rejects_absolute() {
        assert!(safe_app_rel("/etc/passwd").is_err());
    }

    #[test]
    fn box_reset_targets_are_the_four_owned_paths() {
        let ud = std::path::Path::new("/storage/.kodi/userdata");
        let ad = std::path::Path::new("/storage/.kodi/addons");
        let t = box_reset_targets(ud, ad);
        assert_eq!(t.len(), 4);
        // the add-on folder under addons/, never the addons root itself
        assert_eq!(t[0], ad.join("script.oppo203.iso.external"));
        assert!(t.iter().any(|p| p.ends_with("playercorefactory.xml")));
        assert!(t.iter().any(|p| p.ends_with("oppo203iso.xml")));
        assert!(t.iter().any(|p| p.to_string_lossy().contains("addon_data")));
        // neither the userdata nor the addons root is ever a delete target
        assert!(!t.iter().any(|p| p == ud || p == ad));
    }

    #[test]
    fn unc_host_extracts_share_host_and_skips_local_paths() {
        assert_eq!(unc_host(r"\\10.0.1.42\Kodi\userdata").as_deref(), Some("10.0.1.42"));
        assert_eq!(unc_host(r"\\NAS\Kodi").as_deref(), Some("NAS"));
        assert_eq!(unc_host("//10.0.1.42/Kodi/userdata").as_deref(), Some("10.0.1.42"));
        // local / drive paths have no network host -> no probe
        assert_eq!(unc_host(r"C:\Users\me\.kodi\userdata"), None);
        assert_eq!(unc_host("/storage/.kodi/userdata"), None);
        assert_eq!(unc_host(r"\\"), None);
    }

    #[test]
    fn remove_existing_paths_removes_owned_and_spares_the_rest() {
        let base = std::env::temp_dir().join(format!("oppocfg_reset_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let ud = base.join("userdata");
        let ad = base.join("addons");
        let addon_dir = ad.join("script.oppo203.iso.external");
        std::fs::create_dir_all(addon_dir.join("resources")).unwrap();
        std::fs::write(addon_dir.join("addon.xml"), "x").unwrap();
        std::fs::create_dir_all(ud.join("keymaps")).unwrap();
        std::fs::write(ud.join("playercorefactory.xml"), "x").unwrap();
        std::fs::write(ud.join("keymaps").join("oppo203iso.xml"), "x").unwrap();
        std::fs::create_dir_all(ud.join("addon_data").join("script.oppo203.iso.external")).unwrap();
        // an unrelated userdata file must survive the reset
        std::fs::write(ud.join("advancedsettings.xml"), "keep").unwrap();

        let targets = box_reset_targets(&ud, &ad);
        let removed = remove_existing_paths(&targets).unwrap();
        assert_eq!(removed.len(), 4);
        assert!(!addon_dir.exists());
        assert!(!ud.join("playercorefactory.xml").exists());
        assert!(!ud.join("addon_data").join("script.oppo203.iso.external").exists());
        assert!(ud.join("advancedsettings.xml").exists()); // untouched
        assert!(ud.exists() && ad.exists()); // roots survive
        // idempotent: a second pass removes nothing
        assert!(remove_existing_paths(&targets).unwrap().is_empty());
        let _ = std::fs::remove_dir_all(&base);
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(LiveMonitor::default())
        .invoke_handler(tauri::generate_handler![
            load_wizard_state,
            save_wizard_state,
            read_app_json,
            write_app_json,
            generate_files,
            reveal_path,
            read_userdata_file,
            read_ssh_file,
            deploy_to_userdata,
            smb_test_write,
            copy_to_share,
            tcp_probe,
            tv_port_probe,
            oppo_query,
            oppo_power,
            ssh_test,
            deploy_ssh,
            kodi_now_playing,
            oppo_http_play,
            oppo_playback_info,
            bundled_addon_info,
            install_addon,
            kodi_set_addon_enabled,
            tv_switch_roku,
            avr_switch_denon,
            avr_switch_eiscp,
            avr_switch_yamaha,
            avr_switch_sony_audio,
            tv_switch_sony_bravia,
            tv_switch_external,
            tv_switch_adb,
            smartthings_switch_request,
            start_oppo_live_monitor,
            stop_oppo_live_monitor,
            reset_box_userdata,
            reset_box_ssh,
            reset_app_data,
            diagnostics_env,
            write_diagnostics
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
