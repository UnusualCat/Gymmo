import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Admin.css';

const Admin = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [programs, setPrograms] = useState({ drive_files: [], database_programs: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [newProgram, setNewProgram] = useState({ name: '', google_drive_file_id: '' });

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        fetchData();
    }, [navigate]);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            const [usersRes, programsRes] = await Promise.all([
                axios.get('http://localhost:8000/api/admin/users', { headers }),
                axios.get('http://localhost:8000/api/admin/programs', { headers })
            ]);

            setUsers(usersRes.data);
            setPrograms(programsRes.data);
            setLoading(false);
        } catch (err) {
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else if (typeof err.response?.data === 'object') {
                const errorMessages = Object.entries(err.response.data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(', ');
                setError(errorMessages);
            } else {
                setError('Errore nel caricamento dei dati');
            }
            setLoading(false);
        }
    };

    const handleCreateProgram = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const token = localStorage.getItem('token');
            await axios.post('http://localhost:8000/api/admin/programs', newProgram, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setNewProgram({ name: '', google_drive_file_id: '' });
            fetchData();
        } catch (err) {
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else if (typeof err.response?.data === 'object') {
                const errorMessages = Object.entries(err.response.data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(', ');
                setError(errorMessages);
            } else {
                setError('Errore nella creazione del programma');
            }
        }
    };

    const handleAssignProgram = async (userId, programId) => {
        setError('');
        try {
            const token = localStorage.getItem('token');
            await axios.post(`http://localhost:8000/api/admin/users/${userId}/programs/${programId}`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchData();
        } catch (err) {
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else if (typeof err.response?.data === 'object') {
                const errorMessages = Object.entries(err.response.data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(', ');
                setError(errorMessages);
            } else {
                setError('Errore nell\'assegnazione del programma');
            }
        }
    };

    const handleRemoveProgram = async (userId, programId) => {
        setError('');
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://localhost:8000/api/admin/users/${userId}/programs/${programId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchData();
        } catch (err) {
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else if (typeof err.response?.data === 'object') {
                const errorMessages = Object.entries(err.response.data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(', ');
                setError(errorMessages);
            } else {
                setError('Errore nella rimozione del programma');
            }
        }
    };

    if (loading) return <div className="loading">Caricamento...</div>;

    return (
        <div className="admin-container">
            <h1>Pannello Amministratore</h1>
            {error && <div className="error-message">{error}</div>}
            
            <section className="create-program">
                <h2>Crea Nuovo Programma</h2>
                <form onSubmit={handleCreateProgram}>
                    <div className="form-group">
                        <label htmlFor="name">Nome Programma:</label>
                        <input
                            type="text"
                            id="name"
                            value={newProgram.name}
                            onChange={(e) => setNewProgram({ ...newProgram, name: e.target.value })}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="google_drive_file_id">ID File Google Drive:</label>
                        <input
                            type="text"
                            id="google_drive_file_id"
                            value={newProgram.google_drive_file_id}
                            onChange={(e) => setNewProgram({ ...newProgram, google_drive_file_id: e.target.value })}
                            required
                        />
                    </div>
                    <button type="submit">Crea Programma</button>
                </form>
            </section>

            <section className="users-section">
                <h2>Utenti</h2>
                <div className="users-grid">
                    {users.map(user => (
                        <div key={user.id} className="user-card">
                            <h3>{user.name}</h3>
                            <p>Email: {user.email}</p>
                            <div className="user-programs">
                                <h4>Programmi Assegnati:</h4>
                                <ul>
                                    {user.programs?.map(program => (
                                        <li key={program.id}>
                                            {program.name}
                                            <button onClick={() => handleRemoveProgram(user.id, program.id)}>
                                                Rimuovi
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                                <div className="assign-program">
                                    <select
                                        onChange={(e) => {
                                            if (e.target.value) {
                                                handleAssignProgram(user.id, e.target.value);
                                            }
                                        }}
                                    >
                                        <option value="">Assegna programma...</option>
                                        {programs.database_programs
                                            .filter(program => !user.programs?.some(p => p.id === program.id))
                                            .map(program => (
                                                <option key={program.id} value={program.id}>
                                                    {program.name}
                                                </option>
                                            ))}
                                    </select>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default Admin; 