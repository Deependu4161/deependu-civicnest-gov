from django.db import models
from accounts.models import User
from django.utils import timezone

class Property(models.Model):
    TYPE_CHOICES = [('apartment','Apartment'),('villa','Villa'),('commercial','Commercial'),('pg','PG/Hostel')]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    property_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='apartment')
    total_units = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    society_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_properties')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def occupied_units(self):
        return self.units.filter(is_occupied=True).count()

    def __str__(self):
        return f"{self.name} — {self.city}"

class Unit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=20)
    floor = models.CharField(max_length=10, blank=True)
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    area_sqft = models.PositiveIntegerField(default=0)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_occupied = models.BooleanField(default=False)
    amenities = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.property.name} — Unit {self.unit_number}"

class Lease(models.Model):
    STATUS_CHOICES = [('active','Active'),('expired','Expired'),('terminated','Terminated'),('pending','Pending')]
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leases')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_leases')
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    terms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def months_remaining(self):
        today = timezone.now().date()
        if self.end_date > today:
            diff = (self.end_date.year - today.year) * 12 + (self.end_date.month - today.month)
            return max(diff, 0)
        return 0

    def __str__(self):
        return f"Lease: {self.tenant} @ {self.unit}"

class RentPayment(models.Model):
    STATUS_CHOICES = [('paid','Paid'),('pending','Pending'),('overdue','Overdue'),('partial','Partial')]
    METHOD_CHOICES = [('upi','UPI'),('bank_transfer','Bank Transfer'),('cash','Cash'),('cheque','Cheque'),('razorpay','Razorpay')]
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=300, blank=True)
    month_year = models.CharField(max_length=20)
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rent {self.month_year} — {self.lease.tenant} — {self.status}"

class MaintenanceRequest(models.Model):
    CATEGORY_CHOICES = [
        ('plumbing','Plumbing'),('electrical','Electrical'),('carpentry','Carpentry'),
        ('painting','Painting'),('cleaning','Cleaning'),('appliance','Appliance'),('other','Other')
    ]
    PRIORITY_CHOICES = [('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')]
    STATUS_CHOICES = [('open','Open'),('assigned','Assigned'),('in_progress','In Progress'),('resolved','Resolved'),('closed','Closed')]

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='maintenance_requests')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.CharField(max_length=100, blank=True)
    owner_notes = models.TextField(blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.id} {self.title} — {self.status}"

class Complaint(models.Model):
    STATUS_CHOICES = [('open','Open'),('under_review','Under Review'),('resolved','Resolved'),('closed','Closed')]
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Announcement(models.Model):
    AUDIENCE_CHOICES = [('all','All Users'),('tenants','Tenants Only'),('owners','Owners Only'),('property','Specific Property')]
    title = models.CharField(max_length=200)
    message = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    property = models.ForeignKey(Property, null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notif_type = models.CharField(max_length=20, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:40]}"
