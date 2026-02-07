import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/useAuth';
import { ProfileData } from '../contexts/authContext';

const ProfilePage: React.FC = () => {
  const { user, getProfile, updateProfile } = useAuth();

  const [profileData, setProfileData] = useState<ProfileData>({
    phone: '',
    username: '',
    first_name: '',
    last_name: '',
  });

  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (user) {
      setProfileData({
        phone: user.phone || '',
        username: user.username || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
      });
    }
  }, [user]);

  const createdAtText = useMemo(() => {
    if (!user?.created_at) return '';
    try {
      // اگر خواستی فارسی‌ترش کنی: fa-IR
      return new Date(user.created_at).toLocaleString('fa-IR');
    } catch {
      return String(user.created_at);
    }
  }, [user?.created_at]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  const handleEdit = () => {
    setIsEditing(true);
    setMessage(null);
  };

  const handleCancel = () => {
    setIsEditing(false);
    if (user) {
      setProfileData({
        phone: user.phone || '',
        username: user.username || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
      });
    }
    setMessage(null);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      await updateProfile(profileData);
      setIsEditing(false);
      setMessage({ type: 'success', text: 'اطلاعات پروفایل با موفقیت ذخیره شد.' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'ذخیره‌سازی پروفایل ناموفق بود.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefreshProfile = async () => {
    setIsLoading(true);
    setMessage(null);

    try {
      await getProfile();
      setMessage({ type: 'success', text: 'اطلاعات پروفایل به‌روز شد.' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'به‌روزرسانی پروفایل ناموفق بود.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 flex items-center justify-center font-iransans p-4" dir="rtl">
        <div className="text-sky-700 bg-white/80 backdrop-blur-sm border border-sky-100 rounded-2xl px-6 py-4 shadow-lg">
          در حال بارگذاری پروفایل...
        </div>
      </div>
    );
  }

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 flex items-center justify-center font-iransans p-4"
      dir="rtl"
    >
      <div className="max-w-2xl w-full bg-white/95 mt-10 md:mt-0 backdrop-blur-sm p-6 md:p-8 rounded-2xl shadow-2xl border border-sky-100">
        {/* Header */}
        <div className="flex items-center justify-between gap-3 mb-6 ">
          <div className="flex items-center gap-3">
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-sky-900">پروفایل کاربری</h1>
              <p className="text-xs md:text-sm text-sky-600 mt-1">
                اطلاعات حساب خود را مشاهده و در صورت نیاز ویرایش کنید.
              </p>
            </div>
          </div>

          <button
            onClick={handleRefreshProfile}
            disabled={isLoading}
            className="px-4 py-2 text-xs md:text-sm font-bold rounded-xl bg-sky-100 text-sky-800 hover:bg-sky-200 disabled:opacity-50 transition-all"
          >
            {isLoading ? '...' : 'به‌روزرسانی'}
          </button>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`mb-5 p-3 rounded-xl text-xs md:text-sm border flex items-center ${
              message.type === 'success'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-red-50 text-red-600 border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSave} className="space-y-5">
          {/* ID + Created */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-sky-700 mb-2">شناسه کاربر</label>
              <input
                type="text"
                value={user.id}
                disabled
                className="block w-full px-4 py-3 border rounded-xl shadow-sm bg-sky-50/60 text-sky-700 border-sky-200"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sky-700 mb-2">تاریخ ایجاد حساب</label>
              <input
                type="text"
                value={createdAtText}
                disabled
                className="block w-full px-4 py-3 border rounded-xl shadow-sm bg-sky-50/60 text-sky-700 border-sky-200"
              />
            </div>
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-sky-700 mb-2">شماره تلفن</label>
            <input
              type="tel"
              name="phone"
              value={profileData.phone}
              onChange={handleInputChange}
              disabled={!isEditing}
              dir="ltr"
              className={`block w-full px-4 py-3 border rounded-xl shadow-sm outline-none transition-all focus:ring-2 focus:ring-sky-500 ${
                !isEditing ? 'bg-sky-50/60 text-sky-700' : 'bg-white'
              } border-sky-200 disabled:opacity-90`}
              placeholder="09123456789"
            />
          </div>

          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-sky-700 mb-2">نام کاربری</label>
            <input
              type="text"
              name="username"
              value={profileData.username}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`block w-full px-4 py-3 border rounded-xl shadow-sm outline-none transition-all focus:ring-2 focus:ring-sky-500 ${
                !isEditing ? 'bg-sky-50/60 text-sky-700' : 'bg-white'
              } border-sky-200 disabled:opacity-90`}
              placeholder="مثلاً: najm"
            />
          </div>

          {/* First/Last */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-sky-700 mb-2">نام</label>
              <input
                type="text"
                name="first_name"
                value={profileData.first_name}
                onChange={handleInputChange}
                disabled={!isEditing}
                className={`block w-full px-4 py-3 border rounded-xl shadow-sm outline-none transition-all focus:ring-2 focus:ring-sky-500 ${
                  !isEditing ? 'bg-sky-50/60 text-sky-700' : 'bg-white'
                } border-sky-200 disabled:opacity-90`}
                placeholder="نام"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sky-700 mb-2">نام خانوادگی</label>
              <input
                type="text"
                name="last_name"
                value={profileData.last_name}
                onChange={handleInputChange}
                disabled={!isEditing}
                className={`block w-full px-4 py-3 border rounded-xl shadow-sm outline-none transition-all focus:ring-2 focus:ring-sky-500 ${
                  !isEditing ? 'bg-sky-50/60 text-sky-700' : 'bg-white'
                } border-sky-200 disabled:opacity-90`}
                placeholder="نام خانوادگی"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row sm:justify-end gap-3 pt-2">
            {!isEditing ? (
              <button
                type="button"
                onClick={handleEdit}
                className="w-full sm:w-auto px-5 py-3 text-sm font-bold rounded-xl text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 transition-all transform hover:scale-[1.01]"
              >
                ویرایش پروفایل
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={isLoading}
                  className="w-full sm:w-auto px-5 py-3 text-sm font-bold rounded-xl bg-sky-100 text-sky-800 hover:bg-sky-200 disabled:opacity-50 transition-all"
                >
                  انصراف
                </button>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full sm:w-auto px-5 py-3 text-sm font-bold rounded-xl text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 disabled:opacity-50 transition-all transform hover:scale-[1.01]"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin h-5 w-5 ml-2 border-b-2 border-white rounded-full" viewBox="0 0 24 24"></svg>
                      در حال ذخیره...
                    </span>
                  ) : (
                    'ذخیره تغییرات'
                  )}
                </button>
              </>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
