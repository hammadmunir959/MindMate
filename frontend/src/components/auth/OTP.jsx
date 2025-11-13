import { useState, useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import { Sun, Moon, Mail, AlertCircle, CheckCircle } from "react-feather";
import axios from "axios";
import { toast } from "react-hot-toast";
import { API_URL, API_ENDPOINTS } from "../../config/api";
import { ROUTES } from "../../config/routes";
import { AuthStorage } from "../../utils/localStorage";

const OTP = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [otp, setOtp] = useState(new Array(6).fill(""));
  const [timer, setTimer] = useState(40); // 40 seconds
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();
  const location = useLocation();
  const inputRefs = useRef([]);

  // Get email and userType from location state or localStorage (for recovery)
  const email = location.state?.email || localStorage.getItem('pending_verification_email') || "";
  const userType = location.state?.userType || localStorage.getItem('pending_verification_user_type') || "";
  const isPasswordReset = location.state?.isPasswordReset || false;

  // Protect OTP route: Validate registration context
  useEffect(() => {
    // If no email is available from state or localStorage, redirect to appropriate page
    if (!email) {
      if (isPasswordReset) {
        // If password reset context is lost, redirect to forgot password
        toast.error("Please request a password reset again.");
        navigate(ROUTES.FORGOT_PASSWORD, { replace: true });
      } else {
        // If registration context is lost, redirect to signup
        toast.error("Please complete the registration process.");
        navigate(ROUTES.SIGNUP, { replace: true });
      }
      return;
    }

    // If user type is missing, default to patient but warn
    if (!userType && !isPasswordReset) {
      console.warn("User type not found in OTP context, defaulting to patient");
    }
  }, [email, userType, isPasswordReset, navigate]);

  // Clean up pending verification data once we have it from state
  useEffect(() => {
    if (location.state?.email && localStorage.getItem('pending_verification_email')) {
      localStorage.removeItem('pending_verification_email');
      localStorage.removeItem('pending_verification_user_type');
      localStorage.removeItem('pending_specialist_type');
      // Clean up patient-specific data if stored
      localStorage.removeItem('pending_patient_first_name');
      localStorage.removeItem('pending_patient_last_name');
      localStorage.removeItem('pending_patient_gender');
    }
  }, [location.state]);

  // Initialize dark mode from localStorage
  useEffect(() => {
    const savedMode = localStorage.getItem("darkMode") === "true";
    setDarkMode(savedMode);
  }, []);

  // Countdown timer effect
  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prevTimer) => prevTimer - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer]);

  // Focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem("darkMode", newMode.toString());
  };

  const handleChange = (element, index) => {
    if (isNaN(element.value)) return false; // Only allow numbers

    setOtp([...otp.map((d, idx) => (idx === index ? element.value : d))]);

    // Focus next input
    if (element.nextSibling) {
      element.nextSibling.focus();
    }
  };

  const handleKeyDown = (e, index) => {
    // Handle backspace
    if (e.key === "Backspace" && !otp[index] && inputRefs.current[index - 1]) {
      inputRefs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    const pastedData = e.clipboardData.getData("text");
    if (pastedData.length === 6 && !isNaN(pastedData)) {
      setOtp(pastedData.split(""));
      inputRefs.current[5]?.focus();
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    const enteredOtp = otp.join("");
    if (enteredOtp.length !== 6) {
      setError("Please enter the complete 6-digit OTP.");
      return;
    }

    // Validate that we have required context
    if (!email) {
      setError("Email context is missing. Please restart the process.");
      toast.error("Email context is missing. Please restart the process.");
      return;
    }

    setIsSubmitting(true);

    try {
      let response;
      
      // Use default userType if missing (for backward compatibility)
      const effectiveUserType = userType || "patient";
      
      if (isPasswordReset) {
        // Call password reset OTP verification endpoint
        response = await axios.post(`${API_URL}${API_ENDPOINTS.AUTH.VERIFY_RESET_OTP}`, {
          email,
          user_type: effectiveUserType,
          otp: enteredOtp,
        });
        
        toast.success("OTP verified successfully!");
        setSuccess("Redirecting to password reset form...");
        
        setTimeout(() => {
          navigate(ROUTES.RESET_PASSWORD, {
            state: {
              resetToken: response.data.reset_token,
              email: email,
              userType: userType
            }
          });
        }, 2000);
      } else {
        // Call regular email verification endpoint
        response = await axios.post(`${API_URL}${API_ENDPOINTS.VERIFICATION.VERIFY_EMAIL}`, {
          email,
          otp: enteredOtp,
          usertype: effectiveUserType,
        });

        toast.success("Verification successful!");
        
        // Store verified email for auto-fill on login page
        localStorage.setItem('verified_email', email);
        localStorage.setItem('verified_user_type', effectiveUserType);
        
        // Store specialist type if available (from registration or response)
        if (effectiveUserType === 'specialist') {
          const pendingSpecialistType = localStorage.getItem('pending_specialist_type');
          if (pendingSpecialistType) {
            localStorage.setItem('specialist_type', pendingSpecialistType);
            localStorage.removeItem('pending_specialist_type');
          }
          // Also check if specialist type is in response
          if (response.data?.specialist_type) {
            localStorage.setItem('specialist_type', response.data.specialist_type);
          }
        }
        
        // Store tokens if provided in response (for seamless login)
        const hasTokens = response.data?.access_token;
        if (hasTokens) {
          AuthStorage.setToken(response.data.access_token);
          AuthStorage.setRefreshToken(response.data.refresh_token);
          AuthStorage.setUserId(response.data.user_id);
          AuthStorage.setUserType(effectiveUserType);
          if (response.data.full_name) {
            AuthStorage.setFullName(response.data.full_name);
          }
        }

        // Determine redirect path based on user type and context
        let redirectPath;
        let successMessage;

        if (effectiveUserType === 'patient') {
          // Patient flow: If tokens provided or fromLogin, go to dashboard; otherwise login
          if (hasTokens || location.state?.fromLogin) {
            redirectPath = ROUTES.DASHBOARD;
            successMessage = "Verification complete! Redirecting to your dashboard...";
          } else {
            redirectPath = ROUTES.LOGIN;
            successMessage = "Your account is verified! Redirecting to login page...";
          }
        } else if (effectiveUserType === 'specialist') {
          // Specialist flow: Use backend redirect if available, otherwise use context
          if (response.data?.redirect_to) {
            redirectPath = response.data.redirect_to;
            successMessage = response.data.status_message || "Redirecting...";
          } else if (hasTokens || location.state?.fromLogin) {
            redirectPath = ROUTES.SPECIALIST_DASHBOARD;
            successMessage = "Verification complete! Redirecting to your dashboard...";
          } else {
            redirectPath = ROUTES.LOGIN;
            successMessage = "Your account is verified! Redirecting to login page...";
          }
        } else {
          // Fallback: Default to login
          redirectPath = ROUTES.LOGIN;
          successMessage = "Your account is verified! Redirecting to login page...";
        }

        setSuccess(successMessage);

        setTimeout(() => {
          navigate(redirectPath, { replace: true });
        }, 2000);
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        "Invalid or expired OTP. Please try again.";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (timer > 0) {
      toast.error(`Please wait ${timer} seconds before requesting another OTP.`);
      return;
    }
    setError("");
    setSuccess("");
    
    // Set timer immediately to prevent double-clicking
    setTimer(40);
    setIsSubmitting(true);

    try {
      let endpoint, payload;
      
      if (isPasswordReset) {
        endpoint = `${API_URL}${API_ENDPOINTS.AUTH.RESEND_RESET_OTP}`;
        payload = { email, user_type: userType || "patient" };
      } else {
        endpoint = `${API_URL}${API_ENDPOINTS.VERIFICATION.RESEND_OTP}`;
        payload = { email };
      }
      
      await axios.post(endpoint, payload);

      toast.success("A new OTP has been sent to your email.");
      setSuccess("A new OTP has been sent.");
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        "Failed to resend OTP. Please try again later.";
      setError(errorMessage);
      toast.error(errorMessage);
      // Reset timer on error so user can retry
      setTimer(0);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? "0" : ""}${remainingSeconds}`;
  };

  return (
    <motion.div
      className={`min-h-screen flex items-center justify-center transition-colors duration-300 p-4 ${
        darkMode
          ? "bg-gradient-to-br from-gray-800 to-gray-900 text-gray-100"
          : "bg-gradient-to-br from-indigo-50 to-blue-100 text-gray-900"
      }`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        className={`w-full max-w-md rounded-xl shadow-lg overflow-hidden ${
          darkMode ? "bg-gray-700" : "bg-white"
        }`}
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        <div className="p-8 relative">
          {/* Dark Mode Toggle */}
          <motion.button
            onClick={toggleDarkMode}
            className={`absolute top-4 right-4 p-2 rounded-full ${
              darkMode
                ? "bg-gray-600 text-yellow-300"
                : "bg-gray-100 text-gray-700"
            }`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </motion.button>

          <div className="text-center mb-8">
            <motion.h1
              className={`text-3xl font-bold mb-2 ${
                darkMode ? "text-indigo-400" : "text-indigo-600"
              }`}
            >
              {isPasswordReset 
                ? "Verify Password Reset OTP" 
                : location.state?.fromLogin 
                  ? "Complete Your Account" 
                  : "Verify Your Account"
              }
            </motion.h1>
            <p className={darkMode ? "text-gray-300" : "text-gray-600"}>
              {isPasswordReset
                ? "Please enter the OTP sent to your email to reset your password. OTP sent to "
                : location.state?.fromLogin 
                  ? "Please verify your email to complete your account setup. An OTP has been sent to "
                  : "An OTP has been sent to "
              }
              <span className="font-semibold">{email || "your email"}</span>
            </p>
          </div>

          {/* Messages */}
          <AnimatePresence>
            {error && (
              <motion.div
                className={`mb-4 p-3 rounded-lg flex items-center gap-2 text-sm ${
                  darkMode
                    ? "bg-red-900/30 text-red-300"
                    : "bg-red-100 text-red-700"
                }`}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                <AlertCircle size={18} />
                <span>{error}</span>
              </motion.div>
            )}
            {success && (
              <motion.div
                className={`mb-4 p-3 rounded-lg flex items-center gap-2 text-sm ${
                  darkMode
                    ? "bg-green-900/30 text-green-300"
                    : "bg-green-100 text-green-700"
                }`}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                <CheckCircle size={18} />
                <span>{success}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleVerify}>
            <div
              className="flex justify-center gap-2 md:gap-4 mb-6"
              onPaste={handlePaste}
            >
              {otp.map((data, index) => {
                return (
                  <input
                    key={index}
                    type="text"
                    maxLength="1"
                    ref={(el) => (inputRefs.current[index] = el)}
                    className={`w-12 h-14 text-center text-2xl font-semibold border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                      darkMode
                        ? "bg-gray-800 border-gray-600 text-white focus:ring-indigo-400"
                        : "bg-white border-gray-300 text-gray-900 focus:ring-indigo-500"
                    } ${
                      error
                        ? "border-red-500 focus:ring-red-400"
                        : "focus:border-indigo-500"
                    }`}
                    value={data}
                    onChange={(e) => handleChange(e.target, index)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                    onFocus={(e) => e.target.select()}
                    disabled={isSubmitting}
                  />
                );
              })}
            </div>

            <motion.button
              type="submit"
              className={`w-full font-medium py-3 px-4 rounded-lg transition duration-200 flex justify-center items-center ${
                darkMode
                  ? "bg-indigo-600 hover:bg-indigo-700"
                  : "bg-indigo-600 hover:bg-indigo-700"
              } text-white disabled:opacity-70`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                "Verify"
              )}
            </motion.button>
          </form>

          <div className="text-center mt-6 text-sm">
            {timer > 0 ? (
              <p className={darkMode ? "text-gray-400" : "text-gray-600"}>
                Resend OTP in{" "}
                <span
                  className={`font-semibold ${
                    darkMode ? "text-indigo-400" : "text-indigo-600"
                  }`}
                >
                  {formatTime(timer)}
                </span>
              </p>
            ) : (
              <p className={darkMode ? "text-gray-400" : "text-gray-600"}>
                Didn't receive the code?{" "}
                <button
                  onClick={handleResend}
                  className={`font-medium ${
                    darkMode
                      ? "text-indigo-400 hover:text-indigo-300"
                      : "text-indigo-600 hover:text-indigo-800"
                  } disabled:opacity-50`}
                  disabled={timer > 0 || isSubmitting}
                >
                  {isSubmitting ? "Sending..." : "Resend OTP"}
                </button>
              </p>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default OTP;
