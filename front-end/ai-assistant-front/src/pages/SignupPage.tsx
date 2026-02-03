import React, { useState} from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, SignupData } from '../contexts';
// فرض بر این است که توابع را در فایل authSchema.ts ذخیره کرده‌اید
import { signupSchema } from '../schemas/authSchema';

const SignupPage: React.FC = () => {
  const [formData, setFormData] = useState<SignupData>({
    username: '',
    phone: '',
    password: '',
    password_confirm: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // ذخیره خطاها برای هر فیلد به صورت مجزا
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  const { signup } = useAuth();
  const navigate = useNavigate();

 

  // تابع کمکی برای اعتبارسنجی لحظه‌ای هر فیلد
  const validateSingleField = (name: string, value: string) => {
    const dataToValidate = { ...formData, confirmPassword, [name]: value };
    const result = signupSchema.safeParse(dataToValidate);
    
    if (!result.success) {
      // پیدا کردن خطای مربوط به همین فیلد خاص
      const fieldError = result.error.issues.find(issue => issue.path.includes(name));
      setFieldErrors(prev => ({
        ...prev,
        [name]: fieldError ? fieldError.message : ''
      }));
    } else {
      // اگر کل فرم معتبر بود، خطاها را پاک کن
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
      // استخراج تمام خطاها و نمایش آن‌ها
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
      navigate('/dashboards');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'خطایی در ثبت‌نام رخ داد';
      setFieldErrors({ form: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  // کامپوننت کوچک برای نمایش پیام خطا زیر هر اینپوت
  const ErrorMsg = ({ name }: { name: string }) => (
    fieldErrors[name] ? (
      <p className="text-red-500 text-xs mt-1 animate-pulse">{fieldErrors[name]}</p>
    ) : null
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 flex items-center justify-center font-iransans p-4" dir="rtl">
      <div className="max-w-md w-full bg-white/95 backdrop-blur-sm p-8 rounded-2xl shadow-2xl border border-sky-100">
        
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-sky-900 mb-2">ایجاد حساب کاربری</h2>
          <p className="text-sky-600">
            یا <Link to="/login" className="underline font-medium hover:text-sky-500">وارد حساب خود شوید</Link>
          </p>
        </div>
        
        <form className="space-y-4" onSubmit={handleSubmit}>
          {/* خطای کلی فرم */}
          <ErrorMsg name="form" />

          <div>
            <label className="block text-sm font-medium text-sky-700 mb-1">شماره تلفن</label>
            <input name="phone" type="tel" dir="ltr" value={formData.phone} onChange={handleChange} className="w-full px-3 py-2 border border-sky-300 rounded-lg focus:ring-2 focus:ring-sky-500 outline-none" placeholder="09123456789" />
            <ErrorMsg name="phone" />
          </div>

          <div>
            <label className="block text-sm font-medium text-sky-700 mb-1">نام کاربری</label>
            <input name="username" value={formData.username} onChange={handleChange} className="w-full px-3 py-2 border border-sky-300 rounded-lg focus:ring-2 focus:ring-sky-500 outline-none" placeholder="User123" />
            <ErrorMsg name="username" />
          </div>

          <div>
            <label className="block text-sm font-medium text-sky-700 mb-1">رمز عبور</label>
            <input name="password" type="password" dir="ltr" value={formData.password} onChange={handleChange} className="w-full px-3 py-2 border border-sky-300 rounded-lg focus:ring-2 focus:ring-sky-500 outline-none" placeholder="••••••••" />
            <ErrorMsg name="password" />
          </div>

          <div>
            <label className="block text-sm font-medium text-sky-700 mb-1">تکرار رمز عبور</label>
            <input name="confirmPassword" type="password" dir="ltr" value={confirmPassword} onChange={handleConfirmPasswordChange} className="w-full px-3 py-2 border border-sky-300 rounded-lg focus:ring-2 focus:ring-sky-500 outline-none" placeholder="••••••••" />
            <ErrorMsg name="confirmPassword" />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 mt-4 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-lg transition-all disabled:opacity-50"
          >
            {isLoading ? 'در حال ثبت‌نام...' : 'تایید و ایجاد حساب'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignupPage;