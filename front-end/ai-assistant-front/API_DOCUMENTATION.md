# مستندات API احراز هویت

## پایانه‌های احراز هویت

### ۱. ورود کاربر (Login)
**Endpoint:** `POST /api/auth/login`

**Body:**
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**پاسخ موفق:**
```json
{
  "user": {
    "id": "user_id",
    "username": "testuser",
    "email": "test@example.com",
    "firstName": "کاربر",
    "lastName": "آزمایشی"
  },
  "token": "jwt_token_here",
  "refreshToken": "refresh_token_here"
}
```

**پاسخ خطا:**
```json
{
  "message": "ایمیل یا رمز عبور اشتباه است"
}
```

### ۲. ثبت‌نام کاربر (Signup)
**Endpoint:** `POST /api/auth/register`

**Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "firstName": "کاربر",
  "lastName": "آزمایشی"
}
```

**پاسخ موفق:** مشابه ورود کاربر

### ۳. خروج کاربر (Logout)
**Endpoint:** `POST /api/auth/logout`

**Headers:**
```
Authorization: Bearer jwt_token_here
```

## نحوه استفاده در فرانت‌اند

### ۱. نصب پیش‌نیازها
```bash
npm install express cors bcryptjs jsonwebtoken
npm install --save-dev @types/express @types/cors @types/bcryptjs @types/jsonwebtoken
```

### ۲. نمونه سرور Express

```javascript
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Login endpoint
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user in database
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ message: 'ایمیل یا رمز عبور اشتباه است' });
    }
    
    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ message: 'ایمیل یا رمز عبور اشتباه است' });
    }
    
    // Generate JWT token
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    res.json({
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName
      },
      token
    });
  } catch (error) {
    res.status(500).json({ message: 'خطای سرور' });
  }
});

// Start server
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

## نکات مهم

1. **JWT Secret:** حتماً یک JWT_SECRET قوی در متغیرهای محیطی تعریف کنید
2. **CORS:** برای ارتباط فرانت‌اند و بک‌اند نیاز به CORS دارید
3. **Password Hashing:** از bcrypt برای هش کردن رمز عبور استفاده کنید
4. **Token Validation:** توکن JWT را در تمام درخواست‌های محافظت شده اعتبارسنجی کنید
5. **Error Handling:** پیام‌های خطای فارسی و کاربرپسند برگردانید

## تست API

با استفاده از دستور زیر می‌توانید API را تست کنید:

```bash
# تست ورود
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## اتصال به دیتابیس

می‌توانید از MongoDB یا MySQL استفاده کنید:

```javascript
// MongoDB Model
const mongoose = require('mongoose');
const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  firstName: String,
  lastName: String,
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('User', UserSchema);