import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, User, Eye, EyeOff, AlertCircle, Loader, CheckCircle } from 'react-feather';
import { useAuthStore } from '../stores/authStore';
import Header from '../components/layout/Header';

const Signup = () => {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: '',
        userType: 'patient',
    });
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');

    const { signup, isLoading } = useAuthStore();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const validatePassword = (pwd) => {
        const checks = {
            length: pwd.length >= 8,
            lowercase: /[a-z]/.test(pwd),
            number: /\d/.test(pwd),
        };
        return checks;
    };

    const passwordChecks = validatePassword(formData.password);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!formData.firstName || !formData.lastName || !formData.email || !formData.password) {
            setError('Please fill in all fields');
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (!Object.values(passwordChecks).every(Boolean)) {
            setError('Password does not meet requirements');
            return;
        }

        try {
            await signup({
                first_name: formData.firstName,
                last_name: formData.lastName,
                email: formData.email,
                password: formData.password,
                user_type: formData.userType,
            });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Signup failed. Please try again.');
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
                background: `radial-gradient(ellipse at top, rgba(139, 92, 246, 0.1), transparent 70%)`,
            }}>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="card"
                    style={{
                        width: '100%',
                        maxWidth: '450px',
                        padding: 'var(--space-xl)',
                    }}
                >
                    <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
                        <h2 style={{ marginBottom: 'var(--space-sm)' }}>Create Account</h2>
                        <p style={{ fontSize: '0.875rem' }}>Start your mental wellness journey today</p>
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
                        {/* Name Fields */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)', marginBottom: 'var(--space-lg)' }}>
                            <div>
                                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>
                                    First Name
                                </label>
                                <div style={{ position: 'relative' }}>
                                    <User size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                                    <input
                                        type="text"
                                        name="firstName"
                                        value={formData.firstName}
                                        onChange={handleChange}
                                        placeholder="John"
                                        className="input"
                                        style={{ paddingLeft: '40px' }}
                                    />
                                </div>
                            </div>
                            <div>
                                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>
                                    Last Name
                                </label>
                                <input
                                    type="text"
                                    name="lastName"
                                    value={formData.lastName}
                                    onChange={handleChange}
                                    placeholder="Doe"
                                    className="input"
                                />
                            </div>
                        </div>

                        {/* Email */}
                        <div style={{ marginBottom: 'var(--space-lg)' }}>
                            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>
                                Email
                            </label>
                            <div style={{ position: 'relative' }}>
                                <Mail size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    placeholder="you@example.com"
                                    className="input"
                                    style={{ paddingLeft: '40px' }}
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div style={{ marginBottom: 'var(--space-md)' }}>
                            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>
                                Password
                            </label>
                            <div style={{ position: 'relative' }}>
                                <Lock size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    className="input"
                                    style={{ paddingLeft: '40px', paddingRight: '40px' }}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>

                        {/* Password Requirements */}
                        <div style={{ marginBottom: 'var(--space-lg)', fontSize: '0.75rem' }}>
                            {[
                                { check: passwordChecks.length, label: '8+ characters' },
                                { check: passwordChecks.lowercase, label: 'Lowercase letter' },
                                { check: passwordChecks.number, label: 'Number' },
                            ].map((item, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px', color: item.check ? 'var(--success)' : 'var(--text-muted)' }}>
                                    <CheckCircle size={12} />
                                    {item.label}
                                </div>
                            ))}
                        </div>

                        {/* Confirm Password */}
                        <div style={{ marginBottom: 'var(--space-lg)' }}>
                            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>
                                Confirm Password
                            </label>
                            <input
                                type="password"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="••••••••"
                                className="input"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="btn btn-primary"
                            style={{ width: '100%', marginBottom: 'var(--space-lg)' }}
                        >
                            {isLoading ? <Loader size={18} className="animate-spin" /> : 'Create Account'}
                        </button>
                    </form>

                    <p style={{ textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                        Already have an account?{' '}
                        <Link to="/login" style={{ color: 'var(--accent-primary)' }}>Sign in</Link>
                    </p>
                </motion.div>
            </div>
        </div>
    );
};

export default Signup;
