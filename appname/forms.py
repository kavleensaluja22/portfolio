from django import forms
from django.core.validators import EmailValidator
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    """
    Form for handling contact messages
    """

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject (Optional)',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message...',
                'rows': 5,
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add custom styling classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': f'contact-input {field_name}-input'
            })

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name.strip() if name else name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validator = EmailValidator()
            try:
                validator(email)
            except forms.ValidationError:
                raise forms.ValidationError("Please enter a valid email address.")
        return email

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message and len(message.strip()) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message.strip() if message else message

class QuickContactForm(forms.Form):
    """
    Simplified contact form for quick messages
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'quick-contact-input',
            'placeholder': 'Your Name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'quick-contact-input',
            'placeholder': 'Your Email',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'quick-contact-input',
            'placeholder': 'Quick message...',
            'rows': 3,
        })
    )

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message and len(message.strip()) < 5:
            raise forms.ValidationError("Message must be at least 5 characters long.")
        return message.strip() if message else message
