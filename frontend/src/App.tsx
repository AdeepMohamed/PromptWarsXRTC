import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuthContext } from "./contexts/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";

// Pages
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { OnboardingPage } from "./pages/OnboardingPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SkillDNAPage } from "./pages/SkillDNAPage";
import { SkillGapsPage } from "./pages/SkillGapsPage";
import { CareersPage } from "./pages/CareersPage";
import { SimulatorPage } from "./pages/SimulatorPage";
import { RoadmapPage } from "./pages/RoadmapPage";
import { AssessmentsPage } from "./pages/AssessmentsPage";
import { AssessmentDetailPage } from "./pages/AssessmentDetailPage";
import { MentorPage } from "./pages/MentorPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { AgentCenterPage } from "./pages/AgentCenterPage";
import { SettingsPage } from "./pages/SettingsPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthContext();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">
        <div className="text-sm font-medium">Verifying Session...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export function AppRoutes() {
  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <OnboardingPage />
          </ProtectedRoute>
        }
      />

      {/* Protected Dashboard & Command Center */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/skill-dna" element={<SkillDNAPage />} />
        <Route path="/skill-gaps" element={<SkillGapsPage />} />
        <Route path="/careers" element={<CareersPage />} />
        <Route path="/simulator" element={<SimulatorPage />} />
        <Route path="/roadmap" element={<RoadmapPage />} />
        <Route path="/assessments" element={<AssessmentsPage />} />
        <Route path="/assessments/:id" element={<AssessmentDetailPage />} />
        <Route path="/mentor" element={<MentorPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/agent-center" element={<AgentCenterPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

import api from "./lib/api";

function BackendWarmup() {
  React.useEffect(() => {
    // 1. Instantly trigger background wake-up probe when visitor loads app
    api.get("/health").catch(() => {});

    // 2. Heartbeat every 4 minutes while browser tab is open to keep container active
    const timer = setInterval(() => {
      api.get("/health").catch(() => {});
    }, 4 * 60 * 1000);

    return () => clearInterval(timer);
  }, []);

  return null;
}

export default function App() {
  return (
    <AuthProvider>
      <BackendWarmup />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
