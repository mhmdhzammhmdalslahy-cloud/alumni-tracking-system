import os

def add_i18n_to_templates():
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        print(f"❌ مجلد {templates_dir} غير موجود!")
        return

    count = 0
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # تحقق من وجود {% load i18n %}
                if '{% load i18n %}' in content:
                    print(f"⏩ تخطي: {filepath} (موجود مسبقاً)")
                    continue
                
                # أضف {% load i18n %} في السطر الأول (بعد أي تعليقات أو سطر doctype)
                lines = content.splitlines()
                if lines and (lines[0].strip().startswith('<!DOCTYPE') or lines[0].strip().startswith('{% load static')):
                    # أدخل بعد السطر الأول
                    lines.insert(1, '{% load i18n %}')
                else:
                    # أدخل في البداية
                    lines.insert(0, '{% load i18n %}')
                
                new_content = '\n'.join(lines)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ تم التعديل: {filepath}")
                count += 1

    # ✅ تم إصلاح هذا السطر
    print(f"\n🎉 تم إضافة {{% load i18n %}} إلى {count} ملف.")

if __name__ == "__main__":
    add_i18n_to_templates()