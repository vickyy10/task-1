from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Task
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user registered with this email address.")
        return email


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep the current password."
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'assigned_admin', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'assigned_admin': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_admin'].queryset = User.objects.filter(role='admin')

        if self.instance and self.instance.pk:
            self.fields['password'].required = False

        self.fields['role'].choices = [choice for choice in self.fields['role'].choices if choice[0] != 'superadmin']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            if self.user.is_superadmin:
                self.fields['assigned_to'].queryset = User.objects.filter(role='user',is_superuser=False)
            elif self.user.is_admin:
                self.fields['assigned_to'].queryset = User.objects.filter(assigned_admin=self.user, role='user')
            else:
                self.fields['assigned_to'].queryset = User.objects.none()