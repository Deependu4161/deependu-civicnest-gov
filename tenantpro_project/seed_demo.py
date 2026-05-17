"""
TenantPro Demo Data Seeder
Run: python seed_demo.py
Creates demo users, properties, units, leases, and rent payment records.
"""
import os
import sys
import django
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenantpro.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import User
from core.models import Property, Unit, Lease, RentPayment, Notification, Announcement

print("\n🌱  TenantPro Demo Seeder Starting...\n")

# ─── Helper ─────────────────────────────────────────────
def make_month(offset=0):
    """Return 'Mon YYYY' string offset months from today."""
    d = date.today() + relativedelta(months=offset)
    return d.strftime("%b %Y")

def first_of(offset=0):
    """First day of month offset from today."""
    d = date.today() + relativedelta(months=offset)
    return d.replace(day=1)

# ─── 1. USERS ────────────────────────────────────────────
print("👤  Creating users...")

admin, _ = User.objects.get_or_create(username='Raja', defaults={
    'first_name': 'Super', 'last_name': 'Admin',
    'email': 'admin@tenantpro.demo',
    'password': make_password('1234'),
    'role': 'admin', 'is_staff': True, 'is_superuser': True,
    'phone': '9000000001',
})

owner1, _ = User.objects.get_or_create(username='rahul_owner', defaults={
    'first_name': 'Rahul', 'last_name': 'Sharma',
    'email': 'rahul@tenantpro.demo',
    'password': make_password('demo1234'),
    'role': 'owner', 'phone': '9812345678',
})

owner2, _ = User.objects.get_or_create(username='priya_owner', defaults={
    'first_name': 'Priya', 'last_name': 'Mehta',
    'email': 'priya@tenantpro.demo',
    'password': make_password('demo1234'),
    'role': 'owner', 'phone': '9823456789',
})

tenant1, _ = User.objects.get_or_create(username='arjun_tenant', defaults={
    'first_name': 'Arjun', 'last_name': 'Verma',
    'email': 'arjun@tenantpro.demo',
    'password': make_password('demo1234'),
    'role': 'tenant', 'phone': '9876543210',
})

tenant2, _ = User.objects.get_or_create(username='sneha_tenant', defaults={
    'first_name': 'Sneha', 'last_name': 'Patel',
    'email': 'sneha@tenantpro.demo',
    'password': make_password('demo1234'),
    'role': 'tenant', 'phone': '9765432109',
})

tenant3, _ = User.objects.get_or_create(username='vikram_tenant', defaults={
    'first_name': 'Vikram', 'last_name': 'Singh',
    'email': 'vikram@tenantpro.demo',
    'password': make_password('demo1234'),
    'role': 'tenant', 'phone': '9654321098',
})

print("   ✅ 6 users created (admin, 2 owners, 3 tenants)\n")

# ─── 2. PROPERTIES ──────────────────────────────────────
print("🏠  Creating properties...")

prop1, _ = Property.objects.get_or_create(
    name='Greenview Apartments', owner=owner1,
    defaults={
        'address': '12, MG Road, Koramangala',
        'city': 'Bengaluru', 'state': 'Karnataka', 'pincode': '560034',
        'property_type': 'apartment', 'total_units': 12,
        'description': 'Modern apartments with great amenities in the heart of Koramangala.',
    }
)

prop2, _ = Property.objects.get_or_create(
    name='Sunrise Residency', owner=owner1,
    defaults={
        'address': '7, Sector 18, Noida',
        'city': 'Noida', 'state': 'Uttar Pradesh', 'pincode': '201301',
        'property_type': 'apartment', 'total_units': 8,
        'description': 'Peaceful 2BHK & 3BHK apartments with 24/7 security.',
    }
)

prop3, _ = Property.objects.get_or_create(
    name='Blue Lotus Villa', owner=owner2,
    defaults={
        'address': '3, Baner Road, Aundh',
        'city': 'Pune', 'state': 'Maharashtra', 'pincode': '411007',
        'property_type': 'villa', 'total_units': 4,
        'description': 'Luxury independent villas with private garden.',
    }
)

print("   ✅ 3 properties created\n")

# ─── 3. UNITS ────────────────────────────────────────────
print("🚪  Creating units...")

unit_data = [
    # prop, unit_no, floor, beds, baths, sqft, rent, deposit
    (prop1, '101', '1',  2, 1, 850,  18000, 36000),
    (prop1, '201', '2',  3, 2, 1100, 25000, 50000),
    (prop1, '301', '3',  2, 1, 850,  18500, 37000),
    (prop2, 'A-1', 'G',  2, 2, 950,  22000, 44000),
    (prop2, 'B-2', '1',  3, 2, 1200, 28000, 56000),
    (prop3, 'V-1', 'G',  4, 3, 2200, 55000, 110000),
]

units = []
for prop, unit_no, floor, beds, baths, sqft, rent, dep in unit_data:
    u, _ = Unit.objects.get_or_create(
        property=prop, unit_number=unit_no,
        defaults={
            'floor': floor, 'bedrooms': beds, 'bathrooms': baths,
            'area_sqft': sqft, 'monthly_rent': rent, 'security_deposit': dep,
            'is_occupied': False,
            'amenities': 'Parking, Lift, 24/7 Water, Power Backup',
        }
    )
    units.append(u)

print(f"   ✅ {len(units)} units created\n")

# ─── 4. LEASES ───────────────────────────────────────────
print("📄  Creating leases...")

lease_configs = [
    # unit, tenant, owner, start_offset_months, duration_months, rent
    (units[0], tenant1, owner1, -5, 12, 18000),   # Arjun — Greenview 101
    (units[3], tenant2, owner1, -3, 11, 22000),   # Sneha — Sunrise A-1
    (units[5], tenant3, owner2, -2, 12, 55000),   # Vikram — Blue Lotus V-1
]

leases = []
for unit, tenant, owner, start_offset, duration, rent in lease_configs:
    start = first_of(start_offset)
    end   = start + relativedelta(months=duration)
    l, created = Lease.objects.get_or_create(
        unit=unit, tenant=tenant, status='active',
        defaults={
            'owner': owner,
            'start_date': start, 'end_date': end,
            'monthly_rent': rent,
            'security_deposit': unit.security_deposit,
            'terms': 'Standard residential lease agreement. Rent due on 1st of every month.',
        }
    )
    if created:
        unit.is_occupied = True
        unit.save()
    leases.append(l)

print(f"   ✅ {len(leases)} active leases created\n")

# ─── 5. RENT PAYMENTS ────────────────────────────────────
print("💰  Creating rent payment records...")

payment_count = 0

for lease in leases:
    # How many months since lease start?
    today = date.today()
    months_elapsed = (today.year - lease.start_date.year) * 12 + (today.month - lease.start_date.month)

    for i in range(months_elapsed + 2):  # past months + 2 future pending
        month_date = lease.start_date + relativedelta(months=i)
        month_year = month_date.strftime("%b %Y")
        due_date   = month_date.replace(day=1)

        if RentPayment.objects.filter(lease=lease, month_year=month_year).exists():
            continue

        is_future   = month_date > today.replace(day=1)
        is_current  = month_date.month == today.month and month_date.year == today.year
        is_past     = month_date < today.replace(day=1)

        # Determine status & paid info
        if is_future:
            status = 'pending'
            paid_date = None
            method = ''
            txn_id = ''
            late_fee = 0
        elif is_current:
            status = 'pending'
            paid_date = None
            method = ''
            txn_id = ''
            late_fee = 0
        else:
            # Past months: mix of paid / one overdue
            if i == months_elapsed - 1 and lease == leases[1]:
                # Sneha has one overdue
                status = 'overdue'
                paid_date = None
                method = ''
                txn_id = ''
                late_fee = 500
            else:
                status = 'paid'
                paid_date = due_date + timedelta(days=2)
                # Alternate payment methods
                methods = ['upi', 'bank_transfer', 'razorpay', 'upi', 'cash']
                method = methods[i % len(methods)]
                import random, string
                if method == 'razorpay':
                    txn_id = 'pay_' + ''.join(random.choices(string.ascii_letters + string.digits, k=14))
                elif method == 'upi':
                    txn_id = 'UPI' + ''.join(random.choices(string.digits, k=12))
                else:
                    txn_id = 'TXN' + ''.join(random.choices(string.digits, k=10))
                late_fee = 0

        RentPayment.objects.create(
            lease=lease,
            amount=lease.monthly_rent,
            due_date=due_date,
            paid_date=paid_date,
            status=status,
            payment_method=method,
            transaction_id=txn_id,
            month_year=month_year,
            late_fee=late_fee,
        )
        payment_count += 1

print(f"   ✅ {payment_count} rent payment records created\n")

# ─── 6. NOTIFICATIONS ────────────────────────────────────
print("🔔  Creating notifications...")

notif_data = [
    (tenant1, '✅ Welcome to TenantPro!', 'Your account is set up. Your lease starts ' + leases[0].start_date.strftime('%d %b %Y') + '.', 'success'),
    (tenant1, '📅 Rent Due Reminder', f'Your {make_month(0)} rent of ₹{leases[0].monthly_rent} is due on {first_of(0).strftime("%d %b %Y")}.', 'warning'),
    (tenant1, '✅ Rent Paid', f'Your {make_month(-1)} rent has been successfully received.', 'success'),
    (tenant2, '⚠ Rent Overdue', f'Your rent for last month is overdue. A late fee of ₹500 has been applied.', 'error'),
    (tenant2, '📅 Rent Due Reminder', f'Your {make_month(0)} rent of ₹{leases[1].monthly_rent} is due.', 'warning'),
    (tenant3, '✅ Welcome to TenantPro!', 'Your account is set up successfully.', 'success'),
    (tenant3, '📅 Rent Due Reminder', f'Your {make_month(0)} rent of ₹{leases[2].monthly_rent} is due.', 'warning'),
    (owner1, '💰 Rent Received', f'Arjun Verma paid ₹{leases[0].monthly_rent} for {make_month(-1)}.', 'success'),
    (owner1, '⚠ Overdue Alert', 'Sneha Patel has an overdue rent payment.', 'error'),
]

for user, title, msg, ntype in notif_data:
    Notification.objects.get_or_create(user=user, title=title, defaults={'message': msg, 'notif_type': ntype})

print(f"   ✅ {len(notif_data)} notifications created\n")

# ─── 7. ANNOUNCEMENTS ────────────────────────────────────
print("📢  Creating announcements...")

ann_data = [
    ('🔧 Water Supply Maintenance', 'Water supply will be interrupted on Sunday 10 AM–2 PM for maintenance work.', 'all', True),
    ('🎉 Society Diwali Celebration', 'Join us for a Diwali celebration in the common area on 31st Oct at 7 PM.', 'tenants', False),
    ('💡 Electricity Bill Reminder', 'Please ensure electricity bills are cleared before the 15th of every month.', 'all', False),
    ('🚗 New Parking Policy', 'Visitor parking is now allowed only in designated slots B1–B10.', 'all', True),
]

for title, msg, audience, pinned in ann_data:
    Announcement.objects.get_or_create(title=title, defaults={
        'message': msg, 'audience': audience, 'is_pinned': pinned, 'created_by': admin,
    })

print(f"   ✅ {len(ann_data)} announcements created\n")

# ─── Summary ─────────────────────────────────────────────
print("=" * 52)
print("🎉  Demo data seeded successfully!")
print("=" * 52)
print()
print("  LOGIN CREDENTIALS (password: demo1234)")
print("  ─────────────────────────────────────")
print("  👤 Admin      : Raja / 1234")
print("  🏘 Owner 1    : rahul_owner / demo1234")
print("  🏘 Owner 2    : priya_owner / demo1234")
print("  🏡 Tenant 1   : arjun_tenant / demo1234  ← has pending rent")
print("  🏡 Tenant 2   : sneha_tenant / demo1234  ← has overdue rent")
print("  🏡 Tenant 3   : vikram_tenant / demo1234 ← has pending rent")
print()
print("  Go to /tenant/rent/ as any tenant to pay via Razorpay!")
print("=" * 52)
print()
