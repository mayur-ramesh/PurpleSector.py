import React from 'react';

const ErrorBanner = ({ message, onDismiss }) => {
  if (!message) return null;
  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.75rem',
      padding: '1rem 1.25rem',
      marginBottom: '1.5rem',
      background: 'rgba(220, 38, 38, 0.08)',
      border: '1px solid rgba(220, 38, 38, 0.4)',
      borderRadius: '10px',
      color: '#fca5a5',
      fontSize: '0.9rem',
      lineHeight: 1.5,
    }}>
      <span style={{ flexGrow: 1 }}>{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{
            background: 'none',
            border: 'none',
            color: '#fca5a5',
            cursor: 'pointer',
            fontSize: '1.1rem',
            lineHeight: 1,
            padding: 0,
            flexShrink: 0,
            opacity: 0.7,
          }}
          aria-label="Dismiss error"
        >✕</button>
      )}
    </div>
  );
};

export default ErrorBanner;
