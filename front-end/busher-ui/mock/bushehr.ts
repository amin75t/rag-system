import type { BushehrAtAGlance } from "../types/bushehr";

export const bushehrMock: BushehrAtAGlance = {
  title: "بوشهر در یک نگاه",
  mission:
    "تمرکز بر پیشران انرژی، توسعه دریامحور، صنایع پایه و دانش‌بنیان برای توسعه پایدار استان بوشهر",
  updatedAt: "۱۴۰۴/۱۱/۱۱",

  /* ── منظر جنرال ── */
  kpis: [
    {
      id: "pop",
      label: "جمعیت",
      value: "۱,۱۹۳,۰۰۰ نفر",
      compare: "۱.۳٪ جمعیت کشور",
      percent: 42,
      trend: "up",
      icon: "population",
    },
    {
      id: "area",
      label: "مساحت",
      value: "۲۳,۱۶۸ km²",
      compare: "۱.۴٪ مساحت کشور",
      percent: 35,
      trend: "flat",
      icon: "area",
    },
    {
      id: "unemp",
      label: "نرخ بیکاری",
      value: "۱۲.۵٪",
      compare: "بالاتر از میانگین کشور",
      percent: 63,
      trend: "down",
      icon: "unemployment",
    },
    {
      id: "gdp",
      label: "سهم GDP",
      value: "۴.۲٪",
      compare: "جایگاه نسبی: بالا",
      percent: 55,
      trend: "up",
      icon: "gdp",
    },
    {
      id: "coast",
      label: "طول نوار ساحلی",
      value: "۹۰۰ km",
      compare: "۴۰٪ ساحل جنوبی کشور",
      percent: 80,
      trend: "flat",
      icon: "coast",
    },
  ],

  /* ── منظر راهبردی ── */
  priorities: [
    {
      id: "energy",
      title: "انرژی",
      weight: "خیلی بالا",
      weightPercent: 95,
      role: "پیشران ملی",
      roleIcon: "energy",
      horizon: "کوتاه تا میان‌مدت",
      colorKey: "red",
      tech: "AI → پایش، بهره‌وری، ایمنی",
      issues: [
        { id: "e1", text: "تمرکز تصمیم‌گیری خارج استان" },
        { id: "e2", text: "اشتغال پایین" },
        { id: "e3", text: "زنجیره ارزش ناقص" },
        { id: "e4", text: "فشار اجتماعی و محیط‌زیستی" },
        { id: "e5", text: "ضعف حکمرانی داده" },
      ],
    },
    {
      id: "sea",
      title: "اقتصاد دریا",
      weight: "بالا",
      weightPercent: 70,
      role: "اشتغال‌زا و منطقه‌ای",
      roleIcon: "sea",
      horizon: "کوتاه تا بلندمدت",
      colorKey: "blue",
      tech: "AI + زیست‌فناوری → پایداری، ارزش افزوده",
      issues: [
        { id: "s1", text: "ارزش افزوده پایین و تمرکز بر تولید خام" },
        { id: "s2", text: "ریسک زیست‌محیطی و بیماری آبزیان" },
        { id: "s3", text: "ضعف سردخانه، لجستیک و حمل‌ونقل" },
        { id: "s4", text: "ناپیوستگی دانش، پژوهش و بازار" },
        { id: "s5", text: "پراکندگی و تعارض تصمیم‌گیری" },
      ],
    },
    {
      id: "industry",
      title: "صنعت و دانش‌بنیان",
      weight: "متوسط",
      weightPercent: 45,
      role: "مکمل توسعه",
      roleIcon: "industry",
      horizon: "میان تا بلندمدت",
      colorKey: "yellow",
      tech: "AI → بهبود عملکرد، کاهش هزینه",
      issues: [
        { id: "i1", text: "وابستگی به انرژی و دریا" },
        { id: "i2", text: "ناقص بودن زنجیره ارزش" },
        { id: "i3", text: "کمبود شرکت دانش‌بنیان کاربردمحور" },
        { id: "i4", text: "شکاف مهارت و نیروی متخصص" },
        { id: "i5", text: "ضعف هماهنگی دانشگاه و صنعت" },
      ],
    },
  ],

  /* ── لایه نوظهور فناوری ── */
  techItems: [
    {
      id: "t1",
      priority: "energy",
      label: "انرژی: AI",
      detail: "پایش، بهره‌وری، ایمنی",
      colorKey: "red",
    },
    {
      id: "t2",
      priority: "industry",
      label: "صنعت: AI",
      detail: "بهبود عملکرد، کاهش هزینه",
      colorKey: "yellow",
    },
    {
      id: "t3",
      priority: "sea",
      label: "اقتصاد دریا: AI + زیست‌فناوری",
      detail: "پایداری، ارزش افزوده",
      colorKey: "blue",
    },
  ],
};
