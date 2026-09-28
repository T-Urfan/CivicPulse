import React from 'react';
import { Status } from '../api/types';

interface StatusBadgeProps {
  status: Status;
}

const statusColors: Record<Status, { bg: string; color: string; border: string }> = {
  open: { bg: 'rgba(239, 68, 68, 0.1)', color: '#fca5a5', border: '#ef4444' },
  in_progress: { bg: 'rgba(245, 158, 11, 0.1)', color: '#fcd34d', border: '#f59e0b' },
  resolved: { bg: 'rgba(16, 185, 129, 0.1)', color: '#6ee7b7', border: '#10b981' },
  rejected: { bg: 'rgba(107, 114, 128, 0.1)', color: '#9ca3af', border: '#6b7280' },
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const theme = statusColors[status] || statusColors.open;

  return (
    <span
      style={{
        backgroundColor: theme.bg,
        color: theme.color,
        border: `1px solid ${theme.border}`,
        padding: '4px 8px',
        borderRadius: '12px',
        fontSize: '0.75rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        display: 'inline-block',
      }}
    >
      {status.replace('_', ' ')}
    </span>
  );
};

export default StatusBadge;
