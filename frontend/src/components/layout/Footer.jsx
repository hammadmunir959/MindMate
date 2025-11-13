import React from "react";
import { motion } from "framer-motion";
import { Heart, Facebook, Twitter, Instagram, Linkedin } from "react-feather";

const Footer = ({ darkMode }) => {
  const footerLinks = [
    { name: "Privacy Policy", href: "#" },
    { name: "Terms", href: "#" },
    { name: "Contact", href: "#" },
  ];

  const socialLinks = [
    { name: "Facebook", icon: Facebook, href: "#" },
    { name: "Twitter", icon: Twitter, href: "#" },
    { name: "Instagram", icon: Instagram, href: "#" },
    { name: "LinkedIn", icon: Linkedin, href: "#" },
  ];

  return (
    <footer
      className={`transition-all duration-300 ${
        darkMode
          ? "bg-gray-900/95 backdrop-blur-md border-t border-gray-800"
          : "bg-white/95 backdrop-blur-md border-t border-gray-200"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
          >
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                darkMode ? "bg-indigo-600" : "bg-indigo-500"
              }`}
            >
              <Heart size={20} className="text-white" />
            </div>
            <span
              className={`text-xl font-bold ${
                darkMode ? "text-white" : "text-gray-900"
              }`}
            >
              MindMate
            </span>
          </motion.div>

          {/* Footer Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {footerLinks.map((link, index) => (
              <motion.a
                key={index}
                href={link.href}
                className={`text-sm px-4 py-2 rounded-lg transition-all duration-200 ${
                  darkMode
                    ? "text-gray-300 hover:text-white hover:bg-gray-800"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {link.name}
              </motion.a>
            ))}
          </nav>

          {/* Right Side - Copyright & Social */}
          <div className="flex items-center space-x-4">
            {/* Copyright */}
            <div
              className={`hidden lg:block text-sm ${
                darkMode ? "text-gray-400" : "text-gray-600"
              }`}
            >
              © 2024 MindMate
            </div>

            {/* Social Links */}
            <div className="flex items-center space-x-2">
              {socialLinks.map((social, index) => {
                const Icon = social.icon;
                return (
                  <motion.a
                    key={index}
                    href={social.href}
                    className={`p-2 rounded-lg transition-all duration-200 ${
                      darkMode
                        ? "text-gray-300 hover:text-white hover:bg-gray-800"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    aria-label={social.name}
                  >
                    <Icon size={18} />
                  </motion.a>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
