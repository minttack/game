"""Static guard that telemetry is IN the original game controller, not a demo."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
native=(root/"Source/IRL/Visual/IRLAdaptiveMobileFidelityComponent.cpp").read_text()
header=(root/"Source/IRL/Visual/IRLAdaptiveMobileFidelityComponent.h").read_text()
pc=(root/"Source/IRL/IRLPlayerController.cpp").read_text()
hud=(root/"Source/IRL/Mobile/IRLMobileTouchHUD.cpp").read_text()
reader=(root/"Tools/Visual/irl_mobile_evidence_report.py").read_text()
checks={
    "Android only logger":"#if PLATFORM_ANDROID" in native,
    "session-labelled structured logger":"IRL_MOBILE_EVIDENCE_V1 session=%s seq=%u" in native,
    "real delta tick supplied":"MobileEvidence.Observe(static_cast<double>(DeltaTime), Window)" in native,
    "quantile logging":"Window.P50Ms, Window.P95Ms, Window.P99Ms" in native,
    "inherited visual tier stays":"Budget.Observe(static_cast<double>(DeltaTime), Decision)" in native,
    "input recorder exists":"IRLMobileEvidence::Recorder MobileEvidence;" in header,
    "move callback counted":"InputKind::MoveAxis" in pc,
    "look callback counted":"InputKind::LookAxis" in pc,
    "jump callback counted":"InputKind::JumpPress" in hud,
    "experience callback counted":"InputKind::ExperiencePress" in hud,
    "no new sockets":not any(x in native for x in ("HttpModule","TcpSocket","SocketSubsystem")),
    "log parser never uploads data":not any(x in reader for x in ("requests.post(", "urllib.request.urlopen(")),
}
for label,result in checks.items():
    assert result,label
print("PASS",len(checks),"IRL mobile telemetry source integration checks; no UE runtime")
