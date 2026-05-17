# 🏠 TenantPro — Smart Tenant Management System
Full-stack Django app with 4 user zones, deep plum dark theme.

## Quick Start
```bash
pip install django pillow
python manage.py runserver
```
Open: http://127.0.0.1:8000

## Demo Credentials

| Role | Username | Password | Portal |
|------|----------|----------|--------|
| 🔧 Admin | `Raja` | `1234` | `/admin-zone/` |
| 🏘️ Owner 1 | `vijay_mehta` | `owner123` | `/owner/` |
| 🏘️ Owner 2 | `priya_patel` | `owner123` | `/owner/` |
| 🏡 Tenant 1 | `rahul_kumar` | `tenant123` | `/tenant/` |
| 🏡 Tenant 2 | `anita_singh` | `tenant123` | `/tenant/` |
| 🏡 Tenant 3 | `dev_joshi` | `tenant123` | `/tenant/` |
| 🏢 Society | `society_admin1` | `sa123` | `/society-admin/` |

Django Admin: `/django-admin/` (admin / admin123)

## Zones & Features

### 🔧 Admin Zone
- Platform dashboard (users, revenue, properties, maintenance stats)
- Properties & user management
- Rent overview (paid / pending / overdue)
- Maintenance tracking & status updates
- Announcements broadcaster
- Verification queue
- Reports & analytics

### 🏘️ Owner Zone
- Dashboard with revenue, tenant, property stats
- Property portfolio management
- Tenant list with lease details
- Rent collection & confirmation
- Maintenance request management
- Lease creation & tracking
- Tenant messaging (chat)

### 🏡 Tenant Zone
- Dashboard with rent due alert, residence card
- Pay rent online (UPI / bank / cash)
- Raise & track maintenance requests
- File complaints
- View lease details
- Full payment history
- Notifications center
- Direct messaging with owner
- Profile management

### 🏢 Society Admin Zone
- Community overview dashboard
- Maintenance tracking across properties
- Announcements for specific properties
- Resident directory
- Verification queue
- Reports

## Project Structure
```
tenantpro/
├── accounts/      # Custom User model (admin/owner/tenant/society_admin)
├── core/          # All business models + views
├── templates/
│   ├── base.html              # Global navbar + topbar
│   ├── landing.html           # Dark hero landing page
│   ├── accounts/              # Login, register
│   ├── partials/              # Sidebar components (per zone)
│   ├── admin_zone/            # 8 admin pages
│   ├── owner/                 # 7 owner pages
│   ├── tenant/                # 9 tenant pages
│   └── society_admin/         # 7 society admin pages
├── static/css/
│   └── tenantpro.css          # Full design system (deep plum theme)
└── db.sqlite3                 # Pre-seeded database
```
