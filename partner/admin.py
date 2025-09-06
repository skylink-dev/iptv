from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django import forms
from mptt.admin import DraggableMPTTAdmin
from .models import Partner, WalletTransaction
from decimal import Decimal
from django.utils.html import format_html


# --- Form for wallet type and amounts ---
class DistributionForm(forms.Form):
    wallet_type = forms.ChoiceField(choices=WalletTransaction.WALLET_CHOICES, label="Select Wallet Type")
    first_amount = forms.DecimalField(label="First Partner Amount", min_value=0, decimal_places=2, required=True)
    second_amount = forms.DecimalField(label="Second Partner Amount", min_value=0, decimal_places=2, required=True)


# --- Form for WalletTransaction create view ---
class WalletTransactionForm(forms.ModelForm):
    class Meta:
        model = WalletTransaction
        fields = ['partner', 'wallet_type', 'type', 'amount', 'remarks']
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'wallet_type': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'type': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'e.g., 40.00'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter transaction details (e.g., Distribution for main wallet)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partner'].help_text = "Select the partner receiving this transaction."
        self.fields['wallet_type'].help_text = "Choose the wallet (e.g., Main, Offer, Virtual, Physical)."
        self.fields['type'].help_text = "Select 'Credit' to add funds or 'Debit' to subtract funds."
        self.fields['amount'].help_text = "Enter the transaction amount (e.g., 40.00). Must be positive."
        self.fields['remarks'].help_text = "Describe the purpose of this transaction (e.g., 'Payment for services')."


# --- Inline for WalletTransaction ---
class WalletTransactionInline(admin.TabularInline):
    model = WalletTransaction
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('wallet_type', 'type', 'amount', 'remarks', 'created_at')
    show_change_link = False

    def has_delete_permission(self, request, obj=None):
        return False


# --- Admin for Partner ---
@admin.register(Partner)
class PartnerAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions', 'indented_title', 'type', 'code', 'region',
        'email', 'phone_number', 'is_active',
        'main_balance', 'offer_balance', 'virtual_balance', 'physical_balance', 'created_at'
    )
    list_display_links = ('indented_title',)
    list_filter = ('is_active', 'type', 'region')
    search_fields = ('name', 'code', 'email', 'phone_number')
    ordering = ('code',)
    list_per_page = 25

    inlines = [WalletTransactionInline]
    actions = ['apply_distribution']

    # Custom admin page (unchanged, using existing template)
    change_list_template = "admin/partner/partner_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('tree-view/', self.admin_site.admin_view(self.tree_view), name='partner_tree_view'),
        ]
        return custom_urls + urls

    def tree_view(self, request):
        tree_data = Partner.objects.all().order_by('tree_id', 'lft')
        context = dict(
            self.admin_site.each_context(request),
            opts=self.model._meta,
            tree_data=tree_data,
            title="Partner Tree View"
        )
        return TemplateResponse(request, "admin/partner/tree_view.html", context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        Partner.objects.rebuild()

    def apply_distribution(self, request, queryset):
        """
        Admin action to apply distribution with user-specified wallet type and amounts.
        """
        if 'apply' in request.POST:
            form = DistributionForm(request.POST)
            if form.is_valid():
                wallet_type = form.cleaned_data['wallet_type']
                first_amount = form.cleaned_data['first_amount']
                second_amount = form.cleaned_data['second_amount']
                root_partners = queryset.filter(parent__isnull=True).order_by('created_at')
                if root_partners.exists():
                    # Clear existing distribution transactions to avoid duplicates
                    for partner in root_partners:
                        WalletTransaction.objects.filter(
                            partner=partner,
                            remarks__startswith="Distribution:"
                        ).delete()
                    # Trigger distribution with dynamic amounts
                    root_partners[0].calculate_distribution(
                        wallet_type=wallet_type,
                        first_amount=first_amount,
                        second_amount=second_amount
                    )
                    self.message_user(request, f"Distribution applied to {wallet_type} wallet with amounts {first_amount} for first partner and {second_amount} for second partner.")
                else:
                    self.message_user(request, "No root partners selected. Please select at least one root partner.", level='error')
                return None
            else:
                self.message_user(request, "Invalid form submission. Please check the amounts.", level='error')

        form = DistributionForm()
        return TemplateResponse(
            request,
            'admin/partner/distribution_form.html',
            {
                'title': 'Select Wallet Type and Amounts for Distribution',
                'form': form,
                'opts': self.model._meta,
                'action': 'apply_distribution',
                'selected_objects': queryset,
            }
        )

    apply_distribution.short_description = "Apply distribution with custom amounts"

    # Display balances
    def main_balance(self, obj):
        return obj.get_balance_by_wallet_type('main')
    main_balance.short_description = 'Main Balance'

    def offer_balance(self, obj):
        return obj.get_balance_by_wallet_type('offer')
    offer_balance.short_description = 'Offer Balance'

    def virtual_balance(self, obj):
        return obj.get_balance_by_wallet_type('virtual')
    virtual_balance.short_description = 'Virtual Balance'

    def physical_balance(self, obj):
        return obj.get_balance_by_wallet_type('physical')
    physical_balance.short_description = 'Physical Balance'

