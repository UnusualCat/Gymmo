import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  return (
    <div className="home">
      <h1>Benvenuto su Gymmo</h1>
      <p>Il tuo assistente personale per la gestione dei programmi di allenamento</p>
      <div className="cta-buttons">
        <Link to="/register" className="cta-button primary">Inizia Ora</Link>
        <Link to="/login" className="cta-button secondary">Accedi</Link>
      </div>
    </div>
  );
}

export default Home; 