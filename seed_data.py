import os
import django
import random
import requests
from datetime import timedelta
from django.core.files.base import ContentFile

# ✅ تصحيح اسم المتغير البيئي
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from graduates.models import Graduate
from employers.models import Employer
from jobs.models import Job
from dashboard.models import Major, SuccessStory
from django.db.models.signals import post_save
from dashboard.signals import send_job_notifications  # استيراد الإشارة

# ==================== تعطيل الإشارات المؤقتاً ====================
print("🔕 تعطيل إرسال الإشعارات البريدية أثناء التعبئة...")
post_save.disconnect(send_job_notifications, sender=Job)

# ==================== دوال تحميل الصور ====================
def download_and_attach_image(instance, field_name, url):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            ext = 'jpg'
            if 'svg' in url:
                ext = 'svg'
            file_name = f"{instance.__class__.__name__}_{instance.id}.{ext}"
            getattr(instance, field_name).save(file_name, ContentFile(response.content), save=False)
            instance.save()
            return True
    except Exception as e:
        print(f"   ⚠️ فشل تحميل الصورة لـ {instance}: {e}")
    return False

def get_avatar_url(name, size=200, bg_color='random'):
    colors = ['1A5F7A', '27ae60', 'e67e22', '8e44ad', 'c0392b', '2980b9', '2c3e50', 'd35400']
    bg = random.choice(colors) if bg_color == 'random' else bg_color
    return f"https://ui-avatars.com/api/?name={name}&size={size}&background={bg}&color=fff&bold=true"

# ==================== البيانات اليمنية ====================
first_names_male = ['محمد', 'أحمد', 'علي', 'حسن', 'حسين', 'عبدالله', 'إبراهيم', 'إسماعيل', 'يوسف', 'موسى', 'عمر', 'خالد', 'سعيد', 'ناصر', 'منير', 'فؤاد', 'نبيل', 'غازي', 'رائد', 'سامي']
first_names_female = ['فاطمة', 'خديجة', 'عائشة', 'مريم', 'سمية', 'رنا', 'ندى', 'هدى', 'أماني', 'نجلاء', 'أروى', 'بلقيس', 'ريم', 'دانة', 'شذا', 'غادة', 'لينا', 'مها', 'سارة', 'نوره']
last_names = ['العنسي', 'الكبسي', 'الحميري', 'السياغي', 'العمراني', 'النهمي', 'الغفاري', 'الحوري', 'الشامي', 'العدني', 'الحضرمي', 'الصبري', 'العواضي', 'المخلافي', 'الزبيدي', 'الوزير', 'الرزامي', 'اليزيدي', 'الشرجبي', 'المقبلي']
universities = ['جامعة صنعاء', 'جامعة عدن', 'جامعة تعز', 'جامعة حضرموت', 'جامعة إب', 'جامعة ذمار', 'جامعة الحديدة', 'جامعة عمران', 'جامعة البيضاء', 'جامعة صعدة']
majors_list = ['هندسة برمجيات', 'علوم حاسب', 'هندسة مدنية', 'هندسة كهربائية', 'هندسة ميكانيكية', 'إدارة أعمال', 'محاسبة', 'اقتصاد', 'طب عام', 'صيدلة', 'لغة إنجليزية', 'شريعة وقانون', 'علوم سياسية', 'علوم تربوية', 'تكنولوجيا المعلومات']
cities = ['صنعاء', 'عدن', 'تعز', 'الحديدة', 'إب', 'ذمار', 'المكلا', 'سيئون', 'صعدة', 'حجة', 'عمران', 'البيضاء', 'لحج', 'أبين', 'شبوة', 'مأرب']

companies_data = [
    {'name': 'الاتصالات اليمنية (Yemen Telecom)', 'industry': 'اتصالات', 'city': 'صنعاء', 'desc': 'أكبر شركة اتصالات في اليمن'},
    {'name': 'عدن نت', 'industry': 'تقنية معلومات', 'city': 'عدن', 'desc': 'مزود خدمة إنترنت وحلول تقنية'},
    {'name': 'بنك اليمن الدولي', 'industry': 'بنوك ومالية', 'city': 'صنعاء', 'desc': 'أحد أكبر البنوك في اليمن'},
    {'name': 'الخطوط الجوية اليمنية', 'industry': 'طيران', 'city': 'صنعاء', 'desc': 'شركة الطيران الوطنية اليمنية'},
    {'name': 'مجموعة هائل سعيد أنعم', 'industry': 'استثمارات متنوعة', 'city': 'تعز', 'desc': 'مجموعة اقتصادية عملاقة في اليمن'},
    {'name': 'شركة النفط اليمنية (YPC)', 'industry': 'نفط وغاز', 'city': 'مأرب', 'desc': 'الشركة الوطنية للنفط'},
    {'name': 'كاك بنك', 'industry': 'بنوك ومالية', 'city': 'صنعاء', 'desc': 'بنك إسلامي يمني'},
    {'name': 'شركة سبأ للاتصالات', 'industry': 'اتصالات', 'city': 'صنعاء', 'desc': 'مزود خدمة إنترنت وهواتف'},
    {'name': 'شركة المكلا للمقاولات', 'industry': 'مقاولات', 'city': 'المكلا', 'desc': 'شركة إنشاءات ومقاولات'},
    {'name': 'مصنع اسمنت عدن', 'industry': 'صناعات', 'city': 'عدن', 'desc': 'مصنع اسمنت في عدن'},
    {'name': 'شركة النقل البري اليمنية', 'industry': 'نقل ومواصلات', 'city': 'صنعاء', 'desc': 'شركة النقل البري'},
    {'name': 'مؤسسة الكهرباء اليمنية', 'industry': 'طاقة', 'city': 'صنعاء', 'desc': 'مؤسسة الكهرباء العامة'},
    {'name': 'شركة مياه عدن', 'industry': 'خدمات عامة', 'city': 'عدن', 'desc': 'شركة المياه والصرف الصحي'},
    {'name': 'مطاعم ومخابز الأمان', 'industry': 'أغذية', 'city': 'تعز', 'desc': 'سلسلة مطاعم يمنية'},
    {'name': 'شركة الصناعات الغذائية الحديثة', 'industry': 'أغذية', 'city': 'الحديدة', 'desc': 'صناعة أغذية ومشروبات'},
]

job_titles = ['مهندس برمجيات', 'مطور ويب', 'محلل بيانات', 'مدير مشروع', 'مهندس مدني', 'محاسب', 'مسوق رقمي', 'اختصاصي موارد بشرية', 'كاتب تقني', 'مصمم جرافيك', 'مهندس كهرباء', 'مهندس ميكانيكي', 'محلل مالي', 'إداري', 'مبرمج تطبيقات']

success_stories_texts = [
    "بعد التخرج مباشرة، حصلت على وظيفة في شركة اتصالات مرموقة بفضل تدريبي العملي ومشاريعي الجامعية. أنصح كل خريج بالاستثمار في المهارات العملية.",
    "تخرجت من جامعة صنعاء بتقدير امتياز، والآن أعمل مهندس برمجيات في شركة عالمية من منزلي في صنعاء. الحلم يبدأ بخطوة.",
    "بدأت مسيرتي كمتطوع في شركة صغيرة، وبعد 6 أشهر تم تعييني رسمياً. المثابرة والالتزام هما مفتاح النجاح.",
    "أسست شركتي الناشئة في مجال التسويق الرقمي بعد سنة واحدة من التخرج، والآن لدي فريق عمل من 10 أشخاص.",
    "التخصص الدقيق والتميز في مجال الهندسة المدنية فتح لي أبواب العمل في أكبر شركات المقاولات باليمن.",
    "حصلت على منحة دراسية لإكمال الماجستير بعد التخرج بفضل تفوقي الأكاديمي، والآن أنا محاضر جامعي.",
    "الانضمام إلى برامج التدريب الصيفي كان نقطة تحول في مسيرتي المهنية، حيث تحولت إلى وظيفة دائمة بعد التخرج.",
    "أعمل الآن كمحلل بيانات في بنك مرموق، بفضل مهاراتي في البرمجة وتحليل الأرقام التي طورتها أثناء الدراسة."
]

# ==================== دوال مساعدة ====================
def get_or_create_major(name):
    code = ''.join(word[0] for word in name.split())[:5].upper()
    if not code: code = name[:3].upper()
    original = code
    counter = 1
    while Major.objects.filter(code=code).exists():
        code = f"{original}{counter}"
        counter += 1
    major, created = Major.objects.get_or_create(name=name, defaults={'code': code})
    return major

# ==================== بدء التعبئة ====================
print("🌍 بدء تعبئة قاعدة البيانات ببيانات يمنية وصور...")

# 1. إنشاء التخصصات
print("📚 إنشاء التخصصات...")
for major_name in majors_list:
    get_or_create_major(major_name)

# 2. الخريجين (20) مع صور
print("🎓 إنشاء الخريجين مع الصور...")
used_universities = []

for i in range(20):
    first = random.choice(first_names_male if i < 10 else first_names_female)
    last = random.choice(last_names)
    username = f"{first}{last}_{random.randint(100,999)}"
    email = f"{username.lower()}@gmail.com"
    
    user, _ = User.objects.get_or_create(username=username, defaults={'first_name': first, 'last_name': last, 'email': email})
    user.set_password('password123')
    user.save()
    
    major_name = random.choice(majors_list)
    
    available_universities = [u for u in universities if u not in used_universities]
    if not available_universities:
        university = random.choice(universities) + f" ({i+1})"
    else:
        university = random.choice(available_universities)
        used_universities.append(university)
    
    city = random.choice(cities)
    
    grad, created = Graduate.objects.get_or_create(
        user=user,
        defaults={
            'university_id': university,
            'major': major_name,
            'graduation_year': random.randint(2019, 2026),
            'address': city,
            'current_job_status': random.choice(['working', 'seeking', 'freelance']),
            'is_verified': random.choice([True, False]),
            'bio': f"خريج {major_name} من {university}",
            'phone': f"7{random.randint(10000000, 99999999)}",
            'gpa': round(random.uniform(2.0, 4.0), 2)
        }
    )
    grad.save()
    if created:
        avatar_url = get_avatar_url(f"{first}+{last}")
        download_and_attach_image(grad, 'profile_picture', avatar_url)
        print(f"   ✅ {first} {last} - {major_name} - {university}")

# 3. الشركات (15) مع شعارات
print("🏢 إنشاء الشركات مع الشعارات...")
created_employers = []
for comp in companies_data:
    admin_first = random.choice(first_names_male)
    admin_last = random.choice(last_names)
    username = f"{comp['name'].replace(' ', '_')}_{random.randint(100,999)}".lower()
    email = f"{username}@company.com"
    user, _ = User.objects.get_or_create(username=username, defaults={'first_name': admin_first, 'last_name': admin_last, 'email': email})
    user.set_password('company123')
    user.save()
    
    emp, created = Employer.objects.get_or_create(
        user=user,
        defaults={
            'company_name': comp['name'],
            'industry': comp['industry'],
            'headquarters': comp['city'],
            'about': comp['desc'],
            'address': comp['city'],
            'is_verified': True,
            'website': f"www.{comp['name'].replace(' ', '').replace('(','').replace(')','').lower()}.com"
        }
    )
    if created:
        short = comp['name'].replace('(','').replace(')','').replace(' Yemen Telecom','').replace('YPC','')
        short = short[:6]
        logo_url = get_avatar_url(short, size=200, bg_color=random.choice(['2c3e50', '34495e', '7f8c8d', '16a085', '2980b9']))
        download_and_attach_image(emp, 'logo', logo_url)
        created_employers.append(emp)
        print(f"   ✅ {comp['name']}")

# 4. الوظائف (مع تعطيل الإشارات)
print("💼 إنشاء الوظائف...")
job_count = 0
for emp in created_employers:
    for _ in range(random.randint(1, 3)):
        title = random.choice(job_titles)
        job_type = random.choice(['full_time', 'part_time', 'remote', 'internship'])
        experience_level = random.choice(['fresh', 'junior', 'mid', 'senior', 'lead'])
        required_skills = ', '.join(random.sample(['Python', 'Java', 'JavaScript', 'SQL', 'Django', 'React', 'Node.js', 'تحليل بيانات', 'إدارة مشاريع', 'التواصل'], k=3))
        description = f"مطلوب {title} للعمل في {emp.company_name}."
        deadline = timezone.now() + timedelta(days=random.randint(30, 90))
        
        job, created = Job.objects.get_or_create(
            employer=emp,
            title=title,
            defaults={
                'job_type': job_type,
                'experience_level': experience_level,
                'location': emp.headquarters,
                'salary_min': random.randint(200, 1000) * 1000,
                'salary_max': random.randint(1000, 2000) * 1000,
                'is_salary_negotiable': random.choice([True, False]),
                'required_skills': required_skills,
                'preferred_skills': ', '.join(random.sample(['مهارات تواصل', 'قيادة', 'عمل جماعي', 'حل مشكلات', 'تخطيط'], k=2)),
                'description': description,
                'responsibilities': f"المسؤوليات: {random.choice(['إدارة المشاريع', 'تطوير البرمجيات', 'تحليل البيانات', 'التسويق', 'المحاسبة'])}",
                'benefits': f"المزايا: {random.choice(['تأمين صحي', 'مرونة في العمل', 'إجازات مدفوعة', 'تدريب مستمر'])}",
                'deadline': deadline,
                'is_active': True,
                'is_filled': False,
                'is_live': True,
            }
        )
        if created:
            job_count += 1
print(f"   ✅ {job_count} وظيفة")

# 5. قصص نجاح مع صور
print("⭐ إنشاء قصص النجاح مع الصور...")
graduates_list = list(Graduate.objects.all())
story_count = 0
for i, text in enumerate(success_stories_texts):
    if i < len(graduates_list):
        grad = graduates_list[i]
        title = text[:50]
        story, created = SuccessStory.objects.get_or_create(
            graduate=grad,
            title=title,
            defaults={
                'content': text,
                'status': 'approved',
                'is_active': True,
                'created_by': grad.user,
                'created_at': timezone.now() - timedelta(days=random.randint(1, 365))
            }
        )
        if created:
            img_url = f"https://picsum.photos/seed/{grad.id + 100}/600/400"
            download_and_attach_image(story, 'image', img_url)
            story_count += 1
            print(f"   ✅ {grad.user.get_full_name()}")

# 6. إحصائيات
print("\n" + "="*50)
print("🎉 تم الانتهاء!")
print("="*50)
print(f"👨‍🎓 الخريجين: {Graduate.objects.count()}")
print(f"🏢 الشركات: {Employer.objects.count()}")
print(f"💼 الوظائف: {Job.objects.count()}")
print(f"⭐ قصص النجاح: {SuccessStory.objects.count()}")
print("="*50)
print("🔑 بيانات الدخول:")
print("   خريج: (أي اسم مستخدم) / password123")
print("   شركة: (أي شركة) / company123")
print("   مشرف: محمد / 1234m")
print("="*50)