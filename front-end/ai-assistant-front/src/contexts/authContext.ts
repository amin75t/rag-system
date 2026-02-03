import { createContext } from 'react';

export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  roles?: string[];
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (phone: string, password: string) => Promise<void>;
  signup: (userData: SignupData) => Promise<void>;
  logout: () => void;
}

export interface SignupData {
  username: string;
  phone: string;
  password: string;
  password_confirm: string;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);