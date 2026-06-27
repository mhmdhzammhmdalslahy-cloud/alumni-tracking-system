import os
import re

def fix_translations(content):
    """إصلاح جميع أخطاء {% trans %} المتداخلة"""
    
    # 1️⃣ إصلاح الأنماط المتداخلة (مثل: {% trans "نظام متابعة {% trans "الخريجين" %}" %})
    # نبحث عن {% trans "....{% trans "...." %}...." %}
    pattern = r'{%\s*trans\s+"([^"]*){%\s*trans\s+"([^"]+)"\s*%}([^"]*)"\s*%}'
    
    def replace_nested(match):
        before = match.group(1)  # النص قبل الـ trans الداخلي
        inner = match.group(2)   # النص الداخلي
        after = match.group(3)   # النص بعد الـ trans الداخلي
        full_text = before + inner + after
        return f'{{% trans "{full_text}" %}}'
    
    # نطبق الاستبدال بشكل متكرر حتى لا يتبقى أي تداخل
    for _ in range(5):
        new_content = re.sub(pattern, replace_nested, content)
        if new_content == content:
            break
        content = new_content
    
    # 2️⃣ إصلاح الأنماط الشائعة (استبدال مباشر)
    replacements = {
        # الأخطاء الشائعة
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
        '{% trans "نظام متابعة {% trans "الخريجين" %}" %}': '{% trans "نظام متابعة الخريجين" %}',
        '{% trans "منصة متابعة {% trans "الخريجين" %}" %}': '{% trans "منصة متابعة الخريجين" %}',
        '{% trans "نظام متابعة {% trans "الخريجين" %}" %}': '{% trans "نظام متابعة الخريجين" %}',
        '{% trans "خريج" %}ين': '{% trans "خريجين" %}',
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
        '{% trans "خريج" %}ينا': '{% trans "خريجينا" %}',
        '{% trans "ا{% trans "بحث" %} عن {% trans "خريج" %}، تخصص، {% trans "شركة" %}..." %}': '{% trans "ابحث عن خريج، تخصص، شركة..." %}',
        '{% trans "ا{% trans "بحث" %} عن {% trans "خريج" %}، تخصص، مهارة..." %}': '{% trans "ابحث عن خريج، تخصص، مهارة..." %}',
        '{% trans "بحث" %} عن {% trans "خريج" %}': '{% trans "بحث عن خريج" %}',
        '{% trans "الخريجين" %} - {% trans "نظام متابعة {% trans "الخريجين" %}" %}': '{% trans "الخريجين" %} - {% trans "نظام متابعة الخريجين" %}',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    return content

def fix_file(filepath):
    """إصلاح ملف واحد"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = fix_translations(content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"❌ خطأ في {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 إصلاح جميع ملفات القوالب (أخطاء {% trans %} المتداخلة)")
    print("=" * 60)
    print()
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        print(f"❌ مجلد {templates_dir} غير موجود!")
        return
    
    count = 0
    total = 0
    errors = []
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                total += 1
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    print(f"✅ تم إصلاح: {filepath}")
                    count += 1
    
    print()
    print("=" * 60)
    print(f"📊 تم فحص {total} ملف، تم إصلاح {count} ملف.")
    if errors:
        print(f"⚠️ أخطاء في {len(errors)} ملف:")
        for e in errors:
            print(f"   - {e}")
    print("=" * 60)
    print()
    print("🚀 أعد تشغيل الخادم: venv\Scripts\python manage.py runserver")

if __name__ == "__main__":
    main()