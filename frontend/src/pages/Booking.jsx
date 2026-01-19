import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, DollarSign, User, CheckCircle, Loader, ArrowLeft } from 'react-feather';
import { Link } from 'react-router-dom';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import apiClient from '../api/client';

const Booking = () => {
    const [specialists, setSpecialists] = useState([]);
    const [selectedSpecialist, setSelectedSpecialist] = useState(null);
    const [slots, setSlots] = useState([]);
    const [selectedSlot, setSelectedSlot] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isBooking, setIsBooking] = useState(false);
    const [step, setStep] = useState(1); // 1: Select Specialist, 2: Select Slot, 3: Confirm

    useEffect(() => {
        fetchSpecialists();
    }, []);

    const fetchSpecialists = async () => {
        setIsLoading(true);
        try {
            // Mock data for now - will connect to real API
            setSpecialists([
                { id: '1', name: 'Dr. Sarah Ahmed', specialty: 'Clinical Psychologist', fee: 3500, rating: 4.8 },
                { id: '2', name: 'Dr. Ali Hassan', specialty: 'Psychiatrist', fee: 5000, rating: 4.9 },
                { id: '3', name: 'Dr. Fatima Khan', specialty: 'Counselor', fee: 2500, rating: 4.7 },
            ]);
        } catch (err) {
            console.error('Failed to fetch specialists');
        } finally {
            setIsLoading(false);
        }
    };

    const fetchSlots = async (specialistId) => {
        setIsLoading(true);
        try {
            const response = await apiClient.get(`/v1/appointments/slots/${specialistId}`);
            setSlots(response.data.slots || generateMockSlots());
        } catch (err) {
            // Use mock slots on error
            setSlots(generateMockSlots());
        } finally {
            setIsLoading(false);
        }
    };

    const generateMockSlots = () => {
        const slots = [];
        const today = new Date();
        for (let d = 1; d <= 7; d++) {
            const date = new Date(today);
            date.setDate(today.getDate() + d);
            for (let h = 9; h <= 17; h += 2) {
                const start = new Date(date);
                start.setHours(h, 0, 0);
                const end = new Date(date);
                end.setHours(h + 1, 0, 0);
                slots.push({
                    id: `slot-${d}-${h}`,
                    start_time: start.toISOString(),
                    end_time: end.toISOString(),
                });
            }
        }
        return slots;
    };

    const handleSelectSpecialist = (specialist) => {
        setSelectedSpecialist(specialist);
        setStep(2);
        fetchSlots(specialist.id);
    };

    const handleSelectSlot = (slot) => {
        setSelectedSlot(slot);
        setStep(3);
    };

    const handleConfirmBooking = async () => {
        setIsBooking(true);
        try {
            await apiClient.post('/v1/appointments/book', {
                specialist_id: selectedSpecialist.id,
                start_time: selectedSlot.start_time,
                end_time: selectedSlot.end_time,
            });
            setStep(4); // Success
        } catch (err) {
            alert('Booking failed. Please try again.');
        } finally {
            setIsBooking(false);
        }
    };

    const formatDate = (iso) => new Date(iso).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    const formatTime = (iso) => new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    // Group slots by date
    const slotsByDate = slots.reduce((acc, slot) => {
        const date = formatDate(slot.start_time);
        if (!acc[date]) acc[date] = [];
        acc[date].push(slot);
        return acc;
    }, {});

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Header />

            <div className="container" style={{ flex: 1, padding: 'var(--space-xl) var(--space-lg)' }}>
                {/* Progress Steps */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    gap: 'var(--space-xl)',
                    marginBottom: 'var(--space-xl)',
                }}>
                    {['Select Specialist', 'Choose Time', 'Confirm'].map((label, i) => (
                        <div key={i} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--space-sm)',
                            color: step > i + 1 ? 'var(--success)' : step === i + 1 ? 'var(--accent-primary)' : 'var(--text-muted)',
                        }}>
                            <div style={{
                                width: '28px',
                                height: '28px',
                                borderRadius: 'var(--radius-full)',
                                background: step > i + 1 ? 'var(--success)' : step === i + 1 ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '0.75rem',
                                fontWeight: 600,
                                color: 'white',
                            }}>
                                {step > i + 1 ? <CheckCircle size={14} /> : i + 1}
                            </div>
                            <span style={{ fontSize: '0.875rem' }}>{label}</span>
                        </div>
                    ))}
                </div>

                {/* Step 1: Select Specialist */}
                {step === 1 && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>Choose Your Specialist</h2>
                        {isLoading ? (
                            <div style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
                                <Loader size={32} className="animate-spin" style={{ color: 'var(--accent-primary)' }} />
                            </div>
                        ) : (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-lg)' }}>
                                {specialists.map((spec) => (
                                    <motion.div
                                        key={spec.id}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => handleSelectSpecialist(spec)}
                                        className="card"
                                        style={{ cursor: 'pointer', transition: 'border-color 0.2s' }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', marginBottom: 'var(--space-md)' }}>
                                            <div style={{
                                                width: '56px',
                                                height: '56px',
                                                borderRadius: 'var(--radius-full)',
                                                background: 'var(--accent-gradient)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                            }}>
                                                <User size={24} color="white" />
                                            </div>
                                            <div>
                                                <h4 style={{ marginBottom: '2px' }}>{spec.name}</h4>
                                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{spec.specialty}</p>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                                            <span style={{ color: 'var(--success)' }}>PKR {spec.fee.toLocaleString()}</span>
                                            <span style={{ color: 'var(--warning)' }}>★ {spec.rating}</span>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </motion.div>
                )}

                {/* Step 2: Select Slot */}
                {step === 2 && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <button onClick={() => setStep(1)} className="btn btn-ghost btn-sm" style={{ marginBottom: 'var(--space-lg)' }}>
                            <ArrowLeft size={16} /> Back
                        </button>
                        <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>Select Time with {selectedSpecialist?.name}</h2>
                        {isLoading ? (
                            <div style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
                                <Loader size={32} className="animate-spin" style={{ color: 'var(--accent-primary)' }} />
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
                                {Object.entries(slotsByDate).map(([date, dateSlots]) => (
                                    <div key={date}>
                                        <h4 style={{ marginBottom: 'var(--space-md)', color: 'var(--text-secondary)' }}>{date}</h4>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-sm)' }}>
                                            {dateSlots.map((slot) => (
                                                <motion.button
                                                    key={slot.id}
                                                    whileHover={{ scale: 1.05 }}
                                                    whileTap={{ scale: 0.95 }}
                                                    onClick={() => handleSelectSlot(slot)}
                                                    className={`btn ${selectedSlot?.id === slot.id ? 'btn-primary' : 'btn-secondary'}`}
                                                    style={{ fontSize: '0.75rem' }}
                                                >
                                                    <Clock size={12} />
                                                    {formatTime(slot.start_time)}
                                                </motion.button>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </motion.div>
                )}

                {/* Step 3: Confirm */}
                {step === 3 && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ maxWidth: '500px', margin: '0 auto' }}>
                        <button onClick={() => setStep(2)} className="btn btn-ghost btn-sm" style={{ marginBottom: 'var(--space-lg)' }}>
                            <ArrowLeft size={16} /> Back
                        </button>
                        <div className="card" style={{ padding: 'var(--space-xl)' }}>
                            <h3 style={{ marginBottom: 'var(--space-lg)', textAlign: 'center' }}>Confirm Booking</h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', marginBottom: 'var(--space-xl)' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                    <User size={18} style={{ color: 'var(--accent-primary)' }} />
                                    <span>{selectedSpecialist?.name}</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                    <Calendar size={18} style={{ color: 'var(--accent-primary)' }} />
                                    <span>{formatDate(selectedSlot?.start_time)}</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                    <Clock size={18} style={{ color: 'var(--accent-primary)' }} />
                                    <span>{formatTime(selectedSlot?.start_time)}</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                    <DollarSign size={18} style={{ color: 'var(--success)' }} />
                                    <span>PKR {selectedSpecialist?.fee.toLocaleString()}</span>
                                </div>
                            </div>
                            <button
                                onClick={handleConfirmBooking}
                                disabled={isBooking}
                                className="btn btn-primary btn-lg"
                                style={{ width: '100%' }}
                            >
                                {isBooking ? <Loader size={18} className="animate-spin" /> : 'Confirm Booking'}
                            </button>
                        </div>
                    </motion.div>
                )}

                {/* Step 4: Success */}
                {step === 4 && (
                    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
                        <div style={{
                            width: '80px',
                            height: '80px',
                            borderRadius: 'var(--radius-full)',
                            background: 'var(--success)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto var(--space-lg)',
                        }}>
                            <CheckCircle size={40} color="white" />
                        </div>
                        <h2 style={{ marginBottom: 'var(--space-md)' }}>Booking Confirmed!</h2>
                        <p style={{ marginBottom: 'var(--space-xl)' }}>Your appointment has been scheduled successfully.</p>
                        <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
                    </motion.div>
                )}
            </div>

            <Footer />
        </div>
    );
};

export default Booking;
