from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Survey, SurveyResponse
from graduates.models import Graduate

def survey_list(request):
    surveys = Survey.objects.filter(is_active=True)
    return render(request, 'surveys/survey_list.html', {'surveys': surveys})


def take_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    
    if not hasattr(request.user, 'graduate_profile'):
        messages.error(request, 'يجب أن تكون مسجلاً كخريج للإجابة على الاستبيان')
        return redirect('graduate_create')
    
    # التحقق من أن الخريج لم يجب من قبل
    if SurveyResponse.objects.filter(survey=survey, graduate=request.user.graduate_profile).exists():
        messages.warning(request, 'لقد أجبت على هذا الاستبيان مسبقاً')
        return redirect('survey_list')
    
    if request.method == 'POST':
        answers = []
        questions = survey.questions
        
        for i, question in enumerate(questions):
            answer = request.POST.get(f'question_{i}')
            answers.append({
                'question': question.get('text'),
                'type': question.get('type'),
                'answer': answer
            })
        
        SurveyResponse.objects.create(
            survey=survey,
            graduate=request.user.graduate_profile,
            answers=answers
        )
        
        messages.success(request, '✅ شكراً لك! تم إرسال إجاباتك بنجاح')
        return redirect('survey_list')
    
    return render(request, 'surveys/take_survey.html', {'survey': survey})


@staff_member_required
def survey_results(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    responses = survey.responses.all()
    
    # تحليل الإجابات
    results = {}
    for response in responses:
        for answer in response.answers:
            q_text = answer.get('question')
            if q_text not in results:
                results[q_text] = []
            results[q_text].append(answer.get('answer'))
    
    return render(request, 'surveys/survey_results.html', {
        'survey': survey,
        'responses': responses,
        'results': results
    })