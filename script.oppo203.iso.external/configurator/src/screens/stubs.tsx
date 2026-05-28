import { FooterNav } from "../shell/FooterNav";
import type { ScreenProps } from "./types";
import type { ScreenId } from "../steps";

type StubProps = ScreenProps & {
  title: string;
  subtitle: string;
  back?: ScreenId | null;
  next?: ScreenId | null;
  nextLabel?: string;
  body?: React.ReactNode;
};

function Stub({ go, set, state, title, subtitle, back, next, nextLabel, body }: StubProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">{title}</h1>
        <p className="screen-subtitle">{subtitle}</p>
      </div>
      <div className="stub-marker">
        <strong>TODO</strong> — port from{" "}
        <code>docs/installuidraft/design_handoff_oppo_installer/prototype/</code>. Wizard
        state available: <code>{JSON.stringify(state, null, 0)}</code>
        {body && <div style={{ marginTop: 12 }}>{body}</div>}
      </div>
      <FooterNav go={go} back={back ?? undefined} next={next ?? undefined} nextLabel={nextLabel} set={set} />
    </div>
  );
}

// ============================================================
// STEP 1 — Kodi box
// ============================================================
export function Step1Intro(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Your Kodi box"
      subtitle="Enter the Kodi box IP, then choose Tier A (SSH auto-apply), B (SMB write-only), or C (manual file generation)."
      back="step0_gate"
      next="step1_tierA"
      nextLabel="Continue (Tier A)"
    />
  );
}
export function Step1TierA(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Auto-write + auto-apply (SSH)"
      subtitle="One credential set. SFTP-write + SSH-restart on the same login. Diagnostic log with 3 checks."
      back="step1_intro"
      next="step2_brand"
      nextLabel="Continue to TV"
    />
  );
}
export function Step1TierB(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Auto-write only (SMB)"
      subtitle="We copy the files; you restart Kodi yourself. SMB-share creds, 3-check diag log."
      back="step1_intro"
      next="step2_brand"
      nextLabel="Continue to TV"
    />
  );
}
export function Step1TierC(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="You'll install the files yourself"
      subtitle="Generate playercorefactory.xml + remote-bridge keymap. Backup warning, platform paths."
      back="step1_intro"
      next="step2_brand"
      nextLabel="Continue to TV"
    />
  );
}

// ============================================================
// STEP 2 — TV
// ============================================================
export function Step2Brand(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Your TV"
      subtitle="Brand grid: Sony, Samsung, LG, TCL, Hisense, Roku, Vizio, Panasonic, Other."
      back="step1_intro"
      next="step2_model"
    />
  );
}
export function Step2Model(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Which model?"
      subtitle="Year + size filters + search + scrollable model list with backend chips."
      back="step2_brand"
      next="step2_adb_warn"
    />
  );
}
export function Step2NotFound(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="We couldn't find your model."
      subtitle="Two paths: probe (recommended) or manual backend pick."
      back="step2_model"
      next="step2_probe"
    />
  );
}
export function Step2Probe(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Probe your TV"
      subtitle="Port-knock each backend (ADB :5555, Roku :8060, Sony :20060, SmartThings)."
      back="step2_notfound"
      next="step2_test"
    />
  );
}
export function Step2AdbWarn(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Heads-up: your TV may ask permission."
      subtitle='Pick "Always allow from this computer" — a one-time accept can drop on reboot.'
      back="step2_model"
      next="step2_test"
    />
  );
}
export function Step2Test(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Can we control your TV?"
      subtitle="Send a mute blip. No inputs change, no OPPO wake. Yes/no gate."
      back="step2_adb_warn"
      next="step3_brand"
      nextLabel="Yes — continue to Player"
      set={p.set}
    />
  );
}
export function Step2Fail(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Let's figure out why."
      subtitle="Pairing rejected / connected-but-inert / nothing-reached → three diagnostic tiles."
      back="step2_test"
      next="step3_brand"
    />
  );
}

// ============================================================
// STEP 3 — Player
// ============================================================
export function Step3Brand(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Your OPPO or clone"
      subtitle="Brand → model + IP. Posture callout per model (stock / wake-rewrite / warning-only)."
      back="step2_test"
      next="step3_test"
      nextLabel="Continue to control test"
    />
  );
}
export function Step3Test(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Wake & confirm"
      subtitle="#EJT for clones / #PON for stock OPPO. Query #QPW to confirm. Two-way IP control verified."
      back="step3_brand"
      next="step35_intro"
      nextLabel="Continue — capture HDMI inputs"
    />
  );
}
export function Step3Fail(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Player didn't respond."
      subtitle="4 cheapest-first hints: IP Control off / wrong IP / wrong subnet / standby vs off."
      back="step3_test"
      next="step3_test"
      nextLabel="Retry the test"
    />
  );
}

// ============================================================
// STEP 3.5 — Input capture
// ============================================================
export function Step35Intro(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Now the HDMI inputs."
      subtitle="Capture the OPPO's input (switch to) and the Kodi box's input (return target)."
      back="step3_test"
      next="step35_ask"
      nextLabel="Capture inputs"
    />
  );
}
export function Step35Ask(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Which HDMI input is your OPPO on?"
      subtitle="Ask-first HDMI tiles 1–4. Two iterations: OPPO input, then Kodi box input."
      back="step35_intro"
      next="step35_done"
    />
  );
}
export function Step35Fallback(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Let's find it together."
      subtitle="ADB-weak 4-rung funnel: ask number → CEC One-Touch-Play → blind-cycle → manual."
      back="step35_intro"
      next="step35_done"
    />
  );
}
export function Step35Done(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Inputs captured."
      subtitle="Summary: switch-to OPPO HDMI N, return-to Kodi HDMI M."
      back="step35_intro"
      next="test_setup"
      nextLabel="Run the full setup test"
    />
  );
}

// ============================================================
// TEST
// ============================================================
export function TestSetup(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Full setup test."
      subtitle="Pick: use our bundled test disc, or use one of your own UHD ISOs."
      back="step35_done"
      next="test_confirm"
      nextLabel="I played one — how did it go?"
    />
  );
}
export function TestConfirm(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="How did that go?"
      subtitle="3 yes/no questions. Each 'no' routes back to the owning step."
      back="test_setup"
      next="test_success"
      nextLabel="See the summary"
    />
  );
}
export function TestSuccess(p: ScreenProps) {
  return (
    <Stub
      {...p}
      title="Your chain works."
      subtitle="Setup verified end to end. Summary of the resolved chain. Save-report option."
      back="test_confirm"
      next="step0_gate"
      nextLabel="Done (back to start)"
    />
  );
}
