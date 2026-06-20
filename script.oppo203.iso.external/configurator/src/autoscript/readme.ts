import type { AutoScriptOptions } from "./autoscript-gen";

/**
 * The HOW-TO-INSTALL.txt that ships next to the generated autoexec.sh in the Desktop export folder.
 * Tells the user how to get the script onto the player via a USB drive: format requirements, where
 * to copy it, how to boot it, and how to verify it ran — plus the safety caveats. Reflects the
 * chosen options (telnet port, NAS mount, heartbeat path) so the verify steps match what was built.
 */
export function autoscriptReadme(opts: AutoScriptOptions): string {
  const telnetPort = opts.telnetPort ?? 2323;
  const heartbeat = opts.heartbeatPath ?? "/tmp/usb/sda1/oppo_autoexec_ran";
  const mount = opts.mountType && opts.mountType !== "none" ? opts.mountType.toUpperCase() : null;

  const lines: (string | null)[] = [
    "OPPO AutoScript — how to install",
    "=================================",
    "",
    "This folder contains autoexec.sh, an AutoScript your jailbroken OPPO (UDP-203/205 on",
    "firmware 20X-56 or newer) or clone player runs automatically on boot from a USB drive.",
    "",
    "WHAT IT DOES",
    `  - Starts a telnet root shell on port ${telnetPort} (NOT port 23, which would break the`,
    "    OPPO's #SVM verbose-push control the add-on relies on).",
    opts.passwordlessRoot ?? true ? "  - Clears the root password (passwordless root)." : null,
    mount ? `  - Mounts your NAS share over ${mount}.` : null,
    opts.enableAdb ? `  - Enables ADB over TCP on port ${opts.adbPort ?? 5555}.` : null,
    `  - Writes a heartbeat marker at ${heartbeat} so you can confirm it ran.`,
    "",
    "USB DRIVE REQUIREMENTS",
    "  1. Use a small USB flash drive (1-32 GB is ideal).",
    "  2. Format it FAT32 (exFAT also works on most players; FAT32 is the safest).",
    "       Windows: right-click the drive in File Explorer -> Format -> File system: FAT32.",
    "  3. Use a single primary partition (the default).",
    "",
    "COPY THE SCRIPT",
    "  1. Copy autoexec.sh to the ROOT of the USB drive (not inside any folder).",
    "  2. Keep the filename exactly: autoexec.sh (all lowercase).",
    "  3. Do NOT open/edit it in Notepad (it would add Windows CR/LF line endings and break",
    "     the script). If you must edit, use an editor that keeps Unix (LF) line endings.",
    "  4. Safely eject the USB drive from Windows.",
    "",
    "RUN IT ON THE PLAYER",
    "  1. Power the player off.",
    "  2. Insert the USB drive into one of the player's USB ports.",
    "  3. Power the player on. The jailbroken firmware runs autoexec.sh during boot.",
    "",
    "VERIFY IT WORKED",
    `  - Put the USB back in your PC and check that the marker file appeared: ${heartbeat}`,
    "    (its folder is the USB drive once mounted on the player).",
    `  - Or, back in the configurator's Developer Options -> AutoScript -> Check availability,`,
    `    confirm telnet port ${telnetPort} is open on the player.`,
    "",
    "SAFETY",
    "  - Passwordless root + an open telnet shell means anyone on your LAN can fully control the",
    "    player. Only use this on a trusted home network, and remove the USB when you are done",
    "    testing if you do not want it to run on every boot.",
    mount && opts.cifsPass
      ? "  - Your NAS password is stored in PLAIN TEXT inside autoexec.sh on the USB drive. Treat the"
      : null,
    mount && opts.cifsPass ? "    drive as a secret and wipe it when finished." : null,
    "",
  ];
  return lines.filter((l): l is string => l !== null).join("\r\n");
}
