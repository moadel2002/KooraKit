import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import PreMatch from './Prematch';
import PostMatch from './Postmatch';
import TeamPreMatchAnalysis from './TeamPrematchAnalysis';
import PlayerPreMatchAnalysis from './PlayerPrematchAnalysis';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/prematch" element={<PreMatch />} />
        <Route path="/postmatch" element={<PostMatch />} />
        <Route path="/team-prematch-analysis" element={<TeamPreMatchAnalysis />} />
        <Route path="/player-prematch-analysis" element={<PlayerPreMatchAnalysis />} />
      </Routes>
    </Router>
  );
}

export default App;