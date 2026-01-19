import { Link } from 'react-router-dom';
import { Heart, Mail, GitHub, Linkedin } from 'react-feather';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer style={{
            background: 'var(--bg-secondary)',
            borderTop: '1px solid var(--bg-tertiary)',
            padding: 'var(--space-2xl) 0',
            marginTop: 'auto',
        }}>
            <div className="container">
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: 'var(--space-xl)',
                    marginBottom: 'var(--space-xl)',
                }}>
                    {/* Brand */}
                    <div>
                        <h3 style={{
                            background: 'var(--accent-gradient)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            marginBottom: 'var(--space-md)',
                        }}>
                            MindMate
                        </h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Your AI-powered mental health companion. Get support anytime, anywhere.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-md)', color: 'var(--text-primary)' }}>
                            Quick Links
                        </h4>
                        <nav style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                            <Link to="/assessment" style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Assessment</Link>
                            <Link to="/booking" style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Book a Session</Link>
                            <Link to="/dashboard" style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Dashboard</Link>
                        </nav>
                    </div>

                    {/* Resources */}
                    <div>
                        <h4 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-md)', color: 'var(--text-primary)' }}>
                            Resources
                        </h4>
                        <nav style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                            <a href="#" style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Privacy Policy</a>
                            <a href="#" style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Terms of Service</a>
                            <a href="#" style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>FAQ</a>
                        </nav>
                    </div>

                    {/* Contact */}
                    <div>
                        <h4 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-md)', color: 'var(--text-primary)' }}>
                            Contact
                        </h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                            <a href="mailto:support@mindmate.ai" style={{
                                fontSize: '0.875rem',
                                color: 'var(--text-muted)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--space-sm)',
                            }}>
                                <Mail size={14} />
                                support@mindmate.ai
                            </a>
                        </div>
                        <div style={{ display: 'flex', gap: 'var(--space-md)', marginTop: 'var(--space-md)' }}>
                            <a href="#" style={{ color: 'var(--text-muted)' }}><GitHub size={18} /></a>
                            <a href="#" style={{ color: 'var(--text-muted)' }}><Linkedin size={18} /></a>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div style={{
                    borderTop: '1px solid var(--bg-tertiary)',
                    paddingTop: 'var(--space-lg)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: 'var(--space-md)',
                }}>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        © {currentYear} MindMate. All rights reserved.
                    </p>
                    <p style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--space-xs)',
                    }}>
                        Made with <Heart size={12} style={{ color: 'var(--danger)' }} /> for mental wellness
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
