import React, { useState, useEffect } from 'react';
import './Dashboard.css';

function Dashboard() {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          window.location.href = '/login';
          return;
        }

        const response = await fetch('http://localhost:8000/api/users/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setUserData(data);
        } else {
          const errorData = await response.json();
          if (errorData.detail) {
            setError(errorData.detail);
          } else if (typeof errorData === 'object') {
            const errorMessages = Object.entries(errorData)
              .map(([key, value]) => `${key}: ${value}`)
              .join(', ');
            setError(errorMessages);
          } else {
            setError('Errore nel recupero dei dati utente');
          }
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
      } catch (error) {
        console.error('Errore nel recupero dei dati utente:', error);
        setError('Si è verificato un errore durante il recupero dei dati utente');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  if (loading) {
    return <div className="loading">Caricamento...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      {error && <div className="error-message">{error}</div>}
      {userData && (
        <div className="user-info">
          <h2>Benvenuto, {userData.name}!</h2>
          <p>Email: {userData.email}</p>
        </div>
      )}
      <div className="dashboard-content">
        <div className="dashboard-card">
          <h3>I tuoi programmi</h3>
          <p>Visualizza e gestisci i tuoi programmi di allenamento</p>
          <button onClick={() => window.location.href = '/workout-programs'}>
            Vai ai programmi
          </button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 