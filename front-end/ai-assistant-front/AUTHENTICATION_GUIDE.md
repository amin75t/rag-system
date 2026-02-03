# راهنمای احراز هویت با Zod

## 📋 جدول محتویات

| ویژگی | وضعیت | توضیحات |
|--------|--------|--------|
| ✅ Zod Schema | ✅ پیاده‌سازی شده | پیام‌های فارسی، اعتبارسنجی قوی |
| ✅ فرم‌های پیش‌فرم | ✅ داده‌های آزمایشی |
| ✅ اعتبارسنجی واقعی-زنده | ✅ طراحی واکنش‌گرا |
| ✅ اتصال به بک‌اند | ✅ مستندات کامل API |

## 🚀 راهنمای استفاده

### ۱. نصب پیش‌نیازها
```bash
npm install zod
```

### ۲. استفاده در کامپوننت‌ها

#### صفحه لاگین:
```typescript
import { validateLoginForm } from '../schemas/authSchema';

const LoginPage = () => {
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // اعتبارسنجی با Zod
    const formData = { email, password };
    const validationResult = validateLoginForm(formData);
    
    if (!validationResult.success) {
      setError(validationResult.error?.message || 'خطا در اعتبارسنجی');
      return;
    }
    
    // ارسال به بک‌اند
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // موفقیت‌آمیز
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    // JSX با فرم و اعتبارسنجی
  );
};
```

#### صفحه ثبت‌نام:
```typescript
import { validateSignupForm } from '../schemas/authSchema';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: 'testuser',
    email: 'test@example.com',
    password: 'password123',
    firstName: 'کاربر',
    lastName: 'آزمایشی',
    confirmPassword: 'password123',
  });
  
  const [error, setError] = useState(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // اعتبارسنجی با Zod
    const validationResult = validateSignupForm(formData);
    
    if (!validationResult.success) {
      setError(validationResult.error?.message || 'خطا در اعتبارسنجی');
      return;
    }
    
    // ارسال به بک‌اند
    try {
      await signup(formData);
      // موفقیت‌آمیز
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    // JSX با فرم و اعتبارسنجی
  );
};
```

### ۳. اعتبارسنجی زنده

#### اعتبارسنجی ایمیل:
```typescript
import { validateEmail } from '../schemas/authSchema';

const EmailInput = ({ value, onChange, error }) => {
  const validation = validateEmail(value);
  
  return (
    <input
      value={value}
      onChange={onChange}
      className={`border rounded-lg ${
        error && error.includes('ایمیل') ? 'border-red-500' : 'border-gray-300'
      }`}
    />
  );
};
```

#### اعتبارسنجی رمز عبور:
```typescript
import { validatePassword } from '../schemas/authSchema';

const PasswordInput = ({ value, onChange, error }) => {
  const validation = validatePassword(value);
  
  return (
    <input
      type="password"
      value={value}
      onChange={onChange}
      className={`border rounded-lg ${
        error && error.includes('رمز عبور') ? 'border-red-500' : 'border-gray-300'
      }`}
    />
  );
};
```

## 🔧 توابع Zod مفید

### validateLoginForm()
اعتبارسنجی فرم لاگین با Zod schema
```typescript
const result = validateLoginForm({ email, password });
if (!result.success) {
  // نمایش خطا
  console.error(result.error);
  return false;
}
// result.data حاوی داده‌های معتبر است
```

### validateSignupForm()
اعتبارسنجی فرم ثبت‌نام با Zod schema
```typescript
const result = validateSignupForm(formData);
if (!result.success) {
  // نمایش خطا
  console.error(result.error);
  return false;
}
// result.data حاوی داده‌های معتبر است
```

### validateEmail(), validatePassword(), validateUsername(), validateName()
اعتبارسنجی تک فیلدها به صورت جداگانه
```typescript
const emailResult = validateEmail(email);
if (!emailResult.success) {
  return { isValid: false, error: emailResult.error };
}

const passwordResult = validatePassword(password);
if (!passwordResult.success) {
  return { isValid: false, error: passwordResult.error };
}
```

## 🎨 نکات مهم

### ۱. همیشه از `safeParse` استفاده کنید
هرگز از `parse()` استفاده نکنید چون ممکن است خطا پرتابد کند

### ۲. پیام‌های خطا را کاربرپسند کنید
- از ثابت `PERSIAN_ERROR_MESSAGES` استفاده کنید
- پیام‌ها باید واضح و کوتاه باشند

### ۳. فرم‌های پیش‌فرم برای تست
- برای تست سریع، فرم‌ها با داده‌های آزمایشی پر شده‌اند
- کاربران می‌توانند بدون نیاز به تایپ کردن، تست کنند

### ۴. اتصال به بک‌اند
- از `fetch` یا کتابخانه HTTP مانند `axios` استفاده کنید
- توکن JWT را در `localStorage` ذخیره کنید
- از `authService` برای مدیریت احراز هویت استفاده کنید

## 📚 مثال کامل

```typescript
// کامپوننت لاگین کامل
import React, { useState } from 'react';
import { useAuth } from '../contexts';
import { validateLoginForm } from '../schemas/authSchema';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // اعتبارسنجی با Zod
    const formData = { email, password };
    const validationResult = validateLoginForm(formData);
    
    if (!validationResult.success) {
      setError(validationResult.error?.message || 'خطا در اعتبارسنجی');
      return;
    }
    
    try {
      // ارسال به بک‌اند
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      // ذخیره توکن و اطلاعات کاربر
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // به‌روزرسانی context
      await login(formData.email, formData.password);
      
      // هدایت به صفحه اصلی
      navigate('/');
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200">
      <form onSubmit={handleSubmit}>
        {/* فرم با اعتبارسنجی Zod */}
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded">
            {error}
          </div>
        )}
        
        <button type="submit">
          ورود
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
```

## 🔄 به‌روزرسانی وضعیت

```typescript
// در AuthProvider
const { token } = localStorage.getItem('authToken');
const { user } = localStorage.getItem('user');

if (token && user) {
  // کاربر لاگین است
  // به‌روزرسانی context با اطلاعات کاربر
}
```

## 📖 مستندات API

برای مستندات کامل API، فایل `API_DOCUMENTATION.md` را مطالعه کنید که شامل:
- Endpointهای کامل با نمونه Response
- نمونه سرور Express با MongoDB
- نحوه نصب پیش‌نیازها
- نحوه استفاده از Zod
- مثال کد کامل

حالا سیستم شما دارای احراز هویت کامل با:
- ✅ Zod validation
- ✅ پیام‌های فارسی
- ✅ فرم‌های پیش‌فرم
- ✅ اعتبارسنجی واقعی-زنده
- ✅ طراحی واکنش‌گرا
- ✅ اتصال به بک‌اند
- ✅ مستندات کامل