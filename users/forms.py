from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Profile, Feedback, HomeSpace, HomeSpaceReview


# --- Custom Validators ---
def validate_username_min_length(value):
    """Validate that username has at least 8 characters"""
    if len(value) < 8:
        raise ValidationError(
            'Username must be at least 8 characters long.',
            code='username_too_short'
        )


def validate_password_strength(value):
    """Validate that password contains at least one special character and one capital letter"""
    errors = []
    
    # Check for at least one capital letter
    if not re.search(r'[A-Z]', value):
        errors.append('Password must contain at least one capital letter.')
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', value):
        errors.append('Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>/?).')
    
    if errors:
        raise ValidationError(errors)


# --- Signup Form ---
class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[validate_username_min_length],
        help_text='Username must be at least 8 characters long.',
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username (min 8 characters)'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password (min 1 capital letter & 1 special character)'
        }),
        validators=[validate_password_strength],
        help_text='Password must contain at least one capital letter and one special character.'
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password'
        }),
        help_text='Enter the same password as before, for verification.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original help text for template rendering
        # Don't modify help_text here, let template handle it
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password_strength(password1)
        return password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# --- Profile Form ---
class ProfileForm(forms.ModelForm):
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'text',
            'class': 'date-picker-input',
            'placeholder': 'Select date of birth'
        }),
        required=False,
        label='Date of Birth'
    )
    
    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'readonly': True,
            'class': 'age-input-readonly'
        }),
        required=False,
        label='Age (Auto-calculated)'
    )

    class Meta:
        model = Profile
        fields = (
            # 🧍 Basic Info
            'full_name', 'gender', 'dob', 'age',

            # 📞 Contact Info
            'phone', 'area', 'city', 'state',

            # 🎓 Education & Career
            'qualification', 'occupation', 'budget',

            # 🌸 Lifestyle & Preferences
            'religion', 'marital_status', 'hobbies', 'lifestyle',

            # 🖼 Profile Picture & Bio
            'photo', 'bio',

            # 🪪 ID Proof
            'id_proof',
        )

        widgets = {
            'area': forms.TextInput(attrs={
                'placeholder': 'Enter area/locality (e.g., Koramangala, Bandra, Connaught Place)'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'City (optional)'
            }),
            'hobbies': forms.Textarea(attrs={'rows': 2}),
            'lifestyle': forms.Textarea(attrs={'rows': 2}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get('dob')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            cleaned_data['age'] = age
        return cleaned_data


# --- Feedback Form ---
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your thoughts about Cribsy...'}),
        }


# --- HomeSpace Form ---
class HomeSpaceForm(forms.ModelForm):
    class Meta:
        model = HomeSpace
        fields = ['title', 'description', 'address', 'city', 'state', 'rent', 'available_from']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cozy 2BHK in Downtown'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your space...'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'rent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly rent in INR'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# --- HomeSpace Review Form ---
class HomeSpaceReviewForm(forms.ModelForm):
    class Meta:
        model = HomeSpaceReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your review of this space...'}),
        }