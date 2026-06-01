use serde_json::Value;
use std::collections::BTreeMap;
use std::fs;
use std::io::{Read, Write};
use std::net::{TcpStream, ToSocketAddrs};
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

/// Send an OPPO IP-control query (default #QPW on port 23) and return the raw reply.
/// Mirrors resources/lib/oppo/oppo_control.py (CR-terminated; reply form "@CODE OK VALUE").
#[tauri::command]
fn oppo_query(
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

#[cfg(test)]
mod tests {
    use super::{classify_frame, parse_verbose_mode};

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
            start_oppo_live_monitor,
            stop_oppo_live_monitor
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
