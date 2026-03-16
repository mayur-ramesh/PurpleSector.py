import React from 'react';

const Spinner = ({ message = 'Loading data...', color = 'var(--color-primary)' }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '4rem 2rem',
      gap: '1.5rem',
    }}>
      <div style={{
        width: '48px',
        height: '48px',
        border: `3px solid rgba(255,255,255,0.08)`,
        borderTop: `3px solid ${color}`,
        borderRadius: '50%',
        animation: 'spin 0.9s linear infinite',
      }} />
      <p style={{
        color: 'var(--color-text-muted)',
        fontSize: '0.9rem',
        letterSpacing: '0.5px',
        textAlign: 'center',
        maxWidth: '300px',
      }}>
        {message}
      </p>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Spinner;
