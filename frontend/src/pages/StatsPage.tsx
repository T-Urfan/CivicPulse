import React, { useEffect, useState } from 'react';
import { getStats, ApiError } from '../api/client';
import type { StatsResponse } from '../api/types';
import ApiErrorBanner from '../components/ApiErrorBanner';

const StatsPage: React.FC = () => {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [cacheState, setCacheState] = useState<string>('UNKNOWN');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | ApiError | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getStats();
      setStats(res.data);
      setCacheState(res.cacheState);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="page-container stats-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>System Statistics</h2>
        <button onClick={fetchStats} style={{ padding: '8px 16px' }}>Refresh</button>
      </div>
      
      <p className="text-muted">Aggregate analytics over all civic issues reported.</p>

      <ApiErrorBanner error={error} onDismiss={() => setError(null)} />

      {!loading && stats && (
        <>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '24px' }}>
            <span>Stats Cache Status:</span>
            <span style={{ 
              background: cacheState === 'HIT' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
              color: cacheState === 'HIT' ? '#6ee7b7' : '#fcd34d',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 'bold'
            }}>
              {cacheState}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ marginTop: 0 }}>By Category</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(stats.by_category).map(([cat, count]) => (
                  <li key={cat} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-light)', paddingBottom: '8px' }}>
                    <span style={{ textTransform: 'capitalize' }}>{cat}</span>
                    <strong style={{ color: 'var(--primary-color)' }}>{count}</strong>
                  </li>
                ))}
              </ul>
            </div>

            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ marginTop: 0 }}>By Priority</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(stats.by_priority).map(([pri, count]) => (
                  <li key={pri} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-light)', paddingBottom: '8px' }}>
                    <span style={{ textTransform: 'capitalize' }}>{pri}</span>
                    <strong style={{ color: 'var(--primary-color)' }}>{count}</strong>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default StatsPage;
