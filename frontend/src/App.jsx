import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import QualiBattle from './pages/QualiBattle';
import TheDelta from './pages/TheDelta';
import LapLadder from './pages/LapLadder';
import TyreStrategy from './pages/TyreStrategy';
import Overtakes from './pages/Overtakes';
import RacePace from './pages/RacePace';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* Redirect home to QualiBattle could be done here, or just render it */}
        <Route index element={<QualiBattle />} />
        <Route path="delta" element={<TheDelta />} />
        <Route path="laps" element={<LapLadder />} />
        <Route path="tyres" element={<TyreStrategy />} />
        <Route path="pace" element={<RacePace />} />
        <Route path="overtakes" element={<Overtakes />} />
      </Route>
    </Routes>
  );
}

export default App;
