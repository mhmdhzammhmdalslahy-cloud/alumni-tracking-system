from django import forms
from .models import Survey, Event, SystemSetting, AdminProfile, Major, Skill, BannedWord
from django.contrib.auth.models import User

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'timing', 'questions', 'scheduled_date', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'timing': forms.Select(attrs={'class': 'form-control'}),
            'questions': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'JSON format: [{"text": "سؤال?", "type": "text"}]'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'date', 'location', 'is_virtual', 'meeting_link', 'max_attendees', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'is_virtual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'max_attendees': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = ['key', 'value', 'description']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AdminProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    
    class Meta:
        model = AdminProfile
        fields = ['admin_level', 'is_active']
        widgets = {
            'admin_level': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def save(self, commit=True):
        user_data = {
            'username': self.cleaned_data['username'],
            'email': self.cleaned_data['email'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
        }
        
        if self.instance.pk:
            user = self.instance.user
            for key, value in user_data.items():
                setattr(user, key, value)
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
        else:
            user = User.objects.create_user(**user_data)
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            else:
                user.set_password('admin123')
            user.save()
        
        self.instance.user = user
        return super().save(commit)


class MajorForm(forms.ModelForm):
    class Meta:
        model = Major
        fields = ['name', 'code', 'department', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BannedWordForm(forms.ModelForm):
    class Meta:
        model = BannedWord
        fields = ['word']
        widgets = {
            'word': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VerificationReviewForm(forms.Form):
    action = forms.ChoiceField(choices=[('approve', 'قبول'), ('reject', 'رفض')], widget=forms.Select(attrs={'class': 'form-control'}))
    rejection_reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)