import { useState, useCallback } from 'react';
import apiClient from '../utils/axiosConfig';
import { API_ENDPOINTS } from '../config/api';

export const useAssessmentAPI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleError = (err) => {
    console.error('Assessment API Error:', err);
    const errorMessage = err.response?.data?.detail || err.message || 'An error occurred';
    setError(errorMessage);
    throw err;
  };

  const normalizedTimestamp = (value) => {
    if (!value) return null;
    try {
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return value;
      }
      return date.toISOString();
    } catch {
      return value;
    }
  };

  const normalizeProgressSnapshot = (snapshot) => {
    if (!snapshot || typeof snapshot !== 'object') {
      return null;
    }

    const overallPercentage =
      snapshot.overall_percentage ??
      snapshot.progress_percentage ??
      snapshot.overall ??
      snapshot.percentage ??
      null;

    return {
      ...snapshot,
      overall_percentage: overallPercentage,
      current_module: snapshot.current_module ?? snapshot.active_module ?? null,
      next_module: snapshot.next_module ?? null,
      module_sequence: snapshot.module_sequence ?? [],
      module_status: snapshot.module_status ?? [],
      module_timeline: snapshot.module_timeline ?? null,
      updated_at: normalizedTimestamp(snapshot.updated_at ?? snapshot.last_updated),
    };
  };

  const normalizeSymptomSummary = (summary) => {
    if (!summary || typeof summary !== 'object') {
      return null;
    }

    return {
      ...summary,
      categories: summary.categories ?? summary.category_counts ?? [],
      last_updated: normalizedTimestamp(summary.last_updated ?? summary.updated_at),
    };
  };

  const normalizeSessionSummary = (session) => {
    if (!session) return null;
    const sessionId = session.session_id ?? session.id;
    const progressSnapshot = normalizeProgressSnapshot(session.progress_snapshot);
    const progressPercentage =
      session.progress_percentage ??
      progressSnapshot?.overall_percentage ??
      0;

    return {
      id: sessionId,
      session_id: sessionId,
      title:
        session.title ??
        session.session_name ??
        `Assessment ${session.session_number ?? ''}`.trim(),
      session_name: session.session_name ?? session.title ?? sessionId,
      status: session.status ?? (session.is_complete ? 'completed' : 'in_progress'),
      is_complete: Boolean(session.is_complete ?? progressSnapshot?.is_complete),
      created_at: normalizedTimestamp(
        session.created_at ??
          session.started_at ??
          session.startedAt ??
          session.start_time
      ),
      updated_at: normalizedTimestamp(
        session.updated_at ??
          session.last_interaction ??
          progressSnapshot?.updated_at
      ),
      started_at: normalizedTimestamp(session.started_at ?? session.start_time),
      progress_percentage: typeof progressPercentage === 'number'
        ? progressPercentage
        : Number(progressPercentage ?? 0),
      current_module: session.current_module ?? progressSnapshot?.current_module ?? null,
      next_module: session.next_module ?? progressSnapshot?.next_module ?? null,
      module_timeline: session.module_timeline ?? progressSnapshot?.module_timeline ?? null,
      module_sequence: session.module_sequence ?? progressSnapshot?.module_sequence ?? [],
      module_status: session.module_status ?? progressSnapshot?.module_status ?? [],
      progress_snapshot: progressSnapshot,
      symptom_summary: normalizeSymptomSummary(session.symptom_summary),
      metadata: {
        ...(session.metadata ?? {}),
        has_background_services: Boolean(
          (progressSnapshot?.background_services && Object.keys(progressSnapshot.background_services).length) ||
            (session.background_services && Object.keys(session.background_services).length)
        ),
      },
      raw: session,
    };
  };

  const attachSessionToResponse = (response) => {
    if (!response) return null;
    const normalized = normalizeSessionSummary(response);
    return {
      ...response,
      normalized_session: normalized,
    };
  };

  const normalizePagination = (payload = {}) => ({
    page: payload.page ?? 1,
    pageSize: payload.page_size ?? payload.pageSize ?? 20,
    totalPages: payload.total_pages ?? payload.totalPages ?? 0,
    totalSessions: payload.total_sessions ?? payload.totalSessions ?? (payload.sessions?.length ?? 0),
    hasNext: payload.has_next ?? payload.page < payload.total_pages ?? false,
    hasPrevious: payload.has_previous ?? (payload.page ?? 1) > 1,
  });

  // Get all sessions with pagination support
  const getSessions = useCallback(async (page = 1, pageSize = 20) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSIONS, {
        params: { page, page_size: pageSize }
      });

      const data = response.data ?? {};
      const normalizedSessions = Array.isArray(data.sessions)
        ? data.sessions.map(normalizeSessionSummary).filter(Boolean)
        : [];

      return {
        ...data,
        sessions: normalizedSessions,
        pagination: normalizePagination(data),
      };
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Start new assessment session
  const startSession = useCallback(async (customSessionId = null) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const payload = customSessionId ? { session_id: customSessionId } : {};
      const response = await apiClient.post(API_ENDPOINTS.ASSESSMENT.START, payload);
      const data = response.data ?? {};
      const normalized = normalizeSessionSummary({
        session_id: data.session_id,
        title: data.metadata?.session_title ?? data.title,
        current_module: data.current_module,
        module_sequence: data.module_sequence,
        module_status: data.module_status,
        module_timeline: data.module_timeline,
        progress_snapshot: data.progress_snapshot,
        symptom_summary: data.symptom_summary,
        background_services: data.background_services,
        status: 'in_progress',
        created_at: Date.now(),
      });

      return {
        ...data,
        normalized_session: normalized,
      };
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Continue conversation in session
  const continueSession = useCallback(async (sessionId, message) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.post(API_ENDPOINTS.ASSESSMENT.CONTINUE, {
        session_id: sessionId,
        message: message
      });
      const data = response.data ?? {};
      return {
        ...data,
        progress_snapshot: normalizeProgressSnapshot(data.progress_snapshot),
        module_status: data.module_status ?? data.progress_snapshot?.module_status ?? [],
        module_sequence: data.module_sequence ?? data.progress_snapshot?.module_sequence ?? [],
        module_timeline: data.module_timeline ?? data.progress_snapshot?.module_timeline ?? null,
        symptom_summary: normalizeSymptomSummary(data.symptom_summary),
      };
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Delete session
  const deleteSession = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.delete(API_ENDPOINTS.ASSESSMENT.SESSION_DELETE(sessionId));
      return response.data;
    } catch (err) {
      // Don't throw 404 errors - they're handled gracefully in the component
      // (session might already be deleted or not exist)
      if (err.response?.status === 404) {
        // Return a success-like response for 404 to allow graceful handling
        return { success: true, message: 'Session not found (already deleted)', session_id: sessionId };
      }
      // For other errors, throw as usual
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Save session
  const saveSession = useCallback(async (sessionId, data) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.post(API_ENDPOINTS.ASSESSMENT.SESSION_SAVE, {
        session_id: sessionId,
        ...data
      });
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load session
  const loadSession = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSION_LOAD(sessionId));
      const data = response.data ?? {};
      return {
        ...data,
        progress: normalizeProgressSnapshot(data.progress),
        symptom_summary: normalizeSymptomSummary(data.symptom_summary),
        module_timeline: data.module_timeline ?? data.progress?.module_timeline ?? null,
      };
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get session progress
  const getProgress = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSION_PROGRESS(sessionId));
      const data = response.data ?? {};
      return {
        ...data,
        progress_snapshot: normalizeProgressSnapshot(data.progress_snapshot ?? data),
        symptom_summary: normalizeSymptomSummary(data.symptom_summary),
      };
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get enhanced progress
  const getEnhancedProgress = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSION_ENHANCED_PROGRESS(sessionId));
      const data = response.data ?? {};
      return {
        ...data,
        progress_snapshot: normalizeProgressSnapshot(data.progress_snapshot ?? data),
        symptom_summary: normalizeSymptomSummary(data.symptom_summary),
      };
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get session results
  const getResults = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSION_RESULTS(sessionId));
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get assessment result
  const getAssessmentResult = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.ASSESSMENT_RESULT(sessionId));
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get session history
  const getHistory = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSION_HISTORY(sessionId));
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get session analytics
  const getAnalytics = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSION_ANALYTICS(sessionId));
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get comprehensive report
  const getComprehensiveReport = useCallback(async (sessionId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.SESSION_COMPREHENSIVE_REPORT(sessionId));
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get comprehensive assessment data (includes all module results, TPA, DA, SRA)
  const getAssessmentData = useCallback(async (sessionId, format = 'json') => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(
        API_ENDPOINTS.ASSESSMENT.SESSION_ASSESSMENT_DATA(sessionId),
        { params: { format } }
      );
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Switch module
  const switchModule = useCallback(async (sessionId, moduleName) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.post(API_ENDPOINTS.ASSESSMENT.SESSION_SWITCH_MODULE(sessionId), {
        module_name: moduleName
      });
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get available modules
  const getModules = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.MODULES);
      return response.data;
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Health check
  const getHealth = useCallback(async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.ASSESSMENT.HEALTH);
      return response.data;
    } catch (err) {
      console.error('Health check error:', err);
      throw err;
    }
  }, []);

  return {
    // State
    isLoading,
    error,
    
    // Core Actions
    getSessions,
    startSession,
    continueSession,
    deleteSession,
    saveSession,
    loadSession,
    
    // Progress & Results
    getProgress,
    getEnhancedProgress,
    getResults,
    getAssessmentResult,
    getHistory,
    
    // Analytics & Reports
    getAnalytics,
    getComprehensiveReport,
    getAssessmentData,
    
    // Module Management
    switchModule,
    getModules,
    
    // Utilities
    getHealth,
    clearError: () => setError(null)
  };
};
