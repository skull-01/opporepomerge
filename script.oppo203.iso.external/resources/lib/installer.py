import os
import xml.sax.saxutils as xml_escape

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

try:
    from .diagnostic_logging import format_log_message
except ImportError:  # pragma: no cover - top-level Kodi import compatibility
    from diagnostic_logging import format_log_message

try:
    from .disc_classification import (
        XML_4K_TAG_FILENAME_PATTERN,
        XML_DISC_FILETYPES,  # noqa: F401  # re-exported; asserted by tests
        XML_LOOSE_VIDEO_FILETYPES,  # noqa: F401  # re-exported; asserted by tests
    )
except ImportError:  # pragma: no cover - top-level Kodi import compatibility
    from disc_classification import (  # type: ignore
        XML_4K_TAG_FILENAME_PATTERN,
        XML_DISC_FILETYPES,  # noqa: F401  # re-exported; asserted by tests
        XML_LOOSE_VIDEO_FILETYPES,  # noqa: F401  # re-exported; asserted by tests
    )


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")

# v0.8.0: TCL ADB preset definitions
# Each preset is a dict with keys: label, model_hint, oppo_input, kodi_input
TCL_ADB_PRESETS = [
    {
        "label": "TCL C805/C855 HW15/HW16 (most C-series, HW15=HDMI1, HW16=HDMI2)",
        "model_hint": "C805 / C855 HW15/HW16",
        "oppo_input": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW15 -n com.tcl.tv/.TVActivity -f 0x10000000",
        "kodi_input": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW16 -n com.tcl.tv/.TVActivity -f 0x10000000",
    },
    {
        "label": "TCL C805/C855 HW17 (third HDMI input on HW17)",
        "model_hint": "C805 / C855 HW17",
        "oppo_input": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW15 -n com.tcl.tv/.TVActivity -f 0x10000000",
        "kodi_input": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW17 -n com.tcl.tv/.TVActivity -f 0x10000000",
    },
    {
        "label": "TCL C635 HW1413744128/HW1413744384 (numeric IDs, HDMI1/HDMI2)",
        "model_hint": "C635 HW1413744128/HW1413744384",
        "oppo_input": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW1413744128 -n com.tcl.tv/.TVActivity -f 0x10000000",
        "kodi_input": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW1413744384 -n com.tcl.tv/.TVActivity -f 0x10000000",
    },
    {
        "label": "TCL 65S434 droidlogic HDMI1/HDMI2",
        "model_hint": "65S434 droidlogic",
        "oppo_input": "am start -a android.intent.action.VIEW -d content://android.media.tv/passthrough/com.droidlogic.tvinput%2F.services.HdmiInputService%2FHDMI1 -n com.droidlogic.tvinput/.MainActivityT -f 0x10000000",
        "kodi_input": "am start -a android.intent.action.VIEW -d content://android.media.tv/passthrough/com.droidlogic.tvinput%2F.services.HdmiInputService%2FHDMI2 -n com.droidlogic.tvinput/.MainActivityT -f 0x10000000",
    },
]


def tpath(path):
    return xbmcvfs.translatePath(path)


def get_setting(key, default=""):
    value = ADDON.getSetting(key)
    return value if value != "" else default


def bool_setting(key, default=False):
    value = ADDON.getSetting(key)
    if value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _paths():
    addon_path = tpath(ADDON.getAddonInfo("path"))
    script_path = os.path.join(addon_path, "resources", "lib", "external_player.py")
    addon_data = tpath(f"special://profile/addon_data/{ADDON_ID}")
    xbmcvfs.mkdirs(addon_data)
    snippet_path = os.path.join(addon_data, "playercorefactory-oppo203iso-snippet.xml")
    return script_path, addon_data, snippet_path


def build_external_player_xml():
    script_path, addon_data, _ = _paths()

    python_path = get_setting("python_path", "/usr/bin/python3")

    escaped_python = xml_escape.escape(python_path)
    escaped_script = xml_escape.escape(script_path)
    escaped_data = xml_escape.escape(addon_data)

    return f"""<!-- Add this inside the existing <players> element. -->
<player name="Oppo203ISO" type="ExternalPlayer" audio="false" video="true">
      <filename>{escaped_python}</filename>
      <args>"{escaped_script}" --addon-data "{escaped_data}" --file "{{1}}"</args>
      <hidexbmc>false</hidexbmc>
      <hideconsole>true</hideconsole>
      <warpcursor>none</warpcursor>
      <playcountminimumtime>1</playcountminimumtime>
</player>
"""


# v2.5.3 Build 2 / v2.9.1 Build 2: Option 4 conservative tag-aware XML routing.
# XML mode is filename/path driven.  It cannot inspect video metadata, NFO
# files, stream resolution, or the contents of an ISO image, so every XML rule
# must require an explicit 4K/UHD/2160p naming tag.  The constants are imported
# from disc_classification.py so installer and merge-helper rules stay aligned.


def build_xml_naming_warning_text():
    return (
        "4K external-player XML mode requires naming discipline.\n\n"
        "Only disc-style sources whose filename or visible folder path contains "
        "4K, UHD, or 2160p will be routed to the OPPO/Chinoppo external player. "
        "Loose video files such as MKV, MP4, M2TS, TS, and VOB stay with Kodi.\n\n"
        "Recommended examples:\n"
        "Movie Title (Year) 4K UHD.iso\n"
        "Movie Title (Year) 2160p.iso\n"
        "Movie Title (Year) 4K UHD/BDMV/index.bdmv\n"
        "Movie Title (Year) UHD/BDMV/PLAYLIST/00800.mpls\n\n"
        "XML mode is naming-convention driven; it cannot inspect metadata, "
        "NFO files, stream resolution, or ISO internals."
    )


def _option4_rule(filetype):
    return (
        f'<rule filetypes="{filetype}" '
        f'filename="{XML_4K_TAG_FILENAME_PATTERN}" '
        'player="Oppo203ISO"/>'
    )


def build_rule_xml():
    rules = [
        "<!-- Add this inside the existing <rules> element. -->",
        "<!-- v2.5.3 Build 2 Option 4: conservative 4K/UHD/2160p tag-aware routing. -->",
        "<!-- XML mode is filename/path driven; it cannot inspect metadata, NFO files, stream resolution, or ISO internals. -->",
        "<!-- Only tagged disc-style sources are routed to the OPPO/Chinoppo external player. -->",
        _option4_rule("iso"),
    ]
    if bool_setting("include_disc_folder_rules", True):
        rules.extend(
            [
                "",
                "<!-- Tagged BDMV and playlist entry files, e.g. Movie 4K UHD/BDMV/index.bdmv or .../PLAYLIST/00800.mpls. -->",
                _option4_rule("bdmv"),
                _option4_rule("mpls"),
            ]
        )
    return "\n".join(rules).rstrip() + "\n"


def build_keymap_snippet_xml():
    return """<!--
Oppo UDP-203 Kodi remote bridge snippet.

Manual merge instructions:
1. Copy the <FullscreenVideo> block into a keymap file under Kodi userdata/keymaps.
2. If you already have a FullscreenVideo keyboard/remote section, merge only the individual button mappings.
3. Restart Kodi or run the Kodi built-in ReloadKeymaps action.

Important:
- These mappings only work if the remote events still reach Kodi while the TV is showing the Oppo input.
- Kodi app remotes, RF/USB receivers, keyboards, and many Bluetooth remotes should work.
- TV CEC remotes may follow the active HDMI source to the Oppo instead of the Kodi box.

v0.8.0 command corrections: popup_menu -> #MNU, skip_next -> #NXT
v0.9.0 additions:
  cycle_audio     -> HTTP audio track cycling (falls back to #AUD)
  cycle_subtitle  -> HTTP subtitle cycling (falls back to #SUB)
  seek_beginning  -> HTTP setplaytime 0:0:0
  option          -> #OPT  (mapped to keyboard key 'o')
  info (OSD)      -> #OSD  (mapped to keyboard key 'i'; replaces #INF)
  page_up/down    -> #PGU/#PGD (mapped to keyboard pageup/pagedown)
  red/green/blue/yellow -> #RED/#GRN/#BLU/#YLW (no standard Kodi remote key; keyboard only)
-->
<keymap>
  <FullscreenVideo>
    <keyboard>
      <up>RunScript(script.oppo203.iso.external,oppo_key,up)</up>
      <down>RunScript(script.oppo203.iso.external,oppo_key,down)</down>
      <left>RunScript(script.oppo203.iso.external,oppo_key,left)</left>
      <right>RunScript(script.oppo203.iso.external,oppo_key,right)</right>
      <enter>RunScript(script.oppo203.iso.external,oppo_key,select)</enter>
      <return>RunScript(script.oppo203.iso.external,oppo_key,back)</return>
      <m>RunScript(script.oppo203.iso.external,oppo_key,popup_menu)</m>
      <t>RunScript(script.oppo203.iso.external,oppo_key,top_menu)</t>
      <space>RunScript(script.oppo203.iso.external,oppo_key,play)</space>
      <p>RunScript(script.oppo203.iso.external,oppo_key,play)</p>
      <f>RunScript(script.oppo203.iso.external,oppo_key,forward)</f>
      <r>RunScript(script.oppo203.iso.external,oppo_key,reverse)</r>
      <x>RunScript(script.oppo203.iso.external,oppo_key,stop)</x>
      <a>RunScript(script.oppo203.iso.external,oppo_key,cycle_audio)</a>
      <l>RunScript(script.oppo203.iso.external,oppo_key,cycle_subtitle)</l>
      <volume_up>RunScript(script.oppo203.iso.external,oppo_key,volume_up)</volume_up>
      <volume_down>RunScript(script.oppo203.iso.external,oppo_key,volume_down)</volume_down>
      <volume_mute>RunScript(script.oppo203.iso.external,oppo_key,mute)</volume_mute>
      <!-- v0.9.0 additions -->
      <o>RunScript(script.oppo203.iso.external,oppo_key,option)</o>
      <i>RunScript(script.oppo203.iso.external,oppo_key,info)</i>
      <pageup>RunScript(script.oppo203.iso.external,oppo_key,page_up)</pageup>
      <pagedown>RunScript(script.oppo203.iso.external,oppo_key,page_down)</pagedown>
      <F1>RunScript(script.oppo203.iso.external,oppo_key,red)</F1>
      <F2>RunScript(script.oppo203.iso.external,oppo_key,green)</F2>
      <F3>RunScript(script.oppo203.iso.external,oppo_key,blue)</F3>
      <F4>RunScript(script.oppo203.iso.external,oppo_key,yellow)</F4>
      <home>RunScript(script.oppo203.iso.external,oppo_key,seek_beginning)</home>
    </keyboard>
    <remote>
      <up>RunScript(script.oppo203.iso.external,oppo_key,up)</up>
      <down>RunScript(script.oppo203.iso.external,oppo_key,down)</down>
      <left>RunScript(script.oppo203.iso.external,oppo_key,left)</left>
      <right>RunScript(script.oppo203.iso.external,oppo_key,right)</right>
      <select>RunScript(script.oppo203.iso.external,oppo_key,select)</select>
      <back>RunScript(script.oppo203.iso.external,oppo_key,back)</back>
      <menu>RunScript(script.oppo203.iso.external,oppo_key,popup_menu)</menu>
      <title>RunScript(script.oppo203.iso.external,oppo_key,top_menu)</title>
      <play>RunScript(script.oppo203.iso.external,oppo_key,play)</play>
      <pause>RunScript(script.oppo203.iso.external,oppo_key,pause)</pause>
      <stop>RunScript(script.oppo203.iso.external,oppo_key,stop)</stop>
      <forward>RunScript(script.oppo203.iso.external,oppo_key,forward)</forward>
      <reverse>RunScript(script.oppo203.iso.external,oppo_key,reverse)</reverse>
      <skipplus>RunScript(script.oppo203.iso.external,oppo_key,skip_next)</skipplus>
      <skipminus>RunScript(script.oppo203.iso.external,oppo_key,skip_previous)</skipminus>
      <audio>RunScript(script.oppo203.iso.external,oppo_key,cycle_audio)</audio>
      <subtitle>RunScript(script.oppo203.iso.external,oppo_key,cycle_subtitle)</subtitle>
      <volumeplus>RunScript(script.oppo203.iso.external,oppo_key,volume_up)</volumeplus>
      <volumeminus>RunScript(script.oppo203.iso.external,oppo_key,volume_down)</volumeminus>
      <mute>RunScript(script.oppo203.iso.external,oppo_key,mute)</mute>
      <!-- v0.9.0 additions: colour buttons use standard Kodi Leia/Matrix remote names -->
      <red>RunScript(script.oppo203.iso.external,oppo_key,red)</red>
      <green>RunScript(script.oppo203.iso.external,oppo_key,green)</green>
      <blue>RunScript(script.oppo203.iso.external,oppo_key,blue)</blue>
      <yellow>RunScript(script.oppo203.iso.external,oppo_key,yellow)</yellow>
      <info>RunScript(script.oppo203.iso.external,oppo_key,info)</info>
      <pageplus>RunScript(script.oppo203.iso.external,oppo_key,page_up)</pageplus>
      <pageminus>RunScript(script.oppo203.iso.external,oppo_key,page_down)</pageminus>
    </remote>
  </FullscreenVideo>
</keymap>
"""


def build_snippet_xml():
    arch = get_setting("playback_architecture", "external_player")
    if arch == "service_interception":
        header = """<!--
Oppo UDP-203 ISO External Player snippet.

NOTE: playback_architecture is set to service_interception.
In this mode, the service.py monitor intercepts disc playback starts automatically.
The playercorefactory snippet is NOT required for routing -- only the keymap snippet
may be needed for remote-bridge key forwarding.

If you want to switch back to external_player mode, change the playback_architecture
setting and regenerate this snippet.
-->
"""
        return header + build_snippet_xml_body()

    return f"""<!--
Oppo UDP-203 ISO External Player snippet.

Manual merge instructions:
1. Open Kodi's userdata/playercorefactory.xml.
2. If the file does not exist, create it with the full example below.
3. If it exists, copy the <player> block into <players> and the tag-aware <rule> lines into <rules>.
4. Restart Kodi after saving.
-->

<!-- Full standalone example -->
<playercorefactory>
  <players>
{_indent(build_external_player_xml(), "    ")}
  </players>
  <rules action="prepend">
{_indent(build_rule_xml(), "    ")}
  </rules>
</playercorefactory>
"""


def build_snippet_xml_body():
    return f"""<!-- Full standalone example -->
<playercorefactory>
  <players>
{_indent(build_external_player_xml(), "    ")}
  </players>
  <rules action="prepend">
{_indent(build_rule_xml(), "    ")}
  </rules>
</playercorefactory>
"""


def _indent(text, prefix):
    return "\n".join(prefix + line if line else line for line in text.rstrip().splitlines())


def write_snippet():
    _, _, snippet_path = _paths()
    xml = build_snippet_xml()
    handle = xbmcvfs.File(snippet_path, "w")
    try:
        handle.write(xml)
    finally:
        handle.close()

    xbmcgui.Dialog().ok(
        "4K XML naming requirement",
        build_xml_naming_warning_text(),
    )
    xbmcgui.Dialog().ok(
        "Oppo UDP-203 ISO External Player",
        "Generated a playercorefactory snippet. The next screen will show the XML to merge manually.",
    )
    xbmcgui.Dialog().textviewer("playercorefactory snippet", xml)


def write_keymap_snippet():
    _, addon_data, _ = _paths()
    snippet_path = os.path.join(addon_data, "oppo203iso-keymap-snippet.xml")
    xml = build_keymap_snippet_xml()
    handle = xbmcvfs.File(snippet_path, "w")
    try:
        handle.write(xml)
    finally:
        handle.close()

    xbmcgui.Dialog().ok(
        "Oppo UDP-203 ISO External Player",
        "Generated a Kodi remote-bridge keymap snippet. The next screen will show the XML to merge manually.",
    )
    xbmcgui.Dialog().textviewer("Kodi remote bridge keymap snippet", xml)


def show_generated_xml():
    xbmcgui.Dialog().textviewer(
        "Generated playercorefactory snippet",
        build_snippet_xml(),
    )


def show_generated_keymap_xml():
    xbmcgui.Dialog().textviewer(
        "Kodi remote bridge keymap snippet",
        build_keymap_snippet_xml(),
    )


def show_architecture_choice_dialog():
    """Show first-run architecture choice dialog if not already made."""
    choice = xbmcgui.Dialog().select(
        "Oppo UDP-203: Choose Playback Architecture",
        [
            "External Player (recommended): Kodi routes disc files via playercorefactory.xml. "
            "Most predictable, no internal playback race, official Kodi path. Requires playercorefactory snippet merge.",
            "Service Interception: Service monitors Kodi playback, stops it, then activates Oppo. "
            "No playercorefactory snippet needed, but more timing-sensitive. May briefly start Kodi playback.",
        ],
    )
    if choice == 0:
        ADDON.setSetting("playback_architecture", "external_player")
        ADDON.setSetting("architecture_choice_made", "true")
        xbmcgui.Dialog().ok(
            "Oppo UDP-203",
            "External Player mode selected. Run 'Generate playercorefactory snippet' and merge it into Kodi.",
        )
    elif choice == 1:
        ADDON.setSetting("playback_architecture", "service_interception")
        ADDON.setSetting("architecture_choice_made", "true")
        xbmcgui.Dialog().ok(
            "Oppo UDP-203",
            "Service Interception mode selected. The service will monitor Kodi playback automatically. "
            "Only the keymap snippet may be needed for remote-bridge key forwarding.",
        )
    return choice


def run_oppo_discovery():
    """Attempt Oppo UDP multicast discovery and show results.

    v0.9.0: If exactly one device is found, offer a yes/no prompt to apply
    the discovered IP and port to settings automatically.
    """
    import os
    import sys

    # Import discover_oppo without Kodi context (runs in Kodi addon env)
    addon_path = tpath(ADDON.getAddonInfo("path"))
    lib_path = os.path.join(addon_path, "resources", "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    try:
        from oppo_control import discover_oppo

        xbmcgui.Dialog().ok(
            "Oppo UDP-203 Discovery",
            "Listening for Oppo devices on multicast 239.255.255.251:7624 for 5 seconds...",
        )
        results = discover_oppo(timeout=5.0)
        if not results:
            xbmcgui.Dialog().ok(
                "Oppo UDP-203 Discovery",
                "No Oppo devices found on the local network via multicast.\n"
                "Make sure the Oppo is powered on and IP control is enabled.",
            )
            return

        lines = [f"IP: {r['ip']}  Port: {r['port']}  Name: {r['name']}" for r in results]

        if len(results) == 1:
            r = results[0]
            # v0.9.0: offer to apply the single found device to settings
            apply = xbmcgui.Dialog().yesno(
                "Oppo UDP-203 Discovery",
                f"Found one Oppo device:\n{lines[0]}\n\nApply this IP and port to add-on settings?",
                nolabel="No, show only",
                yeslabel="Yes, apply",
            )
            if apply:
                ADDON.setSetting("oppo_ip", r["ip"])
                # Discovery port is the UDP source port, not the TCP control port.
                # Only apply port if it looks like the Oppo TCP control port (23);
                # otherwise keep the existing TCP port setting.
                if str(r["port"]) == "23":
                    ADDON.setSetting("oppo_port", str(r["port"]))
                xbmcgui.Dialog().ok(
                    "Oppo UDP-203 Discovery",
                    f"Oppo IP set to {r['ip']}.\n"
                    "Port left unchanged (discovery UDP port differs from TCP control port).\n"
                    "Verify the IP address in add-on settings.",
                )
            else:
                xbmcgui.Dialog().textviewer("Oppo Discovery Results", "\n".join(lines))
        else:
            # Multiple devices: show all and do not auto-apply.
            xbmcgui.Dialog().textviewer(
                "Oppo Discovery Results (multiple)",
                "Multiple Oppo devices found. Select the correct IP manually in settings.\n\n"
                + "\n".join(lines),
            )
    except Exception as exc:
        xbmcgui.Dialog().ok("Oppo UDP-203 Discovery", f"Discovery failed: {exc}")


def show_tcl_presets():
    """Show TCL ADB preset options and let user copy commands."""
    labels = [p["label"] for p in TCL_ADB_PRESETS] + ["Cancel"]
    choice = xbmcgui.Dialog().select("TCL ADB Presets", labels)
    if choice < 0 or choice >= len(TCL_ADB_PRESETS):
        return
    preset = TCL_ADB_PRESETS[choice]
    info = (
        f"Model hint: {preset['model_hint']}\n\n"
        f"Oppo input command:\n{preset['oppo_input']}\n\n"
        f"Kodi input command:\n{preset['kodi_input']}\n\n"
        "Copy these into Settings > TV > ADB shell commands."
    )
    # Show and offer to apply
    apply_choice = xbmcgui.Dialog().yesno(
        "TCL ADB Preset",
        info,
        nolabel="Preview only",
        yeslabel="Apply to settings",
    )
    if apply_choice:
        ADDON.setSetting("oppo_input_adb_shell", preset["oppo_input"])
        ADDON.setSetting("kodi_input_adb_shell", preset["kodi_input"])
        xbmcgui.Dialog().ok(
            "TCL ADB Preset Applied",
            f"Settings updated for preset: {preset['model_hint']}\n"
            "Verify these commands work by testing with adb logcat before relying on them.",
        )


def run_experimental_filelist_diagnostic():
    """Experimental: preview /getfilelist response with structured parser (v0.9.2).

    v0.9.2: The diagnostic now calls parse_undocumented_file_list(raw,
    base_path=requested_path) so that inferred path fields are rooted at the
    requested directory.  Structured parser output (entry_type, is_dir,
    is_file, size_bytes, extension, disc_type) is shown alongside raw bytes
    for debugging.  The raw response is preserved in a second textviewer
    screen so no debugging visibility is lost.

    WARNING: /getfilelist is an undocumented Oppo endpoint.  The response format
    is binary and firmware-dependent.  This diagnostic is disabled by default and
    must be enabled via Settings > Experimental > Enable file-list diagnostic.
    Do NOT rely on this in production.
    """
    enabled = ADDON.getSetting("oppo_experimental_filelist_enabled")
    if enabled.strip().lower() not in ("1", "true", "yes", "on"):
        xbmcgui.Dialog().ok(
            "Experimental File List",
            "This diagnostic is disabled by default.\n"
            "Enable 'Experimental > Enable file-list diagnostic' in settings first.\n\n"
            "WARNING: This uses an undocumented Oppo endpoint that may behave "
            "unexpectedly on your firmware.",
        )
        return

    import os
    import sys

    addon_path = tpath(ADDON.getAddonInfo("path"))
    lib_path = os.path.join(addon_path, "resources", "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

    try:
        from oppo_control import get_file_list_raw, parse_undocumented_file_list
        from settings_reader import read_settings

        addon_data = tpath(f"special://profile/addon_data/{ADDON_ID}")
        settings = read_settings(addon_data)

        requested_path = "/"
        raw = get_file_list_raw(settings, path=requested_path)

        # v0.9.2: pass base_path so the parser can construct full paths for
        # entries that carry only a bare name in the response.
        entries = parse_undocumented_file_list(raw, base_path=requested_path)

        raw_text = str(raw) if not isinstance(raw, str) else raw

        # --- Structured parser output ---
        structured = (
            f"Path requested: {requested_path}\n"
            f"Raw bytes: {len(raw_text)}\n"
            f"Entries parsed: {len(entries)}\n"
        )
        if entries:
            lines = []
            for i, e in enumerate(entries[:50]):
                # Compact one-line summary per entry
                tag = "[D]" if e["is_dir"] else ("[F]" if e["is_file"] else "[?]")
                size_str = f"  {e['size_bytes']} B" if e["size_bytes"] is not None else ""
                disc_str = f"  {e['disc_type']}" if e["disc_type"] else ""
                ext_str = f"  .{e['extension']}" if e["extension"] else ""
                path_str = (
                    f"\n    path: {e['path']}" if e["path"] and e["path"] != e["name"] else ""
                )
                lines.append(f"{i + 1}. {tag} {e['name']}{ext_str}{size_str}{disc_str}{path_str}")
            structured += "\n" + "\n".join(lines)
            if len(entries) > 50:
                structured += f"\n... and {len(entries) - 50} more entries."
        else:
            structured += "\nNo entries parsed from response."

        xbmcgui.Dialog().textviewer(
            "File List Diagnostic: Parsed Entries (v0.9.2)",
            structured,
        )

        # --- Raw response view (always shown after parsed view) ---
        raw_display = (
            f"Path requested: {requested_path}\n"
            f"Raw bytes: {len(raw_text)}\n\n"
            f"Raw response (first 2000 chars):\n{raw_text[:2000]}"
        )
        xbmcgui.Dialog().textviewer(
            "File List Diagnostic: Raw Response",
            raw_display,
        )

    except Exception as exc:
        xbmcgui.Dialog().ok("Experimental File List", f"Failed: {exc}")


def export_avr_diagnostic_report():
    """Export a sanitized Build 16 AVR diagnostic report."""
    try:
        try:
            from .avr_diagnostics import export_avr_diagnostic_report as _export
            from .settings_reader import DEFAULTS
        except Exception:  # pragma: no cover - top-level Kodi import compatibility
            from avr_diagnostics import export_avr_diagnostic_report as _export  # type: ignore
            from settings_reader import DEFAULTS  # type: ignore
        _, addon_data, _ = _paths()
        settings = dict(DEFAULTS)
        for key in list(settings):
            try:
                settings[key] = ADDON.getSetting(key) or settings[key]
            except Exception:
                pass
        path = _export(settings, addon_data)
        xbmcgui.Dialog().ok("AVR Diagnostics", "AVR diagnostic report exported:\n" + path)
        return path
    except Exception as exc:
        xbmcgui.Dialog().ok("AVR Diagnostics", "Export failed: " + str(exc))
        return None


def export_hardware_validation_readiness():
    """Export a non-invasive Build 5 hardware-validation readiness report."""
    try:
        try:
            from .hardware_validation_readiness import (
                build_readiness_report,
                export_readiness_report,
            )
        except Exception:  # pragma: no cover - top-level Kodi import compatibility
            from hardware_validation_readiness import (
                build_readiness_report,
                export_readiness_report,
            )
        _, addon_data, _ = _paths()
        report = build_readiness_report(
            addon_data_dir=addon_data, root_dir=ADDON.getAddonInfo("path")
        )
        path = export_readiness_report(addon_data, report)
        xbmcgui.Dialog().ok("Hardware Validation Readiness", "Readiness report exported:\n" + path)
        return path
    except Exception as exc:
        xbmcgui.Dialog().ok("Hardware Validation Readiness", "Export failed: " + str(exc))
        return None


def main():
    if ADDON.getSetting("wizard_completed") not in ("true", "1", "yes"):
        try:
            from wizard import run_wizard

            run_wizard()
        except Exception as exc:
            xbmc.log(format_log_message("setup", "Wizard failed: " + str(exc)), xbmc.LOGWARNING)
            if ADDON.getSetting("architecture_choice_made") not in ("true", "1", "yes"):
                show_architecture_choice_dialog()
    else:
        if ADDON.getSetting("architecture_choice_made") not in ("true", "1", "yes"):
            show_architecture_choice_dialog()

    actions = [
        "Generate playercorefactory snippet",
        "Generate Kodi remote bridge keymap snippet",
        "Open add-on settings",
        "Preview generated snippet",
        "Preview remote bridge keymap snippet",
        "Architecture setup (first-run dialog)",
        "Discover Oppo on network (UDP multicast)",
        "TCL ADB preset helper",
        "Experimental: file-list diagnostic (opt-in)",
        "Run first-run wizard (Basic or Full)",
        "Reset first-run wizard",
        "Generate Chinoppo AutoScript (autoexec.sh)",
        "Export hardware-validation readiness report",
        "Export AVR diagnostic report",
        "Cancel",
    ]
    choice = xbmcgui.Dialog().select("Oppo UDP-203 ISO External Player", actions)
    if choice == 0:
        write_snippet()
    elif choice == 1:
        write_keymap_snippet()
    elif choice == 2:
        ADDON.openSettings()
    elif choice == 3:
        show_generated_xml()
    elif choice == 4:
        show_generated_keymap_xml()
    elif choice == 5:
        show_architecture_choice_dialog()
    elif choice == 6:
        run_oppo_discovery()
    elif choice == 7:
        show_tcl_presets()
    elif choice == 8:
        run_experimental_filelist_diagnostic()
    elif choice == 9:
        try:
            from wizard import run_wizard

            run_wizard()
        except Exception as exc:
            xbmcgui.Dialog().ok("Wizard failed", str(exc))
    elif choice == 10:
        try:
            from wizard import reset_wizard

            reset_wizard()
        except Exception as exc:
            xbmcgui.Dialog().ok("Reset failed", str(exc))
    elif choice == 11:
        try:
            from autoscript_helper import run_autoscript_wizard

            run_autoscript_wizard(ADDON)
        except Exception as exc:
            xbmcgui.Dialog().ok("AutoScript failed", str(exc))
    elif choice == 12:
        export_hardware_validation_readiness()
    elif choice == 13:
        export_avr_diagnostic_report()
