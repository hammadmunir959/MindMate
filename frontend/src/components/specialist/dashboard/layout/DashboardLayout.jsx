import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DashboardHeader from './DashboardHeader';
import DashboardSidebar from './DashboardSidebar';
import './DashboardLayout.css';

const DashboardLayout = ({ 
  children, 
  darkMode, 
  onToggleDarkMode, 
  activeTab,
  onTabChange,
  activeSidebarItem,
  onSidebarItemChange,
  specialistInfo,
  onLogout
}) => {
  const [sidebarWidth, setSidebarWidth] = useState(72);

  return (
    <div className={`h-screen flex flex-col ${
      darkMode ? "bg-gray-900" : "bg-gray-50"
    }`}>
      <DashboardHeader
        activeTab={activeTab}
        onTabChange={onTabChange}
        darkMode={darkMode}
        onToggleDarkMode={onToggleDarkMode}
        specialistInfo={specialistInfo}
        onLogout={onLogout}
      />

      <div className="flex flex-1 overflow-hidden">
        <DashboardSidebar
          darkMode={darkMode}
          activeTab={activeTab}
          activeSidebarItem={activeSidebarItem}
          onSidebarItemClick={onSidebarItemChange}
        />

        <motion.main
          className="flex-1 overflow-y-auto"
          initial={false}
          animate={{ width: `calc(100% - ${sidebarWidth}px)` }}
          transition={{ type: "spring", stiffness: 160, damping: 20 }}
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
};

export default DashboardLayout;

