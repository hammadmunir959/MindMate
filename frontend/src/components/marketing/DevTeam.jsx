import { motion } from "framer-motion";
import {
  ChevronLeft,
  Sun,
  Moon,
  Code,
  Database,
  Cpu,
  User,
  Linkedin,
  GitHub,
} from "react-feather";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

const DevTeam = () => {
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const savedMode = localStorage.getItem("darkMode") === "true";
    setDarkMode(savedMode);
  }, []);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem("darkMode", newMode.toString());
  };

  // Optimized image handling
  const preloadImages = () => {
    const images = ["/images/jawad.JPG", "/images/hammad.jpg"];
    images.forEach((src) => {
      const img = new Image();
      img.src = src;
    });
  };

  useEffect(() => {
    preloadImages();
  }, []);

  const teamMembers = [
    {
      name: "Muhammad Jawad Ahsan",
      age: 23,
      education: "BS Computer Science - International Islamic University",
      role: "Frontend Developer",
      expertise: ["Python", "Java", "React JS", "SQL"],
      projects: "Multiple frontend projects including MindMate",
      image: "/images/jawad.JPG",
      linkedin: "https://www.linkedin.com/in/muhammad-jawad-ahsan-0b6704233/",
      dimensions: { width: 3008, height: 4512 },
    },
    {
      name: "Hammad Munir",
      age: 23,
      education: "BS Computer Science - International Islamic University",
      role: "AI & Backend Developer",
      expertise: ["Python", "Django", "Flask", "RAG", "Neural Networks"],
      projects: "MindMate backend and multiple AI projects",
      image: "/images/hammad.jpg",
      linkedin: "https://linkedin.com/in/hammadmunir959",
      dimensions: { width: 676, height: 1262 },
    },
  ];

  return (
    <motion.div
      className={`min-h-screen transition-colors duration-300 ${
        darkMode ? "bg-gray-900 text-gray-100" : "bg-gray-50 text-gray-900"
      }`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Navigation Bar */}
      <nav
        className={`sticky top-0 z-50 ${
          darkMode ? "bg-gray-800" : "bg-white"
        } shadow-md py-4 transition-colors duration-300`}
      >
        <div className="container mx-auto px-6 flex justify-between items-center">
          <motion.button
            onClick={() => navigate("/")}
            className="flex items-center text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent"
            whileHover={{ x: -3 }}
          >
            <ChevronLeft size={24} className="mr-1" />
            MindMate
          </motion.button>

          <button
            onClick={toggleDarkMode}
            className={`p-2 rounded-full transition-colors ${
              darkMode
                ? "bg-gray-700 text-yellow-300 hover:bg-gray-600"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </nav>

      {/* Team Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Our{" "}
              <span className="bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                Development Team
              </span>
            </h2>
            <p
              className={`max-w-2xl mx-auto text-lg ${
                darkMode ? "text-gray-300" : "text-gray-600"
              }`}
            >
              The brilliant minds behind MindMate
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {teamMembers.map((member, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`rounded-2xl overflow-hidden shadow-xl transition-all duration-300 ${
                  darkMode
                    ? "bg-gray-800 hover:shadow-gray-700/50"
                    : "bg-white hover:shadow-lg"
                } hover:-translate-y-1`}
              >
                {/* Optimized Image Container */}
                <div className="relative h-96 w-full overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
                    <motion.img
                      src={member.image}
                      alt={member.name}
                      className={`h-full w-full object-cover transition-opacity duration-500 ${
                        darkMode ? "opacity-90" : "opacity-95"
                      }`}
                      style={{
                        objectPosition: "center top",
                        aspectRatio: `${member.dimensions.width}/${member.dimensions.height}`,
                      }}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.8 }}
                      whileHover={{ scale: 1.03 }}
                      loading="lazy"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = "/images/default-profile.jpg";
                      }}
                    />
                  </div>
                  <div
                    className={`absolute inset-0 bg-gradient-to-t ${
                      darkMode
                        ? "from-gray-900/70 via-gray-900/20"
                        : "from-white/70 via-white/20"
                    } to-transparent`}
                  />
                </div>

                <div className="p-6 sm:p-8">
                  <motion.h3 className="text-2xl font-bold mb-2">
                    {member.name}
                  </motion.h3>

                  <div
                    className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mb-4 ${
                      darkMode
                        ? "bg-blue-900/30 text-blue-300"
                        : "bg-blue-100 text-blue-800"
                    }`}
                  >
                    <User size={16} className="mr-2" />
                    {member.role}
                  </div>

                  <div
                    className={`mb-4 p-4 rounded-lg ${
                      darkMode ? "bg-gray-700/50" : "bg-gray-100"
                    }`}
                  >
                    <p className="mb-2">
                      <strong>Education:</strong> {member.education}
                    </p>
                    <p>
                      <strong>Age:</strong> {member.age}
                    </p>
                  </div>

                  <div className="mb-4">
                    <h4 className="font-bold mb-2 flex items-center">
                      <Database size={18} className="mr-2" />
                      Expertise:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {member.expertise.map((skill, i) => (
                        <motion.span
                          key={i}
                          whileHover={{ scale: 1.05 }}
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            darkMode
                              ? "bg-gray-700 text-blue-400 hover:bg-gray-600"
                              : "bg-blue-50 text-blue-700 hover:bg-blue-100"
                          }`}
                        >
                          {skill}
                        </motion.span>
                      ))}
                    </div>
                  </div>

                  <div
                    className={`p-4 rounded-lg border ${
                      darkMode
                        ? "bg-gray-700/50 border-gray-600"
                        : "bg-blue-50/50 border-blue-100"
                    }`}
                  >
                    <div className="flex items-start">
                      <Cpu
                        size={18}
                        className={`mr-2 mt-1 ${
                          darkMode ? "text-purple-400" : "text-purple-600"
                        }`}
                      />
                      <p>
                        <strong>Projects:</strong> {member.projects}
                      </p>
                    </div>
                  </div>

                  <div className="flex space-x-3 mt-6">
                    <motion.a
                      href={member.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      whileHover={{ y: -2 }}
                      className={`p-2 rounded-full ${
                        darkMode
                          ? "bg-gray-700 hover:bg-gray-600"
                          : "bg-gray-100 hover:bg-gray-200"
                      }`}
                    >
                      <Linkedin
                        size={18}
                        className={darkMode ? "text-blue-400" : "text-blue-600"}
                      />
                    </motion.a>
                    <motion.a
                      href="#"
                      whileHover={{ y: -2 }}
                      className={`p-2 rounded-full ${
                        darkMode
                          ? "bg-gray-700 hover:bg-gray-600"
                          : "bg-gray-100 hover:bg-gray-200"
                      }`}
                    >
                      <GitHub
                        size={18}
                        className={darkMode ? "text-gray-300" : "text-gray-700"}
                      />
                    </motion.a>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </motion.div>
  );
};

export default DevTeam;
