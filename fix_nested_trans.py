import os

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استبدال الأنماط المتداخلة الشائعة
    replacements = {
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
        '{% trans "نظام متابعة {% trans "ال{% trans "خريج" %}ين" %}" %}': '{% trans "نظام متابعة الخريجين" %}',
        '{% trans "خريج" %}ين': '{% trans "خريجين" %}',
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
        '{% trans "ا{% trans "بحث" %} عن {% trans "خريج" %}، تخصص، {% trans "شركة" %}..." %}': '{% trans "ابحث عن خريج، تخصص، شركة..." %}',
        '{% trans "نظام متابعة {% trans "ال{% trans "خريج" %}ين" %}" %}': '{% trans "نظام متابعة الخريجين" %}',
        '{% trans "منصة متابعة {% trans "ال{% trans "خريج" %}ين" %}" %}': '{% trans "منصة متابعة الخريجين" %}',
        '{% trans "خريج" %}ينا': '{% trans "خريجينا" %}',
        '{% trans "ال{% trans "خريج" %}ين" %}': '{% trans "الخريجين" %}',
    }
    
    changed = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ تم إصلاح: {filepath}")
        return True
    return False

def main():
    print("=" * 60)
    print("🔧 إصلاح علامات الترجمة المتداخلة")
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