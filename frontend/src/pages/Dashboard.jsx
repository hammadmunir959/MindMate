import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { MessageCircle, Calendar, Activity, ArrowRight, Clock, CheckCircle } from 'react-feather';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import { useAuthStore } from '../stores/authStore';

const Dashboard = () => {
    const { user } = useAuthStore();

    const quickActions = [
        {
            icon: <MessageCircle size={24} />,
            title: 'Start Assessment',
            description: 'Talk to our AI therapist',
            link: '/assessment',
            color: 'var(--accent-primary)',
        },
        {
            icon: <Calendar size={24} />,
            title: 'Book Session',
            description: 'Schedule with a specialist',
            link: '/booking',
            color: 'var(--accent-secondary)',
        },
    ];

    const recentActivity = [
        { type: 'session', title: 'Completed assessment session', time: '2 hours ago' },
        { type: 'booking', title: 'Booked appointment with Dr. Sarah', time: 'Yesterday' },
    ];

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Header />

            <div className="container" style={{ flex: 1, padding: 'var(--space-xl) var(--space-lg)' }}>
                {/* Welcome Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{ marginBottom: 'var(--space-2xl)' }}
                >
                    <h1 style={{ marginBottom: 'var(--space-sm)' }}>
                        Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}
                    </h1>
                    <p>How are you feeling today?</p>
                </motion.div>

                {/* Quick Actions */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                    gap: 'var(--space-lg)',
                    marginBottom: 'var(--space-2xl)',
                }}>
                    {quickActions.map((action, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <Link to={action.link} style={{ textDecoration: 'none' }}>
                                <motion.div
                                    whileHover={{ scale: 1.02, y: -4 }}
                                    whileTap={{ scale: 0.98 }}
                                    className="card"
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 'var(--space-lg)',
                                        cursor: 'pointer',
                                        background: `linear-gradient(135deg, var(--bg-secondary) 0%, ${action.color}15 100%)`,
                                        border: `1px solid ${action.color}30`,
                                    }}
                                >
                                    <div style={{
                                        width: '56px',
                                        height: '56px',
                                        borderRadius: 'var(--radius-xl)',
                                        background: action.color,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        color: 'white',
                                    }}>
                                        {action.icon}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <h4 style={{ marginBottom: '4px', color: 'var(--text-primary)' }}>{action.title}</h4>
                                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{action.description}</p>
                                    </div>
                                    <ArrowRight size={20} style={{ color: 'var(--text-muted)' }} />
                                </motion.div>
                            </Link>
                        </motion.div>
                    ))}
                </div>

                {/* Stats */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    style={{ marginBottom: 'var(--space-2xl)' }}
                >
                    <h3 style={{ marginBottom: 'var(--space-lg)' }}>Your Progress</h3>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                        gap: 'var(--space-md)',
                    }}>
                        {[
                            { label: 'Sessions', value: '3', icon: <MessageCircle size={18} /> },
                            { label: 'Appointments', value: '1', icon: <Calendar size={18} /> },
                            { label: 'Days Active', value: '12', icon: <Activity size={18} /> },
                        ].map((stat, i) => (
                            <div key={i} className="card" style={{
                                textAlign: 'center',
                                padding: 'var(--space-lg)',
                            }}>
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    borderRadius: 'var(--radius-lg)',
                                    background: 'var(--bg-tertiary)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    margin: '0 auto var(--space-md)',
                                    color: 'var(--accent-primary)',
                                }}>
                                    {stat.icon}
                                </div>
                                <h2 style={{ marginBottom: '4px' }}>{stat.value}</h2>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{stat.label}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Recent Activity */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <h3 style={{ marginBottom: 'var(--space-lg)' }}>Recent Activity</h3>
                    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                        {recentActivity.map((item, i) => (
                            <div key={i} style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--space-md)',
                                padding: 'var(--space-md) var(--space-lg)',
                                borderBottom: i < recentActivity.length - 1 ? '1px solid var(--bg-tertiary)' : 'none',
                            }}>
                                <div style={{
                                    width: '32px',
                                    height: '32px',
                                    borderRadius: 'var(--radius-full)',
                                    background: 'var(--bg-tertiary)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                }}>
                                    <CheckCircle size={14} style={{ color: 'var(--success)' }} />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>{item.title}</p>
                                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <Clock size={10} />
                                        {item.time}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>

            <Footer />
        </div>
    );
};

export default Dashboard;
