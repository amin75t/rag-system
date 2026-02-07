import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLayoutContext, useAuth } from "../contexts";
import ChatWidget from "../components/ChatWidget";


export default function HomePage() {
  const { isSidebarOpen, toggleSidebar } = useLayoutContext();
  const { user, login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isChatExpanded, setIsChatExpanded] = useState(false);

  // Auto-login with specified credentials
  useEffect(() => {
    const autoLogin = async () => {
      try {
        // Send login data to backend
        const response = await fetch('http://localhost:8000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password123'
          }),
        });

        if (!response.ok) {
          throw new Error('Login failed');
        }

        const data = await response.json();
        
        // Store token and user data
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Update auth context
        await login('test@example.com', 'password123');
        
      } catch (error) {
        console.error('Auto-login error:', error);
      }
    };

    // Only auto-login if not already authenticated
    if (!isAuthenticated) {
      autoLogin();
    }
  }, [login, isAuthenticated]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 p-8 font-iransans" dir="rtl">
      {!isSidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="fixed top-4 right-4 z-40 p-2 bg-sky-800 text-white rounded-md shadow-lg hover:bg-sky-700 transition-colors"
          aria-label="Open menu"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}
      <div className="text-center">
        <h1 className="md:text-5xl text-3xl mt-4 md:mt-0 font-bold text-sky-900 mb-4 drop-shadow-md">داشبورد جامع RAG System</h1>
        <p className="text-xl text-sky-700 max-w-2xl mx-auto">سیستم مدیریت و نمایش اطلاعات هوشمند</p>
        {user && (
          <p className="text-lg text-sky-600 mb-6">
            خوش آمدید، {user.first_name && user.last_name
              ? `${user.first_name} ${user.last_name}`
              : user.username
            }!
          </p>
        )}
        
        <div className="mt-12 bg-white/80 backdrop-blur-md rounded-xl p-8 max-w-2xl mx-auto shadow-xl border border-sky-200">
          <h2 className="text-2xl font-semibold text-sky-800 mb-4">به داشبورد جامع خوش آمدید</h2>
          <p className="text-sky-600 leading-relaxed mb-6">
            از منوی سمت راست برای دسترسی به بخش‌های مختلف سیستم استفاده کنید. شما می‌توانید به داشبوردهای Superset و داشبورد بوشهر دسترسی داشته باشید.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => navigate('/dashboards')}
              className="bg-sky-600 hover:bg-sky-700 text-white font-medium py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
            >
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              داشبوردهای Superset
            </button>
            
            <button
              onClick={() => navigate('/busher')}
              className="bg-sky-600 hover:bg-sky-700 text-white font-medium py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
            >
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 13h8V3H3v8zm0 0v8h8V3zm0 0v8h8v-2H3v10zm0 0v8h8v-2H3v10z" />
              </svg>
              داشبورد بوشهر
            </button>
          </div>
        </div>
      </div>
      
      {/* Chat Widget */}
      <ChatWidget 
        isExpanded={isChatExpanded} 
        onToggle={() => setIsChatExpanded(!isChatExpanded)} 
      />
    </div>
  );
}