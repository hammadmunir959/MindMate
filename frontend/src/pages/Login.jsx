import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, Eye, EyeOff, AlertCircle, Loader } from 'react-feather';
import { useAuthStore } from '../stores/authStore';
import Header from '../components/layout/Header';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');

    const { login, isLoading } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!email || !password) {
            setError('Please fill in all fields');
            return;
        }

        try {
            await login({ email, password });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed. Please try again.');
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Header />

            <div style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 'var(--space-xl)',
                background: `radial-gradient(ellipse at top, rgba(99, 102, 241, 0.1), transparent 70%)`,
            }}>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="card"
                    style={{
                        width: '100%',
                        maxWidth: '400px',
                        padding: 'var(--space-xl)',
                    }}
                >
                    <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
                        <h2 style={{ marginBottom: 'var(--space-sm)' }}>Welcome Back</h2>
                        <p style={{ fontSize: '0.875rem' }}>Sign in to continue your journey</p>
                    </div>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--space-sm)',
                                padding: 'var(--space-md)',
                                background: 'rgba(239, 68, 68, 0.1)',
                                border: '1px solid var(--danger)',
                                borderRadius: 'var(--radius-lg)',
                                marginBottom: 'var(--space-lg)',
                                color: 'var(--danger)',
                                fontSize: '0.875rem',
                            }}
                        >
                            <AlertCircle size={16} />
                            {error}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: 'var(--space-lg)' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '0.875rem',
                                marginBottom: 'var(--space-sm)',
                                color: 'var(--text-secondary)',
                            }}>
                                Email
                            </label>
                            <div style={{ position: 'relative' }}>
                                <Mail size={18} style={{
                                    position: 'absolute',
                                    left: '12px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    color: 'var(--text-muted)',
                                }} />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="you@example.com"
                                    className="input"
                                    style={{ paddingLeft: '40px' }}
                                />
                            </div>
                        </div>

                        <div style={{ marginBottom: 'var(--space-lg)' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '0.875rem',
                                marginBottom: 'var(--space-sm)',
                                color: 'var(--text-secondary)',
                            }}>
                                Password
                            </label>
                            <div style={{ position: 'relative' }}>
                                <Lock size={18} style={{
                                    position: 'absolute',
                                    left: '12px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    color: 'var(--text-muted)',
                                }} />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="input"
                                    style={{ paddingLeft: '40px', paddingRight: '40px' }}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    style={{
                                        position: 'absolute',
                                        right: '12px',
                                        top: '50%',
                                        transform: 'translateY(-50%)',
                                        background: 'none',
                                        border: 'none',
                                        color: 'var(--text-muted)',
                                        cursor: 'pointer',
                                    }}
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="btn btn-primary"
                            style={{ width: '100%', marginBottom: 'var(--space-lg)' }}
                        >
                            {isLoading ? (
                                <Loader size={18} className="animate-spin" />
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    <p style={{ textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                        Don't have an account?{' '}
                        <Link to="/signup" style={{ color: 'var(--accent-primary)' }}>Sign up</Link>
                    </p>
                </motion.div>
            </div>
        </div>
    );
};

export default Login;
