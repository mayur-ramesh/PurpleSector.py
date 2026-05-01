import React from 'react';

const StatusBar = ({ loading, message, color = 'var(--color-primary)' }) => {
  if (!loading) return null;
  return (
    <div className="status-bar">
      <div className="status-bar-dot" style={{ background: color }} />
      <span>{message}</span>
    </div>
  );
};

export default StatusBar;
