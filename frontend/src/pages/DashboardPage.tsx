import React, { useEffect, useState } from 'react';
import { listComplaints, updateComplaintStatus, ApiError } from '../api/client';
import type { Complaint, Status } from '../api/types';
import StatusBadge from '../components/StatusBadge';
import ApiErrorBanner from '../components/ApiErrorBanner';

const ALLOWED_TRANSITIONS: Record<Status, Status[]> = {
  open: ['in_progress', 'rejected'],
  in_progress: ['resolved', 'rejected'],
  resolved: [],
  rejected: [],
};

const getPriorityStyle = (priority: string) => {
  const p = priority?.toLowerCase();
  if (p === 'urgent') return { color: '#FF453A', bg: 'rgba(255, 69, 58, 0.15)', border: 'rgba(255, 69, 58, 0.3)' };
  if (p === 'high') return { color: '#FF9F0A', bg: 'rgba(255, 159, 10, 0.15)', border: 'rgba(255, 159, 10, 0.3)' };
  if (p === 'medium') return { color: '#0A84FF', bg: 'rgba(10, 132, 255, 0.15)', border: 'rgba(10, 132, 255, 0.3)' };
  return { color: '#64D2FF', bg: 'rgba(100, 210, 255, 0.12)', border: 'rgba(100, 210, 255, 0.25)' };
};

const DashboardPage: React.FC = () => {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | ApiError | null>(null);

  const fetchComplaints = async (currentPage: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await listComplaints({ page: currentPage, page_size: 10 });
      setComplaints(res.items);
      setTotal(res.total);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints(page);
  }, [page]);

  const handleStatusChange = async (id: string, targetStatus: Status) => {
    try {
      await updateComplaintStatus(id, { status: targetStatus });
      fetchComplaints(page);
    } catch (err: any) {
      setError(err);
    }
  };

  const totalPages = Math.ceil(total / 10) || 1;

  return (
    <div className="page-container dashboard-page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2>Triage Dashboard</h2>
          <p>Manage, review, and transition civic complaints in real time.</p>
        </div>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(255, 255, 255, 0.06)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '6px 14px',
          borderRadius: '9999px',
          fontSize: '0.82rem',
          color: 'var(--text-secondary)'
        }}>
          <span>Total Records:</span>
          <strong style={{ color: '#FFFFFF' }}>{total}</strong>
        </div>
      </div>

      <ApiErrorBanner error={error} onDismiss={() => setError(null)} />

      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : complaints.length === 0 ? (
        <div className="glass-panel" style={{ padding: '60px 20px', textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            background: 'rgba(48, 209, 88, 0.15)',
            border: '1px solid rgba(48, 209, 88, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px auto',
            color: '#34C759',
            fontSize: '1.4rem'
          }}>
            ✓
          </div>
          <h3 style={{ margin: '0 0 8px 0', fontWeight: 600 }}>All Caught Up</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            No complaints are pending in this view.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '22px' }}>
          {complaints.map((c) => {
            const prioStyle = getPriorityStyle(c.priority);
            return (
              <div 
                key={c.id} 
                className="glass-panel" 
                style={{ 
                  padding: '24px', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  gap: '14px',
                  borderRadius: '22px',
                }}
              >
                {/* Header row: Status + Priority & Date */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <StatusBadge status={c.status as Status} />
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span 
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: '9999px',
                        background: prioStyle.bg,
                        color: prioStyle.color,
                        border: `1px solid ${prioStyle.border}`,
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em'
                      }}
                    >
                      {c.priority}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                      {new Date(c.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                </div>
                
                {/* Category Title */}
                <div>
                  <h4 style={{ 
                    margin: '0', 
                    fontSize: '1.05rem', 
                    fontWeight: 600, 
                    letterSpacing: '-0.02em', 
                    color: '#FFFFFF',
                    textTransform: 'capitalize' 
                  }}>
                    {c.category}
                  </h4>
                  {c.location && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                      📍 {c.location}
                    </span>
                  )}
                </div>

                {/* AI Summary Inset */}
                <div style={{
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: '14px',
                  padding: '12px 14px',
                  minHeight: '52px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: 'var(--apple-cyan)', fontWeight: 600, letterSpacing: '0.02em' }}>
                    <span>✨ AI TRIAGE SUMMARY</span>
                  </div>
                  <p style={{ margin: '0', fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                    {c.ai_summary ? (c.ai_summary.length > 150 ? c.ai_summary.substring(0, 147) + '...' : c.ai_summary) : 'No summary generated yet.'}
                  </p>
                </div>
                
                {/* Action Footer */}
                <div style={{ marginTop: 'auto', paddingTop: '14px', borderTop: '1px solid rgba(255, 255, 255, 0.07)', display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                  {ALLOWED_TRANSITIONS[c.status as Status]?.map((target) => (
                    <button
                      key={target}
                      onClick={() => handleStatusChange(c.id, target)}
                      className="btn-glass"
                      style={{
                        padding: '6px 14px',
                        fontSize: '0.78rem',
                        fontWeight: 500,
                        borderRadius: '9999px',
                      }}
                    >
                      Mark {target.replace('_', ' ')}
                    </button>
                  ))}
                  {ALLOWED_TRANSITIONS[c.status as Status]?.length === 0 && (
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', fontStyle: 'italic' }}>
                      Terminal State
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!loading && complaints.length > 0 && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          gap: '12px', 
          marginTop: '40px',
          background: 'rgba(18, 22, 34, 0.65)',
          backdropFilter: 'blur(24px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '6px 12px',
          borderRadius: '9999px',
          width: 'fit-content',
          margin: '40px auto 0 auto',
          boxShadow: '0 8px 24px rgba(0,0,0,0.3)'
        }}>
          <button 
            onClick={() => setPage(p => Math.max(1, p - 1))} 
            disabled={page === 1}
            className="btn-glass"
            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
          >
            Previous
          </button>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '0 8px', fontWeight: 500 }}>
            Page <strong style={{ color: '#fff' }}>{page}</strong> of {totalPages}
          </span>
          <button 
            onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
            disabled={page === totalPages}
            className="btn-glass"
            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
