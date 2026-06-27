import os

# نفس قاموسك السابق (نأخذ المفاتيح فقط للترجمة)
translations = {
    "الرئيسية": "Dashboard",
    "الخريجين": "Graduates",
    "الشركات": "Companies",
    "الوظائف": "Jobs",
    "لوحة الإدارة": "Admin Panel",
    "القائمة": "Menu",
    "حسابي": "My Account",
    "المهارات": "Skills",
    "التخصصات": "Majors",
    "الإعدادات": "Settings",
    "سجل التدقيق": "Audit Log",
    "المشرفين": "Admins",
    "التقارير": "Reports",
    "الفعاليات": "Events",
    "الاستبيانات": "Surveys",
    "تسجيل دخول": "Login",
    "تسجيل خروج": "Logout",
    "إنشاء حساب": "Sign Up",
    "الوضع الداكن": "Dark Mode",
    "ملفي الشخصي": "My Profile",
    "عرض الكل": "View All",
    "أضف قصتك": "Add Your Story",
    "كن أول من يضيف قصته!": "Be the first to add your story!",
    "سجل الآن": "Register Now",
    "استعرض الوظائف": "Browse Jobs",
    "تعرف أكثر": "Learn More",
    "ابحث عن خريج، تخصص، شركة...": "Search for graduate, major, company...",
    "خريج": "Graduate",
    "شركة": "Company",
    "وظيفة": "Job",
    "نسبة التوظيف": "Employment Rate",
    "أحدث الخريجين": "Latest Graduates",
    "آخر الوظائف": "Recent Jobs",
    "قصص نجاح خريجينا": "Our Graduates' Success Stories",
    "منصتك الأولى للتواصل مع الخريجين وفرص العمل": "Your first platform for connecting with graduates and job opportunities",
    "روابط سريعة": "Quick Links",
    "تواصل معنا": "Contact Us",
    "جميع الحقوق محفوظة": "All Rights Reserved",
    "لا يوجد خريجين": "No graduates found",
    "لا توجد وظائف حالياً": "No jobs currently",
    "لا توجد قصص نجاح بعد": "No success stories yet",
    "سجل الدخول لمشاركة قصتك الملهمة": "Login to share your inspiring story",
    "مرحباً بك": "Welcome",
    "نتمنى لك تجربة ممتعة على منصة متابعة الخريجين": "We wish you an enjoyable experience on the Alumni Follow-up Platform",
    "بحث": "Search",
    "إضافة": "Add",
    "حفظ": "Save",
    "حذف": "Delete",
    "تعديل": "Edit",
    "نشر": "Publish",
    "إلغاء": "Cancel",
    "تأكيد": "Confirm",
    "إرسال": "Send",
    "استقبال": "Receive",
    "تفعيل": "Activate",
    "تعطيل": "Deactivate",
    "موثق": "Verified",
    "غير موثق": "Unverified",
    "قيد المراجعة": "Under Review",
}

po_content = '''msgid ""
msgstr ""
"Project-Id-Version: alumni_system\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-06-27 03:50+0300\\n"
"PO-Revision-Date: 2026-06-27 03:50+0300\\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''

for ar, en in translations.items():
    po_content += f'msgid "{ar}"\n'
    po_content += f'msgstr "{en}"\n\n'

# إنشاء المجلدات إذا لم تكن موجودة
os.makedirs('locale/en/LC_MESSAGES', exist_ok=True)

# كتابة الملف
with open('locale/en/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
    f.write(po_content)

print("✅ تم إنشاء ملف locale/en/LC_MESSAGES/django.po بنجاح!")