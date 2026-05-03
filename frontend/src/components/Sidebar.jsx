import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Trophy, 
  BarChart2, 
  Timer, 
  Disc, 
  Flag,
  LineChart 
} from 'lucide-react';

const Sidebar = ({ isOpen, closeSidebar }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Qualifying Battle', icon: Trophy, color: '#b026ff' },
    { path: '/delta', label: 'The Delta', icon: BarChart2, color: '#ff3333' },
    { path: '/pace', label: 'Race Pace', icon: LineChart, color: '#39b54a' },
    { path: '/laps', label: 'Lap Ladder', icon: Timer, color: '#ffd12b' },
    { path: '/tyres', label: 'Tyre Strategy', icon: Disc, color: '#e0e0e0' },
    { path: '/overtakes', label: 'Overtakes', icon: Flag, color: '#00aef0' },
  ];

  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`} style={{ padding: '2rem 1rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, marginBottom: '0.2rem', fontFamily: 'Consolas, "Courier New", monospace', color: '#b026ff' }}>
          @purplesector.py
        </h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem', letterSpacing: '2px', textTransform: 'uppercase' }}>
          F1 Analytics
        </p>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={closeSidebar}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '0.8rem 1.2rem',
                borderRadius: '8px',
                textDecoration: 'none',
                color: isActive ? '#fff' : 'var(--color-text-muted)',
                background: isActive ? 'var(--color-surface-hover)' : 'transparent',
                border: '1px solid',
                borderColor: isActive ? 'var(--color-border)' : 'transparent',
                transition: 'all 0.2s ease',
              }}
            >
              <item.icon size={20} color={isActive ? item.color : 'currentColor'} />
              <span style={{ fontWeight: isActive ? 600 : 400, fontSize: '0.95rem' }}>
                {item.label}
              </span>
            </NavLink>
          );
        })}
      </nav>
      
      <div style={{ marginTop: 'auto', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '0.7rem' }}>
        <p>Data provided by FastF1</p>
      </div>
    </div>
  );
};

export default Sidebar;
