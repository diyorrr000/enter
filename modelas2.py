# enterprise_erp/backend/finance/models.py
"""
Finance module for Enterprise ERP
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid

class Currency(models.Model):
    """Currency definitions"""
    
    code = models.CharField(_('Currency Code'), max_length=3, primary_key=True)
    name = models.CharField(_('Currency Name'), max_length=50)
    symbol = models.CharField(_('Symbol'), max_length=5)
    exchange_rate = models.DecimalField(_('Exchange Rate'), max_digits=15, decimal_places=6, default=1)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ChartOfAccounts(models.Model):
    """Chart of Accounts structure"""
    
    ACCOUNT_TYPES = (
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    )
    
    ACCOUNT_SUBTYPES = (
        ('current_asset', 'Current Asset'),
        ('fixed_asset', 'Fixed Asset'),
        ('current_liability', 'Current Liability'),
        ('long_term_liability', 'Long Term Liability'),
        ('operating_revenue', 'Operating Revenue'),
        ('non_operating_revenue', 'Non-Operating Revenue'),
        ('operating_expense', 'Operating Expense'),
        ('non_operating_expense', 'Non-Operating Expense'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='chart_of_accounts')
    account_code = models.CharField(_('Account Code'), max_length=20, unique=True)
    account_name = models.CharField(_('Account Name'), max_length=200)
    account_type = models.CharField(_('Account Type'), max_length=20, choices=ACCOUNT_TYPES)
    account_subtype = models.CharField(_('Account Subtype'), max_length=30, choices=ACCOUNT_SUBTYPES)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_accounts')
    
    # Financial Details
    opening_balance = models.DecimalField(_('Opening Balance'), max_digits=20, decimal_places=2, default=0)
    current_balance = models.DecimalField(_('Current Balance'), max_digits=20, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default='USD')
    
    # Settings
    is_active = models.BooleanField(_('Active'), default=True)
    is_system_account = models.BooleanField(_('System Account'), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Chart of Account')
        verbose_name_plural = _('Chart of Accounts')
        unique_together = ['company', 'account_code']
        ordering = ['account_code']
        db_table = 'chart_of_accounts'
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"


class JournalEntry(models.Model):
    """General Journal Entries"""
    
    ENTRY_TYPES = (
        ('general', 'General Journal'),
        ('sales', 'Sales Journal'),
        ('purchase', 'Purchase Journal'),
        ('cash_receipt', 'Cash Receipt Journal'),
        ('cash_disbursement', 'Cash Disbursement Journal'),
        ('adjusting', 'Adjusting Entry'),
        ('closing', 'Closing Entry'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='journal_entries')
    entry_number = models.CharField(_('Entry Number'), max_length=50, unique=True)
    entry_date = models.DateField(_('Entry Date'))
    entry_type = models.CharField(_('Entry Type'), max_length=20, choices=ENTRY_TYPES)
    description = models.TextField(_('Description'))
    
    # Reference
    reference_number = models.CharField(_('Reference Number'), max_length=100, blank=True)
    reference_model = models.CharField(_('Reference Model'), max_length=100, blank=True)
    reference_id = models.UUIDField(_('Reference ID'), null=True, blank=True)
    
    # Status
    status = models.CharField(_('Status'), max_length=20, default='draft', 
                             choices=[('draft', 'Draft'), ('posted', 'Posted'), ('cancelled', 'Cancelled')])
    
    # Financial Summary
    total_debit = models.DecimalField(_('Total Debit'), max_digits=20, decimal_places=2, default=0)
    total_credit = models.DecimalField(_('Total Credit'), max_digits=20, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default='USD')
    
    # Audit
    created_by = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='created_journal_entries')
    posted_by = models.ForeignKey('users.User', on_delete=models.PROTECT, null=True, blank=True, 
                                 related_name='posted_journal_entries')
    posted_at = models.DateTimeField(_('Posted At'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Journal Entry')
        verbose_name_plural = _('Journal Entries')
        ordering = ['-entry_date', '-created_at']
        db_table = 'journal_entries'
        indexes = [
            models.Index(fields=['company', 'entry_date']),
            models.Index(fields=['entry_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.entry_number} - {self.description}"
    
    @property
    def is_balanced(self):
        return self.total_debit == self.total_credit


class JournalEntryLine(models.Model):
    """Individual lines in a journal entry"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    line_number = models.IntegerField(_('Line Number'))
    
    # Account
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='journal_lines')
    
    # Amounts
    debit = models.DecimalField(_('Debit Amount'), max_digits=20, decimal_places=2, default=0)
    credit = models.DecimalField(_('Credit Amount'), max_digits=20, decimal_places=2, default=0)
    
    # Description
    description = models.TextField(_('Description'), blank=True)
    
    # Reference
    reference = models.CharField(_('Reference'), max_length=200, blank=True)
    
    # Tracking
    tracking_category = models.CharField(_('Tracking Category'), max_length=100, blank=True)
    tracking_value = models.CharField(_('Tracking Value'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Journal Entry Line')
        verbose_name_plural = _('Journal Entry Lines')
        ordering = ['journal_entry', 'line_number']
        db_table = 'journal_entry_lines'
    
    def __str__(self):
        return f"Line {self.line_number} of {self.journal_entry.entry_number}"


class Invoice(models.Model):
    """Sales and Purchase Invoices"""
    
    INVOICE_TYPES = (
        ('sales', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
        ('credit_note', 'Credit Note'),
        ('debit_note', 'Debit Note'),
    )
    
    INVOICE_STATUS = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='invoices')
    invoice_type = models.CharField(_('Invoice Type'), max_length=20, choices=INVOICE_TYPES)
    invoice_number = models.CharField(_('Invoice Number'), max_length=100, unique=True)
    
    # Dates
    invoice_date = models.DateField(_('Invoice Date'))
    due_date = models.DateField(_('Due Date'))
    
    # Parties
    customer = models.ForeignKey('sales.Customer', on_delete=models.PROTECT, null=True, blank=True, 
                                related_name='invoices')
    supplier = models.ForeignKey('purchasing.Supplier', on_delete=models.PROTECT, null=True, blank=True, 
                               related_name='invoices')
    
    # Financials
    subtotal = models.DecimalField(_('Subtotal'), max_digits=20, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('Tax Amount'), max_digits=20, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('Discount Amount'), max_digits=20, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('Total Amount'), max_digits=20, decimal_places=2, default=0)
    paid_amount = models.DecimalField(_('Paid Amount'), max_digits=20, decimal_places=2, default=0)
    balance_due = models.DecimalField(_('Balance Due'), max_digits=20, decimal_places=2, default=0)
    
    # Currency
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default='USD')
    exchange_rate = models.DecimalField(_('Exchange Rate'), max_digits=15, decimal_places=6, default=1)
    
    # Status
    status = models.CharField(_('Status'), max_length=20, choices=INVOICE_STATUS, default='draft')
    
    # Payment Terms
    payment_terms = models.TextField(_('Payment Terms'), blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    
    # Metadata
    created_by = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='created_invoices')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-invoice_date', '-created_at']
        db_table = 'invoices'
        indexes = [
            models.Index(fields=['company', 'invoice_type', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.total_amount} {self.currency.code}"
    
    @property
    def is_overdue(self):
        from django.utils.timezone import now
        return self.due_date < now().date() and self.status not in ['paid', 'cancelled']
    
    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        from django.db.models import Sum
        line_items = self.line_items.all()
        self.subtotal = line_items.aggregate(total=Sum('line_total'))['total'] or Decimal('0')
        self.tax_amount = line_items.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.balance_due = self.total_amount - self.paid_amount
        self.save()


class InvoiceLine(models.Model):
    """Invoice line items"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    line_number = models.IntegerField(_('Line Number'))
    
    # Item Details
    product = models.ForeignKey('inventory.Product', on_delete=models.PROTECT, null=True, blank=True)
    service = models.ForeignKey('sales.Service', on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(_('Description'))
    
    # Quantity and Price
    quantity = models.DecimalField(_('Quantity'), max_digits=15, decimal_places=4, default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=15, decimal_places=4, default=0)
    discount_percent = models.DecimalField(_('Discount %'), max_digits=5, decimal_places=2, default=0)
    
    # Financials
    line_total = models.DecimalField(_('Line Total'), max_digits=20, decimal_places=2, default=0)
    tax_rate = models.DecimalField(_('Tax Rate %'), max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('Tax Amount'), max_digits=20, decimal_places=2, default=0)
    
    # Accounting
    revenue_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, 
                                       related_name='invoice_revenue_lines')
    
    class Meta:
        verbose_name = _('Invoice Line')
        verbose_name_plural = _('Invoice Lines')
        ordering = ['invoice', 'line_number']
        db_table = 'invoice_lines'
    
    def __str__(self):
        return f"Line {self.line_number} of {self.invoice.invoice_number}"
    
    def calculate_totals(self):
        """Calculate line totals"""
        discount_factor = 1 - (self.discount_percent / 100)
        subtotal = self.quantity * self.unit_price * discount_factor
        self.line_total = subtotal
        self.tax_amount = subtotal * (self.tax_rate / 100)
        self.save()


class Payment(models.Model):
    """Customer and Supplier Payments"""
    
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('other', 'Other'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='payments')
    payment_number = models.CharField(_('Payment Number'), max_length=100, unique=True)
    
    # Payment Details
    payment_date = models.DateField(_('Payment Date'))
    payment_method = models.CharField(_('Payment Method'), max_length=20, choices=PAYMENT_METHODS)
    payment_reference = models.CharField(_('Payment Reference'), max_length=200, blank=True)
    amount = models.DecimalField(_('Amount'), max_digits=20, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default='USD')
    exchange_rate = models.DecimalField(_('Exchange Rate'), max_digits=15, decimal_places=6, default=1)
    
    # Parties
    customer = models.ForeignKey('sales.Customer', on_delete=models.PROTECT, null=True, blank=True)
    supplier = models.ForeignKey('purchasing.Supplier', on_delete=models.PROTECT, null=True, blank=True)
    
    # Bank Details
    bank_account = models.ForeignKey('BankAccount', on_delete=models.PROTECT, null=True, blank=True)
    
    # Status
    status = models.CharField(_('Status'), max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    
    # Metadata
    created_by = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='created_payments')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date', '-created_at']
        db_table = 'payments'
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount} {self.currency.code}"


class PaymentAllocation(models.Model):
    """Allocate payments to invoices"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='allocations')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payment_allocations')
    allocated_amount = models.DecimalField(_('Allocated Amount'), max_digits=20, decimal_places=2)
    
    # Metadata
    allocated_at = models.DateTimeField(_('Allocated At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Payment Allocation')
        verbose_name_plural = _('Payment Allocations')
        unique_together = ['payment', 'invoice']
        db_table = 'payment_allocations'
    
    def __str__(self):
        return f"{self.payment.payment_number} -> {self.invoice.invoice_number}"


class BankAccount(models.Model):
    """Company bank accounts"""
    
    ACCOUNT_TYPES = (
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('credit_card', 'Credit Card'),
        ('loan', 'Loan Account'),
        ('investment', 'Investment Account'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='bank_accounts')
    account_name = models.CharField(_('Account Name'), max_length=200)
    account_type = models.CharField(_('Account Type'), max_length=20, choices=ACCOUNT_TYPES)
    
    # Bank Details
    bank_name = models.CharField(_('Bank Name'), max_length=200)
    branch_name = models.CharField(_('Branch Name'), max_length=200, blank=True)
    account_number = models.CharField(_('Account Number'), max_length=50)
    routing_number = models.CharField(_('Routing Number'), max_length=50, blank=True)
    iban = models.CharField(_('IBAN'), max_length=50, blank=True)
    swift_code = models.CharField(_('SWIFT/BIC Code'), max_length=20, blank=True)
    
    # Financials
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default='USD')
    opening_balance = models.DecimalField(_('Opening Balance'), max_digits=20, decimal_places=2, default=0)
    current_balance = models.DecimalField(_('Current Balance'), max_digits=20, decimal_places=2, default=0)
    
    # Settings
    is_active = models.BooleanField(_('Active'), default=True)
    is_default = models.BooleanField(_('Default Account'), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')
        unique_together = ['company', 'account_number']
        ordering = ['bank_name', 'account_name']
        db_table = 'bank_accounts'
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_name}"


class FinancialReport(models.Model):
    """Generated financial reports"""
    
    REPORT_TYPES = (
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
        ('cash_flow', 'Cash Flow Statement'),
        ('trial_balance', 'Trial Balance'),
        ('general_ledger', 'General Ledger'),
        ('aged_receivables', 'Aged Receivables'),
        ('aged_payables', 'Aged Payables'),
        ('profit_loss', 'Profit & Loss Statement'),
        ('budget_vs_actual', 'Budget vs Actual'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='financial_reports')
    report_type = models.CharField(_('Report Type'), max_length=50, choices=REPORT_TYPES)
    report_name = models.CharField(_('Report Name'), max_length=200)
    
    # Period
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    
    # Report Data
    report_data = models.JSONField(_('Report Data'), default=dict)
    summary = models.JSONField(_('Summary'), default=dict)
    generated_filters = models.JSONField(_('Generated Filters'), default=dict)
    
    # Format
    format = models.CharField(_('Format'), max_length=20, default='json',
                            choices=[('json', 'JSON'), ('html', 'HTML'), ('pdf', 'PDF'), ('excel', 'Excel')])
    
    # Status
    status = models.CharField(_('Status'), max_length=20, default='generating',
                            choices=[('generating', 'Generating'), ('ready', 'Ready'), ('failed', 'Failed')])
    
    # Storage
    file_path = models.CharField(_('File Path'), max_length=500, blank=True)
    file_size = models.BigIntegerField(_('File Size'), null=True, blank=True)
    
    # Metadata
    generated_by = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='generated_reports')
    generated_at = models.DateTimeField(_('Generated At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Financial Report')
        verbose_name_plural = _('Financial Reports')
        ordering = ['-generated_at']
        db_table = 'financial_reports'
    
    def __str__(self):
        return f"{self.report_name} - {self.start_date} to {self.end_date}"
