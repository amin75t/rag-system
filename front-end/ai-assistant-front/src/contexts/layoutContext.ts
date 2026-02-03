import { createContext } from 'react';

export interface LayoutContextType {
  isSidebarOpen: boolean;
  isMobile: boolean;
  toggleSidebar: () => void;
  closeSidebar: () => void;
  openSidebar: () => void;
}

export const LayoutContext = createContext<LayoutContextType | undefined>(undefined);