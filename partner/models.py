import logging
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)

class Partner(MPTTModel):
    TYPE_CHOICES = (
        ('distributor', 'Distributor'),
        ('operator', 'Operator'),
    )

    name = models.CharField(max_length=255, default="Unnamed Partner")
    code = models.CharField(max_length=50, unique=True, default="PARTNER_000")
    region = models.CharField(max_length=100, default="", blank=True)
    email = models.EmailField(default="", blank=True)
    phone_number = models.CharField(max_length=20, default="", blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="distributor")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            # Create initial zero-balance transactions for all wallet types
            for wallet_type, _ in WalletTransaction.WALLET_CHOICES:
                WalletTransaction.objects.create(
                    partner=self,
                    wallet_type=wallet_type,
                    type='credit',
                    amount=Decimal('0.00'),
                    remarks=f'Initial {wallet_type} wallet balance'
                )
        logger.info(f"Saved Partner {self.name}")

    def calculate_distribution(self, wallet_type='main', first_amount=Decimal('0.00'), second_amount=Decimal('0.00')):
        """
        Distribute dynamic amounts to the specified wallet type for root partners.
        Creates WalletTransaction entries for the first and second partners.
        """
        if wallet_type not in [choice[0] for choice in WalletTransaction.WALLET_CHOICES]:
            logger.error(f"Invalid wallet type {wallet_type} for distribution")
            return

        root_partners = Partner.objects.filter(parent__isnull=True).order_by('created_at')
        if not root_partners.exists():
            logger.warning("No root partners found for distribution")
            return

        for index, partner in enumerate(root_partners):
            amount = Decimal('0.00')
            remarks = f"Distribution: No allocation to {wallet_type} wallet"
            if index == 0 and first_amount > 0:
                amount = first_amount
                remarks = f"Distribution: First partner allocation to {wallet_type} wallet ({amount})"
            elif index == 1 and second_amount > 0:
                amount = second_amount
                remarks = f"Distribution: Second partner allocation to {wallet_type} wallet ({amount})"
            
            if amount > 0:
                WalletTransaction.objects.create(
                    partner=partner,
                    wallet_type=wallet_type,
                    type='credit',
                    amount=amount,
                    remarks=remarks
                )
                logger.info(f"Created transaction for {partner.name}: {amount} to {wallet_type} wallet")
            else:
                logger.info(f"No transaction created for {partner.name}: {amount} to {wallet_type} wallet")

    def get_balance_by_wallet_type(self, wallet_type):
        transactions = self.wallettransaction_set.filter(wallet_type=wallet_type)
        credit = transactions.filter(type='credit').aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
        debit = transactions.filter(type='debit').aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
        return credit - debit

    def get_all_balances(self):
        balances = {}
        for wallet_type, _ in WalletTransaction.WALLET_CHOICES:
            balances[wallet_type] = self.get_balance_by_wallet_type(wallet_type)
        return balances


class WalletTransaction(models.Model):
    WALLET_CHOICES = (
        ('main', 'Main Wallet'),
        ('offer', 'Offer Wallet'),
        ('virtual', 'Virtual Wallet'),
        ('physical', 'Physical Wallet'),
    )

    TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, default=None)
    wallet_type = models.CharField(max_length=10, choices=WALLET_CHOICES, default='main')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='credit')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    remarks = models.TextField(default="No remarks", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.partner.name} - {self.wallet_type} - {self.type} - {self.amount}"