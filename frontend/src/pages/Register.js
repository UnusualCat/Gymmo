import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Register.css';

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError('Le password non coincidono');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/api/auth/register', {
        email: formData.email,
        password: formData.password,
        name: formData.name
      });

      if (response.status === 200) {
        navigate('/login');
      }
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (typeof err.response?.data === 'object') {
        const errorMessages = Object.entries(err.response.data)
          .map(([key, value]) => `${key}: ${value}`)
          .join(', ');
        setError(errorMessages);
      } else {
        setError('Errore durante la registrazione');
      }
    }
  };

  return (
    <div className="register-container">
      <form onSubmit={handleSubmit} className="register-form">
        <h2>Registrati</h2>
        {error && <div className="error-message">{error}</div>}
        <div className="form-group">
          <label htmlFor="name">Nome</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
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
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="confirmPassword">Conferma Password</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit" className="register-button">Registrati</button>
      </form>
    </div>
  );
}

export default Register; 