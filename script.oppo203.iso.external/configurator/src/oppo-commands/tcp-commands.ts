// OPPO IP-control (TCP port 23) command catalog for the Developer Options OPPO console.
//
// The control tokens mirror the canonical 76-key remote map in
// resources/data/oppo_command_map.json (the add-on's source of truth), grouped here for a quick
// quick-fire palette; the query tokens (#Q..) come from docs/OPPO_PROTOCOL_REFERENCE.md (the
// Dec-2017 RS-232 & IP doc). Each is fired verbatim over TCP via the Rust `oppo_query` command
// (which CR-terminates and reads one reply). Anything not in this curated set — including
// undocumented or parameterised commands — goes through the console's free-text raw box.
//
// `control` marks state-changing commands (power / transport / nav / source / a-v / color /
// verbose); queries are read-only and omit it. The add-on's three forbidden tokens
// (#SIS / #PGU / #PGD, see command_map.py) are intentionally absent.

export type OppoTcpCategory =
  | "power"
  | "transport"
  | "navigation"
  | "source"
  | "audio-video"
  | "color"
  | "query"
  | "verbose";

export type OppoTcpCommand = {
  command: string;
  label: string;
  category: OppoTcpCategory;
  control?: boolean;
};

export const OPPO_TCP_CATEGORY_LABELS: Record<OppoTcpCategory, string> = {
  power: "Power",
  transport: "Transport",
  navigation: "Navigation",
  source: "Input source",
  "audio-video": "Audio / video",
  color: "Colour buttons",
  query: "Status queries (#Q..)",
  verbose: "Verbose push (#SVM)",
};

export const OPPO_TCP_COMMANDS: readonly OppoTcpCommand[] = [
  // Power
  { command: "#PON", label: "Power on", category: "power", control: true },
  { command: "#POF", label: "Power off", category: "power", control: true },
  { command: "#POW", label: "Power toggle", category: "power", control: true },
  { command: "#EJT", label: "Eject / wake clone", category: "power", control: true },
  // Transport
  { command: "#PLA", label: "Play", category: "transport", control: true },
  { command: "#PAU", label: "Pause", category: "transport", control: true },
  { command: "#STP", label: "Stop", category: "transport", control: true },
  { command: "#PRE", label: "Previous", category: "transport", control: true },
  { command: "#NXT", label: "Next", category: "transport", control: true },
  { command: "#REV", label: "Reverse", category: "transport", control: true },
  { command: "#FWD", label: "Forward", category: "transport", control: true },
  { command: "#ATB", label: "A-B replay", category: "transport", control: true },
  { command: "#RPT", label: "Repeat", category: "transport", control: true },
  { command: "#GOT", label: "Go to", category: "transport", control: true },
  // Navigation
  { command: "#NUP", label: "Up", category: "navigation", control: true },
  { command: "#NDN", label: "Down", category: "navigation", control: true },
  { command: "#NLT", label: "Left", category: "navigation", control: true },
  { command: "#NRT", label: "Right", category: "navigation", control: true },
  { command: "#SEL", label: "Select / Enter", category: "navigation", control: true },
  { command: "#RET", label: "Back / Return", category: "navigation", control: true },
  { command: "#HOM", label: "Home", category: "navigation", control: true },
  { command: "#MNU", label: "Menu / popup", category: "navigation", control: true },
  { command: "#TTL", label: "Top menu", category: "navigation", control: true },
  { command: "#SET", label: "Setup", category: "navigation", control: true },
  { command: "#OPT", label: "Option", category: "navigation", control: true },
  { command: "#OSD", label: "Info (OSD)", category: "navigation", control: true },
  { command: "#INH", label: "Info (hold)", category: "navigation", control: true },
  { command: "#PUP", label: "Page up", category: "navigation", control: true },
  { command: "#PDN", label: "Page down", category: "navigation", control: true },
  { command: "#CLR", label: "Clear", category: "navigation", control: true },
  { command: "#NU0", label: "0", category: "navigation", control: true },
  { command: "#NU1", label: "1", category: "navigation", control: true },
  { command: "#NU2", label: "2", category: "navigation", control: true },
  { command: "#NU3", label: "3", category: "navigation", control: true },
  { command: "#NU4", label: "4", category: "navigation", control: true },
  { command: "#NU5", label: "5", category: "navigation", control: true },
  { command: "#NU6", label: "6", category: "navigation", control: true },
  { command: "#NU7", label: "7", category: "navigation", control: true },
  { command: "#NU8", label: "8", category: "navigation", control: true },
  { command: "#NU9", label: "9", category: "navigation", control: true },
  // Input source
  { command: "#SRC", label: "Input menu", category: "source", control: true },
  { command: "#SRC 0", label: "Blu-ray", category: "source", control: true },
  { command: "#SRC 1", label: "HDMI-in", category: "source", control: true },
  { command: "#SRC 2", label: "ARC", category: "source", control: true },
  { command: "#SRC 3", label: "Optical", category: "source", control: true },
  { command: "#SRC 4", label: "Coaxial", category: "source", control: true },
  { command: "#SRC 5", label: "USB audio", category: "source", control: true },
  { command: "#SRC 6", label: "Bluetooth", category: "source", control: true },
  // Audio / video
  { command: "#AUD", label: "Audio", category: "audio-video", control: true },
  { command: "#SUB", label: "Subtitle", category: "audio-video", control: true },
  { command: "#SUH", label: "Subtitle (hold)", category: "audio-video", control: true },
  { command: "#SAP", label: "Secondary audio", category: "audio-video", control: true },
  { command: "#ANG", label: "Angle", category: "audio-video", control: true },
  { command: "#ZOM", label: "Zoom", category: "audio-video", control: true },
  { command: "#AVS", label: "A/V sync", category: "audio-video", control: true },
  { command: "#GPA", label: "Gapless", category: "audio-video", control: true },
  { command: "#HDR", label: "HDR", category: "audio-video", control: true },
  { command: "#HDM", label: "Resolution", category: "audio-video", control: true },
  { command: "#RLH", label: "Resolution (hold)", category: "audio-video", control: true },
  { command: "#M3D", label: "3D", category: "audio-video", control: true },
  { command: "#PIP", label: "Picture-in-picture", category: "audio-video", control: true },
  { command: "#PUR", label: "Pure audio", category: "audio-video", control: true },
  { command: "#DIM", label: "Dimmer", category: "audio-video", control: true },
  { command: "#SEH", label: "Picture adjust", category: "audio-video", control: true },
  { command: "#MUT", label: "Mute", category: "audio-video", control: true },
  { command: "#VUP", label: "Volume up", category: "audio-video", control: true },
  { command: "#VDN", label: "Volume down", category: "audio-video", control: true },
  // Colour buttons
  { command: "#RED", label: "Red", category: "color", control: true },
  { command: "#GRN", label: "Green", category: "color", control: true },
  { command: "#BLU", label: "Blue", category: "color", control: true },
  { command: "#YLW", label: "Yellow", category: "color", control: true },
  // Status queries (read-only)
  { command: "#QPW", label: "Power status", category: "query" },
  { command: "#QPL", label: "Playback status", category: "query" },
  { command: "#QFN", label: "Media file name", category: "query" },
  { command: "#QFT", label: "Media file format", category: "query" },
  { command: "#QTK", label: "Track / title", category: "query" },
  { command: "#QCH", label: "Chapter", category: "query" },
  { command: "#QTE", label: "Title elapsed", category: "query" },
  { command: "#QTR", label: "Title remaining", category: "query" },
  { command: "#QEL", label: "Total elapsed", category: "query" },
  { command: "#QRE", label: "Total remaining", category: "query" },
  { command: "#QDT", label: "Disc type", category: "query" },
  { command: "#QAT", label: "Audio type", category: "query" },
  { command: "#QST", label: "Subtitle type", category: "query" },
  { command: "#QIS", label: "Input source", category: "query" },
  { command: "#QHD", label: "HDMI resolution", category: "query" },
  { command: "#QVL", label: "Volume", category: "query" },
  { command: "#QVR", label: "Firmware version", category: "query" },
  { command: "#QVM", label: "Verbose mode", category: "query" },
  // Verbose push
  { command: "#SVM 0", label: "Verbose off", category: "verbose", control: true },
  { command: "#SVM 1", label: "Verbose 1", category: "verbose", control: true },
  { command: "#SVM 2", label: "Verbose 2 (status)", category: "verbose", control: true },
  { command: "#SVM 3", label: "Verbose 3 (status + time)", category: "verbose", control: true },
];
