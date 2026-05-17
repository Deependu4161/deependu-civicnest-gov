from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('chat/', views.chatbot, name='chatbot'),

    path('api/notif/count/', views.notif_count, name='notif_count'),
    path('api/notif/dropdown/', views.notif_dropdown, name='notif_dropdown'),
    path('api/notif/mark-all/', views.notif_mark_all_read, name='notif_mark_all'),
    path('api/notif/mark/<int:notif_id>/', views.notif_mark_one, name='notif_mark_one'),

    path('tenant/receipt/<int:pay_id>/', views.payment_receipt, name='payment_receipt'),

    path('admin-zone/', views.admin_dash, name='admin_dash'),
    path('admin-zone/properties/', views.admin_properties, name='admin_properties'),
    path('admin-zone/users/', views.admin_users, name='admin_users'),
    path('admin-zone/rent/', views.admin_rent, name='admin_rent'),
    path('admin-zone/maintenance/', views.admin_maintenance, name='admin_maintenance'),
    path('admin-zone/verify/', views.admin_verify, name='admin_verify'),
    path('admin-zone/announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin-zone/reports/', views.admin_reports, name='admin_reports'),

    path('owner/', views.owner_dash, name='owner_dash'),
    path('owner/properties/', views.owner_properties, name='owner_properties'),
    path('owner/tenants/', views.owner_tenants, name='owner_tenants'),
    path('owner/rent/', views.owner_rent, name='owner_rent'),
    path('owner/maintenance/', views.owner_maintenance, name='owner_maintenance'),
    path('owner/complaints/', views.owner_complaints, name='owner_complaints'),  # NEW
    path('owner/leases/', views.owner_leases, name='owner_leases'),
    path('owner/messages/', views.owner_messages, name='owner_messages'),

    path('tenant/', views.tenant_dash, name='tenant_dash'),
    path('tenant/rent/', views.tenant_rent, name='tenant_rent'),
    path('tenant/maintenance/', views.tenant_maintenance, name='tenant_maintenance'),
    path('tenant/complaints/', views.tenant_complaints, name='tenant_complaints'),
    path('tenant/lease/', views.tenant_lease, name='tenant_lease'),
    path('tenant/history/', views.tenant_history, name='tenant_history'),
    path('tenant/notifications/', views.tenant_notifications, name='tenant_notifications'),
    path('tenant/messages/', views.tenant_messages, name='tenant_messages'),
    path('tenant/profile/', views.tenant_profile, name='tenant_profile'),

    path('society-admin/', views.sa_dash, name='sa_dash'),
    path('society-admin/maintenance/', views.sa_maintenance, name='sa_maintenance'),
    path('society-admin/announcements/', views.sa_announcements, name='sa_announcements'),
    path('society-admin/community/', views.sa_community, name='sa_community'),
    path('society-admin/complaints/', views.sa_complaints, name='sa_complaints'),  # NEW
    path('society-admin/reports/', views.sa_reports, name='sa_reports'),
    path('society-admin/users/', views.sa_users, name='sa_users'),
    path('society-admin/verify/', views.sa_verify, name='sa_verify'),

    path('pay/simulate/', views.simulate_pay, name='simulate_pay'),
    path('razorpay/create-order/', views.razorpay_create_order, name='razorpay_create_order'),
    path('razorpay/verify/', views.razorpay_verify_payment, name='razorpay_verify'),
]
