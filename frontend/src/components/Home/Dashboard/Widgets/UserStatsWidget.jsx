import { motion } from 'framer-motion';
import { TrendingUp, Activity, Target, Award, Calendar, Zap } from 'react-feather';
import CountUp from 'react-countup';

const UserStatsWidget = ({ data, darkMode }) => {
  if (!data) return null;

  const stats = [
    {
      label: 'Total Sessions',
      value: data.total_sessions || 0,
      icon: Activity,
      color: 'text-blue-500',
      bgColor: darkMode ? 'bg-blue-500/10' : 'bg-blue-50',
    },
    {
      label: 'Current Streak',
      value: data.current_streak || 0,
      icon: Zap,
      color: 'text-orange-500',
      bgColor: darkMode ? 'bg-orange-500/10' : 'bg-orange-50',
      suffix: ' days',
    },
    {
      label: 'Longest Streak',
      value: data.longest_streak || 0,
      icon: TrendingUp,
      color: 'text-green-500',
      bgColor: darkMode ? 'bg-green-500/10' : 'bg-green-50',
      suffix: ' days',
    },
    {
      label: 'Exercises Completed',
      value: data.total_exercises || 0,
      icon: Target,
      color: 'text-purple-500',
      bgColor: darkMode ? 'bg-purple-500/10' : 'bg-purple-50',
    },
    {
      label: 'Achievements',
      value: data.achievements_unlocked || 0,
      icon: Award,
      color: 'text-yellow-500',
      bgColor: darkMode ? 'bg-yellow-500/10' : 'bg-yellow-50',
    },
    {
      label: 'Goals Completed',
      value: `${data.completed_goals || 0} / ${data.total_goals || 0}`,
      icon: Calendar,
      color: 'text-indigo-500',
      bgColor: darkMode ? 'bg-indigo-500/10' : 'bg-indigo-50',
    },
  ];

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
        Your Statistics
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-xl ${stat.bgColor} transition-all duration-300 hover:scale-105`}
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div className="text-2xl font-bold mb-1">
                {typeof stat.value === 'number' && !stat.suffix ? (
                  <CountUp
                    end={stat.value}
                    duration={2}
                    separator=","
                    className={darkMode ? 'text-gray-100' : 'text-gray-900'}
                  />
                ) : (
                  <span className={darkMode ? 'text-gray-100' : 'text-gray-900'}>
                    {stat.value}
                  </span>
                )}
                {stat.suffix && (
                  <span className={`text-sm ml-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {stat.suffix}
                  </span>
                )}
              </div>
              <p
                className={`text-sm font-medium ${
                  darkMode ? 'text-gray-400' : 'text-gray-600'
                }`}
              >
                {stat.label}
              </p>
            </motion.div>
          );
        })}
      </div>
      {data.wellness_score !== undefined && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className={`mt-6 p-4 rounded-xl ${
            darkMode ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20' : 'bg-gradient-to-r from-purple-50 to-pink-50'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className={`font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
              Wellness Score
            </span>
            <span className={`text-3xl font-bold ${
              data.wellness_score >= 70 
                ? 'text-green-500' 
                : data.wellness_score >= 50 
                ? 'text-yellow-500' 
                : 'text-red-500'
            }`}>
              <CountUp end={data.wellness_score} duration={2} decimals={1} />%
            </span>
          </div>
          <div className={`mt-2 h-2 rounded-full overflow-hidden ${
            darkMode ? 'bg-gray-700' : 'bg-gray-200'
          }`}>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${data.wellness_score}%` }}
              transition={{ duration: 2, delay: 0.5 }}
              className={`h-full ${
                data.wellness_score >= 70 
                  ? 'bg-gradient-to-r from-green-400 to-green-600' 
                  : data.wellness_score >= 50 
                  ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' 
                  : 'bg-gradient-to-r from-red-400 to-red-600'
              }`}
            />
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default UserStatsWidget;

