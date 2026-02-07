import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useLayoutContext, useAuth } from '../contexts';

interface SidebarProps {
  isCollapsed?: boolean;
  onToggle?: () => void;
  isMobile?: boolean;
}

interface SidebarItem {
  id: string;
  name: string;
  icon: React.ReactNode;
  path: string;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed = false, onToggle, isMobile = false }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { closeSidebar } = useLayoutContext();
  const { user, logout } = useAuth();

  const sidebarItems: SidebarItem[] = [
    {
      id: 'home',
      name: 'خانه',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
      path: '/'
    },
   
    {
      id: 'bushehr',
      name: 'بوشهر در یک نگاه',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 13h8V3H3v8zm0 0v8h8V3zm0 0v8h8v-2H3v10zm0 0v8h8v-2H3v10z" />
        </svg>
      ),
      path: '/busher'
    },
    {
      id: 'chat',
      name: 'دستیار هوشمند',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      path: '/chat'
    },
    {
      id: 'profile',
      name: 'پروفایل',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
      path: '/profile'
    }
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const handleItemClick = (path: string) => {
    navigate(path);
    // Close sidebar on mobile after navigation
    if (isMobile) {
      closeSidebar();
    }
  };

  const handleToggle = () => {
    if (onToggle) {
      onToggle();
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
      if (isMobile) {
        closeSidebar();
      }
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className={`bg-gradient-to-b from-sky-800 to-sky-900 text-white transition-all duration-300 ease-in-out ${isCollapsed ? 'w-16' : 'w-64'} min-h-screen flex flex-col font-iransans ${isMobile ? 'h-full' : ''}`} dir="rtl">
      <div className="p-4">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <h1 className="text-xl font-bold text-white">RAG System</h1>
          )}
          <button
            onClick={handleToggle}
            className="p-1 rounded-md hover:bg-sky-700/50 transition-colors"
            aria-label={isCollapsed ? "Open sidebar" : "Close sidebar"}
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {isMobile ? (
                // Close icon for mobile
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                // Toggle icon for desktop
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isCollapsed ? "M15 5l-7 7 7 7" : "M9 19l7-7-7-7"} />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* User info section */}
      {!isCollapsed && user && (
        <div className="px-4 py-3 border-b border-sky-700">
          <div className="flex items-center space-x-reverse space-x-3">
          
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user.first_name && user.last_name
                  ? `${user.first_name} ${user.last_name}`
                  : user.username
                }
              </p>
              <p className="text-xs text-sky-300 truncate">
                {user.phone}
              </p>
            </div>
          </div>
        </div>
      )}

      <nav className="flex-1 px-2 space-y-2">
        {sidebarItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleItemClick(item.path)}
            className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'justify-start'} px-3 py-2 rounded-md transition-colors ${
              isActive(item.path)
                ? 'bg-sky-600 text-white'
                : 'text-sky-100 hover:bg-sky-700/50 hover:text-white'
            }`}
            title={isCollapsed ? item.name : undefined}
          >
            <span className="flex-shrink-0">{item.icon}</span>
            {!isCollapsed && (
              <span className="mr-3 text-sm font-medium">{item.name}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-sky-700 space-y-2">
        {/* Logout button */}
        <button
          onClick={handleLogout}
          className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'justify-start'} px-3 py-2 rounded-md transition-colors text-sky-100 hover:bg-red-600/50 hover:text-white`}
          title={isCollapsed ? "خروج" : undefined}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          {!isCollapsed && (
            <span className="mr-3 text-sm font-medium">خروج</span>
          )}
        </button>
        
        {!isCollapsed && (
          <div className="text-xs text-sky-200">
            <p>سیستم مدیریت هوشمند</p>
            <p>نسخه 1.0.0</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;