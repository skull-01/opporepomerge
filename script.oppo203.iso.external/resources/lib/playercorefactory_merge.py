"""playercorefactory snippet generator + safe merge (v1.1.2).

Generates hardware-aware <player>/<rules> snippets and merges them
into the user's existing playercorefactory.xml with:
  - well-formedness validation of any pre-existing file (refuses to
    merge into a broken file - the user fixes it manually first).
  - timestamped .bak side-by-side backup before any write.
  - idempotent merge: re-running with the same preset produces the
    same final document (no duplicate <player> or Option 4 <rule> entries).
  - transactional rollback: if final write/post-write validation fails after
    backup, the original file is restored from the backup when possible.
  - Option 4 routing: generated rules are conservative, tag-aware, and
    limited to ISO/BDMV/MPLS disc-style candidates only.

Public API
----------
- PRESETS: dict of preset_id -> {start_commands, label}
- snippet_for(preset_id, *, player_path, addon_id="script.oppo203.iso.external")
                                          -> str (XML fragment)
- generate(preset_id, **kwargs)           -> str (alias)
- is_well_formed(text_or_none)            -> bool
- backup_path(target_path, *, now=None)   -> str
- merge(target_path, snippet_xml, *, fs=None, now=None) -> dict
                                  ({"backup": path|None, "written": True,
                                    "validated": True, "added_players": int})

`fs` is an optional filesystem-injection object with .exists(path),
.read(path), .write(path, text), .copy(src, dst) - tests pass an
in-memory stub; production passes None to use real `os`/`shutil`.
"""

import os
import re
import shutil as _shutil
import time as _time
import xml.etree.ElementTree as ET

try:
    from .disc_classification import (
        XML_4K_TAG_FILENAME_PATTERN,
        XML_DISC_FILETYPES,
        XML_LOOSE_VIDEO_FILETYPES,
    )
except ImportError:  # pragma: no cover - top-level test import compatibility
    from disc_classification import (  # type: ignore
        XML_4K_TAG_FILENAME_PATTERN,
        XML_DISC_FILETYPES,
        XML_LOOSE_VIDEO_FILETYPES,
    )


# v2.5.3 Build 4 / v2.9.1 Build 2: keep this helper aligned with the
# installer Option 4 playercorefactory.xml model. XML mode is
# naming-convention driven and must not route loose/raw video files. The shared
# constants are imported from disc_classification.py.

def _option4_rule_xml(player_name, filetype):
    return (
        '    <rule name="' + player_name + '_rule_' + filetype + '" '
        'filetypes="' + filetype + '" '
        'filename="' + XML_4K_TAG_FILENAME_PATTERN + '" '
        'player="' + player_name + '"/>\n'
    )


# Hardware-aware command sequences. The OPPO203 stops on disc folders
# without #EJT, but Chinese clones ("Chinoppo") need an explicit eject
# first to avoid resuming a previous title.
PRESETS = {
    "oppo203": {
        "label": "OPPO 203/205",
        "start_commands": "#PLA",
        "stop_commands":  "#STP",
    },
    "oppo103": {
        "label": "OPPO 103/105",
        "start_commands": "#PLA",
        "stop_commands":  "#STP",
    },
    "chinoppo": {
        "label": "Chinoppo (UDP-203/205 clones)",
        "start_commands": "#EJT,#PLA",
        "stop_commands":  "#STP",
    },
    "reavon_x200": {
        "label": "Reavon UBR-X200",
        "start_commands": "#PON,#PLA",
        "stop_commands":  "#STP",
    },
    "zappiti_reference": {
        "label": "Zappiti Reference",
        "start_commands": "#PLA",
        "stop_commands":  "#STP",
    },
    "magnetar": {
        "label": "Magnetar UDP800",
        "start_commands": "#PLA",
        "stop_commands":  "#STP",
    },
}


def is_well_formed(text):
    """Return True iff `text` parses as XML.  None/empty -> True."""
    if text is None or not str(text).strip():
        return True
    try:
        ET.fromstring(text)
        return True
    except ET.ParseError:
        return False


def _ts(now=None):
    t = _time.localtime(now() if callable(now) else (now if now else _time.time()))
    return _time.strftime("%Y%m%d-%H%M%S", t)


def backup_path(target_path, *, now=None):
    return target_path + "." + _ts(now) + ".bak"


_PLAYER_NAME_TMPL = "OPPO_External_{preset}"


def snippet_for(preset_id, *, player_path,
                addon_id="script.oppo203.iso.external"):
    """Generate a self-contained <playercorefactory> XML fragment
    for the given preset.  The fragment contains exactly one <player>
    and conservative Option 4 matching <rule> entries.
    """
    if preset_id not in PRESETS:
        raise KeyError("unknown preset: " + str(preset_id))
    p = PRESETS[preset_id]
    name = _PLAYER_NAME_TMPL.format(preset=preset_id)
    cmds = p["start_commands"]
    return (
        '<playercorefactory>\n'
        '  <players>\n'
        '    <player name="' + name + '" type="ExternalPlayer" audio="false" video="true">\n'
        '      <filename>' + player_path + '</filename>\n'
        '      <args>"{0}" --preset=' + preset_id
        + ' --start="' + cmds + '" --addon=' + addon_id + '</args>\n'
        '      <hidexbmc>true</hidexbmc>\n'
        '      <hideconsole>true</hideconsole>\n'
        '      <forceontop>false</forceontop>\n'
        '    </player>\n'
        '  </players>\n'
        '  <rules action="prepend">\n'
        + ''.join(_option4_rule_xml(name, filetype) for filetype in XML_DISC_FILETYPES)
        + '  </rules>\n'
        '</playercorefactory>\n'
    )


# Backwards-friendly alias
def generate(preset_id, **kwargs):
    return snippet_for(preset_id, **kwargs)


# ---------------------------------------------------------------------
# Filesystem injection
# ---------------------------------------------------------------------

class _RealFS(object):
    def exists(self, p): return os.path.exists(p)
    def read(self, p):
        with open(p, "r", encoding="utf-8") as f: return f.read()
    def write(self, p, text):
        d = os.path.dirname(p)
        if d: os.makedirs(d, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f: f.write(text)
    def copy(self, src, dst):
        d = os.path.dirname(dst)
        if d: os.makedirs(d, exist_ok=True)
        _shutil.copy2(src, dst)


def _merge_xml(existing_text, snippet_text):
    """Merge two <playercorefactory> documents.  Idempotent: a
    <player name="X"> already present in the existing document is
    not duplicated; rules with the same name are likewise deduped.
    Returns (merged_text, added_players_count).
    """
    if not existing_text or not existing_text.strip():
        return snippet_text, _count_players(snippet_text)

    base = ET.fromstring(existing_text)
    new = ET.fromstring(snippet_text)
    if base.tag != "playercorefactory":
        # If the file isn't a playercorefactory document, refuse to merge.
        raise ValueError("existing root is <" + base.tag + ">, "
                         "expected <playercorefactory>")
    base_players = base.find("players")
    if base_players is None:
        base_players = ET.SubElement(base, "players")
    base_rules = base.find("rules")
    if base_rules is None:
        base_rules = ET.SubElement(base, "rules")
        base_rules.set("action", "prepend")

    existing_player_names = {p.get("name") for p in base_players.findall("player")}
    existing_rule_names   = {r.get("name") for r in base_rules.findall("rule")}

    added = 0
    new_players = new.find("players")
    if new_players is not None:
        for p in new_players.findall("player"):
            if p.get("name") not in existing_player_names:
                base_players.append(p)
                added += 1
    new_rules = new.find("rules")
    if new_rules is not None:
        for r in new_rules.findall("rule"):
            if r.get("name") not in existing_rule_names:
                base_rules.append(r)

    return ET.tostring(base, encoding="unicode"), added


def _count_players(text):
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return 0
    players = root.find("players")
    return 0 if players is None else len(players.findall("player"))


def _restore_original_after_failed_write(fs, target_path, backup, original_text):
    """Best-effort rollback helper used only after a failed write/validation.

    Filesystem test doubles may not implement delete/rename, so the most
    portable recovery is copy-back from backup when a backup exists, otherwise
    rewrite the original text that was read before the transaction. Rollback
    failures are intentionally swallowed so the original exception remains the
    caller-visible error.
    """
    try:
        if backup:
            fs.copy(backup, target_path)
        elif original_text is not None:
            fs.write(target_path, original_text)
    except Exception:
        pass


def merge(target_path, snippet_xml, *, fs=None, now=None):
    """Merge snippet_xml into target_path safely.

    - Refuses to merge if the existing file is malformed (raises
      ValueError so the caller can surface a clear error to the user).
    - Backs up the existing file to `<target>.<ts>.bak` before replacing it.
    - Rolls back to the backup/original text if writing or post-write
      validation fails.
    - Returns a dict with backup path (or None), added_players count,
      validated flag, post_write_validated flag, rolled_back flag, and written
      flag.
    """
    fs = fs if fs is not None else _RealFS()
    if not is_well_formed(snippet_xml):
        raise ValueError("snippet is not well-formed XML")

    existing = fs.read(target_path) if fs.exists(target_path) else None
    if existing is not None and not is_well_formed(existing):
        raise ValueError("existing playercorefactory.xml is malformed; "
                         "refusing to merge. Fix or move the file first.")

    backup = None
    if existing is not None and existing.strip():
        backup = backup_path(target_path, now=now)
        fs.copy(target_path, backup)

    try:
        merged, added = _merge_xml(existing, snippet_xml)
        if not is_well_formed(merged):
            raise ValueError("merged playercorefactory.xml is not well-formed")
        fs.write(target_path, merged)
        written_text = fs.read(target_path)
        if not is_well_formed(written_text):
            raise ValueError("written playercorefactory.xml failed validation")
    except Exception:
        _restore_original_after_failed_write(fs, target_path, backup, existing)
        raise

    return {
        "backup": backup,
        "written": True,
        "validated": True,
        "post_write_validated": True,
        "rolled_back": False,
        "added_players": added,
    }

