import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import ErrorBanner from '../components/ErrorBanner';
import Spinner from '../components/Spinner';

const Overtakes = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get('/api/overtakes/');
      setData(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Could not load data.';
      setError(`Failed to load overtakes: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const CustomLabel = ({ x, y, width, value }) => (
    <text x={x + width / 2} y={y - 6} fill="#aaa" textAnchor="middle" fontSize={11} fontWeight={600}>
      {value}
    </text>
  );

  return (
    <div>
      <div style={{ borderLeft: '4px solid #00aef0', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Overtakes Leaderboard</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          Most overtakes made in the 2025 season.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <form onSubmit={handleAnalyze} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <button type="submit" className="btn-premium" disabled={loading}
            style={{ background: 'linear-gradient(135deg, #006fa3, #00aef0)', color: '#fff' }}>
            {loading ? 'Loading...' : 'Show Leaderboard'}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && <Spinner message="Loading overtakes leaderboard…" color="#00aef0" />}

      {data && !loading && (
        <div className="glass-card" style={{ padding: '2rem', height: '560px' }}>
          <h4 style={{ textAlign: 'center', color: '#ccc', marginBottom: '1rem' }}>
            2025 Season — Overtakes Per Driver
          </h4>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={data.overtakes} margin={{ top: 25, right: 20, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis
                dataKey="driver"
                angle={-45}
                textAnchor="end"
                height={70}
                tick={{ fill: '#aaa', fontSize: 11, fontWeight: 600 }}
              />
              <YAxis hide domain={[0, 'dataMax + 15']} />
              <Tooltip
                cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                contentStyle={{ backgroundColor: '#111', borderColor: '#333', borderRadius: '8px' }}
                itemStyle={{ color: '#fff', fontWeight: 'bold' }}
                formatter={(val, name, props) => [val, props.payload.team]}
              />
              <Bar dataKey="overtakes" radius={[4, 4, 0, 0]} label={<CustomLabel />}>
                {data.overtakes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || '#444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default Overtakes;
