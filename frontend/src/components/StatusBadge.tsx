import React from 'react';
import { Status } from '../api/types';

interface StatusBadgeProps {
  status: Status;
}

const statusColors: Record<Status, { bg: string; color: string; border: string; dot: string }> = {
  open: { 
    bg: 'rgba(255, 69, 58, 0.14)', 
    color: '#FF6961', 
    border: 'rgba(255, 69, 58, 0.28)', 
    dot: '#FF453A' 
  },
  in_progress: { 
    bg: 'rgba(255, 159, 10, 0.14)', 
    color: '#FFB340', 
    border: 'rgba(255, 159, 10, 0.28)', 
    dot: '#FF9F0A' 
  },
  resolved: { 
    bg: 'rgba(48, 209, 88, 0.14)', 
    color: '#34C759', 
    border: 'rgba(48, 209, 88, 0.28)', 
    dot: '#30D158' 
  },
  rejected: { 
    bg: 'rgba(142, 142, 147, 0.14)', 
    color: '#AEAEB2', 
    border: 'rgba(142, 142, 147, 0.28)', 
    dot: '#8E8E93' 
  },
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const theme = statusColors[status] || statusColors.open;

  return (
    <span
      style={{
        backgroundColor: theme.bg,
        color: theme.color,
        border: `1px solid ${theme.border}`,
        padding: '3px 10px',
        borderRadius: '9999px',
        fontSize: '0.73rem',
        fontWeight: 600,
        letterSpacing: '0.02em',
        textTransform: 'uppercase',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        boxShadow: `0 0 12px ${theme.bg}`,
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: theme.dot,
          boxShadow: `0 0 6px ${theme.dot}`,
        }}
      />
      {status.replace('_', ' ')}
    </span>
  );
};

export default StatusBadge;
