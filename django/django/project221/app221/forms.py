from django import forms
from django.core.exceptions import ValidationError

class RegistrationForm(forms.Form):
    username = forms.CharField(
        label="Логін", 
        min_length=4,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Мінімум 4 символи'})
    )
    
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте складний пароль'})
    )
    
    confirm_password = forms.CharField(
        label="Підтвердіть пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    age = forms.IntegerField(
        label="Вік",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Валідація окремого поля (username)
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if "admin" in username.lower():
            raise ValidationError("Логін не може містити слово 'admin'.")
        return username

    # Валідація віку
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18:
            raise ValidationError("Реєстрація дозволена лише особам від 18 років.")
        return age

    # Валідація всієї форми (співпадіння паролів)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Паролі не співпадають!")