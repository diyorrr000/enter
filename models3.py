# enterprise_erp/backend/hr/models.py
"""
Human Resources module for Enterprise ERP
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from datetime import date

class Employee(models.Model):
    """Extended employee information"""
    
    EMPLOYMENT_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('intern', 'Intern'),
        ('freelance', 'Freelance'),
    )
    
    EMPLOYMENT_STATUS = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )
    
    MARITAL_STATUS = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='employee_profile')
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='employees_hr')
    
    # Employment Details
    employee_number = models.CharField(_('Employee Number'), max_length=50, unique=True)
    employment_type = models.CharField(_('Employment Type'), max_length=20, choices=EMPLOYMENT_TYPES)
    employment_status = models.CharField(_('Employment Status'), max_length=20, choices=EMPLOYMENT_STATUS, default='active')
    
    # Job Information
    job_title = models.CharField(_('Job Title'), max_length=200)
    job_level = models.CharField(_('Job Level'), max_length=50, blank=True)
    job_description = models.TextField(_('Job Description'), blank=True)
    
    # Department and Reporting
    department = models.ForeignKey('users.Department', on_delete=models.PROTECT, related_name='department_employees')
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                         related_name='subordinates')
    matrix_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='matrix_subordinates')
    
    # Dates
    hire_date = models.DateField(_('Hire Date'))
    probation_end_date = models.DateField(_('Probation End Date'), null=True, blank=True)
    contract_end_date = models.DateField(_('Contract End Date'), null=True, blank=True)
    termination_date = models.DateField(_('Termination Date'), null=True, blank=True)
    
    # Personal Information
    date_of_birth = models.DateField(_('Date of Birth'))
    gender = models.CharField(_('Gender'), max_length=20, choices=GENDER_CHOICES)
    marital_status = models.CharField(_('Marital Status'), max_length=20, choices=MARITAL_STATUS, blank=True)
    nationality = models.CharField(_('Nationality'), max_length=100, blank=True)
    
    # Contact Information
    personal_email = models.EmailField(_('Personal Email'), blank=True)
    personal_phone = models.CharField(_('Personal Phone'), max_length=17, blank=True)
    
    # Emergency Contact
    emergency_contact = models.JSONField(_('Emergency Contact'), default=dict)
    
    # Identification
    national_id = models.CharField(_('National ID'), max_length=50, blank=True)
    passport_number = models.CharField(_('Passport Number'), max_length=50, blank=True)
    passport_expiry = models.DateField(_('Passport Expiry Date'), null=True, blank=True)
    
    # Work Information
    work_location = models.CharField(_('Work Location'), max_length=200, blank=True)
    work_schedule = models.JSONField(_('Work Schedule'), default=dict)
    work_shift = models.CharField(_('Work Shift'), max_length=50, blank=True)
    
    # Financial Information
    salary_currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, default='USD')
    base_salary = models.DecimalField(_('Base Salary'), max_digits=15, decimal_places=2)
    hourly_rate = models.DecimalField(_('Hourly Rate'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Bank Information
    bank_details = models.JSONField(_('Bank Details'), default=dict)
    
    # Benefits
    benefits = models.JSONField(_('Benefits'), default=dict)
    
    # Leave Information
    annual_leave_balance = models.DecimalField(_('Annual Leave Balance'), max_digits=5, decimal_places=1, default=0)
    sick_leave_balance = models.DecimalField(_('Sick Leave Balance'), max_digits=5, decimal_places=1, default=0)
    
    # Documents
    documents = models.JSONField(_('Documents'), default=list)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['employee_number']
        db_table = 'employees'
        indexes = [
            models.Index(fields=['company', 'department']),
            models.Index(fields=['employment_status', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee_number} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def tenure(self):
        """Calculate employment tenure in years"""
        if self.termination_date:
            end_date = self.termination_date
        else:
            end_date = date.today()
        
        if self.hire_date:
            years = (end_date - self.hire_date).days / 365.25
            return round(years, 2)
        return 0


class Attendance(models.Model):
    """Employee attendance tracking"""
    
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('late', 'Late'),
        ('on_leave', 'On Leave'),
        ('holiday', 'Holiday'),
        ('weekend', 'Weekend'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='attendances')
    
    # Date and Time
    attendance_date = models.DateField(_('Attendance Date'))
    check_in_time = models.DateTimeField(_('Check-in Time'), null=True, blank=True)
    check_out_time = models.DateTimeField(_('Check-out Time'), null=True, blank=True)
    
    # Status
    status = models.CharField(_('Attendance Status'), max_length=20, choices=ATTENDANCE_STATUS, default='present')
    
    # Hours
    scheduled_hours = models.DecimalField(_('Scheduled Hours'), max_digits=5, decimal_places=2, default=8)
    worked_hours = models.DecimalField(_('Worked Hours'), max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(_('Overtime Hours'), max_digits=5, decimal_places=2, default=0)
    
    # Leave
    leave_type = models.ForeignKey('LeaveType', on_delete=models.SET_NULL, null=True, blank=True)
    leave_hours = models.DecimalField(_('Leave Hours'), max_digits=5, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    
    # Verification
    verified_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='verified_attendances')
    verified_at = models.DateTimeField(_('Verified At'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendances')
        ordering = ['-attendance_date', 'employee']
        unique_together = ['employee', 'attendance_date']
        db_table = 'attendances'
    
    def __str__(self):
        return f"{self.employee.employee_number} - {self.attendance_date} - {self.status}"
    
    @property
    def is_present(self):
        return self.status == 'present'
    
    @property
    def is_on_leave(self):
        return self.status == 'on_leave'


class LeaveType(models.Model):
    """Types of leave available"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='leave_types')
    name = models.CharField(_('Leave Type Name'), max_length=100)
    code = models.CharField(_('Leave Code'), max_length=20, unique=True)
    
    # Configuration
    is_paid = models.BooleanField(_('Paid Leave'), default=True)
    max_days_per_year = models.IntegerField(_('Maximum Days per Year'), default=0)
    carry_over_days = models.IntegerField(_('Carry Over Days'), default=0)
    requires_approval = models.BooleanField(_('Requires Approval'), default=True)
    approval_workflow = models.JSONField(_('Approval Workflow'), default=list)
    
    # Eligibility
    eligibility_criteria = models.JSONField(_('Eligibility Criteria'), default=dict)
    
    # Documentation
    required_documents = models.JSONField(_('Required Documents'), default=list)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Leave Type')
        verbose_name_plural = _('Leave Types')
        ordering = ['name']
        db_table = 'leave_types'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LeaveRequest(models.Model):
    """Employee leave requests"""
    
    LEAVE_STATUS = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('taken', 'Taken'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='leave_requests')
    
    # Leave Details
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name='requests')
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    total_days = models.DecimalField(_('Total Days'), max_digits=5, decimal_places=1)
    half_day = models.BooleanField(_('Half Day'), default=False)
    
    # Reason
    reason = models.TextField(_('Reason for Leave'))
    contact_during_leave = models.JSONField(_('Contact During Leave'), default=dict)
    
    # Status
    status = models.CharField(_('Status'), max_length=20, choices=LEAVE_STATUS, default='draft')
    
    # Approval
    approvers = models.JSONField(_('Approvers'), default=list)
    current_approver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='pending_leave_approvals')
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_leaves')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)
    
    # Documents
    supporting_documents = models.JSONField(_('Supporting Documents'), default=list)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Leave Request')
        verbose_name_plural = _('Leave Requests')
        ordering = ['-created_at']
        db_table = 'leave_requests'
    
    def __str__(self):
        return f"{self.employee.employee_number} - {self.leave_type.name} - {self.start_date} to {self.end_date}"
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        return self.status == 'pending'


class Payroll(models.Model):
    """Employee payroll processing"""
    
    PAYROLL_STATUS = (
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='payrolls')
    payroll_period = models.CharField(_('Payroll Period'), max_length=50)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    
    # Status
    status = models.CharField(_('Status'), max_length=20, choices=PAYROLL_STATUS, default='draft')
    
    # Financials
    total_gross_salary = models.DecimalField(_('Total Gross Salary'), max_digits=20, decimal_places=2, default=0)
    total_deductions = models.DecimalField(_('Total Deductions'), max_digits=20, decimal_places=2, default=0)
    total_net_salary = models.DecimalField(_('Total Net Salary'), max_digits=20, decimal_places=2, default=0)
    total_employer_contributions = models.DecimalField(_('Total Employer Contributions'), max_digits=20, decimal_places=2, default=0)
    
    # Currency
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, default='USD')
    
    # Processing
    processed_by = models.ForeignKey('users.User', on_delete=models.PROTECT, null=True, blank=True, 
                                    related_name='processed_payrolls')
    processed_at = models.DateTimeField(_('Processed At'), null=True, blank=True)
    approved_by = models.ForeignKey('users.User', on_delete=models.PROTECT, null=True, blank=True, 
                                   related_name='approved_payrolls')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payroll')
        verbose_name_plural = _('Payrolls')
        ordering = ['-start_date']
        db_table = 'payrolls'
        unique_together = ['company', 'payroll_period']
    
    def __str__(self):
        return f"{self.payroll_period} - {self.total_net_salary} {self.currency.code}"


class PayrollItem(models.Model):
    """Individual payroll items for each employee"""
    
    EARNING_TYPES = (
        ('basic', 'Basic Salary'),
        ('allowance', 'Allowance'),
        ('bonus', 'Bonus'),
        ('commission', 'Commission'),
        ('overtime', 'Overtime'),
        ('reimbursement', 'Reimbursement'),
        ('other_earning', 'Other Earning'),
    )
    
    DEDUCTION_TYPES = (
        ('tax', 'Tax'),
        ('social_security', 'Social Security'),
        ('health_insurance', 'Health Insurance'),
        ('pension', 'Pension'),
        ('loan', 'Loan Repayment'),
        ('advance', 'Advance Deduction'),
        ('other_deduction', 'Other Deduction'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='items')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_items')
    
    # Earnings
    basic_salary = models.DecimalField(_('Basic Salary'), max_digits=15, decimal_places=2, default=0)
    allowances = models.JSONField(_('Allowances'), default=list)
    bonuses = models.JSONField(_('Bonuses'), default=list)
    commissions = models.JSONField(_('Commissions'), default=list)
    overtime_earnings = models.DecimalField(_('Overtime Earnings'), max_digits=15, decimal_places=2, default=0)
    other_earnings = models.JSONField(_('Other Earnings'), default=list)
    
    # Deductions
    tax_deductions = models.DecimalField(_('Tax Deductions'), max_digits=15, decimal_places=2, default=0)
    social_security = models.DecimalField(_('Social Security'), max_digits=15, decimal_places=2, default=0)
    health_insurance = models.DecimalField(_('Health Insurance'), max_digits=15, decimal_places=2, default=0)
    pension_contributions = models.DecimalField(_('Pension Contributions'), max_digits=15, decimal_places=2, default=0)
    loan_deductions = models.JSONField(_('Loan Deductions'), default=list)
    other_deductions = models.JSONField(_('Other Deductions'), default=list)
    
    # Totals
    total_earnings = models.DecimalField(_('Total Earnings'), max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(_('Total Deductions'), max_digits=15, decimal_places=2, default=0)
    net_salary = models.DecimalField(_('Net Salary'), max_digits=15, decimal_places=2, default=0)
    
    # Employer Contributions
    employer_contributions = models.JSONField(_('Employer Contributions'), default=list)
    
    # Payment
    bank_account = models.JSONField(_('Bank Account'), default=dict)
    payment_method = models.CharField(_('Payment Method'), max_length=50, default='bank_transfer')
    payment_status = models.CharField(_('Payment Status'), max_length=20, default='pending',
                                     choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')])
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payroll Item')
        verbose_name_plural = _('Payroll Items')
        ordering = ['employee']
        db_table = 'payroll_items'
        unique_together = ['payroll', 'employee']
    
    def __str__(self):
        return f"{self.employee.employee_number} - {self.payroll.payroll_period}"
    
    def calculate_totals(self):
        """Calculate payroll totals"""
        # Calculate total earnings
        allowance_total = sum(item['amount'] for item in self.allowances)
        bonus_total = sum(item['amount'] for item in self.bonuses)
        commission_total = sum(item['amount'] for item in self.commissions)
        other_earning_total = sum(item['amount'] for item in self.other_earnings)
        
        self.total_earnings = (
            self.basic_salary + 
            allowance_total + 
            bonus_total + 
            commission_total + 
            self.overtime_earnings + 
            other_earning_total
        )
        
        # Calculate total deductions
        loan_total = sum(item['amount'] for item in self.loan_deductions)
        other_deduction_total = sum(item['amount'] for item in self.other_deductions)
        
        self.total_deductions = (
            self.tax_deductions +
            self.social_security +
            self.health_insurance +
            self.pension_contributions +
            loan_total +
            other_deduction_total
        )
        
        # Calculate net salary
        self.net_salary = self.total_earnings - self.total_deductions
        
        self.save()
