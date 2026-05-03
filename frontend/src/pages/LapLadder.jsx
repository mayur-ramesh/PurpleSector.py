import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';
import { DEFAULT_YEAR } from '../config';
import ErrorBanner from '../components/ErrorBanner';
import StatusBar from '../components/StatusBar';
import { SkeletonLapLadder } from '../components/Skeleton';
import ChartExportButton from '../components/ChartExportButton';
import useDocumentTitle from '../hooks/useDocumentTitle';

const LapLadder = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const chartRef = useRef(null);
  const slug = s => String(s).toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [year, setYear] = useState(() => parseInt(searchParams.get('year')) || DEFAULT_YEAR);
  const [gp, setGp] = useState(() => searchParams.get('gp') || '');
  const [session, setSessionType] = useState(() => searchParams.get('session') || 'Q');

  useDocumentTitle(
    data
      ? `${data.sessionName} Lap Ladder`
      : 'Lap Ladder'
  );

  const runAnalysis = async ({ year, gp, session }) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await api.post('/api/laps/', { year, gp, session_type: session });
      setData(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error. Check GP and year.';
      setError(`Failed to load lap data: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (searchParams.toString()) runAnalysis({ year, gp, session });
  }, []);

  const handleAnalyze = (e) => {
    e.preventDefault();
    setSearchParams({ year: String(year), gp, session });
    runAnalysis({ year, gp, session });
  };

  const maxGap = data ? Math.max(...data.laps.map(l => l.gapToP1), 0.001) : 1;

  return (
    <div>
      <StatusBar loading={loading} message="Processing lap times…" color="#ffd12b" />
      <div style={{ borderLeft: '4px solid #ffd12b', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Lap Ladder</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          All drivers' personal best lap times sorted by gap to P1.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <form onSubmit={handleAnalyze} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Year</label>
            <input className="input-premium" type="number" value={year} onChange={e => setYear(parseInt(e.target.value))} style={{ width: '90px' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Grand Prix</label>
            <input className="input-premium" type="text" value={gp} onChange={e => setGp(e.target.value)} placeholder="e.g. Bahrain" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Session</label>
            <input className="input-premium" type="text" value={session} onChange={e => setSessionType(e.target.value)} style={{ width: '70px' }} placeholder="Q / R" />
          </div>
          <button type="submit" className="btn-premium" disabled={loading}
            style={{ marginLeft: '1rem', background: 'linear-gradient(135deg, #b8960a, #ffd12b)', color: '#111' }}>
            {loading ? 'Processing...' : 'Build Ladder'}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && <SkeletonLapLadder />}

      {data && !loading && (
        <div ref={chartRef} className="glass-card" style={{ position: 'relative', padding: '2rem' }}>
          <ChartExportButton targetRef={chartRef} filename={`purplesector-lapladder-${slug(gp)}-${slug(session)}-${year}.png`} />
          <h4 style={{ marginBottom: '2rem', color: '#ccc', textAlign: 'center' }}>
            {data.sessionName}
          </h4>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '44px 64px 1fr 90px 100px',
            gap: '0.5rem',
            padding: '0 0.4rem 0.5rem',
            borderBottom: '1px solid var(--color-border)',
            fontSize: '0.72rem',
            color: '#555',
            textTransform: 'uppercase',
            letterSpacing: '1px',
          }}>
            <span>Pos</span>
            <span>Driver</span>
            <span>Gap Bar</span>
            <span style={{ textAlign: 'right' }}>Gap</span>
            <span style={{ textAlign: 'right' }}>Lap Time</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.5rem' }}>
            {data.laps.map((lap, idx) => {
              const barPct = idx === 0 ? 0 : Math.min((lap.gapToP1 / maxGap) * 100, 100);
              return (
                <div key={idx} style={{
                  display: 'grid',
                  gridTemplateColumns: '44px 64px 1fr 90px 100px',
                  gap: '0.5rem',
                  alignItems: 'center',
                  background: idx === 0 ? 'rgba(176,38,255,0.07)' : 'rgba(255,255,255,0.02)',
                  borderRadius: '6px',
                  padding: '0.5rem 0.4rem',
                  borderLeft: idx === 0 ? `3px solid ${lap.color}` : '3px solid transparent',
                  transition: 'background 0.15s',
                }}>
                  <div style={{ textAlign: 'center', color: '#555', fontWeight: 700, fontSize: '0.9rem' }}>
                    {idx + 1}
                  </div>
                  <div style={{ fontWeight: 800, color: lap.color, fontSize: '0.95rem' }}>
                    {lap.driver}
                  </div>
                  <div style={{ position: 'relative', height: '20px', background: 'rgba(255,255,255,0.04)', borderRadius: '3px', overflow: 'hidden' }}>
                    {idx === 0 ? (
                      <div style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', fontSize: '0.7rem', color: '#ffd12b', fontWeight: 700, letterSpacing: '1px' }}>
                        POLE
                      </div>
                    ) : (
                      <div style={{
                        position: 'absolute', left: 0, top: 0, bottom: 0,
                        width: `${barPct}%`,
                        minWidth: '2px',
                        background: `linear-gradient(90deg, ${lap.color}99, ${lap.color})`,
                        borderRadius: '0 3px 3px 0',
                      }} />
                    )}
                  </div>
                  <div style={{ textAlign: 'right', color: idx === 0 ? '#ffd12b' : '#aaa', fontWeight: 600, fontSize: '0.88rem' }}>
                    {idx === 0 ? '—' : `+${lap.gapToP1.toFixed(3)}s`}
                  </div>
                  <div style={{ textAlign: 'right', color: '#ddd', fontFamily: 'monospace', fontSize: '0.88rem' }}>
                    {lap.lapTimeFormatted || `${lap.lapTimeS.toFixed(3)}s`}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default LapLadder;
