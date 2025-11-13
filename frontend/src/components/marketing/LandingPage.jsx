import { Footer } from "../layout";
import React, { useState, useEffect, useRef } from "react";
import CountUp from 'react-countup';
import { AnimatePresence, motion, useScroll, useTransform } from "framer-motion";
import { Sun, Moon,Star, ArrowRight, ArrowUp, MessageCircle, BookOpen, HelpCircle, Users } from "react-feather";
import { useNavigate } from "react-router-dom";
import CookieConsent from "react-cookie-consent";
import LoadingBar from "react-top-loading-bar";
import Tilt from "react-parallax-tilt";

const LandingPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [hoveredItem, setHoveredItem] = useState(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [activeFAQ, setActiveFAQ] = useState(null);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const navigate = useNavigate();
  const { scrollYProgress } = useScroll();

  // Configure scroll progress indicator
  const scaleX = useTransform(scrollYProgress, [0, 1], [0, 1]);

  const navItems = [
    { name: "Home", id: "home" },
    { name: "Features", id: "features" },
    { name: "Testimonials", id: "testimonials" },
    { name: "Resources", id: "resources" },
    { name: "FAQ", id: "faq" },
    // { name: "About", id: "about" },
  ];

  // Animation variants
  const fadeUp = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8 } },
  };

  const fadeLeft = {
    hidden: { opacity: 0, x: -60 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.8 } },
  };

  const fadeRight = {
    hidden: { opacity: 0, x: 60 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.8 } },
  };

  const scaleIn = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.8 } },
  };

  const splitText = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.1,
        duration: 0.8,
      },
    }),
  };

  // Preload images and track loading progress
  useEffect(() => {
    const imageUrls = [
      "https://play-lh.googleusercontent.com/3hasRHyxrNRhLiwAfJTcNEyP1Pq8YMlwpm30ylANoIVVbrFiK_nqE_keJKpyhquOrw=w3840-h2160-rw",
      "https://play-lh.googleusercontent.com/3hasRHyxrNRhLiwAfJTcNEyP1Pq8YMlwpm30ylANoIVVbrFiK_nqE_keJKpyhquOrw=w3840-h2160-rw",
    ];

    let loadedCount = 0;
    const totalImages = imageUrls.length;

    const loadImage = (url) => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.src = url;
        img.onload = () => {
          loadedCount++;
          setLoadingProgress((loadedCount / totalImages) * 100);
          resolve();
        };
        img.onerror = reject;
      });
    };

    Promise.all(imageUrls.map((url) => loadImage(url)))
      .then(() => setImagesLoaded(true))
      .catch(() => setImagesLoaded(true));

    const handleScroll = () => {
      setShowScrollButton(window.scrollY > 300);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (imagesLoaded) {
      setLoadingProgress(100);
    }
  }, [imagesLoaded]);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const toggleFAQ = (index) => {
    setActiveFAQ(activeFAQ === index ? null : index);
  };

  // Sample data
  const testimonials = [
    {
      quote:
        "MindMate helped me manage my anxiety better than anything I've tried before.",
      author: "Sarah J.",
      role: "Teacher",
    },
    {
      quote:
        "The mood tracking feature gave me insights into patterns I never noticed.",
      author: "Michael T.",
      role: "Software Developer",
    },
    {
      quote:
        "Finally an app that makes mental health approachable and practical.",
      author: "Lisa M.",
      role: "Nurse",
    },
  ];

  const stats = [
    { value: "10,000+", label: "Active Users" },
    { value: "92%", label: "Report Improved Mood" },
    { value: "4.9", label: "App Rating" },
    { value: "24/7", label: "Support Available" },
  ];

  const faqs = [
    {
      question: "Is MindMate free to use?",
      answer:
        "Yes, our basic features are completely free. We offer premium features with additional benefits.",
    },
    {
      question: "How does MindMate protect my privacy?",
      answer:
        "We use end-to-end encryption and never share your data with third parties.",
    },
    {
      question: "Can I use MindMate without creating an account?",
      answer:
        "Some features are available without an account, but for full functionality we recommend signing up.",
    },
  ];

  const blogPosts = [
    {
      title: "5 Mindfulness Techniques for Beginners",
      excerpt:
        "Learn simple practices to reduce stress and improve focus in your daily life.",
      category: "Mindfulness",
    },
    {
      title: "Understanding Mood Patterns",
      excerpt:
        "How tracking your emotions can reveal important insights about your mental health.",
      category: "Mental Health",
    },
    {
      title: "Building Resilience Through Journaling",
      excerpt:
        "Discover the therapeutic benefits of regular journaling practice.",
      category: "Journaling",
    },
  ];

  // Enhanced CTA colors
  const ctaColors = {
    primary: darkMode
      ? "from-purple-500 to-pink-500"
      : "from-blue-600 to-purple-600",
    secondary: darkMode
      ? "from-gray-600 to-gray-700"
      : "from-gray-200 to-gray-300",
  };

  return (
    <div
      className={`min-h-screen transition-colors duration-300 ${
        darkMode ? "bg-gray-900 text-gray-100" : "bg-gray-50 text-gray-900"
      }`}
    >
      {/* Loading Bar */}
      <LoadingBar
        progress={loadingProgress}
        color={darkMode ? "#818cf8" : "#3b82f6"}
        height={4}
      />

      {/* Scroll Progress Indicator */}
      <motion.div
        className={`fixed top-0 left-0 right-0 h-1 z-50 ${
          darkMode ? "bg-purple-500" : "bg-blue-600"
        }`}
        style={{ scaleX, transformOrigin: "0%" }}
      />

      {/* Navigation Bar */}
      <nav
        className={`sticky top-0 z-40 ${
          darkMode ? "bg-gray-800" : "bg-white"
        } shadow-md py-4`}
      >
        <div className="container mx-auto px-6 flex justify-between items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent"
          >
            MindMate
          </motion.div>

          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <motion.div
                key={item.id}
                onHoverStart={() => setHoveredItem(item.id)}
                onHoverEnd={() => setHoveredItem(null)}
                className="relative"
              >
                <a
                  href={`#${item.id}`}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    darkMode ? "hover:text-blue-300" : "hover:text-blue-600"
                  } transition-colors`}
                >
                  {item.name}
                </a>
                {hoveredItem === item.id && (
                  <motion.div
                    layoutId="underline"
                    className={`absolute bottom-0 left-0 w-full h-0.5 ${
                      darkMode ? "bg-blue-400" : "bg-blue-600"
                    }`}
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{
                      type: "spring",
                      stiffness: 300,
                      damping: 20,
                    }}
                  />
                )}
              </motion.div>
            ))}
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-full ${
                darkMode
                  ? "bg-gray-700 text-yellow-300"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-4 py-2 rounded-md font-medium bg-gradient-to-r ${ctaColors.primary} text-white shadow-lg`}
              onClick={() => navigate("/login")}
            >
              Log In
            </motion.button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="py-20">
        <div className="container mx-auto px-6 flex flex-col md:flex-row items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="md:w-1/2 mb-12 md:mb-0"
          >
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ staggerChildren: 0.1, delayChildren: 0.3 }}
              className="text-4xl md:text-5xl font-bold mb-6"
            >
              <motion.span variants={splitText} custom={0}>
                Your{" "}
              </motion.span>
              <motion.span
                variants={splitText}
                custom={1}
                className="bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent"
              >
                Mental Wellness
              </motion.span>{" "}
              <motion.span variants={splitText} custom={2}>
                Companion
              </motion.span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className={`text-lg mb-8 ${
                darkMode ? "text-gray-300" : "text-gray-600"
              }`}
            >
              MindMate helps you track your mood, practice mindfulness, and
              improve your mental health journey with personalized tools and
              resources.
            </motion.p>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="flex space-x-4"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-6 py-3 rounded-md font-medium ${
                  darkMode
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-blue-500 hover:bg-blue-600"
                } text-white shadow-lg`}
                onClick={() => navigate("/signup")}
              >
                Get Started
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-6 py-3 rounded-md font-medium ${
                  darkMode
                    ? "bg-gray-700 hover:bg-gray-600"
                    : "bg-gray-200 hover:bg-gray-300"
                } ${darkMode ? "text-white" : "text-gray-700"} shadow-lg`}
                onClick={() => {
                  const featuresSection = document.getElementById("features");
                  featuresSection?.scrollIntoView({ behavior: "smooth" });
                }}
              >
                Learn More
              </motion.button>
            </motion.div>
          </motion.div>
          <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8 }}
      whileHover={{ scale: 1.05 }}
      className="md:w-1/2 flex justify-center"
    >
      <Tilt
        tiltMaxAngleX={5}
        tiltMaxAngleY={5}
        glareEnable={true}
        glareMaxOpacity={0.2}
        className="w-full max-w-md"
      >
        <div className={`relative w-full h-80 rounded-2xl overflow-hidden shadow-xl ${darkMode ? "bg-gray-700" : "bg-blue-100"}`}>
          <img
            src="https://play-lh.googleusercontent.com/3hasRHyxrNRhLiwAfJTcNEyP1Pq8YMlwpm30ylANoIVVbrFiK_nqE_keJKpyhquOrw=w3840-h2160-rw"
            alt="MindMate App Screenshot"
            className="absolute inset-0 w-full h-full object-cover"
            loading="eager"
            onError={(e) => {
              e.target.onerror = null;
              // Use a data URI instead of external placeholder
              e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='400'%3E%3Crect fill='%236366F1' width='600' height='400'/%3E%3Ctext x='50%25' y='50%25' font-size='48' font-weight='bold' text-anchor='middle' dy='.3em' fill='white' font-family='Arial'%3EMindMate App%3C/text%3E%3C/svg%3E";
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500 opacity-20"></div>
        </div>
      </Tilt>
    </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section
  id="features"
  className={`py-28 ${darkMode ? "bg-gray-800" : "bg-gray-100"}`}
>
  <div className="container mx-auto px-6">
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-100px" }}
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: { staggerChildren: 0.1 },
        },
      }}
      className="text-center mb-20"
    >
      <motion.h2
        variants={fadeUp}
        className="text-4xl md:text-5xl font-bold mb-6"
      >
        Powerful Features
      </motion.h2>
      <motion.p
        variants={fadeUp}
        className={`max-w-2xl mx-auto text-xl ${darkMode ? "text-gray-300" : "text-gray-600"}`}
      >
        Designed to support your mental health journey with intuitive tools
      </motion.p>
    </motion.div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {[
        {
          title: "Mood Tracking",
          description: "Track your emotions daily and visualize patterns over time with our intuitive dashboard.",
          icon: "📊",
          animation: fadeLeft,
          bg: darkMode ? "from-indigo-900 to-indigo-800" : "from-indigo-100 to-indigo-50",
          text: darkMode ? "text-indigo-200" : "text-indigo-700",
          button: darkMode ? "text-indigo-300 hover:text-indigo-200" : "text-indigo-600 hover:text-indigo-700"
        },
        {
          title: "Guided Meditations",
          description: "Access a growing library of mindfulness exercises tailored to your needs and experience level.",
          icon: "🧘‍♂️",
          animation: fadeUp,
          bg: darkMode ? "from-teal-900 to-teal-800" : "from-teal-100 to-teal-50",
          text: darkMode ? "text-teal-200" : "text-teal-700",
          button: darkMode ? "text-teal-300 hover:text-teal-200" : "text-teal-600 hover:text-teal-700"
        },
        {
          title: "Journal Prompts",
          description: "Thoughtful prompts to help you reflect, process emotions, and cultivate self-awareness.",
          icon: "📝",
          animation: fadeRight,
          bg: darkMode ? "from-purple-900 to-purple-800" : "from-purple-100 to-purple-50",
          text: darkMode ? "text-purple-200" : "text-purple-700",
          button: darkMode ? "text-purple-300 hover:text-purple-200" : "text-purple-600 hover:text-purple-700"
        },
      ].map((feature, index) => (
        <motion.div
          key={index}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          variants={feature.animation}
          className="h-full"
        >
          <Tilt
            tiltMaxAngleX={5}
            tiltMaxAngleY={5}
            glareEnable={true}
            glareMaxOpacity={0.1}
            className="h-full"
          >
            <div className={`p-8 rounded-2xl h-full flex flex-col bg-gradient-to-br ${feature.bg} shadow-xl hover:shadow-2xl transition-all duration-300`}>
              <div className="text-5xl mb-6">{feature.icon}</div>
              <h3 className={`text-2xl font-bold mb-4 ${darkMode ? "text-white" : "text-gray-900"}`}>
                {feature.title}
              </h3>
              <p className={`${feature.text} mb-6`}>
                {feature.description}
              </p>
              <div className="mt-auto">
                <motion.button
                  whileHover={{ x: 5 }}
                  className={`flex items-center ${feature.button} font-medium text-lg transition-colors`}
                >
                  Learn more <ArrowRight size={18} className="ml-2" />
                </motion.button>
                <div className={`w-12 h-1 mt-4 rounded-full ${darkMode ? "bg-white/30" : "bg-black/10"}`}></div>
              </div>
            </div>
          </Tilt>
        </motion.div>
      ))}
    </div>
  </div>
      </section>

      {/* Statistics Section */}
      <section
        id="stats"
        className={`py-28 ${darkMode ? "bg-gray-900" : "bg-white"}`}
      >
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Our Impact</h2>
            <p className={`max-w-2xl mx-auto text-xl ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
              Join thousands who have transformed their mental health journey
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => {
              // Define color schemes for each stat
              const colorSchemes = [
                {
                  bg: darkMode ? "from-teal-900 to-teal-800" : "from-teal-100 to-teal-50",
                  text: darkMode ? "text-teal-300" : "text-teal-600",
                  value: darkMode ? "text-teal-200" : "text-teal-700"
                },
                {
                  bg: darkMode ? "from-blue-900 to-blue-800" : "from-blue-100 to-blue-50",
                  text: darkMode ? "text-blue-300" : "text-blue-600",
                  value: darkMode ? "text-blue-200" : "text-blue-700"
                },
                {
                  bg: darkMode ? "from-purple-900 to-purple-800" : "from-purple-100 to-purple-50",
                  text: darkMode ? "text-purple-300" : "text-purple-600",
                  value: darkMode ? "text-purple-200" : "text-purple-700"
                },
                {
                  bg: darkMode ? "from-amber-900 to-amber-800" : "from-amber-100 to-amber-50",
                  text: darkMode ? "text-amber-300" : "text-amber-600",
                  value: darkMode ? "text-amber-200" : "text-amber-700"
                }
              ];

              const colors = colorSchemes[index % colorSchemes.length];
              const is24_7 = stat.value === "24/7";
              const numericValue = is24_7 ? 24 : parseFloat(stat.value.replace(/[^0-9.]/g, ''));

              return (
                <motion.div
                  key={index}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, amount: 0.5 }}
                  variants={scaleIn}
                  custom={index}
                  className="h-full group"
                >
                  <Tilt
                    tiltMaxAngleX={5}
                    tiltMaxAngleY={5}
                    scale={1.05}
                    glareEnable={true}
                    glareMaxOpacity={0.2}
                    className="h-full relative overflow-hidden"
                  >

                    <div className={`p-8 rounded-2xl h-full bg-gradient-to-br ${colors.bg} shadow-lg hover:shadow-xl transition-all duration-300 relative z-10`}>
                      <CountUp
                        end={numericValue}
                        duration={2.5}
                        decimals={stat.value.includes('.') ? 1 : 0}
                        suffix={is24_7 ? '/7' : (stat.value.includes('%') ? '%' : stat.value.match(/[a-zA-Z+]+/)?.join('') || '')}
                        className={`text-5xl font-bold mb-3 ${colors.value}`}
                      />

                      <div className={`text-xl font-medium ${colors.text}`}>
                        {stat.label}
                      </div>
                      
                      <div className={`w-12 h-1 mx-auto mt-4 rounded-full ${darkMode ? "bg-white/30" : "bg-black/10"}`}></div>
                    </div>
                  </Tilt>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section
        id="testimonials"
        className={`py-28 ${darkMode ? "bg-gray-800" : "bg-gray-100"}`}
      >
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              What Our Users Say
            </h2>
            <p className={`max-w-2xl mx-auto text-xl ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
              Real stories from people who found support through MindMate
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => {
              // Color schemes for each testimonial card
              const colorSchemes = [
                {
                  bg: darkMode ? "from-indigo-900 to-indigo-800" : "from-indigo-100 to-indigo-50",
                  text: darkMode ? "text-indigo-200" : "text-indigo-700",
                  iconBg: darkMode ? "bg-indigo-800" : "bg-indigo-100",
                  iconColor: darkMode ? "text-indigo-300" : "text-indigo-600"
                },
                {
                  bg: darkMode ? "from-teal-900 to-teal-800" : "from-teal-100 to-teal-50",
                  text: darkMode ? "text-teal-200" : "text-teal-700",
                  iconBg: darkMode ? "bg-teal-800" : "bg-teal-100",
                  iconColor: darkMode ? "text-teal-300" : "text-teal-600"
                },
                {
                  bg: darkMode ? "from-purple-900 to-purple-800" : "from-purple-100 to-purple-50",
                  text: darkMode ? "text-purple-200" : "text-purple-700",
                  iconBg: darkMode ? "bg-purple-800" : "bg-purple-100",
                  iconColor: darkMode ? "text-purple-300" : "text-purple-600"
                }
              ];

              const colors = colorSchemes[index % colorSchemes.length];

              return (
                <motion.div
                  key={index}
                  initial={{
                    opacity: 0,
                    x: index === 1 ? 0 : index === 0 ? -100 : 100,
                  }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className="h-full flex"
                >
                  <Tilt
                    tiltMaxAngleX={5}
                    tiltMaxAngleY={5}
                    glareEnable={true}
                    glareMaxOpacity={0.1}
                    className="flex-1"
                  >
                    <div className={`p-8 rounded-2xl h-full flex flex-col bg-gradient-to-br ${colors.bg} shadow-xl hover:shadow-2xl transition-shadow duration-300`}>
                      <div className="flex items-center mb-6">
                        <div className={`w-16 h-16 rounded-full ${colors.iconBg} flex items-center justify-center mr-4`}>
                          <MessageCircle className={colors.iconColor} size={24} />
                        </div>
                        <div>
                          <div className={`font-bold text-xl ${darkMode ? "text-white" : "text-gray-900"}`}>
                            {testimonial.author}
                          </div>
                          <div className={`text-sm ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
                            {testimonial.role}
                          </div>
                        </div>
                      </div>
                      <blockquote className={`italic text-lg flex-grow ${colors.text} relative pl-6`}>
                        <span className="absolute left-0 top-0 text-3xl leading-none">“</span>
                        {testimonial.quote}
                      </blockquote>
                      <div className={`w-12 h-1 mt-6 rounded-full ${darkMode ? "bg-white/30" : "bg-black/10"}`}></div>
                    </div>
                  </Tilt>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Resources Section */}
      <section
        id="resources"
        className={`py-28 ${darkMode ? "bg-gray-900" : "bg-white"}`}
      >
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Resources & Blog
            </h2>
            <p className={`max-w-2xl mx-auto text-xl ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
              Learn more about mental health and wellness
            </p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: { staggerChildren: 0.1 },
              },
            }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {blogPosts.map((post, index) => {
              // Define icons and colors for each category
              const categoryData = {
                Mindfulness: {
                  icon: <Sun size={32} />,
                  bgColor: darkMode ? "from-green-700 to-green-800" : "from-green-100 to-green-200",
                  textColor: darkMode ? "text-green-400" : "text-green-600"
                },
                "Mental Health": {
                  icon: <HelpCircle size={32} />,
                  bgColor: darkMode ? "from-purple-700 to-purple-800" : "from-purple-100 to-purple-200",
                  textColor: darkMode ? "text-purple-400" : "text-purple-600"
                },
                Journaling: {
                  icon: <BookOpen size={32} />,
                  bgColor: darkMode ? "from-orange-700 to-orange-800" : "from-orange-100 to-orange-200",
                  textColor: darkMode ? "text-orange-400" : "text-orange-600"
                }
              };

              return (
                <motion.div
                  key={index}
                  variants={index % 2 === 0 ? fadeLeft : fadeRight}
                  className="h-full"
                >
                  <Tilt 
                    tiltMaxAngleX={5}
                    tiltMaxAngleY={5}
                    glareEnable={true}
                    glareMaxOpacity={0.1}
                    className="h-full"
                  >
                    <div className={`rounded-2xl overflow-hidden shadow-xl h-full flex flex-col transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 ${darkMode ? "bg-gray-800" : "bg-white"}`}>
                      {/* Image Header with Gradient */}
                      <div className={`relative h-48 bg-gradient-to-r ${categoryData[post.category].bgColor} flex items-center justify-center`}>
                        {categoryData[post.category].icon}
                        <div className="absolute inset-0 bg-black/10"></div>
                      </div>

                      <div className="p-6 flex flex-col flex-grow">
                        <div className="flex-grow">
                          <div className={`flex items-center ${categoryData[post.category].textColor} mb-3`}>
                            {categoryData[post.category].icon}
                            <span className="ml-2 text-sm font-semibold">{post.category}</span>
                            <span className="ml-auto text-xs bg-black/10 dark:bg-white/10 px-2 py-1 rounded-full">5 min read</span>
                          </div>
                          <h3 className="text-xl font-bold mb-3">{post.title}</h3>
                          <p className={`mb-4 ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
                            {post.excerpt}
                          </p>
                          <div className="text-xs italic text-gray-400 mt-2">
                            "This guide changed my routine! - Sarah T."
                          </div>
                        </div>
                        <motion.button
                          whileHover={{ x: 5 }}
                          className={`flex items-center mt-4 ${darkMode ? "text-blue-400" : "text-blue-600"} font-medium`}
                        >
                          Read more <ArrowRight size={16} className="ml-1" />
                        </motion.button>
                      </div>
                    </div>
                  </Tilt>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section
        id="faq"
        className={`py-28 ${darkMode ? "bg-gray-800" : "bg-gray-100"}`}
      >
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Frequently Asked Questions
            </h2>
            <p className={`max-w-2xl mx-auto text-xl ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
              Find answers to common questions about MindMate
            </p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: { staggerChildren: 0.1 },
              },
            }}
            className="max-w-3xl mx-auto"
          >
            {faqs.map((faq, index) => {
              // Color schemes for each FAQ item
              const colorSchemes = [
                {
                  bg: darkMode ? "from-indigo-900 to-indigo-800" : "from-indigo-100 to-indigo-50",
                  text: darkMode ? "text-indigo-200" : "text-indigo-700",
                  hover: darkMode ? "hover:bg-indigo-800" : "hover:bg-indigo-50"
                },
                {
                  bg: darkMode ? "from-teal-900 to-teal-800" : "from-teal-100 to-teal-50",
                  text: darkMode ? "text-teal-200" : "text-teal-700",
                  hover: darkMode ? "hover:bg-teal-800" : "hover:bg-teal-50"
                },
                {
                  bg: darkMode ? "from-purple-900 to-purple-800" : "from-purple-100 to-purple-50",
                  text: darkMode ? "text-purple-200" : "text-purple-700",
                  hover: darkMode ? "hover:bg-purple-800" : "hover:bg-purple-50"
                }
              ];

              const colors = colorSchemes[index % colorSchemes.length];

              return (
                <motion.div key={index} variants={fadeUp} className="mb-6">
                  <Tilt tiltMaxAngleX={3} tiltMaxAngleY={3} scale={1.02} glareEnable={true} glareMaxOpacity={0.05}>
                    <div className={`rounded-xl overflow-hidden bg-gradient-to-br ${colors.bg} shadow-lg hover:shadow-xl transition-all`}>
                      <button
                        onClick={() => toggleFAQ(index)}
                        className={`w-full flex justify-between items-center p-6 text-left ${colors.hover} transition-colors`}
                      >
                        <h3 className={`font-bold text-xl ${darkMode ? "text-white" : "text-gray-900"}`}>
                          {faq.question}
                        </h3>
                        <motion.div
                          animate={{ rotate: activeFAQ === index ? 90 : 0 }}
                          transition={{ duration: 0.3 }}
                          className={darkMode ? "text-white" : "text-gray-700"}
                        >
                          <ArrowRight size={24} />
                        </motion.div>
                      </button>
                      <AnimatePresence>
                        {activeFAQ === index && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className={`px-6 pb-6 text-lg ${colors.text}`}
                          >
                            {faq.answer}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </Tilt>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>


      {/* Footer */}
      <Footer darkMode={darkMode} />

      {/* Scroll to Top Button */}
      <AnimatePresence>
        {showScrollButton && (
          <motion.button
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
            onClick={scrollToTop}
            className={`fixed bottom-8 right-8 p-4 rounded-full shadow-xl ${
              darkMode
                ? "bg-gray-700 text-yellow-300"
                : "bg-blue-500 text-white"
            }`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <ArrowUp size={24} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Cookie Consent Banner */}
      <CookieConsent
        location="bottom"
        buttonText="Accept"
        declineButtonText="Reject"
        enableDeclineButton
        cookieName="mindMateCookieConsent"
        style={{
          background: darkMode ? "#1F2937" : "#FFFFFF",
          color: darkMode ? "#E5E7EB" : "#111827",
          borderTop: darkMode ? "1px solid #374151" : "1px solid #E5E7EB",
          boxShadow: "0 -2px 10px rgba(0,0,0,0.1)",
        }}
        buttonStyle={{
          background: darkMode ? "#4F46E5" : "#2563EB",
          color: "white",
          fontSize: "14px",
          borderRadius: "6px",
          padding: "10px 15px",
        }}
        declineButtonStyle={{
          background: darkMode ? "#4B5563" : "#E5E7EB",
          color: darkMode ? "#E5E7EB" : "#374151",
          fontSize: "14px",
          borderRadius: "6px",
          padding: "10px 15px",
          margin: "0 10px 0 0",
        }}
        expires={150}
      >
        This website uses cookies to enhance the user experience. By continuing
        to browse, you agree to our use of cookies.
      </CookieConsent>
    </div>
  );
};

export default LandingPage;
