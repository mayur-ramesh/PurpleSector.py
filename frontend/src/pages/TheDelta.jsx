import React, { useState } from 'react';
import axios from 'axios';
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Cell
} from 'recharts';
import ErrorBanner from '../components/ErrorBanner';
import Spinner from '../components/Spinner';

const TheDelta = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [year, setYear] = useState(2024);
  const [d1, setD1] = useState('VER');
  const [d2, setD2] = useState('NOR');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await axios.post('/api/delta/', {
        year, ref_driver: d1, comp_driver: d2
      });

      const bars = res.data.bars.map((b, i) => ({
        ...b,
        name: `R${b.round} ${b.race.substring(0, 3).toUpperCase()}`,
        trend: res.data.trend.length > 0 ? res.data.trend[i] : undefined
      }));
      setData({ ...res.data, chartData: bars });
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error. Check driver codes.';
      setError(`Failed to load delta data: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ borderLeft: '4px solid #ff3333', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>📊 The Delta</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          Season-long qualifying gap between two drivers across all rounds.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <form onSubmit={handleAnalyze} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Year</label>
            <input className="input-premium" type="number" value={year} onChange={e => setYear(parseInt(e.target.value))} style={{ width: '90px' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginLeft: '1rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Ref Driver</label>
            <input className="input-premium" type="text" value={d1} onChange={e => setD1(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="VER" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Comp Driver</label>
            <input className="input-premium" type="text" value={d2} onChange={e => setD2(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="NOR" />
          </div>
          <button type="submit" className="btn-premium" disabled={loading}
            style={{ marginLeft: '1rem', background: 'linear-gradient(135deg, #c0392b, #ff3333)' }}>
            {loading ? 'Building Chart...' : '📊 Build Chart'}
          </button>
        </form>
        <p style={{ marginTop: '0.75rem', fontSize: '0.78rem', color: '#555' }}>
          ℹ️ Uses 3-digit driver codes (e.g. VER, NOR, HAM). Loading the full season may take 30–90 seconds.
        </p>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && <Spinner message="Loading qualifying data for every round… Please wait." color="#ff3333" />}

      {data && !loading && (
        <div className="glass-card" style={{ padding: '2rem', height: '520px' }}>
          <h4 style={{ marginBottom: '0.5rem', color: '#ccc', textAlign: 'center' }}>
            {year} Qualifying Gap — {data.ref_driver} vs {data.comp_driver}
          </h4>
          <p style={{ textAlign: 'center', fontSize: '0.8rem', color: '#555', marginBottom: '1rem' }}>
            (+) {data.ref_driver} faster &nbsp;/&nbsp; (-) {data.comp_driver} faster
          </p>
          <ResponsiveContainer width="100%" height="85%">
            <ComposedChart data={data.chartData} margin={{ top: 10, right: 30, left: 10, bottom: 55 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={60} tick={{ fill: '#aaa', fontSize: 11 }} />
              <YAxis tick={{ fill: '#aaa' }} tickFormatter={(v) => `${v.toFixed(2)}s`} />
              <Tooltip
                cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                contentStyle={{ backgroundColor: '#111', borderColor: '#333', borderRadius: '8px' }}
                formatter={(val, name) => name === 'trend' ? [`${val.toFixed(3)}s`, 'Trend'] : [`${val.toFixed(3)}s`, 'Gap']}
              />
              <ReferenceLine y={0} stroke="#444" />
              <Bar dataKey="gap" radius={[3, 3, 0, 0]}>
                {data.chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
              {data.trend.length > 0 && (
                <Line
                  type="monotone" dataKey="trend"
                  stroke="var(--color-primary)"
                  strokeWidth={2.5}
                  dot={false}
                  strokeDasharray="6 3"
                  isAnimationActive={false}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default TheDelta;
