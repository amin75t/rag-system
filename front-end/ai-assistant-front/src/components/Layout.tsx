import React from 'react';
import { useLayoutContext } from '../contexts';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isSidebarOpen, isMobile, toggleSidebar } = useLayoutContext();

  return (
    <div className="min-h-screen font-iransans" dir="rtl">
      {/* Mobile Menu Button */}
      {isMobile && !isSidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="fixed top-4 right-4 z-50 p-2 bg-sky-800 text-white rounded-md shadow-lg hover:bg-sky-700 transition-colors"
          aria-label="Open menu"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}

      {/* Sidebar Overlay for Mobile */}
      {isMobile && isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar - Fixed on desktop, overlay on mobile */}
      <div className={`${isMobile ? 'fixed inset-y-0 right-0 z-50' : 'fixed inset-y-0 right-0'} transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'}`}>
        <Sidebar
          isCollapsed={!isSidebarOpen}
          onToggle={toggleSidebar}
          isMobile={isMobile}
        />
      </div>

      {/* Main Content */}
      <div className={`transition-all duration-300 ${isMobile ? 'w-full' : isSidebarOpen ? 'mr-64' : 'mr-16'} min-h-screen relative`}>
        {/* Menu Button for Desktop when sidebar is collapsed */}
        
        {children}
      </div>
    </div>
  );
};

export default Layout;