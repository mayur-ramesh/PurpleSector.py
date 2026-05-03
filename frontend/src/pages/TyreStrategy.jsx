import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';
import { DEFAULT_YEAR } from '../config';
import ErrorBanner from '../components/ErrorBanner';
import StatusBar from '../components/StatusBar';
import { SkeletonTyreStrategy } from '../components/Skeleton';
import ChartExportButton from '../components/ChartExportButton';
import useDocumentTitle from '../hooks/useDocumentTitle';

const TyreStrategy = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const chartRef = useRef(null);
  const slug = s => String(s).toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [year, setYear] = useState(() => parseInt(searchParams.get('year')) || DEFAULT_YEAR);
  const [gp, setGp] = useState(() => searchParams.get('gp') || '');
  const [session, setSessionType] = useState(() => searchParams.get('session') || 'R');

  useDocumentTitle(
    data
      ? `${data.sessionName} Tyre Strategy`
      : 'Tyre Strategy'
  );

  const runAnalysis = async ({ year, gp, session }) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await api.post('/api/tyres/', { year, gp, session_type: session });
      setData(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Check the GP / year / session.';
      setError(`Failed to load tyre strategies: ${detail}`);
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

  const compoundLabel = {
    SOFT: 'S', MEDIUM: 'M', HARD: 'H',
    INTERMEDIATE: 'I', WET: 'W', UNKNOWN: '?'
  };

  return (
    <div>
      <StatusBar loading={loading} message="Loading stint and tyre data…" color="#e0e0e0" />
      <div style={{ borderLeft: '4px solid #e0e0e0', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Tyre Strategy</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          Pit stops, stints and compounds across the top 10.
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
            <input className="input-premium" type="text" value={session} onChange={e => setSessionType(e.target.value)} style={{ width: '70px' }} placeholder="R" />
          </div>
          <button type="submit" className="btn-premium" disabled={loading}
            style={{ marginLeft: '1rem', background: 'linear-gradient(135deg, #888, #e0e0e0)', color: '#111' }}>
            {loading ? 'Processing...' : 'Analyze Tyres'}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && <SkeletonTyreStrategy />}

      {data && !loading && (
        <div ref={chartRef} className="glass-card" style={{ position: 'relative', padding: '2rem' }}>
          <ChartExportButton targetRef={chartRef} filename={`purplesector-tyres-${slug(gp)}-${slug(session)}-${year}.png`} />
          <h4 style={{ marginBottom: '2rem', color: '#ccc', textAlign: 'center' }}>
            {data.sessionName}
          </h4>

          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            {[['SOFT','#ff3333'],['MEDIUM','#ffd12b'],['HARD','#e0e0e0'],['INTERMEDIATE','#39b54a'],['WET','#00aef0']].map(([c, col]) => (
              <div key={c} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: '#aaa' }}>
                <div style={{ width: '14px', height: '14px', background: col, borderRadius: '3px' }} />
                {c[0] + c.slice(1).toLowerCase()}
              </div>
            ))}
          </div>

          <div style={{ position: 'relative', paddingLeft: '60px', paddingTop: '10px' }}>
            <div style={{ position: 'absolute', left: 0, top: '10px', bottom: 0, display: 'flex', flexDirection: 'column' }}>
              {data.drivers.map((driver, idx) => (
                <div key={idx} style={{ height: '40px', display: 'flex', alignItems: 'center', fontWeight: 700, color: '#aaa', fontSize: '0.85rem' }}>
                  {driver}
                </div>
              ))}
            </div>

            <div style={{ position: 'relative', width: '100%', height: `${data.drivers.length * 40}px`, background: 'rgba(255,255,255,0.02)', borderRadius: '4px' }}>
              {[0.25, 0.5, 0.75, 1].map(frac => (
                <div key={frac} style={{
                  position: 'absolute',
                  left: `${frac * 100}%`,
                  top: 0, bottom: 0,
                  borderLeft: `1px dashed rgba(255,255,255,${frac === 1 ? '0.15' : '0.06'})`
                }} />
              ))}

              {data.stints.map((stint, idx) => {
                const width = (stint.duration / data.totalLaps) * 100;
                const left = (stint.start / data.totalLaps) * 100;
                const top = stint.yPos * 40 + 5;
                const label = compoundLabel[stint.compound] || stint.compound[0];
                return (
                  <div key={idx} title={`${stint.driver} – ${stint.compound} (L${stint.start}–L${stint.start + stint.duration})`}
                    style={{
                      position: 'absolute',
                      top: `${top}px`,
                      left: `${left}%`,
                      width: `${Math.max(width, 0.5)}%`,
                      height: '30px',
                      background: stint.color,
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#111',
                      fontWeight: 800,
                      fontSize: '11px',
                      boxShadow: '0 2px 6px rgba(0,0,0,0.35)',
                      border: '1px solid rgba(0,0,0,0.2)',
                      cursor: 'default',
                      overflow: 'hidden',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {width > 4 ? label : ''}
                  </div>
                );
              })}

              {data.pitStops.map((stop, idx) => (
                <div key={`stop-${idx}`} style={{
                  position: 'absolute',
                  top: `${stop.yPos * 40 + 3}px`,
                  left: `${(stop.lap / data.totalLaps) * 100}%`,
                  transform: 'translateX(-50%)',
                  background: '#1a1a1a',
                  color: '#fff',
                  fontSize: '8px',
                  fontWeight: 'bold',
                  padding: '2px 4px',
                  borderRadius: '3px',
                  zIndex: 10,
                  border: '1px solid #444',
                  pointerEvents: 'none',
                }}>
                  L{stop.lap}
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', color: '#555', fontSize: '11px' }}>
              <span>Lap 1</span>
              <span>Lap {Math.floor(data.totalLaps / 2)}</span>
              <span>Lap {data.totalLaps}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TyreStrategy;
