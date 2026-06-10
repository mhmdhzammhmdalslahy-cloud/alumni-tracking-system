import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import FAQ

def get_deepseek_response(user_message):
    """إرسال رسالة المستخدم إلى DeepSeek والحصول على الرد."""
    api_key = settings.DEEPSEEK_API_KEY
    api_url = settings.DEEPSEEK_API_URL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي ومفيد لمتابعة الخريجين."},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        deepseek_reply = response.json()["choices"][0]["message"]["content"]
        return deepseek_reply, None
    except Exception as e:
        return None, f"خطأ في الاتصال بـ DeepSeek: {str(e)}"

@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'answer': 'خطأ: تنسيق الطلب غير صحيح.'}, status=400)

    if not user_message:
        return JsonResponse({'answer': 'الرجاء كتابة سؤال.'}, status=400)

    # البحث المبدئي في قاعدة FAQ المحلية (اختياري)
    faq_answer = FAQ.objects.filter(question__icontains=user_message).first()
    if faq_answer:
        return JsonResponse({'answer': faq_answer.answer})

    ai_reply, error = get_deepseek_response(user_message)
    if ai_reply:
        return JsonResponse({'answer': ai_reply})
    else:
        return JsonResponse({'answer': f'عذرًا، حدث خطأ. {error}'}, status=500)