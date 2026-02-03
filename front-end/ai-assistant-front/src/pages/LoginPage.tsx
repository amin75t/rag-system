import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts';
// اسکیما و تایپ‌ها را ایمپورت می‌کنیم
import { loginSchema, LoginFormData } from '../schemas/authSchema';

const LoginPage: React.FC = () => {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  
  // مدیریت خطاها به صورت تفکیک شده
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  // تشخیص دستگاه موبایل
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

 

  // تابع کمکی برای اعتبارسنجی تکی (Real-time)
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
    
    // اعتبارسنجی نهایی با Zod
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
      // لاگین از طریق Context (شامل لاگیک Fetch و ذخیره توکن)
      await login(phone, password);
      navigate('/');
    } catch (err: unknown) {
      // نمایش خطای سمت سرور
      const errorMessage = err instanceof Error ? err.message : 'شماره تلفن یا رمز عبور اشتباه است';
      setFieldErrors({ form: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 flex items-center justify-center font-iransans p-4`} dir="rtl">
      <div className={`max-w-md w-full bg-white/95 backdrop-blur-sm ${isMobile ? 'p-6' : 'p-8'} rounded-2xl shadow-2xl border border-sky-100`}>
        
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-sky-500 to-sky-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4 4m-4-4v4m0 0v4M12 4a8 8 0 100 16 8 8 0 000-16z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-sky-900 mb-2">ورود به پنل کاربری</h2>
          <p className="text-sm text-sky-600">
            هنوز ثبت‌نام نکرده‌اید؟ {' '}
            <Link to="/signup" className="font-bold text-sky-700 hover:text-sky-500 underline transition-colors">ایجاد حساب جدید</Link>
          </p>
        </div>
        
        <form className="space-y-5" onSubmit={handleSubmit}>
          {/* خطای کلی (مثل خطای سرور) */}
          {fieldErrors.form && (
            <div className="bg-red-50 border border-red-200 text-red-600 p-3 rounded-lg text-xs flex items-center animate-shake">
              {fieldErrors.form}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-sky-700 mb-2">شماره تلفن</label>
            <input
              type="tel"
              value={phone}
              onChange={handlePhoneChange}
              dir="ltr"
              className={`block w-full px-4 py-3 border rounded-xl shadow-sm focus:ring-2 focus:ring-sky-500 outline-none transition-all ${
                fieldErrors.phone ? 'border-red-400 bg-red-50' : 'border-sky-200'
              }`}
              placeholder="09123456789"
            />
            {fieldErrors.phone && <p className="text-red-500 text-[11px] mt-1 mr-1 font-bold">{fieldErrors.phone}</p>}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-sky-700 mb-2">رمز عبور</label>
            <input
              type="password"
              value={password}
              onChange={handlePasswordChange}
              dir="ltr"
              className={`block w-full px-4 py-3 border rounded-xl shadow-sm focus:ring-2 focus:ring-sky-500 outline-none transition-all ${
                fieldErrors.password ? 'border-red-400 bg-red-50' : 'border-sky-200'
              }`}
              placeholder="••••••••"
            />
            {fieldErrors.password && <p className="text-red-500 text-[11px] mt-1 mr-1 font-bold">{fieldErrors.password}</p>}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 disabled:opacity-50 transition-all transform hover:scale-[1.01]"
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