import React from 'react';
import { useNavigate } from 'react-router-dom';

interface MenuButtonProps {
  onToggleSidebar: () => void;
  currentPage?: string;
}

const MenuButton: React.FC<MenuButtonProps> = ({ onToggleSidebar, currentPage }) => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate('/');
  };

  return (
    <div className="flex items-center justify-between p-4 bg-white shadow-sm border-b border-gray-200">
      <button
        onClick={onToggleSidebar}
        className="p-2 rounded-md bg-sky-800 text-white hover:bg-sky-700 transition-colors"
        aria-label="Open menu"
      >
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {currentPage && (
        <div className="flex items-center gap-2">
          <button
            onClick={handleBackClick}
            className="p-2 rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
            aria-label="Back to home"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <span className="text-sm font-medium text-gray-700">{currentPage}</span>
        </div>
      )}
    </div>
  );
};

export default MenuButton;