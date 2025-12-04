# enterprise_erp/backend/users/models.py
"""
User and Company models for Enterprise ERP
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid

class Company(models.Model):
    """Enterprise company model"""
    
    COMPANY_TYPES = (
        ('corporation', 'Corporation'),
        ('llc', 'Limited Liability Company'),
        ('partnership', 'Partnership'),
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('nonprofit', 'Non-Profit Organization'),
    )
    
    COMPANY_SIZES = (
        ('small', '1-50 employees'),
        ('medium', '51-500 employees'),
        ('large', '501-5000 employees'),
        ('enterprise', '5000+ employees'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Company Name'), max_length=255, unique=True)
    legal_name = models.CharField(_('Legal Name'), max_length=255)
    tax_id = models.CharField(_('Tax ID/VAT'), max_length=50, unique=True)
    company_type = models.CharField(_('Company Type'), max_length=50, choices=COMPANY_TYPES)
    company_size = models.CharField(_('Company Size'), max_length=20, choices=COMPANY_SIZES)
    
    # Contact Information
    email = models.EmailField(_('Email Address'), unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(_('Phone Number'), validators=[phone_regex], max_length=17)
    
    # Address
    address_line1 = models.CharField(_('Address Line 1'), max_length=255)
    address_line2 = models.CharField(_('Address Line 2'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=100)
    state = models.CharField(_('State/Province'), max_length=100)
    postal_code = models.CharField(_('Postal Code'), max_length=20)
    country = models.CharField(_('Country'), max_length=100, default='United States')
    
    # Financial Information
    currency = models.CharField(_('Currency'), max_length=3, default='USD')
    fiscal_year_start = models.DateField(_('Fiscal Year Start'))
    timezone = models.CharField(_('Timezone'), max_length=50, default='UTC')
    
    # Settings
    is_active = models.BooleanField(_('Active'), default=True)
    subscription_plan = models.CharField(_('Subscription Plan'), max_length=50, default='enterprise')
    subscription_end_date = models.DateField(_('Subscription End Date'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        ordering = ['name']
        db_table = 'companies'
    
    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        return f"{self.address_line1}, {self.city}, {self.state} {self.postal_code}, {self.country}"


class Department(models.Model):
    """Company departments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(_('Department Name'), max_length=100)
    code = models.CharField(_('Department Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    
    # Hierarchy
    parent_department = models.ForeignKey('self', on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name='subdepartments')
    
    # Management
    manager = models.ForeignKey('User', on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='managed_departments')
    
    # Budget
    annual_budget = models.DecimalField(_('Annual Budget'), max_digits=15, decimal_places=2, default=0)
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['company', 'name']
        unique_together = ['company', 'name']
        db_table = 'departments'
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


class User(AbstractUser):
    """Custom User model for Enterprise ERP"""
    
    USER_ROLES = (
        ('super_admin', 'Super Administrator'),
        ('company_admin', 'Company Administrator'),
        ('department_manager', 'Department Manager'),
        ('hr_manager', 'HR Manager'),
        ('finance_manager', 'Finance Manager'),
        ('sales_manager', 'Sales Manager'),
        ('purchase_manager', 'Purchase Manager'),
        ('inventory_manager', 'Inventory Manager'),
        ('employee', 'Employee'),
        ('contractor', 'Contractor'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email Address'), unique=True)
    username = models.CharField(_('Username'), max_length=150, unique=True)
    
    # Company Information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, 
                                  related_name='members', null=True, blank=True)
    
    # Role and Permissions
    role = models.CharField(_('Role'), max_length=50, choices=USER_ROLES, default='employee')
    is_company_admin = models.BooleanField(_('Company Admin'), default=False)
    is_department_manager = models.BooleanField(_('Department Manager'), default=False)
    
    # Personal Information
    phone = models.CharField(_('Phone Number'), max_length=17, blank=True)
    mobile = models.CharField(_('Mobile Number'), max_length=17, blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    national_id = models.CharField(_('National ID'), max_length=50, blank=True)
    passport_number = models.CharField(_('Passport Number'), max_length=50, blank=True)
    
    # Employment Information
    employee_id = models.CharField(_('Employee ID'), max_length=50, unique=True, null=True, blank=True)
    hire_date = models.DateField(_('Hire Date'), null=True, blank=True)
    termination_date = models.DateField(_('Termination Date'), null=True, blank=True)
    job_title = models.CharField(_('Job Title'), max_length=100, blank=True)
    
    # Address
    address_line1 = models.CharField(_('Address Line 1'), max_length=255, blank=True)
    address_line2 = models.CharField(_('Address Line 2'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    state = models.CharField(_('State/Province'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(_('Emergency Contact Name'), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_('Emergency Contact Phone'), max_length=17, blank=True)
    emergency_contact_relation = models.CharField(_('Relationship'), max_length=50, blank=True)
    
    # Financial Information
    bank_name = models.CharField(_('Bank Name'), max_length=100, blank=True)
    bank_account_number = models.CharField(_('Account Number'), max_length=50, blank=True)
    bank_routing_number = models.CharField(_('Routing Number'), max_length=20, blank=True)
    
    # Settings
    language = models.CharField(_('Language'), max_length=10, default='en')
    timezone = models.CharField(_('Timezone'), max_length=50, default='UTC')
    theme = models.CharField(_('Theme'), max_length=20, default='light')
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    is_verified = models.BooleanField(_('Verified'), default=False)
    last_login_ip = models.GenericIPAddressField(_('Last Login IP'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    # Replace AbstractUser fields
    first_name = models.CharField(_('First Name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=150, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['company', 'department']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_employed(self):
        return self.hire_date is not None and self.termination_date is None
    
    @property
    def permissions(self):
        """Get user permissions based on role"""
        from .permissions import get_role_permissions
        return get_role_permissions(self.role)
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """Extended user profile information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Professional Information
    biography = models.TextField(_('Biography'), blank=True)
    skills = models.JSONField(_('Skills'), default=list)
    certifications = models.JSONField(_('Certifications'), default=list)
    education = models.JSONField(_('Education'), default=list)
    work_experience = models.JSONField(_('Work Experience'), default=list)
    
    # Social Media
    linkedin_url = models.URLField(_('LinkedIn Profile'), blank=True)
    twitter_url = models.URLField(_('Twitter Profile'), blank=True)
    github_url = models.URLField(_('GitHub Profile'), blank=True)
    
    # Preferences
    notification_preferences = models.JSONField(_('Notification Preferences'), default=dict)
    email_preferences = models.JSONField(_('Email Preferences'), default=dict)
    
    # Avatar
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"


class UserSession(models.Model):
    """Track user sessions for security"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(_('Session Key'), max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(_('IP Address'))
    user_agent = models.TextField(_('User Agent'))
    location = models.JSONField(_('Location Data'), default=dict, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    last_activity = models.DateTimeField(_('Last Activity'), auto_now=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expires At'))
    
    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-last_activity']
        db_table = 'user_sessions'
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class AuditLog(models.Model):
    """System audit log for tracking all changes"""
    
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('access', 'Access'),
        ('export', 'Export'),
        ('import', 'Import'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='audit_logs')
    
    # Action Details
    action_type = models.CharField(_('Action Type'), max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(_('Model Name'), max_length=100)
    object_id = models.CharField(_('Object ID'), max_length=100)
    object_repr = models.CharField(_('Object Representation'), max_length=255)
    
    # Changes
    old_values = models.JSONField(_('Old Values'), null=True, blank=True)
    new_values = models.JSONField(_('New Values'), null=True, blank=True)
    changes = models.JSONField(_('Changes'), default=dict)
    
    # Request Information
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    request_path = models.CharField(_('Request Path'), max_length=500)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created_at']
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['company', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'model_name']),
        ]
    
    def __str__(self):
        return f"{self.action_type} {self.model_name} by {self.user}"
