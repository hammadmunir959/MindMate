import { motion } from 'framer-motion';
import { useState } from 'react';
import {
  Activity,
  BookOpen,
  MessageSquare,
  Calendar,
  Heart,
  Target,
  Plus,
  Users,
  TrendingUp,
} from 'react-feather';
import { MoodAssessmentModal, JournalEntryModal, StartExerciseModal } from '../../../Modals';
import toast from 'react-hot-toast';

const QuickActionsWidget = ({ actions, darkMode, onActionComplete }) => {
  const [showMoodModal, setShowMoodModal] = useState(false);
  const [showJournalModal, setShowJournalModal] = useState(false);
  const [showExerciseModal, setShowExerciseModal] = useState(false);

  // Map icon strings to React components
  const iconMap = {
    'activity': Activity,
    'book-open': BookOpen,
    'calendar': Calendar,
    'heart': Heart,
    'target': Target,
    'message-square': MessageSquare,
    'users': Users,
    'trending-up': TrendingUp,
    'plus': Plus,
  };

  const getIconComponent = (icon) => {
    if (typeof icon === 'string') {
      // If it's a string, look it up in the icon map
      return iconMap[icon.toLowerCase()] || Plus;
    }
    // If it's already a component, return it
    return icon || Plus;
  };

  // Filter to show only the 3 required actions: start_exercise, journal_entry, mood_check
  const filteredActions = actions && actions.length > 0 
    ? actions.filter(action => 
        ['start_exercise', 'journal_entry', 'mood_check'].includes(action.id)
      )
    : [];

  const defaultActions = [
    {
      id: 'start_exercise',
      title: 'Start Exercise',
      description: 'Begin a new exercise session',
      icon: 'activity',
      route: '/dashboard/exercises',
      color: 'blue',
    },
    {
      id: 'journal_entry',
      title: 'Journal Entry',
      description: 'Write in your journal',
      icon: 'book-open',
      route: '/dashboard/journal',
      color: 'green',
    },
    {
      id: 'mood_check',
      title: 'Mood Check',
      description: 'Log your current mood',
      icon: 'heart',
      route: '/dashboard/progress-tracker/mood',
      color: 'purple',
    },
  ];

  const displayActions = filteredActions.length > 0 ? filteredActions : defaultActions;

  const getColorClasses = (color) => {
    const colors = {
      blue: {
        bg: darkMode ? 'bg-blue-500/10 hover:bg-blue-500/20' : 'bg-blue-50 hover:bg-blue-100',
        text: darkMode ? 'text-blue-400' : 'text-blue-600',
        border: darkMode ? 'border-blue-500/30' : 'border-blue-200',
      },
      purple: {
        bg: darkMode ? 'bg-purple-500/10 hover:bg-purple-500/20' : 'bg-purple-50 hover:bg-purple-100',
        text: darkMode ? 'text-purple-400' : 'text-purple-600',
        border: darkMode ? 'border-purple-500/30' : 'border-purple-200',
      },
      yellow: {
        bg: darkMode ? 'bg-yellow-500/10 hover:bg-yellow-500/20' : 'bg-yellow-50 hover:bg-yellow-100',
        text: darkMode ? 'text-yellow-400' : 'text-yellow-600',
        border: darkMode ? 'border-yellow-500/30' : 'border-yellow-200',
      },
      green: {
        bg: darkMode ? 'bg-green-500/10 hover:bg-green-500/20' : 'bg-green-50 hover:bg-green-100',
        text: darkMode ? 'text-green-400' : 'text-green-600',
        border: darkMode ? 'border-green-500/30' : 'border-green-200',
      },
      indigo: {
        bg: darkMode ? 'bg-indigo-500/10 hover:bg-indigo-500/20' : 'bg-indigo-50 hover:bg-indigo-100',
        text: darkMode ? 'text-indigo-400' : 'text-indigo-600',
        border: darkMode ? 'border-indigo-500/30' : 'border-indigo-200',
      },
    };
    return colors[color] || colors.blue;
  };

  const handleActionClick = (action) => {
    if (action.is_available === false) {
      return;
    }

    // Open appropriate modal based on action ID
    switch (action.id) {
      case 'mood_check':
        setShowMoodModal(true);
        break;
      case 'journal_entry':
        setShowJournalModal(true);
        break;
      case 'start_exercise':
        setShowExerciseModal(true);
        break;
      default:
        console.warn('Unknown action:', action.id);
    }
  };

  const handleMoodComplete = (metrics) => {
    if (onActionComplete) {
      onActionComplete('mood', metrics);
    }
  };

  const handleJournalComplete = (entry) => {
    if (onActionComplete) {
      onActionComplete('journal', entry);
    }
  };

  const handleExerciseComplete = (session) => {
    if (onActionComplete) {
      onActionComplete('exercise', session);
    }
  };

  return (
    <div
      className={`rounded-2xl p-6 ${
        darkMode
          ? 'bg-gray-800/50 backdrop-blur-sm border border-gray-700'
          : 'bg-white shadow-lg border border-gray-100'
      }`}
    >
      <h3
        className={`text-xl font-bold mb-6 ${
          darkMode ? 'text-gray-100' : 'text-gray-900'
        }`}
      >
        Quick Actions
      </h3>
      <div className="grid grid-cols-1 gap-3">
        {displayActions.map((action, index) => {
          const Icon = getIconComponent(action.icon);
          const colors = getColorClasses(action.color || 'blue');
          const isDisabled = action.is_available === false;

          return (
            <motion.button
              key={action.id || index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => handleActionClick(action)}
              disabled={isDisabled}
              className={`p-4 rounded-xl border-2 ${colors.bg} ${colors.border} ${colors.text} transition-all duration-200 text-left ${
                isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-105'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className="w-5 h-5 flex-shrink-0" />
                <div className="flex-1 text-left">
              <div className="font-semibold text-sm mb-1">{action.title}</div>
              {action.description && (
                <div
                  className={`text-xs ${
                    darkMode ? 'text-gray-400' : 'text-gray-600'
                  }`}
                >
                  {action.description}
                </div>
              )}
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* Modals */}
      <MoodAssessmentModal
        isOpen={showMoodModal}
        onClose={() => setShowMoodModal(false)}
        darkMode={darkMode}
        onComplete={handleMoodComplete}
      />
      <JournalEntryModal
        isOpen={showJournalModal}
        onClose={() => setShowJournalModal(false)}
        darkMode={darkMode}
        onComplete={handleJournalComplete}
      />
      <StartExerciseModal
        isOpen={showExerciseModal}
        onClose={() => setShowExerciseModal(false)}
        darkMode={darkMode}
        onComplete={handleExerciseComplete}
      />
    </div>
  );
};

export default QuickActionsWidget;

