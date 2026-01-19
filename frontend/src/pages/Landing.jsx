import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MessageCircle, Shield, Clock, Users, ArrowRight } from 'react-feather';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';

const Landing = () => {
    const features = [
        {
            icon: <MessageCircle size={24} />,
            title: 'AI Therapist',
            description: 'Have meaningful conversations with our AI-powered therapist, available 24/7.',
        },
        {
            icon: <Shield size={24} />,
            title: 'Private & Secure',
            description: 'Your conversations are encrypted and completely confidential.',
        },
        {
            icon: <Clock size={24} />,
            title: 'Always Available',
            description: 'Get support whenever you need it, day or night.',
        },
        {
            icon: <Users size={24} />,
            title: 'Expert Matching',
            description: 'Connect with licensed specialists tailored to your needs.',
        },
    ];

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Header />

            {/* Hero Section */}
            <section style={{
                padding: 'var(--space-2xl) 0',
                background: `radial-gradient(ellipse at top, rgba(99, 102, 241, 0.15), transparent 70%)`,
                minHeight: '80vh',
                display: 'flex',
                alignItems: 'center',
            }}>
                <div className="container" style={{ textAlign: 'center' }}>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <span style={{
                            display: 'inline-block',
                            padding: 'var(--space-xs) var(--space-md)',
                            background: 'var(--bg-tertiary)',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '0.75rem',
                            color: 'var(--accent-primary)',
                            marginBottom: 'var(--space-lg)',
                        }}>
                            Powered by Advanced AI
                        </span>

                        <h1 style={{
                            fontSize: 'clamp(2.5rem, 5vw, 4rem)',
                            maxWidth: '800px',
                            margin: '0 auto var(--space-lg)',
                            lineHeight: 1.1,
                        }}>
                            Your Mental Health,{' '}
                            <span style={{
                                background: 'var(--accent-gradient)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                            }}>
                                Reimagined
                            </span>
                        </h1>

                        <p style={{
                            fontSize: '1.125rem',
                            maxWidth: '600px',
                            margin: '0 auto var(--space-xl)',
                            color: 'var(--text-secondary)',
                        }}>
                            MindMate combines AI-powered therapy with expert specialist matching to provide personalized mental health support that fits your life.
                        </p>

                        <div style={{ display: 'flex', gap: 'var(--space-md)', justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Link to="/signup" className="btn btn-primary btn-lg">
                                Start Your Journey
                                <ArrowRight size={18} />
                            </Link>
                            <Link to="/login" className="btn btn-secondary btn-lg">
                                Sign In
                            </Link>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Features Section */}
            <section style={{
                padding: 'var(--space-2xl) 0',
                background: 'var(--bg-secondary)',
            }}>
                <div className="container">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        style={{ textAlign: 'center', marginBottom: 'var(--space-2xl)' }}
                    >
                        <h2 style={{ marginBottom: 'var(--space-md)' }}>Why MindMate?</h2>
                        <p style={{ maxWidth: '500px', margin: '0 auto' }}>
                            We combine cutting-edge AI with human expertise to provide comprehensive mental health support.
                        </p>
                    </motion.div>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: 'var(--space-lg)',
                    }}>
                        {features.map((feature, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.4, delay: index * 0.1 }}
                                className="card card-glass"
                                style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    textAlign: 'center',
                                    padding: 'var(--space-xl)',
                                }}
                            >
                                <div style={{
                                    width: '56px',
                                    height: '56px',
                                    borderRadius: 'var(--radius-xl)',
                                    background: 'var(--accent-gradient)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    marginBottom: 'var(--space-md)',
                                    color: 'white',
                                }}>
                                    {feature.icon}
                                </div>
                                <h4 style={{ marginBottom: 'var(--space-sm)' }}>{feature.title}</h4>
                                <p style={{ fontSize: '0.875rem' }}>{feature.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section style={{
                padding: 'var(--space-2xl) 0',
                background: `linear-gradient(135deg, var(--bg-primary) 0%, #1a1a2e 100%)`,
            }}>
                <div className="container" style={{ textAlign: 'center' }}>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                    >
                        <h2 style={{ marginBottom: 'var(--space-md)' }}>
                            Ready to Start Your Journey?
                        </h2>
                        <p style={{ maxWidth: '500px', margin: '0 auto var(--space-lg)' }}>
                            Take the first step towards better mental health today.
                        </p>
                        <Link to="/signup" className="btn btn-primary btn-lg">
                            Get Started Free
                            <ArrowRight size={18} />
                        </Link>
                    </motion.div>
                </div>
            </section>

            <Footer />
        </div>
    );
};

export default Landing;
