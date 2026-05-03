import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';
import { DEFAULT_YEAR } from '../config';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine
} from 'recharts';
import ErrorBanner from '../components/ErrorBanner';
import StatusBar from '../components/StatusBar';
import { SkeletonStatCards, SkeletonLineChart } from '../components/Skeleton';
import ChartExportButton from '../components/ChartExportButton';
import useDocumentTitle from '../hooks/useDocumentTitle';

const QualiBattle = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const speedChartRef = useRef(null);
  const deltaChartRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [year, setYear] = useState(() => parseInt(searchParams.get('year')) || DEFAULT_YEAR);
  const [gp, setGp] = useState(() => searchParams.get('gp') || '');
  const [session, setSessionType] = useState(() => searchParams.get('session') || 'Q');
  const [d1, setD1] = useState(() => searchParams.get('d1') || '');
  const [d2, setD2] = useState(() => searchParams.get('d2') || '');

  const runAnalysis = async ({ year, gp, session, d1, d2 }) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await api.post('/api/telemetry/', {
        year, gp, session_type: session, driver1: d1, driver2: d2
      });

      const chartData = [];
      const dists = res.data.driver1.telemetry.distance;
      const s1 = res.data.driver1.telemetry.speed;
      const s2 = res.data.driver2.telemetry.speed;
      const t1 = res.data.driver1.telemetry.throttle;
      const t2 = res.data.driver2.telemetry.throttle;
      const delta = res.data.delta;

      for (let i = 0; i < dists.length; i++) {
        chartData.push({
          distance: dists[i],
          speed1: s1[i], speed2: s2[i],
          throttle1: t1[i], throttle2: t2[i],
          delta: delta[i],
        });
      }
      res.data.chartData = chartData;
      setData(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error occurred.';
      setError(`Failed to fetch telemetry: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (searchParams.toString()) runAnalysis({ year, gp, session, d1, d2 });
  }, []);

  const handleAnalyze = (e) => {
    e.preventDefault();
    setSearchParams({ year: String(year), gp, session, d1, d2 });
    runAnalysis({ year, gp, session, d1, d2 });
  };

  const slug = s => String(s).toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');

  useDocumentTitle(
    data
      ? `${data.driver1.name} vs ${data.driver2.name} — ${gp} ${session} ${year}`
      : 'Qualifying Battle'
  );

  const fmt = (val) => {
    if (val == null || isNaN(val)) return 'N/A';
    return val > 0 ? `+${val.toFixed(3)}s` : `${val.toFixed(3)}s`;
  };

  const sectorGap = (a, b) => {
    if (a == null || b == null) return 'N/A';
    return fmt(a - b);
  };

  return (
    <div>
      <StatusBar loading={loading} message="Fetching telemetry data…" color="var(--color-primary)" />
      <div style={{ borderLeft: '4px solid var(--color-primary)', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Qualifying Battle</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          Compare fastest lap telemetry between any two drivers.
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginLeft: '1rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 1</label>
            <input className="input-premium" type="text" value={d1} onChange={e => setD1(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="e.g. VER" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 2</label>
            <input className="input-premium" type="text" value={d2} onChange={e => setD2(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="e.g. NOR" />
          </div>
          <button type="submit" className="btn-premium" disabled={loading} style={{ marginLeft: '1rem' }}>
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <SkeletonStatCards count={4} />
          <SkeletonLineChart height="360px" showLegend />
          <SkeletonLineChart height="220px" />
        </div>
      )}

      {data && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
            <div className="glass-card" style={{ padding: '1.5rem', borderTop: `3px solid ${data.driver1.color}` }}>
              <p style={{ color: '#888', fontSize: '0.8rem', textTransform: 'uppercase' }}>Lap Gap</p>
              <h3 style={{ fontSize: '1.4rem', color: 'var(--color-primary-light)', marginTop: '0.3rem' }}>
                {fmt(data.driver1.lapTime - data.driver2.lapTime)}
              </h3>
              <p style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.2rem' }}>
                {data.driver1.name} vs {data.driver2.name}
              </p>
            </div>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <p style={{ color: '#888', fontSize: '0.8rem', textTransform: 'uppercase' }}>Sector 1</p>
              <h3 style={{ fontSize: '1.4rem', marginTop: '0.3rem' }}>{sectorGap(data.driver1.sector1, data.driver2.sector1)}</h3>
            </div>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <p style={{ color: '#888', fontSize: '0.8rem', textTransform: 'uppercase' }}>Sector 2</p>
              <h3 style={{ fontSize: '1.4rem', marginTop: '0.3rem' }}>{sectorGap(data.driver1.sector2, data.driver2.sector2)}</h3>
            </div>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <p style={{ color: '#888', fontSize: '0.8rem', textTransform: 'uppercase' }}>Sector 3</p>
              <h3 style={{ fontSize: '1.4rem', marginTop: '0.3rem' }}>{sectorGap(data.driver1.sector3, data.driver2.sector3)}</h3>
            </div>
          </div>

          <div ref={speedChartRef} className="glass-card" style={{ position: 'relative', padding: '2rem', height: '360px' }}>
            <ChartExportButton targetRef={speedChartRef} filename={`purplesector-${slug(d1)}-${slug(d2)}-quali-speed-${slug(gp)}-${year}.png`} />
            <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1rem', alignItems: 'center' }}>
              <h4 style={{ color: '#ccc', margin: 0 }}>Speed (km/h)</h4>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', color: data.driver1.color }}>
                <span style={{ width: '20px', height: '2px', background: data.driver1.color, display: 'inline-block' }} />
                {data.driver1.name}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', color: data.driver2.color }}>
                <span style={{ width: '20px', height: '2px', background: data.driver2.color, display: 'inline-block', borderTop: '2px dashed' }} />
                {data.driver2.name}
              </span>
            </div>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={data.chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="distance" type="number" hide domain={['dataMin', 'dataMax']} />
                <YAxis domain={['auto', 'auto']} width={40} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111', borderColor: '#333' }}
                  labelFormatter={(v) => `Dist: ${v.toFixed(0)}m`}
                  formatter={(val, name) => [`${val.toFixed(1)} km/h`, name]}
                />
                {data.corners.map(c => (
                  <ReferenceLine key={c.number} x={c.distance} stroke="#333" strokeDasharray="3 3" />
                ))}
                <Line type="monotone" dataKey="speed1" name={data.driver1.name} stroke={data.driver1.color} strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="speed2" name={data.driver2.name} stroke={data.driver2.color} strokeWidth={2} strokeDasharray="5 5" dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div ref={deltaChartRef} className="glass-card" style={{ position: 'relative', padding: '2rem', height: '220px' }}>
            <ChartExportButton targetRef={deltaChartRef} filename={`purplesector-${slug(d1)}-${slug(d2)}-quali-delta-${slug(gp)}-${year}.png`} />
            <h4 style={{ marginBottom: '0.5rem', color: '#ccc' }}>
              Speed Delta — <span style={{ color: data.driver1.color }}>(+) {data.driver1.name} faster</span> / <span style={{ color: data.driver2.color }}>(-) {data.driver2.name} faster</span>
            </h4>
            <ResponsiveContainer width="100%" height="80%">
              <LineChart data={data.chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="distance" type="number" hide domain={['dataMin', 'dataMax']} />
                <YAxis domain={['auto', 'auto']} width={40} />
                <Tooltip contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} labelFormatter={(v) => `Dist: ${v.toFixed(0)}m`} />
                <ReferenceLine y={0} stroke="#555" />
                <Line type="monotone" dataKey="delta" stroke="var(--color-primary)" strokeWidth={1.5} dot={false} isAnimationActive={false} name="Delta" />
              </LineChart>
            </ResponsiveContainer>
          </div>

        </div>
      )}
    </div>
  );
};

export default QualiBattle;
