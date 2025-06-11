import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

const Login = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        try {
            const response = await axios.post('http://localhost:8000/api/auth/login', {
                email: formData.email,
                password: formData.password
            });
            localStorage.setItem('token', response.data.access_token);
            navigate('/dashboard');
        } catch (err) {
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else if (typeof err.response?.data === 'object') {
                // Handle validation errors
                const errorMessages = Object.entries(err.response.data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(', ');
                setError(errorMessages);
            } else {
                setError('Errore durante il login');
            }
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Login</h2>
                {error && <div className="error-message">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email:</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password:</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    <button type="submit">Accedi</button>
                </form>
                <p className="register-link">
                    Non hai un account? <a href="/register">Registrati</a>
                </p>
            </div>
        </div>
    );
};

export default Login; 