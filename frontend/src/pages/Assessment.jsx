import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, AlertTriangle, Loader, MessageSquare, User } from 'react-feather';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import apiClient from '../api/client';

const Assessment = () => {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Start session on mount
    useEffect(() => {
        startSession();
    }, []);

    const startSession = async () => {
        setIsLoading(true);
        try {
            const response = await apiClient.post('/v2/assessment/start', {
                patient_id: 'current-user', // Will be replaced with actual user ID
            });
            setSessionId(response.data.session_id);
            setMessages([{
                role: 'assistant',
                content: response.data.response,
                phase: response.data.phase,
            }]);
        } catch (err) {
            setError('Failed to start session. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || isLoading || !sessionId) return;

        const userMessage = { role: 'user', content: input.trim() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await apiClient.post('/v2/assessment/message', {
                session_id: sessionId,
                patient_id: 'current-user',
                message: input.trim(),
            });

            const botMessage = {
                role: 'assistant',
                content: response.data.response,
                phase: response.data.phase,
                isSafety: response.data.phase === 'safety',
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Header />

            <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                maxWidth: '800px',
                width: '100%',
                margin: '0 auto',
                padding: 'var(--space-lg)',
            }}>
                {/* Chat Header */}
                <div style={{
                    padding: 'var(--space-lg)',
                    background: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius-2xl) var(--radius-2xl) 0 0',
                    borderBottom: '1px solid var(--bg-tertiary)',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                        <div style={{
                            width: '48px',
                            height: '48px',
                            borderRadius: 'var(--radius-full)',
                            background: 'var(--accent-gradient)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}>
                            <MessageSquare size={24} color="white" />
                        </div>
                        <div>
                            <h3 style={{ marginBottom: '2px' }}>MindMate Therapist</h3>
                            <p style={{ fontSize: '0.75rem', color: 'var(--success)' }}>Online</p>
                        </div>
                    </div>
                </div>

                {/* Messages */}
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: 'var(--space-lg)',
                    background: 'var(--bg-primary)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--space-md)',
                }}>
                    <AnimatePresence initial={false}>
                        {messages.map((msg, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                style={{
                                    display: 'flex',
                                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                }}
                            >
                                <div style={{
                                    maxWidth: '75%',
                                    padding: 'var(--space-md)',
                                    borderRadius: 'var(--radius-xl)',
                                    background: msg.role === 'user'
                                        ? 'var(--accent-primary)'
                                        : msg.isSafety
                                            ? 'rgba(239, 68, 68, 0.2)'
                                            : 'var(--bg-secondary)',
                                    border: msg.isSafety ? '1px solid var(--danger)' : 'none',
                                    borderBottomRightRadius: msg.role === 'user' ? '4px' : 'var(--radius-xl)',
                                    borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : 'var(--radius-xl)',
                                }}>
                                    {msg.isSafety && (
                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '4px',
                                            marginBottom: 'var(--space-sm)',
                                            color: 'var(--danger)',
                                            fontSize: '0.75rem',
                                            fontWeight: 600,
                                        }}>
                                            <AlertTriangle size={12} />
                                            Safety Response
                                        </div>
                                    )}
                                    <p style={{
                                        fontSize: '0.875rem',
                                        lineHeight: 1.6,
                                        color: msg.role === 'user' ? 'white' : 'var(--text-primary)',
                                        whiteSpace: 'pre-wrap',
                                    }}>
                                        {msg.content}
                                    </p>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            style={{ display: 'flex' }}
                        >
                            <div style={{
                                padding: 'var(--space-md)',
                                background: 'var(--bg-secondary)',
                                borderRadius: 'var(--radius-xl)',
                            }}>
                                <Loader size={18} className="animate-spin" style={{ color: 'var(--accent-primary)' }} />
                            </div>
                        </motion.div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Error */}
                {error && (
                    <div style={{
                        padding: 'var(--space-md)',
                        background: 'rgba(239, 68, 68, 0.1)',
                        borderLeft: '3px solid var(--danger)',
                        color: 'var(--danger)',
                        fontSize: '0.875rem',
                    }}>
                        {error}
                    </div>
                )}

                {/* Input */}
                <div style={{
                    padding: 'var(--space-lg)',
                    background: 'var(--bg-secondary)',
                    borderRadius: '0 0 var(--radius-2xl) var(--radius-2xl)',
                    borderTop: '1px solid var(--bg-tertiary)',
                }}>
                    <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Share what's on your mind..."
                            rows={1}
                            className="input"
                            style={{
                                flex: 1,
                                resize: 'none',
                                minHeight: '44px',
                            }}
                            disabled={isLoading}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={isLoading || !input.trim()}
                            className="btn btn-primary"
                            style={{ padding: 'var(--space-sm) var(--space-md)' }}
                        >
                            <Send size={18} />
                        </button>
                    </div>
                    <p style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        marginTop: 'var(--space-sm)',
                        textAlign: 'center',
                    }}>
                        Your conversation is confidential and encrypted
                    </p>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default Assessment;
