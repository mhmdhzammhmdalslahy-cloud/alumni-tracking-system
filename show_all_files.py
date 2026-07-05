# show_all_files.py
import os

def show_all_files():
    project = r'C:\Alumni_Project'
    
    print("\n" + "="*90)
    print("📂 جامعة إقليم سبأ - عرض جميع الملفات")
    print("="*90)
    
    # الامتدادات المطلوبة
    extensions = {
        '.html': '📄 HTML',
        '.py': '🐍 Python',
        '.css': '🎨 CSS',
        '.js': '⚡ JavaScript'
    }
    
    total_files = 0
    files_by_ext = {ext: 0 for ext in extensions}
    
    print("\n📋 قائمة جميع الملفات:")
    print("-"*90)
    
    for root, dirs, files in os.walk(project):
        # تجاهل مجلدات معينة
        if '__pycache__' in root or 'venv' in root or '.git' in root:
            continue
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            
            if ext in extensions:
                total_files += 1
                files_by_ext[ext] += 1
                
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                
                # عرض المسار بطريقة مختصرة
                rel_path = os.path.relpath(full_path, project)
                size_str = f"{size:,}" if size < 1024 else f"{size/1024:.1f} KB"
                
                print(f"{extensions[ext]}  {rel_path}  ({size_str})")
    
    # ====== إحصائيات ======
    print("\n" + "="*90)
    print("📊 إحصائيات الملفات:")
    print("-"*90)
    
    for ext, name in extensions.items():
        count = files_by_ext[ext]
        print(f"   {name}: {count} ملف")
    
    print(f"\n   📦 إجمالي الملفات: {total_files} ملف")
    print("="*90)

if __name__ == "__main__":
    show_all_files()