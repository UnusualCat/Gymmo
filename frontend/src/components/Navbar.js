import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <Link to="/">Gymmo</Link>
            </div>
            <div className="navbar-menu">
                {token ? (
                    <>
                        <Link to="/dashboard">Dashboard</Link>
                        <Link to="/programs">Programmi</Link>
                        <Link to="/admin">Admin</Link>
                        <button onClick={handleLogout} className="logout-button">
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/login">Login</Link>
                        <Link to="/register">Registrati</Link>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar; 