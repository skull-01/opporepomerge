use serde_json::Value;
use std::collections::BTreeMap;
use std::fs;
use std::io::{Read, Write};
use std::net::{TcpStream, ToSocketAddrs};
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

/// Write the generated files (keyed by path relative to Kodi userdata/) into the app's
/// data dir under `generated/`, mirroring the userdata layout. Returns the output dir.
#[tauri::command]
fn generate_files(app: tauri::AppHandle, files: BTreeMap<String, String>) -> Result<String, String> {
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
        return Err(format!("ssh {label} '{v}' contains an invalid character '{c}'"));
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
    fs::read_to_string(&path).map(Some).map_err(|e| e.to_string())
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
    let mut written = Vec::new();
    let mut backed_up = Vec::new();
    for (rel, contents) in &files {
        let target = base.join(rel);
        if let Some(parent) = target.parent() {
            fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        if target.exists() {
            let bak = format!("{}.{}.bak", target.to_string_lossy(), backup_suffix());
            fs::copy(&target, &bak).map_err(|e| e.to_string())?;
            backed_up.push(bak);
        }
        // Write to a sibling temp file then swap it in, so an interrupted write can't leave a
        // truncated target (the .bak above covers the brief replace window).
        let tmp = std::path::PathBuf::from(format!("{}.oppocfg-tmp", target.to_string_lossy()));
        fs::write(&tmp, contents).map_err(|e| e.to_string())?;
        if target.exists() {
            fs::remove_file(&target).map_err(|e| e.to_string())?;
        }
        fs::rename(&tmp, &target).map_err(|e| e.to_string())?;
        written.push(target.to_string_lossy().into_owned());
    }
    Ok(DeployReport { written, backed_up })
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
    stream.set_read_timeout(Some(timeout)).map_err(|e| e.to_string())?;
    stream.set_write_timeout(Some(timeout)).map_err(|e| e.to_string())?;
    let mut cmd = command.unwrap_or_else(|| "#QPW".to_string());
    if !cmd.ends_with('\r') {
        cmd.push('\r');
    }
    emit_wire(&app, "sent", &host, port, cmd.as_bytes());
    stream.write_all(cmd.as_bytes()).map_err(|e| e.to_string())?;
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

fn ssh_base_args(target: &str) -> Vec<String> {
    vec![
        "-o".into(),
        "BatchMode=yes".into(),
        "-o".into(),
        "StrictHostKeyChecking=accept-new".into(),
        "-o".into(),
        "ConnectTimeout=8".into(),
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
    let mut written = Vec::new();
    let mut backed_up = Vec::new();
    for (rel, contents) in &files {
        let remote = format!("{base}/{rel}");
        let parent = remote.rsplit_once('/').map(|(p, _)| p).unwrap_or(".");
        let bak = format!("{remote}.{}.bak", backup_suffix());
        // Back up an existing file before overwriting; '&&' chaining ABORTS the write if the
        // backup fails, and the echoed marker lets us report the real .bak path.
        let script = format!(
            "mkdir -p '{parent}' && if [ -f '{remote}' ]; then cp -p '{remote}' '{bak}' && printf 'BAK:%s\\n' '{bak}'; fi && cat > '{remote}'"
        );
        let stdout = run_ssh_stdin(&target, &script, contents.as_bytes())?;
        written.push(remote);
        if let Some(line) = stdout.lines().find(|l| l.starts_with("BAK:")) {
            backed_up.push(line.trim_start_matches("BAK:").to_string());
        }
    }
    if restart {
        run_ssh(&target, "systemctl restart kodi")?;
    }
    Ok(DeployReport { written, backed_up })
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
            if let Ok(item) = run_ssh_capture(&target, &kodi_jsonrpc_cmd(&kodi_get_item_body(pid))) {
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
    stop: Arc<AtomicBool>,
    join: Option<std::thread::JoinHandle<()>>,
}

#[derive(Default)]
struct LiveMonitor(Mutex<Option<LiveHandle>>);

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
    let _ = app.emit("oppo-live", LiveFrame { seq, kind: kind.to_string(), raw });
}

fn run_live_loop(app: tauri::AppHandle, mut stream: TcpStream, prior: Option<u8>, stop: Arc<AtomicBool>) {
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
) -> Result<(), String> {
    let port = port.unwrap_or(23);
    let mut guard = monitor.0.lock().map_err(|e| e.to_string())?;
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
    *guard = Some(LiveHandle { stop, join: Some(join) });
    Ok(())
}

/// Stop the live monitor (signals the thread, waits for it to restore verbose mode + close).
#[tauri::command]
fn stop_oppo_live_monitor(monitor: tauri::State<'_, LiveMonitor>) -> Result<(), String> {
    let handle = monitor.0.lock().map_err(|e| e.to_string())?.take();
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
    stream.set_read_timeout(Some(timeout)).map_err(|e| e.to_string())?;
    stream.set_write_timeout(Some(timeout)).map_err(|e| e.to_string())?;
    stream.write_all(request.as_bytes()).map_err(|e| e.to_string())?;
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

#[cfg(test)]
mod tests {
    use super::{
        classify_frame, extract_zip_into, kodi_get_item_body, parse_addon_version,
        parse_kodi_active_player_id, parse_kodi_log_file, parse_kodi_player_file,
        parse_verbose_mode, roku_keypress_request, to_hex,
    };

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
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(LiveMonitor::default())
        .invoke_handler(tauri::generate_handler![
            load_wizard_state,
            save_wizard_state,
            generate_files,
            reveal_path,
            read_userdata_file,
            read_ssh_file,
            deploy_to_userdata,
            smb_test_write,
            tcp_probe,
            tv_port_probe,
            oppo_query,
            ssh_test,
            deploy_ssh,
            kodi_now_playing,
            bundled_addon_info,
            install_addon,
            tv_switch_roku,
            start_oppo_live_monitor,
            stop_oppo_live_monitor
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
