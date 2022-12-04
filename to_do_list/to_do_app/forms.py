from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User


# Create your forms here.
'''This file consists of fields that we want to show in Registration form. We can configure the way we need
But our class should inherit the already existing class - 'UserCreationForm' See 'UserRegisterForm' class
The 'Meta' class is used to tell - "To which model should our form submit data to." Here it is - 'User' Model
'''


class NewUserForm(UserCreationForm):
    # Adding a email field in the User Register Form
    first_name = forms.CharField(max_length=15)
    last_name = forms.CharField(max_length=15)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username","first_name", "last_name", "email", "password1", "password2")
    #
    # def save(self, commit=True):
    #     user = super(NewUserForm, self).save(commit=False)
    #     user.email = self.cleaned_data['email']
    #     if commit:
    #         user.save()
    #     return user


# Notify the User when he tries to Reset Password with Incorrect Email
class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = 'There is no user registered with this email address.'
            self.add_error('email', msg)
        return email
