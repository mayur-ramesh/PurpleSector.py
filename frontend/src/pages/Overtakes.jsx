import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';
import { DEFAULT_YEAR } from '../config';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import ErrorBanner from '../components/ErrorBanner';
import StatusBar from '../components/StatusBar';
import { SkeletonBarChart } from '../components/Skeleton';
import ChartExportButton from '../components/ChartExportButton';
import useDocumentTitle from '../hooks/useDocumentTitle';

const Overtakes = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const chartRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [year, setYear] = useState(() => parseInt(searchParams.get('year')) || DEFAULT_YEAR);

  useDocumentTitle(
    data
      ? `${year} Overtakes Leaderboard`
      : 'Overtakes Leaderboard'
  );

  const runAnalysis = async ({ year }) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/api/overtakes/${year}`);
      setData(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Could not load data.';
      setError(`Failed to load overtakes: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (searchParams.toString()) runAnalysis({ year });
  }, []);

  const handleAnalyze = (e) => {
    e.preventDefault();
    setSearchParams({ year: String(year) });
    runAnalysis({ year });
  };

  const CustomLabel = ({ x, y, width, value }) => (
    <text x={x + width / 2} y={y - 6} fill="#aaa" textAnchor="middle" fontSize={11} fontWeight={600}>
      {value}
    </text>
  );

  return (
    <div>
      <StatusBar loading={loading} message="Aggregating overtake data across completed rounds…" color="#00aef0" />
      <div style={{ borderLeft: '4px solid #00aef0', paddingLeft: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Overtakes Leaderboard</h2>
        <p style={{ color: 'var(--color-text-muted)', margin: '0.3rem 0 0 0' }}>
          Most overtakes made in the {year} season.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <form className="filter-form" onSubmit={handleAnalyze}>
          <div className="filter-field">
            <label style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase' }}>Year</label>
            <input className="input-premium" type="number" value={year} onChange={e => setYear(parseInt(e.target.value))} style={{ width: '90px' }} />
          </div>
          <button type="submit" className="btn-premium" disabled={loading}
            style={{ background: 'linear-gradient(135deg, #006fa3, #00aef0)', color: '#fff' }}>
            {loading ? 'Loading...' : 'Show Leaderboard'}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {loading && <SkeletonBarChart height="560px" />}

      {data && !loading && (
        <div ref={chartRef} className="glass-card chart-card" style={{ position: 'relative', padding: '2rem', height: '560px' }}>
          <ChartExportButton targetRef={chartRef} filename={`purplesector-overtakes-${year}.png`} />
          <h4 style={{ textAlign: 'center', color: '#ccc', marginBottom: '1rem' }}>
            {data.year} Season — Overtakes Per Driver ({data.rounds_completed} rounds)
          </h4>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={data.drivers} margin={{ top: 25, right: 20, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis
                dataKey="driver_code"
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
              <Bar dataKey="overtakes_made" radius={[4, 4, 0, 0]} label={<CustomLabel />}>
                {data.drivers.map((entry, index) => (
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
