"""
Forms for Supermart application
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Product, Category, StockEntry


class UserRegistrationForm(UserCreationForm):
    """User Registration Form"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}))
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'address', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_email(self):
        """Validate email - prevent unauthorized @supermart.com registrations"""
        email = self.cleaned_data.get('email', '').lower()
        
        # Check if email already exists
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        # Check if trying to register with @supermart.com domain
        if '@supermart.com' in email:
            raise forms.ValidationError(
                "❌ @supermart.com email addresses are reserved for authorized staff only. "
                "Please contact the administrator if you're a staff member."
            )
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Auto-generate username from email
        user.username = self.cleaned_data['email'].split('@')[0]
        # Make username unique if it already exists
        base_username = user.username
        counter = 1
        while User.objects.filter(username=user.username).exists():
            user.username = f'{base_username}{counter}'
            counter += 1
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """User Login Form"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ProductForm(forms.ModelForm):
    """Product Form"""
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'description', 'price', 'quantity', 'supplier', 'low_stock_threshold', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
        }


class CategoryForm(forms.ModelForm):
    """Category Form"""
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StockEntryForm(forms.ModelForm):
    """Stock Entry Form"""
    class Meta:
        model = StockEntry
        fields = ['product', 'entry_type', 'quantity', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'entry_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes'}),
        }


class CheckoutForm(forms.Form):
    """Checkout Form"""
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your shipping address'}),
        required=True
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
        required=True
    )
