import type { CSSProperties } from "react";

type AmbientHudProps = { active: boolean; level: number };

const spectrumBars = Array.from({ length: 28 }, (_, index) => {
  const centerDistance = Math.abs(index - 13.5) / 14;
  const baseHeight = Math.round(18 + (1 - centerDistance * 0.5) * 50 + ((index * 19) % 22));
  return {
    x: 18 + index * 20,
    height: baseHeight,
    delay: `${(index % 7) * -0.15}s`,
  };
});

export function AmbientHud({ active, level }: AmbientHudProps) {
  return (
    <div
      className={`ambient-hud ${active ? "is-active" : ""}`}
      style={{ "--audio-level": level } as CSSProperties}
      aria-hidden="true"
    >
      {/* Corner HUD framing brackets */}
      <div className="hud-corner top-left">
        <svg viewBox="0 0 60 60" className="corner-svg">
          <path d="M 2 30 L 2 2 L 30 2" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <circle cx="2" cy="2" r="2" fill="currentColor" />
          <line x1="12" y1="12" x2="26" y2="12" stroke="currentColor" strokeWidth="1" strokeDasharray="3 2" />
        </svg>
      </div>
      <div className="hud-corner top-right">
        <svg viewBox="0 0 60 60" className="corner-svg">
          <path d="M 58 30 L 58 2 L 30 2" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <circle cx="58" cy="2" r="2" fill="currentColor" />
          <line x1="48" y1="12" x2="34" y2="12" stroke="currentColor" strokeWidth="1" strokeDasharray="3 2" />
        </svg>
      </div>

      {/* Decorative cybernetic circuit telemetry */}
      <svg className="circuit-overlay" viewBox="0 0 400 160" preserveAspectRatio="none">
        <defs>
          <linearGradient id="circuit-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.8" />
            <stop offset="60%" stopColor="#00f5c4" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#00f0ff" stopOpacity="0.1" />
          </linearGradient>
        </defs>
        <path d="M 10 25 L 110 25 L 140 55 L 280 55 L 310 25 L 380 25" fill="none" stroke="url(#circuit-grad)" strokeWidth="1.2" />
        <path d="M 35 40 L 120 40 L 145 68 L 240 68" fill="none" stroke="url(#circuit-grad)" strokeWidth="1" strokeDasharray="4 3" />
        <path d="M 70 85 L 160 85 L 185 115 L 330 115" fill="none" stroke="url(#circuit-grad)" strokeWidth="1" />
        <circle cx="10" cy="25" r="2.5" className="circuit-node" />
        <circle cx="280" cy="55" r="2.5" className="circuit-node" />
        <circle cx="380" cy="25" r="2" className="circuit-node" />
        <circle cx="240" cy="68" r="2" className="circuit-node" />
        <circle cx="330" cy="115" r="2.5" className="circuit-node" />
        <rect x="136" y="51" width="8" height="8" transform="rotate(45 140 55)" fill="none" stroke="#00f5c4" strokeWidth="1" />
      </svg>

      {/* Audio Visualiser Spectrum Field */}
      <svg className="signal-field" viewBox="0 0 580 160" preserveAspectRatio="none">
        <defs>
          <linearGradient id="spectrum-grad" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor="#005a75" stopOpacity="0.5" />
            <stop offset="55%" stopColor="#00f0ff" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#00f5c4" stopOpacity="1" />
          </linearGradient>
        </defs>
        <line x1="10" y1="150" x2="570" y2="150" stroke="rgba(0, 240, 255, 0.25)" strokeWidth="1" strokeDasharray="3 3" />
        {spectrumBars.map((bar) => (
          <line
            className="signal-line"
            key={bar.x}
            style={{ "--line-delay": bar.delay, "--base-height": `${bar.height}px` } as CSSProperties}
            x1={bar.x}
            x2={bar.x}
            y1="148"
            y2={148 - bar.height}
          />
        ))}
      </svg>

      {/* Telemetry caption & channel status */}
      <div className="hud-caption">
        <span className="caption-tag">AUDIO LINK</span>
        <span className="caption-divider">//</span>
        <span className="caption-state">{active ? "STREAM ACTIVE [24-BIT / 48kHz]" : "STANDBY [CARRIER READY]"}</span>
      </div>
    </div>
  );
}
