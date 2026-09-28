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
      // Refresh after update
      fetchComplaints(page);
    } catch (err: any) {
      setError(err);
    }
  };

  const totalPages = Math.ceil(total / 10) || 1;

  return (
    <div className="page-container dashboard-page">
      <h2>Triage Dashboard</h2>
      <p className="text-muted">Manage and transition complaints effectively.</p>

      <ApiErrorBanner error={error} onDismiss={() => setError(null)} />

      {loading ? (
        <p>Loading complaints...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {complaints.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <StatusBadge status={c.status as Status} />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(c.created_at).toLocaleDateString()}</span>
              </div>
              
              <h4 style={{ margin: '5px 0 0 0', textTransform: 'capitalize' }}>{c.category} - {c.priority}</h4>
              <p style={{ margin: '0', fontSize: '0.9rem', color: 'var(--text-main)', minHeight: '40px' }}>
                {c.ai_summary ? (c.ai_summary.length > 140 ? c.ai_summary.substring(0, 137) + '...' : c.ai_summary) : 'No summary generated'}
              </p>
              
              <div style={{ marginTop: 'auto', paddingTop: '10px', borderTop: '1px solid var(--border-light)', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {ALLOWED_TRANSITIONS[c.status as Status]?.map((target) => (
                  <button
                    key={target}
                    onClick={() => handleStatusChange(c.id, target)}
                    style={{
                      padding: '4px 10px',
                      fontSize: '0.8rem',
                      background: 'rgba(255, 255, 255, 0.1)',
                      boxShadow: 'none',
                    }}
                  >
                    Mark {target.replace('_', ' ')}
                  </button>
                ))}
                {ALLOWED_TRANSITIONS[c.status as Status]?.length === 0 && (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Terminal State</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && complaints.length > 0 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '30px', alignItems: 'center' }}>
          <button 
            onClick={() => setPage(p => Math.max(1, p - 1))} 
            disabled={page === 1}
            style={{ padding: '8px 16px', background: page === 1 ? 'gray' : undefined }}
          >
            Previous
          </button>
          <span>Page {page} of {totalPages}</span>
          <button 
            onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
            disabled={page === totalPages}
            style={{ padding: '8px 16px', background: page === totalPages ? 'gray' : undefined }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
