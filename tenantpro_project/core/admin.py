from django.contrib import admin
from .models import Property, Unit, Lease, RentPayment, MaintenanceRequest, Complaint, Announcement, Notification, Message
for m in [Property, Unit, Lease, RentPayment, MaintenanceRequest, Complaint, Announcement, Notification, Message]:
    admin.site.register(m)
