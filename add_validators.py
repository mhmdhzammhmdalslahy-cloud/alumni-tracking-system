import os
import re
from pathlib import Path

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent

# قائمة بملفات النماذج التي نريد تعديلها
model_files = [
    'graduates/models.py',
    'accounts/models.py',
    'employers/models.py',
    'jobs/models.py',
]

# النصوص المطلوب إضافتها
validators_code = '''
from django.core.validators import RegexValidator

# ============================================================
# ✅ Validators مركزية لجميع الحقول
# ============================================================
letters_validator = RegexValidator(
    r'^[\\u0621-\\u064A\\u0660-\\u0669a-zA-Z\\s]+$',
    'يسمح بالحروف فقط'
)
numbers_validator = RegexValidator(
    r'^\\d+$',
    'يسمح بالأرقام فقط'
)
both_validator = RegexValidator(
    r'^[\\u0621-\\u064A\\u0660-\\u0669a-zA-Z0-9\\s]+$',
    'يسمح بالحروف والأرقام فقط'
)
phone_validator = RegexValidator(
    r'^(0|7|9)\\d{8,9}$',
    'رقم الهاتف يجب أن يبدأ بـ 0 أو 7 أو 9'
)
university_validator = RegexValidator(
    r'^\\d+$',
    'الرقم الجامعي أرقام فقط'
)
'''

# تعديل كل ملف
for file_path in model_files:
    full_path = BASE_DIR / file_path
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إذا كان الملف يحتوي على 'validators' بالفعل، تخطى
        if 'validators' in content:
            print(f"✅ {file_path} يحتوي بالفعل على validators")
            continue
        
        # إضافة الـ validators بعد استيراد models
        if 'from django.db import models' in content:
            new_content = content.replace(
                'from django.db import models',
                f'from django.db import models\n{validators_code}'
            )
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ تم تحديث {file_path}")
        else:
            print(f"⚠️ {file_path} لا يحتوي على 'from django.db import models'")
    else:
        print(f"❌ {file_path} غير موجود")

print("\n✅ تم الانتهاء من تحديث جميع النماذج!")