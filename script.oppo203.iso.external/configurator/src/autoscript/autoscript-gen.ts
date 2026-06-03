// Configurator mirror of the add-on's OPPO AutoScript generator.
//
// EXACT byte-for-byte port of resources/lib/oppo/autoscript_helper.py `generate()` — the add-on is
// the single source of truth. Pinned identical by autoscript.test.ts against fixtures captured from
// the Python source (and re-asserted add-on-side by tests/test_autoscript_consistency.py). If the
// add-on generator changes, regenerate the fixtures and update this mirror in the same change.

export type AutoScriptMountType = "none" | "nfs" | "cifs";

export type AutoScriptOptions = {
  enableTelnet?: boolean;
  telnetPort?: number;
  passwordlessRoot?: boolean;
  mountType?: AutoScriptMountType;
  mountRemote?: string;
  mountLocal?: string;
  mountOptions?: string;
  cifsUser?: string;
  cifsPass?: string;
  heartbeatPath?: string;
  enableAdb?: boolean;
  adbPort?: number;
};

/** Mirror of the add-on's `_safe_int`: a strict int parse falling back to `dflt`. */
function safeInt(v: unknown, dflt: number): number {
  const n = typeof v === "number" ? v : Number(String(v).trim());
  return Number.isFinite(n) ? Math.trunc(n) : dflt;
}

/** Generate the OPPO AutoScript `autoexec.sh`. Mirrors `autoscript_helper.generate(opts)`. */
export function generateAutoexec(opts: AutoScriptOptions = {}): string {
  const et = opts.enableTelnet ?? true;
  const tp = safeInt(opts.telnetPort ?? 2323, 2323);
  const pr = opts.passwordlessRoot ?? true;
  const mt = String(opts.mountType || "none").toLowerCase();
  const mr = opts.mountRemote ?? "";
  const ml = opts.mountLocal ?? "/tmp/share";
  const mo = opts.mountOptions ?? "";
  const cu = opts.cifsUser ?? "";
  const cp = opts.cifsPass ?? "";
  const hb = opts.heartbeatPath ?? "/tmp/usb/sda1/oppo_autoexec_ran";
  const ea = opts.enableAdb ?? false;
  const ap = safeInt(opts.adbPort ?? 5555, 5555);

  const L: string[] = [
    "#!/bin/sh",
    "# autoexec.sh - Chinoppo AutoScript v1.0.3",
    "set +e",
    "LOG=/tmp/oppo_autoexec.log",
    'echo "[autoexec] starting" > "$LOG"',
    "",
  ];
  if (hb) {
    L.push('echo "started" > "' + hb + '" 2>>"$LOG" || true', "");
  }
  if (pr) {
    L.push(
      "sed -i 's|^root:[^:]*|root:|' /etc/shadow 2>>\"$LOG\" || true",
      "sed -i 's|^root:[^:]*|root:|' /etc/passwd 2>>\"$LOG\" || true",
      ""
    );
  }
  if (et) {
    L.push(
      "if ! pidof telnetd >/dev/null 2>&1; then",
      "  telnetd -p " + tp + ' -l /bin/sh >>"$LOG" 2>&1 &',
      "fi",
      ""
    );
  }
  if ((mt === "nfs" || mt === "cifs") && mr) {
    L.push('mkdir -p "' + ml + '"');
    if (mt === "nfs") {
      const opt = mo || "nolock,soft,intr,vers=3";
      L.push("mount -t nfs -o " + opt + ' "' + mr + '" "' + ml + '" >>"$LOG" 2>&1 || true');
    } else {
      const opt = mo || "iocharset=utf8,vers=2.0";
      let cred = "";
      if (cu) {
        cred = ",username=" + cu;
        if (cp) cred += ",password=" + cp;
      }
      L.push("mount -t cifs -o " + opt + cred + ' "' + mr + '" "' + ml + '" >>"$LOG" 2>&1 || true');
    }
    L.push("");
  }
  if (ea) {
    L.push(
      "setprop service.adb.tcp.port " + ap + ' 2>>"$LOG" || true',
      'stop adbd 2>>"$LOG" || true',
      'start adbd 2>>"$LOG" || true',
      ""
    );
  }
  if (hb) {
    L.push('echo "completed" >> "' + hb + '" 2>>"$LOG" || true', "");
  }
  L.push('echo "[autoexec] done" >> "$LOG"', "exit 0", "");
  return L.join("\n");
}
