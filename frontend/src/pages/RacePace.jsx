import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';
import { DEFAULT_YEAR } from '../config';
import {
  ComposedChart, Scatter, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import ErrorBanner from '../components/ErrorBanner';
import StatusBar from '../components/StatusBar';
import { SkeletonLineChart } from '../components/Skeleton';
import ChartExportButton from '../components/ChartExportButton';
import useDocumentTitle from '../hooks/useDocumentTitle';

const formatLapTime = (secs) => {
  if (secs == null) return '';
  const m = Math.floor(secs / 60);
  const s = (secs % 60).toFixed(3);
  return m > 0 ? `${m}:${s.padStart(6, '0')}` : `${s}s`;
};

const formatYAxis = (secs) => {
  if (secs == null) return '';
  const m = Math.floor(secs / 60);
  const s = Math.round(secs % 60);
  return m > 0 ? `${m}:${String(s).padStart(2, '0')}` : `${s}s`;
};

const getPitLaps = (drivers) => {
  const pitSet = new Set();
  drivers.forEach(driver => {
    for (let i = 0; i < driver.laps.length - 1; i++) {
      if (driver.laps[i + 1] - driver.laps[i] > 1) {
        pitSet.add(driver.laps[i + 1]);
      }
    }
  });
  return [...pitSet].sort((a, b) => a - b);
};

const RacePace = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const chartRef = useRef(null);
  const slug = s => String(s).toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [year, setYear] = useState(() => parseInt(searchParams.get('year')) || DEFAULT_YEAR);
  const [gp, setGp] = useState(() => searchParams.get('gp') || '');
  const [session, setSessionType] = useState(() => searchParams.get('session') || 'R');
  const [d1, setD1] = useState(() => searchParams.get('d1') || '');
  const [d2, setD2] = useState(() => searchParams.get('d2') || '');
  const [d3, setD3] = useState(() => searchParams.get('d3') || '');

  useDocumentTitle(
    data
      ? `${d1} vs ${d2}${d3 ? ` vs ${d3}` : ''} — ${data.sessionName}`
      : 'Race Pace'
  );

  const runAnalysis = async ({ year, gp, session, d1, d2, d3 }) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await api.post('/api/race_pace/', {
        year, gp, session_type: session,
        driver1: d1, driver2: d2, driver3: d3 || undefined,
      });

      const chartData = [];
      const maxLap = Math.max(...res.data.drivers.flatMap(d => d.laps), 0);

      for (let i = 0; i < maxLap; i++) {
        const row = { lap: i + 1 };
        res.data.drivers.forEach(driver => {
          const lapIdx = driver.laps.indexOf(i + 1);
          if (lapIdx !== -1) {
            row[`${driver.name}_time`] = driver.times[lapIdx];
            row[`${driver.name}_trend`] = driver.trend[lapIdx];
          }
        });
        chartData.push(row);
      }

      setData({ ...res.data, chartData });
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Error loading race pace.';
      setError(`Failed to load race pace data: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (searchParams.toString()) runAnalysis({ year, gp, session, d1, d2, d3 });
  }, []);

  const handleAnalyze = (e) => {
    e.preventDefault();
    const params = { year: String(year), gp, session, d1, d2 };
    if (d3) params.d3 = d3;
    setSearchParams(params);
    runAnalysis({ year, gp, session, d1, d2, d3 });
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    const times = payload
      .filter(p => p.dataKey?.includes('_time') && p.value != null)
      .sort((a, b) => a.value - b.value);
    if (!times.length) return null;
    return (
      <div style={{
        backgroundColor: '#0d0d0d',
        padding: '10px 14px',
        border: '1px solid #2a2a2a',
        borderRadius: '8px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.6)',
        minWidth: '150px',
      }}>
        <p style={{ color: '#666', margin: '0 0 8px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          Lap {label}
        </p>
        {times.map((entry, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: i < times.length - 1 ? '5px' : 0 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: entry.color, flexShrink: 0 }} />
            <span style={{ color: '#999', fontSize: '12px', width: '36px' }}>
              {entry.dataKey.replace('_time', '')}
            </span>
            <span style={{ color: '#fff', fontSize: '12px', fontWeight: 700, fontFamily: 'monospace' }}>
              {formatLapTime(entry.value)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const pitLaps = data ? getPitLaps(data.drivers) : [];

  return (
    <div>
      <StatusBar loading={loading} message="Downloading race laps and filtering outliers…" color="#39b54a" />
      <div style={{ borderLeft: '4px solid #39b54a', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Race Pace Analysis</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          Compare true race pace and tyre degradation trends (outliers removed).
        </p>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <form className="filter-form" onSubmit={handleAnalyze}>
          <div className="filter-field">
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Year</label>
            <input className="input-premium" type="number" value={year} onChange={e => setYear(parseInt(e.target.value))} style={{ width: '90px' }} />
          </div>
          <div className="filter-field">
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Grand Prix</label>
            <input className="input-premium" type="text" value={gp} onChange={e => setGp(e.target.value)} placeholder="e.g. Bahrain" />
          </div>
          <div className="filter-field" style={{ marginLeft: '1rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 1</label>
            <input className="input-premium" type="text" value={d1} onChange={e => setD1(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="e.g. VER" />
          </div>
          <div className="filter-field">
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 2</label>
            <input className="input-premium" type="text" value={d2} onChange={e => setD2(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="e.g. NOR" />
          </div>
          <div className="filter-field">
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 3</label>
            <input className="input-premium" type="text" value={d3} onChange={e => setD3(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="optional" />
          </div>
          <button type="submit" className="btn-premium" disabled={loading}
            style={{ marginLeft: '1rem', background: 'linear-gradient(135deg, #1e824c, #39b54a)' }}>
            {loading ? 'Analyzing...' : 'Analyze Pace'}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && <SkeletonLineChart height="560px" showLegend />}

      {data && !loading && (
        <div ref={chartRef} className="glass-card" style={{ position: 'relative', padding: '2rem', paddingBottom: '1.5rem' }}>
          <ChartExportButton targetRef={chartRef} filename={`purplesector-${slug(d1)}-${slug(d2)}${d3 ? `-${slug(d3)}` : ''}-pace-${slug(gp)}-${year}.png`} />

          <h4 style={{ marginBottom: '1rem', color: '#ccc', textAlign: 'center', fontSize: '0.95rem', fontWeight: 600 }}>
            {data.sessionName} Race Pace
          </h4>

          {/* Custom driver legend — dots + trend line combined per driver */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '2.5rem', marginBottom: '1.25rem' }}>
            {data.drivers.map(driver => (
              <div key={driver.name} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="30" height="14">
                  <line x1="2" y1="7" x2="28" y2="7" stroke={driver.color} strokeWidth="2.5" />
                  <circle cx="15" cy="7" r="4.5" fill={driver.color} opacity="0.85" />
                </svg>
                <span style={{ color: '#ddd', fontSize: '12px', fontWeight: 600, letterSpacing: '0.06em' }}>
                  {driver.name}
                </span>
              </div>
            ))}
            {pitLaps.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="30" height="14">
                  <line x1="2" y1="7" x2="28" y2="7" stroke="#555" strokeWidth="1.5" strokeDasharray="4 3" />
                </svg>
                <span style={{ color: '#666', fontSize: '11px', letterSpacing: '0.04em' }}>Pit stop</span>
              </div>
            )}
          </div>

          <ResponsiveContainer width="100%" height={420}>
            <ComposedChart data={data.chartData} margin={{ top: 5, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1c1c1c" />
              <XAxis
                dataKey="lap"
                type="category"
                allowDuplicatedCategory={false}
                tick={{ fill: '#666', fontSize: 11 }}
                tickLine={false}
                label={{ value: 'Lap', position: 'insideBottom', offset: -10, fill: '#555', fontSize: 11 }}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fill: '#666', fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                tickFormatter={formatYAxis}
                width={52}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#2a2a2a', strokeWidth: 1 }} />

              {/* Pit stop markers */}
              {pitLaps.map(lap => (
                <ReferenceLine
                  key={`pit-${lap}`}
                  x={lap}
                  stroke="#3a3a3a"
                  strokeDasharray="4 3"
                  label={{ value: 'PIT', position: 'insideTopRight', fill: '#555', fontSize: 9, fontWeight: 700 }}
                />
              ))}

              {data.drivers.map((driver) => [
                <Scatter
                  key={`scatter-${driver.name}`}
                  name={driver.name}
                  dataKey={`${driver.name}_time`}
                  fill={driver.color}
                  opacity={0.5}
                  r={4}
                />,
                <Line
                  key={`line-${driver.name}`}
                  name={`${driver.name} (Trend)`}
                  type="monotone"
                  dataKey={`${driver.name}_trend`}
                  stroke={driver.color}
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={false}
                  isAnimationActive={false}
                  connectNulls={false}
                />,
              ])}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default RacePace;
