import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استبدال كل الأنماط التي تحتوي على {% trans داخل {% trans
    # نبحث عن: {% trans "نص يحتوي على {% trans "نص آخر" %}" %}
    pattern = r'{%\s*trans\s+"([^"]*){%\s*trans\s+"([^"]+)"\s*%}([^"]*)"\s*%}'
    
    def replace_match(m):
        # نستخرج الأجزاء الثلاثة وندمجها
        before = m.group(1)  # الجزء قبل الـ trans الداخلي
        inner = m.group(2)   # النص الداخلي المترجم
        after = m.group(3)   # الجزء بعد الـ trans الداخلي
        # نبني النص الكامل ونضعه في trans واحد
        full_text = before + inner + after
        return f'{{% trans "{full_text}" %}}'
    
    new_content = re.sub(pattern, replace_match, content)
    
    # أيضاً استبدال الأنماط الشائعة مباشرة
    replacements = {
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
        '{% trans "نظام متابعة {% trans "الخريجين" %}" %}': '{% trans "نظام متابعة الخريجين" %}',
        '{% trans "منصة متابعة {% trans "الخريجين" %}" %}': '{% trans "منصة متابعة الخريجين" %}',
        '{% trans "خريج" %}ين': '{% trans "خريجين" %}',
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
        '{% trans "خريج" %}ينا': '{% trans "خريجينا" %}',
        '{% trans "ا{% trans "بحث" %} عن {% trans "خريج" %}، تخصص، {% trans "شركة" %}..." %}': '{% trans "ابحث عن خريج، تخصص، شركة..." %}',
        '{% trans "نظام متابعة {% trans "ال{% trans "خريج" %}ين" %}" %}': '{% trans "نظام متابعة الخريجين" %}',
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
    }
    
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            new_content = content  # نعيد تعيين المحتوى المعدل
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ تم إصلاح: {filepath}")
        return True
    return False

def main():
    print("=" * 60)
    print("🔧 إصلاح جميع علامات الترجمة المتداخلة")
    print("=" * 60)
    count = 0
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    count += 1
    print("=" * 60)
    print(f"✅ تم إصلاح {count} ملف.")
    print("=" * 60)

if __name__ == '__main__':
    main()