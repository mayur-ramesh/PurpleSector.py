import React, { useState } from 'react';
import axios from 'axios';
import { DEFAULT_YEAR } from '../config';
import {
  ComposedChart, Scatter, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import ErrorBanner from '../components/ErrorBanner';
import Spinner from '../components/Spinner';

const RacePace = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [year, setYear] = useState(DEFAULT_YEAR);
  const [gp, setGp] = useState('Monaco');
  const [session, setSessionType] = useState('R');
  const [d1, setD1] = useState('VER');
  const [d2, setD2] = useState('NOR');
  const [d3, setD3] = useState('LEC');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await axios.post('/api/race_pace/', {
        year, gp, session_type: session, 
        driver1: d1, driver2: d2, driver3: d3 || undefined
      });
      
      // Transform data for Recharts ComposedChart
      // We need it in an array of objects where each object is a lap
      const chartData = [];
      const maxLength = Math.max(...res.data.drivers.map(d => d.laps.length), 0);
      
      // We will pivot the data: { lap: 1, VER_time: 80.5, VER_trend: 80.6, ... }
      for (let i = 0; i < maxLength; i++) {
          const row = { lap: i + 1 };
          res.data.drivers.forEach(driver => {
              // Find the data point that corresponds to this lap number
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

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ backgroundColor: '#111', padding: '10px', border: '1px solid #333', borderRadius: '8px' }}>
          <p style={{ color: '#ccc', margin: '0 0 5px 0', fontSize: '12px' }}>Lap {label}</p>
          {payload.map((entry, index) => {
            if (entry.dataKey.includes('_trend')) return null; // Only show scatter points in tooltip
            return (
              <p key={index} style={{ color: entry.color, margin: '2px 0', fontSize: '11px', fontWeight: 'bold' }}>
                {entry.name.split('_')[0]}: {entry.value.toFixed(3)}s
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <div style={{ borderLeft: '4px solid #39b54a', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>🏎️ Race Pace Analysis</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          Compare true race pace and tyre degradation trends (outliers removed).
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
            <input className="input-premium" type="text" value={gp} onChange={e => setGp(e.target.value)} placeholder="e.g. Monaco" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginLeft: '1rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 1</label>
            <input className="input-premium" type="text" value={d1} onChange={e => setD1(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="VER" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 2</label>
            <input className="input-premium" type="text" value={d2} onChange={e => setD2(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="NOR" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Driver 3</label>
            <input className="input-premium" type="text" value={d3} onChange={e => setD3(e.target.value.toUpperCase())} style={{ width: '80px' }} placeholder="LEC (opt)" />
          </div>
          <button type="submit" className="btn-premium" disabled={loading}
            style={{ marginLeft: '1rem', background: 'linear-gradient(135deg, #1e824c, #39b54a)' }}>
            {loading ? 'Analyzing...' : 'Analyze Pace'}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && <Spinner message="Downloading telemetry & filtering outliers... This takes ~30s." color="#39b54a" />}

      {data && !loading && (
        <div className="glass-card" style={{ padding: '2rem', height: '520px' }}>
          <h4 style={{ marginBottom: '1.5rem', color: '#ccc', textAlign: 'center' }}>
            {data.sessionName} Race Pace
          </h4>
          <ResponsiveContainer width="100%" height="85%">
            <ComposedChart data={data.chartData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="lap" type="category" allowDuplicatedCategory={false} tick={{ fill: '#aaa', fontSize: 11 }} />
              <YAxis domain={['auto', 'auto']} tick={{ fill: '#aaa', fontSize: 11 }} tickFormatter={(val) => `${val.toFixed(1)}s`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              
              {data.drivers.map((driver) => [
                <Scatter key={`scatter-${driver.name}`} name={`${driver.name}`} dataKey={`${driver.name}_time`} fill={driver.color} opacity={0.6} />,
                <Line key={`line-${driver.name}`} name={`${driver.name} (Trend)`} type="monotone" dataKey={`${driver.name}_trend`} stroke={driver.color} strokeWidth={3} dot={false} activeDot={false} isAnimationActive={false} />
              ])}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default RacePace;
