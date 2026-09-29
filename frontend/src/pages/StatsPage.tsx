import React, { useEffect, useState } from 'react';
import { getStats, ApiError } from '../api/client';
import type { StatsResponse } from '../api/types';
import ApiErrorBanner from '../components/ApiErrorBanner';

const CATEGORY_COLORS = [
  '#0A84FF', // Blue
  '#5E5CE6', // Indigo
  '#BF5AF2', // Purple
  '#FF375F', // Pink
  '#64D2FF', // Cyan
  '#30D158', // Green
];

const PRIORITY_COLORS: Record<string, string> = {
  urgent: '#FF453A',
  high: '#FF9F0A',
  medium: '#0A84FF',
  low: '#64D2FF',
};

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

  const totalComplaints = stats 
    ? Object.values(stats.by_category).reduce((acc, curr) => acc + curr, 0)
    : 0;

  return (
    <div className="page-container stats-page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2>System Statistics</h2>
          <p>Real-time analytics and municipal intake telemetry.</p>
        </div>
        <button 
          onClick={fetchStats} 
          disabled={loading}
          className="btn-glass"
          style={{ padding: '8px 18px', fontSize: '0.84rem' }}
        >
          {loading ? 'Refreshing...' : '↻ Refresh Data'}
        </button>
      </div>

      <ApiErrorBanner error={error} onDismiss={() => setError(null)} />

      {/* Dynamic Status Capsule */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(18, 22, 34, 0.75)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '6px 14px',
          borderRadius: '9999px',
          fontSize: '0.8rem',
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: cacheState === 'HIT' ? '#30D158' : '#FF9F0A',
            boxShadow: `0 0 8px ${cacheState === 'HIT' ? '#30D158' : '#FF9F0A'}`,
          }} />
          <span style={{ color: 'var(--text-secondary)' }}>Cache Engine:</span>
          <strong style={{ color: cacheState === 'HIT' ? '#34C759' : '#FFB340', letterSpacing: '0.04em' }}>
            {cacheState}
          </strong>
        </div>

        {stats && (
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            padding: '6px 14px',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            color: 'var(--text-secondary)'
          }}>
            <span>Total Captured:</span>
            <strong style={{ color: '#FFFFFF' }}>{totalComplaints}</strong>
          </div>
        )}
      </div>

      {loading && !stats ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '22px' }}>
          <div className="skeleton-card" style={{ height: '280px' }} />
          <div className="skeleton-card" style={{ height: '280px' }} />
        </div>
      ) : stats ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
          {/* By Category Card */}
          <div className="glass-panel" style={{ padding: '28px', borderRadius: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600, letterSpacing: '-0.02em' }}>
                Intake by Category
              </h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Distribution</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.entries(stats.by_category).length === 0 ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>No categories registered yet.</p>
              ) : (
                Object.entries(stats.by_category).map(([cat, count], idx) => {
                  const percentage = totalComplaints > 0 ? Math.round((count / totalComplaints) * 100) : 0;
                  const color = CATEGORY_COLORS[idx % CATEGORY_COLORS.length];
                  return (
                    <div key={cat} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                        <span style={{ textTransform: 'capitalize', fontWeight: 500, color: 'var(--text-main)' }}>
                          {cat}
                        </span>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>{percentage}%</span>
                          <strong style={{ color, minWidth: '24px', textAlign: 'right' }}>{count}</strong>
                        </div>
                      </div>
                      <div style={{
                        width: '100%',
                        height: '6px',
                        background: 'rgba(255, 255, 255, 0.08)',
                        borderRadius: '9999px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${percentage}%`,
                          height: '100%',
                          background: color,
                          borderRadius: '9999px',
                          transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
                          boxShadow: `0 0 10px ${color}`
                        }} />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* By Priority Card */}
          <div className="glass-panel" style={{ padding: '28px', borderRadius: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600, letterSpacing: '-0.02em' }}>
                Intake by Priority
              </h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Severity</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.entries(stats.by_priority).length === 0 ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>No priorities registered yet.</p>
              ) : (
                Object.entries(stats.by_priority).map(([pri, count]) => {
                  const percentage = totalComplaints > 0 ? Math.round((count / totalComplaints) * 100) : 0;
                  const color = PRIORITY_COLORS[pri.toLowerCase()] || 'var(--apple-blue)';
                  return (
                    <div key={pri} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                        <span style={{ textTransform: 'capitalize', fontWeight: 500, color: 'var(--text-main)' }}>
                          {pri}
                        </span>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>{percentage}%</span>
                          <strong style={{ color, minWidth: '24px', textAlign: 'right' }}>{count}</strong>
                        </div>
                      </div>
                      <div style={{
                        width: '100%',
                        height: '6px',
                        background: 'rgba(255, 255, 255, 0.08)',
                        borderRadius: '9999px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${percentage}%`,
                          height: '100%',
                          background: color,
                          borderRadius: '9999px',
                          transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
                          boxShadow: `0 0 10px ${color}`
                        }} />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default StatsPage;
