import React, { useState} from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, SignupData } from '../contexts';
import { signupSchema } from '../schemas/authSchema';

const SignupPage: React.FC = () => {
  const [formData, setFormData] = useState<SignupData>({
    username: '',
    phone: '',
    password: '',
    password_confirm: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  const { signup } = useAuth();
  const navigate = useNavigate();

 

  const validateSingleField = (name: string, value: string) => {
    const dataToValidate = { ...formData, confirmPassword, [name]: value };
    const result = signupSchema.safeParse(dataToValidate);
    
    if (!result.success) {
      const fieldError = result.error.issues.find(issue => issue.path.includes(name));
      setFieldErrors(prev => ({
        ...prev,
        [name]: fieldError ? fieldError.message : ''
      }));
    } else {

      setFieldErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    validateSingleField(name, value);
  };

  const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setConfirmPassword(value);
    setFormData(prev => ({ ...prev, password_confirm: value }));
    validateSingleField('confirmPassword', value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const result = signupSchema.safeParse(formData);
    
    if (!result.success) {
      const errors: Record<string, string> = {};
      result.error.issues.forEach(issue => {
        const pathKey = issue.path[0];
        if (typeof pathKey === 'string') {
          errors[pathKey] = issue.message;
        }
      });
      setFieldErrors(errors);
      setIsLoading(false);
      return;
    }

    try {
      await signup(formData);
      navigate('/');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'خطایی در ثبت‌نام رخ داد';
      setFieldErrors({ form: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };


  const ErrorMsg = ({ name }: { name: string }) => (
    fieldErrors[name] ? (
      <p className="text-red-500 text-xs mt-1 animate-pulse">{fieldErrors[name]}</p>
    ) : null
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-slate-50 to-sky-50/30 flex items-center justify-center font-iransans p-4" dir="rtl">
      <div className="max-w-md w-full bg-white/95 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-neutral-200/70 animate-scale-in">
        
        {/* Header with same style as LoginPage */}
        <header className="relative overflow-hidden bg-gradient-to-l from-sky-700 via-sky-800 to-sky-900 -m-8 mb-6 p-6 text-white rounded-t-2xl">
          {/* decorative circles */}
          <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-white/5" />
          <div className="pointer-events-none absolute -bottom-16 left-1/3 h-48 w-48 rounded-full bg-sky-400/10" />
          <div className="pointer-events-none absolute -right-10 top-4 h-32 w-32 rounded-full bg-sky-300/8" />
          
          <div className="relative text-center">
            <div className="mx-auto w-16 h-16 bg-white/15 backdrop-blur-sm rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <svg className="w-8 h-8 text-sky-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white">ایجاد حساب کاربری</h2>
          </div>
        </header>
        
        <div className="text-center mb-6">
          <p className="text-sm text-neutral-600">
            یا <Link to="/login" className="underline font-bold text-sky-700 hover:text-sky-500">وارد حساب خود شوید</Link>
          </p>
        </div>
        
        <form className="space-y-4" onSubmit={handleSubmit}>
          <ErrorMsg name="form" />

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">شماره تلفن</label>
            <input name="phone" type="tel" dir="ltr" value={formData.phone} onChange={handleChange} className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all" placeholder="09123456789" />
            <ErrorMsg name="phone" />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">نام کاربری</label>
            <input name="username" value={formData.username} onChange={handleChange} className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all" placeholder="User123" />
            <ErrorMsg name="username" />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">رمز عبور</label>
            <input name="password" type="password" dir="ltr" value={formData.password} onChange={handleChange} className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all" placeholder="••••••••" />
            <ErrorMsg name="password" />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">تکرار رمز عبور</label>
            <input name="confirmPassword" type="password" dir="ltr" value={confirmPassword} onChange={handleConfirmPasswordChange} className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all" placeholder="••••••••" />
            <ErrorMsg name="confirmPassword" />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 mt-4 bg-gradient-to-l from-sky-600 to-sky-700 hover:from-sky-700 hover:to-sky-800 text-white font-bold rounded-xl transition-all transform hover:scale-[1.01] shadow-lg disabled:opacity-50"
          >
            {isLoading ? 'در حال ثبت‌نام...' : 'تایید و ایجاد حساب'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignupPage;