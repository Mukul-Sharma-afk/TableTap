from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Business
from .models import Table
from .models import Menu, MenuItem, MenuCategory

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']


class CompleteRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    role = forms.ChoiceField(choices=[
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ])

    # Owner fields
    business_name = forms.CharField(max_length=255, required=False)
    business_type = forms.CharField(max_length=100, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_no = forms.CharField(max_length=20, required=False)

    # Non owner fields
    business_id = forms.ModelChoiceField(
        queryset=Business.objects.all(),
        required=False,
        label='Select Business',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'owner':
            for field in ['business_name', 'business_type', 'address', 'phone_no']:
                if not cleaned_data.get(field):
                    self.add_error(field, f'{field.replace("_", " ").capitalize()} is required for owners.')
        elif role in ['manager', 'staff']:
            if not cleaned_data.get('business_id'):
                self.add_error('business_id', 'Please select a business.')


class BusinessForm(forms.ModelForm):

    existing_business = forms.ModelChoiceField(
        queryset=Business.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'Select a business...'})
    )

    class Meta:
        model = Business
        fields = ['name', 'business_type', 'address', 'table_count', 'description', 'phone_no']
        exclude = ['table_count']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_no', 'description', 'capacity', 'status']

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.fields['category'].queryset = MenuCategory.objects.filter(menu__business=business)



class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }