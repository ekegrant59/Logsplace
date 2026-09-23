from django.db import models
from django.utils.html import mark_safe
from userauths.models import User
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
from decimal import Decimal
from django.utils.timezone import now

CATEGORY = (
    ("facebook_50", "Facebook (Below 50 Friends)"),
    ("facebook_other", "Facebook (Other Countries)"),
    ("facebook_dating", "Facebook Dating"),
    ("facebook_usa", "Facebook USA"),
    ("instagram", "Instagram"),
    ("texting_numbers", "Texting Numbers"),
    ("tools", "Tools"),
    ("twitter", "Twitter"),
    ("vpn", "VPN"),
    ("reddit", "Reddit"),
    ("tiktok", "Tiktok"),
    ("mails", "Mails"),
)

class Category(models.Model):
    cid = ShortUUIDField(length=10, max_length=20, prefix="cat", alphabet="abcdefgaccs", null=True)
    name = models.CharField(max_length=5000)
    image = models.URLField(blank=True)
    from_api = models.BooleanField(default=False)
    from_acc = models.BooleanField(default=False)
    cat_id = models.CharField(max_length=5000, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Bank_Account(models.Model):
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     bank_name = models.CharField(max_length=300)
     account_name = models.CharField(max_length=300)
     account_number = models.CharField(max_length=300)
     
     
     class Meta:
          verbose_name_plural = "Bank Accounts"
          
          
class Logs(models.Model):
    name = models.CharField(max_length=5000)
    category = models.CharField(choices=CATEGORY, max_length=200, blank=True, null=True)
    cat = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="thelogs", blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="log_image", blank=True, default="fb.jpeg")
    image_url = models.TextField(null=True, blank=True)
    from_api = models.BooleanField(default=False)
    from_acc = models.BooleanField(default=False)
    api_id = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, default="us")
    qty = models.CharField(max_length=300, default="1")
    price = models.CharField(max_length=300)

    class Meta:
            verbose_name_plural = "Logs"

    def log_image(self):
        return mark_safe('<img src="%s" width="50" height="50" >' % (self.image.url))
    
    def __str__(self):
        return self.name

class LogDetails(models.Model):
    which_log = models.ForeignKey(Logs, on_delete=models.SET_NULL, null=True, related_name="logcount")
    details = models.TextField(null=True)
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "LogDetails"

    def __str__(self):
        return self.which_log.name
        
class ProfileDetails(models.Model):
    which_log = models.ForeignKey(Logs, on_delete=models.SET_NULL, null=True, related_name="profilelog")
    details = models.TextField(null=True)
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "ProfileDetails"

    def __str__(self):
        return self.which_log.name
    

class Wallet(models.Model):
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     email = models.EmailField(blank=True, null=True)
     balance = models.CharField(max_length=10000000)
     to_add = models.CharField(max_length=10000000, blank=True, null=True, default="0")
     vendor = models.BooleanField(default=False)

     class Meta:
          verbose_name_plural = "Wallet"
          
     def __str__(self):
        return self.user.email

class Transaction_History(models.Model):
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     email = models.EmailField(blank=True, null=True)
     amount = models.CharField(max_length=20000, null=True, blank=True)
     feedback = models.TextField(null=True, blank=True)
     status = models.CharField(max_length=200, null=True, blank=True)
     date = models.DateTimeField(auto_now_add=True, null=True)

     class Meta:
          verbose_name_plural = "Transaction History"

        
class Order(models.Model):
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     log = models.CharField(max_length=20000, null=True)
     category = models.CharField(max_length=20000, null=True, blank=True)
     email = models.EmailField(blank=True, null=True)
     amount = models.CharField(max_length=20000, null=True, blank=True)
     qty = models.CharField(max_length=300, null="True", default="1")
     info = models.TextField(null=True, blank=True)
     date = models.DateTimeField(auto_now_add=True, null=True)
     
class LogOrder(models.Model):
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name="logorder")
     log = models.TextField(null=True, blank=True)
     date = models.DateTimeField(auto_now_add=True, null=True)
     
     class Meta:
          verbose_name_plural = "Log Order"
          
class Cart(models.Model):
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     log = models.ForeignKey(Logs, on_delete=models.SET_NULL, null=True)

     class Meta:
          verbose_name_plural = "Cart"

class ViewLog(models.Model):
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     log = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)

     class Meta:
          verbose_name_plural = "View Logs"
          
class Payment(models.Model):
    transaction_id = models.TextField(blank=True, null=True)
          
class Shopviaclone22(models.Model):
     username = models.TextField(null=True)
     password = models.TextField(null=True)
     percentage = models.CharField(max_length=100, null=True, blank=True)
     balance = models.CharField(max_length=100, null=True, blank=True)

     class Meta:
          verbose_name_plural = "Shopviaclone22"
         
     def apply_to_logs(self):
        """Apply the current percentage to all log prices."""
        logs = Logs.objects.filter(from_api=True)
        for log in logs:
            log_price = float(log.price)  # Ensure log.price is treated as a float
            percentage = float(self.percentage)  # Ensure percentage is treated as a float
            log.price = int(log_price * (1 + percentage / 100))
            log.save()

     def reverse_logs(self):
        """Reverse the previously applied percentage from log prices before updating."""
        logs = Logs.objects.filter(from_api=True)
        for log in logs:
            log.price = log.price / (1 + self.percentage / 100)
            log.save()

     def save(self, *args, **kwargs):
        # Check if this instance already exists
        if self.pk:
            # Reverse old percentage effect before updating
            old_instance = Shopviaclone22.objects.get(pk=self.pk)
            old_percentage = old_instance.percentage
            logs = Logs.objects.filter(from_api=True)
            for log in logs:
                log.price = Decimal(log.price) / (1 + Decimal(old_percentage) / 100)
                log.save()

        super().save(*args, **kwargs)
        self.apply_to_logs()  # Apply new percentage after saving
        
class Clonevn(models.Model):
     username = models.TextField(null=True)
     password = models.TextField(null=True)
     percentage = models.CharField(max_length=100, null=True, blank=True)
     balance = models.CharField(max_length=100, null=True, blank=True)

     class Meta:
          verbose_name_plural = "Clonevn"
         
     def apply_to_logs(self):
        """Apply the current percentage to all log prices."""
        logs = Logs.objects.filter(from_api=True)
        for log in logs:
            log_price = float(log.price)  # Ensure log.price is treated as a float
            percentage = float(self.percentage)  # Ensure percentage is treated as a float
            log.price = int(log_price * (1 + percentage / 100))
            log.save()

     def reverse_logs(self):
        """Reverse the previously applied percentage from log prices before updating."""
        logs = Logs.objects.filter(from_api=True)
        for log in logs:
            log.price = log.price / (1 + self.percentage / 100)
            log.save()

     def save(self, *args, **kwargs):
        # Check if this instance already exists
        if self.pk:
            # Reverse old percentage effect before updating
            old_instance = Clonevn.objects.get(pk=self.pk)
            old_percentage = old_instance.percentage
            logs = Logs.objects.filter(from_api=True)
            for log in logs:
                log.price = Decimal(log.price) / (1 + Decimal(old_percentage) / 100)
                log.save()

        super().save(*args, **kwargs)
        self.apply_to_logs()  # Apply new percentage after saving
        
class Accsmtp(models.Model):
     username = models.TextField(null=True)
     password = models.TextField(null=True)
     percentage = models.CharField(max_length=100, null=True, blank=True)
     balance = models.CharField(max_length=100, null=True, blank=True)

     class Meta:
          verbose_name_plural = "Accsmtp"
         
     def apply_to_logs(self):
        """Apply the current percentage to all log prices."""
        logs = Logs.objects.filter(from_acc=True)
        for log in logs:
            log_price = float(log.price)  # Ensure log.price is treated as a float
            percentage = float(self.percentage)  # Ensure percentage is treated as a float
            log.price = int(log_price * (1 + percentage / 100))
            log.save()

     def reverse_logs(self):
        """Reverse the previously applied percentage from log prices before updating."""
        logs = Logs.objects.filter(from_acc=True)
        for log in logs:
            log.price = log.price / (1 + self.percentage / 100)
            log.save()

     def save(self, *args, **kwargs):
        # Check if this instance already exists
        if self.pk:
            # Reverse old percentage effect before updating
            old_instance = Accsmtp.objects.get(pk=self.pk)
            old_percentage = old_instance.percentage
            logs = Logs.objects.filter(from_acc=True)
            for log in logs:
                log.price = Decimal(log.price) / (1 + Decimal(old_percentage) / 100)
                log.save()

        super().save(*args, **kwargs)
        self.apply_to_logs()  # Apply new percentage after saving

class Contact(models.Model):
     name = models.CharField(max_length=10000)
     email = models.EmailField()
     subject = models.CharField(max_length=10000)
     message = models.TextField()

     class Meta:
          verbose_name_plural = "Contact"
          
class DollarRate(models.Model):
    rate = models.CharField(max_length=100, help_text="Please do not add another dollar rate. Keep Changing this one")
    
    class Meta:
        verbose_name_plural = "Dollar Rate"
        
class Verify_Payment(models.Model):
    key = models.TextField(null=True)

    class Meta:
            verbose_name_plural = "Verify Payments"
            

# SMS Section

class SMSOrder(models.Model):
     number_id = models.TextField(null=True)
     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     service = models.TextField(null=True)
     key = models.TextField(null=True)
     amount = models.TextField(null=True, blank=True)
     time = models.PositiveIntegerField(null=True, blank=True)
     last_updated = models.DateTimeField(auto_now_add=True, null=True)
     status = models.TextField(null=True)
     profit = models.TextField(null=True)
     phone_number = models.TextField(null=True)
     delete = models.BooleanField(default=False)
     type = models.CharField(null=True, max_length=300)
     info = models.TextField(null=True, blank=True)
     vendor = models.BooleanField(default=False)
     date = models.DateTimeField(auto_now_add=True, null=True)
     
     def get_dynamic_duration(self):
        """
        Calculate the dynamically reduced duration based on the time passed.
        """
        elapsed_time = (now() - self.last_updated).total_seconds()
        remaining_time = max(0, self.time - int(elapsed_time))
        return remaining_time

class S2_Num(models.Model):
    key = models.TextField(blank=True, null=True)
    name = models.TextField()
    price = models.TextField()
    # vendor_price = models.TextField(null=True)
    custom_price = models.TextField(null=True)
    country = models.TextField(null=True, blank=True)
    has_premium = models.BooleanField(default=True)
    price_changed = models.BooleanField(default=False)
    type = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.TextField(blank=True)

    class Meta:
            verbose_name_plural = "S2 Numbers"

    def __str__(self):
        return self.name
        
class Country(models.Model):
     cid = models.TextField(null=True)
     name = models.TextField(null=True)
     flag= models.TextField(null=True)

     def __str__(self):
          return self.name

class Service(models.Model):
     sid = models.TextField(null=True)
     name = models.TextField(null=True)
     flag= models.TextField(null=True)

     def __str__(self):
          return self.name

# SMM Part
class SMMCategory(models.Model):
    name = models.CharField(max_length=500, null=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "SMM Categories"
        
    def __str__(self):
        return self.name
        
class Platform(models.Model):
    name = models.CharField(max_length=500, null=True)
    code = models.CharField(max_length=500, null=True)
    
    class Meta:
        verbose_name_plural = "Platform"
        
    def __str__(self):
        return self.name
        
class SMMService(models.Model):
    service_id = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=500, null=True)
    type = models.CharField(max_length=100, null=True)
    rate = models.TextField(null=True)
    min = models.TextField(null=True)
    max = models.TextField(null=True)    
    from_id = models.CharField(max_length=100, null=True)
    dripfeed = models.CharField(max_length=100, null=True)
    refill = models.CharField(max_length=100, null=True)
    cancel = models.CharField(max_length=100, null=True)
    category = models.ForeignKey(SMMCategory, null=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "SMM Services"
        
    def __str__(self):
        return self.name
        
class SMMOrder(models.Model):
    order_id = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    serviceid = models.TextField(null=True)
    service = models.ForeignKey(SMMService, null=True, blank=True, on_delete=models.SET_NULL)
    link = models.URLField(null=True)
    comment = models.TextField(null=True, blank=True)
    qty = models.TextField(null=True)
    api_key = models.TextField(null=True)
    api_url = models.TextField(null=True)
    api_name = models.TextField(null=True)
    price = models.TextField(null=True)
    charge = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    start_count = models.CharField(max_length=100, null=True, blank=True)
    remain = models.CharField(max_length=100, null=True, blank=True)
    refunded = models.BooleanField(default=False)
    admin_change = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        verbose_name_plural = "SMM Orders"
        
    def __str__(self):
        return self.user.username
        
class APIs(models.Model):
    name = models.TextField(null=True)
    api_key = models.TextField(null=True)
    api_url = models.TextField(null=True)
    status = models.BooleanField(default=False)
    percentage = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True, blank=True)
    balance = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "APIs"
        
    def __str__(self):
        return self.name         