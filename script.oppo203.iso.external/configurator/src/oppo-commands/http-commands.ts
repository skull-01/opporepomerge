// OPPO HTTP (port 436) command catalog for the Developer Options OPPO console.
//
// The endpoint list was contributed by tester Darren Solomon (2026-06) from the OPPO MediaControl
// app, observed against an OPPO UDP-203 on Free RU 65-0131 jailbreak firmware. These are the
// player's own HTTP API endpoints; the dev console fires any of them with a generic GET to the
// player (reusing the Rust `oppo_http_request` / `oppo_http_exchange` path) and shows the
// request/response in the live transcript. Most are undocumented/best-effort and hardware-pending.
//
// `sensitive` endpoints carry credentials/tokens (share logins) — the transcript must redact their
// params (the shared debug redactor already masks psk/token/password/secret/credential) and they
// must never be persisted. `control` marks state-changing endpoints (vs read-only queries, which
// are safe to fire freely). `needsParams` marks endpoints that require a query string / payload.

export type OppoHttpCategory =
  | "playback"
  | "playback-info"
  | "file-media-info"
  | "disc-info"
  | "setup-config"
  | "network-shares"
  | "account-session"
  | "other";

export type OppoHttpCommand = {
  endpoint: string;
  category: OppoHttpCategory;
  control?: boolean;
  needsParams?: boolean;
  sensitive?: boolean;
};

export const OPPO_HTTP_CATEGORY_LABELS: Record<OppoHttpCategory, string> = {
  playback: "Media playback & control",
  "playback-info": "Playback info queries",
  "file-media-info": "File & media info",
  "disc-info": "Disc info",
  "setup-config": "Setup & config",
  "network-shares": "Network & shares",
  "account-session": "Account & session",
  other: "Other",
};

export const OPPO_HTTP_COMMANDS: readonly OppoHttpCommand[] = [
  // Media playback & control
  { endpoint: "/playnormalfile", category: "playback", control: true, needsParams: true },
  { endpoint: "/playcdfile", category: "playback", control: true, needsParams: true },
  { endpoint: "/playdisc", category: "playback", control: true },
  { endpoint: "/playlistcontrolcommand", category: "playback", control: true, needsParams: true },
  { endpoint: "/prepareforplaydisc", category: "playback", control: true },
  { endpoint: "/requestcontrolkey", category: "playback", control: true },
  { endpoint: "/sksendremotekey", category: "playback", control: true, needsParams: true },
  { endpoint: "/sendremotekey", category: "playback", control: true, needsParams: true },
  { endpoint: "/tclsendremotekey", category: "playback", control: true, needsParams: true },
  { endpoint: "/setgaplessplay", category: "playback", control: true, needsParams: true },
  { endpoint: "/setplaytime", category: "playback", control: true, needsParams: true },
  { endpoint: "/setvolume", category: "playback", control: true, needsParams: true },
  { endpoint: "/setzoominout", category: "playback", control: true, needsParams: true },
  { endpoint: "/setupsync", category: "playback", control: true, needsParams: true },
  // Playback info queries
  { endpoint: "/getmovieplayinfo", category: "playback-info" },
  { endpoint: "/getmusicplayinfo", category: "playback-info" },
  { endpoint: "/getphotoplayinfo", category: "playback-info" },
  { endpoint: "/getplayingtime", category: "playback-info" },
  { endpoint: "/getplayingappname", category: "playback-info" },
  { endpoint: "/getplaymode", category: "playback-info" },
  { endpoint: "/getvolume", category: "playback-info" },
  // File & media info
  { endpoint: "/getfilelist", category: "file-media-info", needsParams: true },
  { endpoint: "/checkfolderhasBDMV", category: "file-media-info", needsParams: true },
  { endpoint: "/getdevicelist", category: "file-media-info" },
  { endpoint: "/getvideogninfo", category: "file-media-info", needsParams: true },
  { endpoint: "/getvideofilegncover", category: "file-media-info", needsParams: true },
  { endpoint: "/getmoviefileusercover", category: "file-media-info", needsParams: true },
  { endpoint: "/getmoviefileusercoverisready", category: "file-media-info", needsParams: true },
  { endpoint: "/getmusicgnid3info", category: "file-media-info", needsParams: true },
  { endpoint: "/getmusiclocalid3info", category: "file-media-info", needsParams: true },
  { endpoint: "/getmusicfilegncover", category: "file-media-info", needsParams: true },
  { endpoint: "/getmusicfilelocalcover", category: "file-media-info", needsParams: true },
  { endpoint: "/getmusicfileusercover", category: "file-media-info", needsParams: true },
  { endpoint: "/getmusicfileusercoverisready", category: "file-media-info", needsParams: true },
  { endpoint: "/getmusiccdgncover", category: "file-media-info" },
  { endpoint: "/getmusiccdgninfo", category: "file-media-info" },
  { endpoint: "/getdmrmoviecover", category: "file-media-info" },
  { endpoint: "/getdmrmusiccover", category: "file-media-info" },
  // Disc info
  { endpoint: "/getcdtracklist", category: "disc-info" },
  { endpoint: "/getcddadiscinfo", category: "disc-info" },
  { endpoint: "/getdtscddiscinfo", category: "disc-info" },
  { endpoint: "/gethdcddiscinfo", category: "disc-info" },
  { endpoint: "/getsacddiscinfo", category: "disc-info" },
  { endpoint: "/getdvdbdgninfo", category: "disc-info" },
  { endpoint: "/getdvdbdgncover", category: "disc-info" },
  // Setup & config
  { endpoint: "/getsetupmenu", category: "setup-config" },
  { endpoint: "/getsetupdbfile", category: "setup-config" },
  { endpoint: "/setaudiomenulist", category: "setup-config", control: true, needsParams: true },
  { endpoint: "/setsubttmenulist", category: "setup-config", control: true, needsParams: true },
  // Network & shares (relate to the OPPO NAS-access path; dev-test only — not the user-facing setup)
  { endpoint: "/getNfsShareFolderlist", category: "network-shares", needsParams: true },
  { endpoint: "/getSambaShareFolderlist", category: "network-shares", needsParams: true },
  { endpoint: "/loginNfsServer", category: "network-shares", control: true, needsParams: true, sensitive: true },
  { endpoint: "/loginSambaWithID", category: "network-shares", control: true, needsParams: true, sensitive: true },
  { endpoint: "/loginSambaWithOutID", category: "network-shares", control: true, needsParams: true },
  { endpoint: "/mountNfsSharedFolder", category: "network-shares", control: true, needsParams: true },
  { endpoint: "/mountNfsSharedFolderAgain", category: "network-shares", control: true, needsParams: true },
  { endpoint: "/mountSharedFolder", category: "network-shares", control: true, needsParams: true },
  // Account & session
  { endpoint: "/signin", category: "account-session", control: true },
  { endpoint: "/signout", category: "account-session", control: true },
  { endpoint: "/c2crequest", category: "account-session", control: true, needsParams: true },
  // Other
  { endpoint: "/speakergroupeventcommand", category: "other", control: true, needsParams: true },
];
