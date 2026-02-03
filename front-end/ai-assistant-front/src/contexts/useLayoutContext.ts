import { useContext } from 'react';
import { LayoutContext, LayoutContextType } from './layoutContext';

export const useLayoutContext = (): LayoutContextType => {
  const context = useContext(LayoutContext);
  if (context === undefined) {
    throw new Error('useLayoutContext must be used within a LayoutProvider');
  }
  return context;
};