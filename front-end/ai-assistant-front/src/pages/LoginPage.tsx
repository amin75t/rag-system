import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts';
import { loginSchema, LoginFormData } from '../schemas/authSchema';

const LoginPage: React.FC = () => {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

 

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

 


  const validateField = (name: string, value: string) => {
    const dataToValidate = { phone, password, [name]: value };
    const result = loginSchema.safeParse(dataToValidate);
    
    if (!result.success) {
      const error = result.error.issues.find(issue => issue.path.includes(name));
      setFieldErrors(prev => ({ ...prev, [name]: error ? error.message : '' }));
    } else {
      setFieldErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setPhone(val);
    validateField('phone', val);
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setPassword(val);
    validateField('password', val);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFieldErrors({});
    
  
    const formData: LoginFormData = { phone, password };
    const result = loginSchema.safeParse(formData);
    
    if (!result.success) {
      const errors: Record<string, string> = {};
      result.error.issues.forEach(issue => {
        const pathKey = issue.path[0];
        if (typeof pathKey === 'string') {
          errors[pathKey] = issue.message;
        }
      });
      setFieldErrors(errors);
      return;
    }

    setIsLoading(true);

    try {
      await login(phone, password);
      navigate('/');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'شماره تلفن یا رمز عبور اشتباه است';
      setFieldErrors({ form: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`min-h-screen bg-gradient-to-b from-slate-50 via-slate-50 to-sky-50/30 flex items-center justify-center font-iransans p-4`} dir="rtl">
      <div className={`max-w-md w-full bg-white/95 backdrop-blur-sm ${isMobile ? 'p-6' : 'p-8'} rounded-2xl shadow-xl border border-neutral-200/70 animate-scale-in`}>
        
        {/* Header with busher-ui style */}
        <header className="relative overflow-hidden bg-gradient-to-l from-sky-700 via-sky-800 to-sky-900 -m-8 mb-6 p-6 text-white rounded-t-2xl">
          {/* decorative circles */}
          <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-white/5" />
          <div className="pointer-events-none absolute -bottom-16 left-1/3 h-48 w-48 rounded-full bg-sky-400/10" />
          <div className="pointer-events-none absolute -right-10 top-4 h-32 w-32 rounded-full bg-sky-300/8" />
          
          <div className="relative text-center">
            <div className="mx-auto w-16 h-16 bg-white/15 backdrop-blur-sm rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <svg className="w-8 h-8 text-sky-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4 4m-4-4v4m0 0v4M12 4a8 8 0 100 16 8 8 0 000-16z" />
              </svg>
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white">ورود به پنل کاربری</h2>
          </div>
        </header>
        
        <div className="text-center mb-6">
          <p className="text-sm text-neutral-600">
            هنوز ثبت‌نام نکرده‌اید؟ {' '}
            <Link to="/signup" className="font-bold text-sky-700 hover:text-sky-500 underline transition-colors">ایجاد حساب جدید</Link>
          </p>
        </div>
        
        <form className="space-y-5" onSubmit={handleSubmit}>
          {fieldErrors.form && (
            <div className="bg-red-50 border border-red-200 text-red-600 p-3 rounded-xl text-xs flex items-center animate-shake">
              {fieldErrors.form}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">شماره تلفن</label>
            <input
              type="tel"
              value={phone}
              onChange={handlePhoneChange}
              dir="ltr"
              className={`block w-full px-4 py-3 border rounded-xl shadow-sm focus:ring-2 focus:ring-sky-500 outline-none transition-all ${
                fieldErrors.phone ? 'border-red-400 bg-red-50' : 'border-neutral-200'
              }`}
              placeholder="09123456789"
            />
            {fieldErrors.phone && <p className="text-red-500 text-[11px] mt-1 mr-1 font-bold">{fieldErrors.phone}</p>}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">رمز عبور</label>
            <input
              type="password"
              value={password}
              onChange={handlePasswordChange}
              dir="ltr"
              className={`block w-full px-4 py-3 border rounded-xl shadow-sm focus:ring-2 focus:ring-sky-500 outline-none transition-all ${
                fieldErrors.password ? 'border-red-400 bg-red-50' : 'border-neutral-200'
              }`}
              placeholder="••••••••"
            />
            {fieldErrors.password && <p className="text-red-500 text-[11px] mt-1 mr-1 font-bold">{fieldErrors.password}</p>}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-gradient-to-l from-sky-600 to-sky-700 hover:from-sky-700 hover:to-sky-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 disabled:opacity-50 transition-all transform hover:scale-[1.01] shadow-lg"
          >
            {isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin h-5 w-5 ml-2 border-b-2 border-white rounded-full" viewBox="0 0 24 24"></svg>
                در حال احراز هویت...
              </span>
            ) : 'ورود به حساب'}
          </button>

          
        </form>
      </div>
    </div>
  );
};

export default LoginPage;