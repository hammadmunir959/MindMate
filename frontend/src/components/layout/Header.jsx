import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Menu, X, User, LogOut, Calendar, MessageCircle } from 'react-feather';
import { useAuthStore } from '../../stores/authStore';

const Header = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const { isAuthenticated, user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <header style={{
            position: 'sticky',
            top: 0,
            zIndex: 50,
            background: 'var(--bg-glass)',
            backdropFilter: 'blur(16px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}>
            <div className="container" style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                height: '64px',
            }}>
                {/* Logo */}
                <Link to="/" style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-sm)',
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    color: 'var(--text-primary)',
                }}>
                    <span style={{
                        background: 'var(--accent-gradient)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                    }}>
                        MindMate
                    </span>
                </Link>

                {/* Desktop Navigation */}
                <nav style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-lg)',
                }} className="desktop-nav">
                    {isAuthenticated ? (
                        <>
                            <Link to="/dashboard" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                Dashboard
                            </Link>
                            <Link to="/assessment" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                <MessageCircle size={16} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                                Assessment
                            </Link>
                            <Link to="/booking" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                <Calendar size={16} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                                Book Session
                            </Link>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--space-md)',
                                marginLeft: 'var(--space-md)',
                                paddingLeft: 'var(--space-md)',
                                borderLeft: '1px solid var(--bg-tertiary)',
                            }}>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    {user?.email}
                                </span>
                                <button
                                    onClick={handleLogout}
                                    className="btn btn-ghost btn-sm"
                                    style={{ gap: '4px' }}
                                >
                                    <LogOut size={14} />
                                    Logout
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <Link to="/login" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                Login
                            </Link>
                            <Link to="/signup" className="btn btn-primary btn-sm">
                                Get Started
                            </Link>
                        </>
                    )}
                </nav>

                {/* Mobile Menu Button */}
                <button
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                    style={{
                        display: 'none',
                        padding: 'var(--space-sm)',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-primary)',
                        cursor: 'pointer',
                    }}
                    className="mobile-menu-btn"
                >
                    {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
                <div style={{
                    position: 'absolute',
                    top: '64px',
                    left: 0,
                    right: 0,
                    background: 'var(--bg-secondary)',
                    padding: 'var(--space-lg)',
                    borderBottom: '1px solid var(--bg-tertiary)',
                }}>
                    {isAuthenticated ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                            <Link to="/dashboard" onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
                            <Link to="/assessment" onClick={() => setIsMenuOpen(false)}>Assessment</Link>
                            <Link to="/booking" onClick={() => setIsMenuOpen(false)}>Book Session</Link>
                            <button onClick={handleLogout} className="btn btn-ghost">Logout</button>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                            <Link to="/login" onClick={() => setIsMenuOpen(false)}>Login</Link>
                            <Link to="/signup" onClick={() => setIsMenuOpen(false)} className="btn btn-primary">Get Started</Link>
                        </div>
                    )}
                </div>
            )}

            <style>{`
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          .mobile-menu-btn { display: block !important; }
        }
      `}</style>
        </header>
    );
};

export default Header;
