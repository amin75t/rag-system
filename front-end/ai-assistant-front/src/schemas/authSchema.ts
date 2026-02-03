import { z } from 'zod';

// ۱. لیست متمرکز پیام‌های خطا (فقط فارسی)
const PERSIAN_ERROR_MESSAGES = {
  email_invalid: 'ایمیل وارد شده معتبر نیست',
  email_required: 'وارد کردن ایمیل الزامی است',
  password_min: 'رمز عبور باید حداقل ۶ کاراکتر باشد',
  password_required: 'وارد کردن رمز عبور الزامی است',
  password_match: 'رمز عبور و تکرار آن یکسان نیستند',
  username_min: 'نام کاربری باید حداقل ۳ کاراکتر باشد',
  username_required: 'نام کاربری الزامی است',
  name_min: 'نام باید حداقل ۲ کاراکتر باشد',
  name_required: 'وارد کردن نام الزامی است',
};

// ۲. تعریف اسکیماهای پایه برای جلوگیری از تکرار کد
const emailSchema = z
  .string(PERSIAN_ERROR_MESSAGES.email_required)
  .min(1, PERSIAN_ERROR_MESSAGES.email_required)
  .email(PERSIAN_ERROR_MESSAGES.email_invalid);

const passwordSchema = z
  .string(PERSIAN_ERROR_MESSAGES.password_required)
  .min(6, PERSIAN_ERROR_MESSAGES.password_min);

const nameSchema = z
  .string(PERSIAN_ERROR_MESSAGES.name_required)
  .min(2, PERSIAN_ERROR_MESSAGES.name_min);

const usernameSchema = z
  .string(PERSIAN_ERROR_MESSAGES.username_required)
  .min(3, PERSIAN_ERROR_MESSAGES.username_min);

// ۳. اسکیمای نهایی برای فرم‌ها
export const loginSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
});

export const signupSchema = z.object({
  username: usernameSchema,
  email: emailSchema,
  password: passwordSchema,
  firstName: nameSchema,
  lastName: nameSchema,
  confirmPassword: z.string(PERSIAN_ERROR_MESSAGES.password_required),
}).refine((data) => data.password === data.confirmPassword, {
  message: PERSIAN_ERROR_MESSAGES.password_match,
  path: ['confirmPassword'],
});

/**
 * ۴. تابع کمکی هوشمند برای اعتبارسنجی لحظه‌ای (Real-time)
 * این تابع فقط متن فارسی را برمی‌گرداند و از شلوغی جلوگیری می‌کند
 */
const validateField = (schema: z.ZodSchema, value: string) => {
  const result = schema.safeParse(value);
  if (!result.success) {
    // فقط اولین پیام خطا (فارسی) را استخراج می‌کنیم
    return { isValid: false, message: result.error.issues[0].message };
  }
  return { isValid: true, message: '' };
};

// Types for forms
export type LoginFormData = z.infer<typeof loginSchema>;
export type SignupFormData = z.infer<typeof signupSchema>;

// توابع خروجی برای استفاده در کامپوننت‌ها
export const checkEmail = (email: string) => validateField(emailSchema, email);
export const checkPassword = (pass: string) => validateField(passwordSchema, pass);
export const checkUsername = (user: string) => validateField(usernameSchema, user);
export const checkName = (name: string) => validateField(nameSchema, name);

// Legacy validation functions for backward compatibility
export const validateLoginForm = (data: unknown) => {
  return loginSchema.safeParse(data);
};

export const validateSignupForm = (data: unknown) => {
  return signupSchema.safeParse(data);
};

export const validateEmail = (email: string) => {
  return emailSchema.safeParse(email);
};

export const validatePassword = (password: string) => {
  return passwordSchema.safeParse(password);
};

export const validateUsername = (username: string) => {
  return usernameSchema.safeParse(username);
};

export const validateName = (name: string) => {
  return nameSchema.safeParse(name);
};