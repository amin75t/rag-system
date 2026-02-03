import { createContext } from 'react';

export interface User {
  id: number;
  username: string;
  phone: string;
  first_name?: string;
  last_name?: string;
  created_at?: string;
  roles?: string[];
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (phone: string, password: string) => Promise<void>;
  signup: (userData: SignupData) => Promise<void>;
  logout: () => void;
  getProfile: () => Promise<User>;
  updateProfile: (profileData: ProfileData) => Promise<User>;
}

export interface ProfileData {
  phone?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
}

export interface SignupData {
  username: string;
  phone: string;
  password: string;
  password_confirm: string;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);