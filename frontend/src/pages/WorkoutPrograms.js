import React, { useState, useEffect } from 'react';
import './WorkoutPrograms.css';

function WorkoutPrograms() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          window.location.href = '/login';
          return;
        }

        const response = await fetch('http://localhost:8000/api/workout-programs', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setPrograms(data);
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
            setError('Errore nel recupero dei programmi');
          }
        }
      } catch (error) {
        console.error('Errore nel recupero dei programmi:', error);
        setError('Si è verificato un errore durante il recupero dei programmi');
      } finally {
        setLoading(false);
      }
    };

    fetchPrograms();
  }, []);

  if (loading) {
    return <div className="loading">Caricamento...</div>;
  }

  return (
    <div className="workout-programs">
      <h1>Programmi di Allenamento</h1>
      {error && <div className="error-message">{error}</div>}
      <div className="programs-grid">
        {programs.map(program => (
          <div key={program.id} className="program-card">
            <h3>{program.name}</h3>
            <p>{program.description}</p>
            <div className="program-details">
              <span>Durata: {program.duration} settimane</span>
              <span>Livello: {program.level}</span>
            </div>
            <button onClick={() => window.location.href = `/workout-programs/${program.id}`}>
              Visualizza Dettagli
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default WorkoutPrograms; 