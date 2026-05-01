import React from 'react';

// Base skeleton block — all measurements in px unless w/h are strings.
export const Skel = ({ h = 12, w = '100%', style = {} }) => (
  <div className="skeleton" style={{ height: h, width: w, flexShrink: 0, ...style }} />
);

// ── Line / scatter chart (QualiBattle traces, RacePace) ───────────────────────
export const SkeletonLineChart = ({ height, showLegend = false }) => {
  const legendH = showLegend ? 40 : 0;
  return (
    <div className="glass-card" style={{ padding: '2rem', height, overflow: 'hidden' }}>
      {showLegend && (
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.75rem', alignItems: 'center' }}>
          <Skel h={12} w={84} />
          <Skel h={12} w={48} />
          <Skel h={12} w={48} />
        </div>
      )}
      <div style={{ position: 'relative', height: `calc(100% - ${legendH + 32}px)` }}>
        {/* Horizontal grid lines */}
        {[15, 35, 55, 75].map(top => (
          <div key={top} style={{
            position: 'absolute', left: 44, right: 0, top: `${top}%`,
            height: 1, background: 'rgba(255,255,255,0.04)',
          }} />
        ))}
        {/* Y-axis */}
        <div className="skeleton" style={{ position: 'absolute', left: 40, top: 0, bottom: 0, width: 2, height: 'auto' }} />
        {/* X-axis */}
        <div style={{ position: 'absolute', left: 44, right: 0, bottom: 0, height: 1, background: 'rgba(255,255,255,0.04)' }} />
        {/* Fake Y-axis tick labels */}
        {[15, 35, 55, 75].map(top => (
          <Skel key={top} h={9} w={28} style={{ position: 'absolute', left: 4, top: `calc(${top}% - 5px)` }} />
        ))}
      </div>
    </div>
  );
};

// ── Bar chart (TheDelta bars-per-round, Overtakes leaderboard) ────────────────
const BAR_HEIGHTS = [85, 72, 61, 90, 45, 78, 55, 40, 68, 82, 52, 73, 35, 88, 64, 48, 77, 59, 43, 66];

export const SkeletonBarChart = ({ height, count = 20 }) => (
  <div className="glass-card" style={{ padding: '2rem', height, overflow: 'hidden' }}>
    <Skel h={13} w={160} style={{ margin: '0 auto 1.5rem' }} />
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 5, height: 'calc(100% - 82px)' }}>
      {/* Y-axis spine */}
      <div style={{ width: 2, alignSelf: 'stretch', background: 'rgba(255,255,255,0.04)', flexShrink: 0 }} />
      {BAR_HEIGHTS.slice(0, count).map((h, i) => (
        <div key={i} className="skeleton" style={{ flex: 1, height: `${h}%`, borderRadius: '3px 3px 0 0', minWidth: 6 }} />
      ))}
    </div>
    {/* Angled label stubs */}
    <div style={{ display: 'flex', gap: 5, paddingLeft: 7, marginTop: 6 }}>
      {BAR_HEIGHTS.slice(0, count).map((_, i) => (
        <div key={i} style={{ flex: 1, minWidth: 6, display: 'flex', justifyContent: 'center' }}>
          <Skel h={9} w={14} />
        </div>
      ))}
    </div>
  </div>
);

// ── Lap ladder table ──────────────────────────────────────────────────────────
// Gap bar widths mirror the real proportional bars (P1 = 0, rest increasing).
const GAP_WIDTHS = [0, 24, 37, 44, 55, 62, 69, 74, 78, 82, 84, 86, 88, 90, 91, 93, 94, 95, 97, 99];

export const SkeletonLapLadder = () => (
  <div className="glass-card" style={{ padding: '2rem' }}>
    <Skel h={13} w={220} style={{ margin: '0 auto 2rem' }} />
    {/* Header row */}
    <div style={{
      display: 'grid', gridTemplateColumns: '44px 64px 1fr 90px 100px',
      gap: '0.5rem', padding: '0 0.4rem 0.5rem',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
    }}>
      {[20, 38, 56, 44, 64].map((w, i) => <Skel key={i} h={9} w={w} />)}
    </div>
    {/* Driver rows */}
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.5rem' }}>
      {GAP_WIDTHS.map((gapPct, idx) => (
        <div key={idx} style={{
          display: 'grid', gridTemplateColumns: '44px 64px 1fr 90px 100px',
          gap: '0.5rem', alignItems: 'center',
          background: idx === 0 ? 'rgba(176,38,255,0.05)' : 'rgba(255,255,255,0.02)',
          borderRadius: 6, padding: '0.5rem 0.4rem',
          borderLeft: '3px solid transparent',
        }}>
          <Skel h={12} w={20} style={{ margin: '0 auto' }} />
          <Skel h={12} w={36} />
          {/* Proportional gap bar */}
          <div style={{ height: 18, background: 'rgba(255,255,255,0.04)', borderRadius: 3, overflow: 'hidden' }}>
            {gapPct > 0 && (
              <div className="skeleton" style={{ width: `${gapPct}%`, height: '100%', borderRadius: '0 3px 3px 0' }} />
            )}
          </div>
          <Skel h={12} w={48} style={{ marginLeft: 'auto' }} />
          <Skel h={12} w={66} style={{ marginLeft: 'auto' }} />
        </div>
      ))}
    </div>
  </div>
);

// ── Tyre strategy stints ──────────────────────────────────────────────────────
// Each sub-array = one driver's stints as % of race distance.
const STINT_MOCK = [
  [100],
  [44, 56],
  [32, 68],
  [58, 42],
  [35, 65],
  [100],
  [40, 28, 32],
  [51, 49],
  [30, 70],
  [45, 55],
];

export const SkeletonTyreStrategy = () => (
  <div className="glass-card" style={{ padding: '2rem' }}>
    <Skel h={13} w={240} style={{ margin: '0 auto 2rem' }} />
    {/* Compound legend */}
    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
      {[54, 56, 44, 78, 42].map((w, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div className="skeleton" style={{ width: 14, height: 14, borderRadius: 3 }} />
          <Skel h={10} w={w} />
        </div>
      ))}
    </div>
    {/* Mirrors real layout: paddingLeft 60px for driver labels */}
    <div style={{ position: 'relative', paddingLeft: 60, paddingTop: 10 }}>
      {/* Driver label stubs */}
      <div style={{ position: 'absolute', left: 0, top: 10, display: 'flex', flexDirection: 'column' }}>
        {STINT_MOCK.map((_, i) => (
          <div key={i} style={{ height: 40, display: 'flex', alignItems: 'center' }}>
            <Skel h={12} w={32} />
          </div>
        ))}
      </div>
      {/* Stint bar rows */}
      <div>
        {STINT_MOCK.map((stints, dIdx) => (
          <div key={dIdx} style={{ height: 40, display: 'flex', alignItems: 'center', gap: 4 }}>
            {stints.map((wPct, sIdx) => (
              <div key={sIdx} className="skeleton" style={{
                width: `${wPct}%`, height: 28, borderRadius: 4,
                // Alternate slight opacity so adjacent stints are visually distinct.
                opacity: sIdx % 2 === 0 ? 1 : 0.65,
              }} />
            ))}
          </div>
        ))}
      </div>
    </div>
    {/* X-axis labels */}
    <div style={{ display: 'flex', justifyContent: 'space-between', paddingLeft: 60, marginTop: 8 }}>
      <Skel h={9} w={32} />
      <Skel h={9} w={40} />
      <Skel h={9} w={32} />
    </div>
  </div>
);

// ── Stat cards row (QualiBattle gap/sector cards) ─────────────────────────────
export const SkeletonStatCards = ({ count = 4 }) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="glass-card" style={{ padding: '1.5rem' }}>
        <Skel h={10} w={60} style={{ marginBottom: '0.75rem' }} />
        <Skel h={26} w={84} style={{ marginBottom: '0.5rem' }} />
        <Skel h={10} w={110} />
      </div>
    ))}
  </div>
);
