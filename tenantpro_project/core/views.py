from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
import random, string, functools, json, hmac, hashlib

from .models import (Property, Unit, Lease, RentPayment, MaintenanceRequest,
                     Complaint, Announcement, Notification, Message)
from accounts.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

PREDEFINED_QA = [
    (["hi","hello","hey","namaste"], "👋 Hello! Welcome to CivicNest! Ask me about rent, maintenance, complaints, lease, or payments!"),
    (["pay rent","how to pay","rent payment","make payment"], "💳 To pay rent:\n1. Go to My Rent in the sidebar\n2. See your pending amount\n3. Click 'Pay via Razorpay' for secure payment\n4. Choose UPI / Card / NetBanking / Wallet"),
    (["razorpay","online payment","upi","gpay","phonepe","paytm"], "🔵 CivicNest supports Razorpay! Click 'Pay via Razorpay' on the Rent page. Use UPI, Cards, NetBanking or Wallets. 100% secure with 256-bit SSL."),
    (["late fee","overdue","penalty","missed"], "⚠️ Overdue payments attract a late fee shown on your Rent page. Pay as soon as possible to avoid extra charges."),
    (["receipt","proof","download"], "🧾 Click the receipt icon (🧾) in Payment History after paying. You can download/print it."),
    (["payment history","past payments","paid rent"], "📋 Go to Payment History in the sidebar to see all paid records with transaction IDs."),
    (["payment due","due date","when to pay","reminder"], "📅 Your due date is on the dashboard and Rent page. Your owner sends a Due Alert notification when rent is due — check your notifications!"),
    (["maintenance","repair","fix","broken","plumbing","electrical"], "🔧 Raise a request:\n1. Go to Maintenance\n2. Click New Request\n3. Choose category & priority\n4. Submit — owner is notified immediately!"),
    (["complaint","file complaint","raise complaint","issue"], "📝 File a complaint:\n1. Go to Complaints\n2. Click New Complaint\n3. Describe the issue\n4. Submit — owner & society admin are both notified!"),
    (["complaint status","complaint update"], "Check the Complaints page for status: Open → Under Review → Resolved → Closed."),
    (["lease","agreement","contract","tenancy"], "📄 Your lease details are in 'My Lease' — start/end dates, rent amount, and property info."),
    (["security deposit","deposit"], "Your security deposit is held by the owner, refundable at lease end. Amount shown on My Lease page."),
    (["society","society admin","community"], "🏢 Your Society Admin manages common area maintenance, announcements, and community matters."),
    (["announcement","notice","news"], "📢 Check Announcements/Notifications for society news, maintenance schedules, and important notices."),
    (["profile","update profile","change name"], "👤 Update profile in the sidebar → Profile. Change name, phone, and email."),
    (["logout","sign out"], "Click your avatar/name in the top-right to find the Logout option."),
    (["pg","hostel","paying guest","room"], "🏠 For PG/Hostel units, your room details are in My Lease. Raise maintenance for room issues."),
    (["owner","landlord","contact owner"], "💬 Use the Messages section to chat directly with your property owner!"),
    (["message","chat"], "💬 Go to Messages in the sidebar to chat with your owner. Replies appear in real time."),
    (["notification","alert","bell"], "🔔 Click the bell icon in the navbar for latest notifications. Click 'Mark all read' to clear."),
    (["help","what can you do","options","guide"], "🤖 I can help with:\n• 💳 Rent & Razorpay\n• 🔧 Maintenance\n• 📝 Complaints\n• 📄 Lease info\n• 📢 Announcements\n• 💬 Owner messaging\n• 🔔 Notifications\n\nType your question!"),
    (["support","contact support","email"], "📧 Email support@civicnest.in or message your owner/society admin via the platform."),
    (["civicnest","about","what is"], "🏡 CivicNest connects tenants, property owners & society admins. Manage rent, maintenance, complaints, and community all in one place!"),
    (["thank","thanks","awesome","great"], "😊 You're welcome! Happy to help anytime."),
    (["bye","goodbye","see you"], "👋 Goodbye! Have a great day!"),
]

def chatbot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            msg = data.get("message", "").strip().lower()
            if not msg:
                return JsonResponse({"reply": "Please type something."})
            for keywords, answer in PREDEFINED_QA:
                if any(kw in msg for kw in keywords):
                    return JsonResponse({"reply": answer})
            return JsonResponse({"reply": "🤔 I'm not sure about that. Try asking about:\n• rent payment / razorpay\n• maintenance request\n• filing a complaint\n• lease details\n• society admin\n\nOr type 'help' to see all options."})
        except Exception as e:
            return JsonResponse({"reply": f"Error: {str(e)}"})
    return JsonResponse({"reply": "Invalid request"})

def notify(user, title, msg, ntype="info"):
    Notification.objects.create(user=user, title=title, message=msg, notif_type=ntype)

def role_required(*roles):
    def decorator(view):
        @functools.wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("/accounts/login/")
            # Fix 3: staff/superuser bypass + proper role check
            if request.user.is_staff or request.user.is_superuser:
                return view(request, *args, **kwargs)
            if request.user.role not in roles:
                messages.error(request, "Access denied.")
                return redirect("/")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
def notif_count(request):
    c = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"count": c})

@login_required
def notif_dropdown(request):
    ns = Notification.objects.filter(user=request.user).order_by("-created_at")[:8]
    data = [{"id": n.id, "title": n.title, "message": n.message, "type": n.notif_type,
             "is_read": n.is_read, "time": n.created_at.strftime("%d %b, %I:%M %p")} for n in ns]
    return JsonResponse({"notifications": data})

@login_required
def notif_mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"error": "POST required"}, status=400)

@login_required
def notif_mark_one(request, notif_id):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, id=notif_id).update(is_read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"error": "POST required"}, status=400)

@login_required
def payment_receipt(request, pay_id):
    payment = get_object_or_404(RentPayment, id=pay_id, lease__tenant=request.user, status="paid")
    return render(request, "tenant/receipt.html", {"payment": payment})

def landing(request):
    if request.user.is_authenticated:
        from accounts.views import _redirect_role
        return _redirect_role(request.user)
    stats = {"properties": Property.objects.count(), "tenants": User.objects.filter(role="tenant").count(), "owners": User.objects.filter(role="owner").count()}
    return render(request, "landing.html", {"stats": stats})

@role_required("admin")
def admin_dash(request):
    props = Property.objects.all(); users = User.objects.all()
    leases = Lease.objects.filter(status="active"); payments = RentPayment.objects.all()
    maint = MaintenanceRequest.objects.all()
    revenue = payments.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0
    pending_rent = payments.filter(status="pending").aggregate(t=Sum("amount"))["t"] or 0
    open_maint = maint.filter(status__in=["open", "assigned", "in_progress"])
    recent_complaints = Complaint.objects.filter(status__in=["open", "under_review"]).order_by("-created_at")[:5]
    return render(request, "admin_zone/dashboard.html", {
        "total_properties": props.count(), "total_tenants": users.filter(role="tenant").count(),
        "total_owners": users.filter(role="owner").count(), "active_leases": leases.count(),
        "revenue": revenue, "pending_rent": pending_rent, "open_maint": open_maint.count(),
        "recent_payments": payments.order_by("-created_at")[:8], "recent_complaints": recent_complaints,
        "props": props[:6],
    })

@role_required("admin")
def admin_properties(request):
    props = Property.objects.all().select_related("owner").order_by("-created_at")
    if request.method == "POST":
        owner_id = request.POST.get("owner_id")
        owner = get_object_or_404(User, id=owner_id, role="owner") if owner_id else None
        Property.objects.create(name=request.POST.get("name","").strip(), address=request.POST.get("address","").strip(),
            city=request.POST.get("city","").strip(), state=request.POST.get("state","").strip(),
            pincode=request.POST.get("pincode","").strip(), property_type=request.POST.get("property_type","apartment"),
            total_units=int(request.POST.get("total_units",1)), owner=owner or request.user)
        messages.success(request, "Property created."); return redirect("admin_properties")
    return render(request, "admin_zone/properties.html", {"props": props, "owners": User.objects.filter(role="owner")})

@role_required("admin")
def admin_users(request):
    return render(request, "admin_zone/users.html", {"users": User.objects.all().order_by("-date_joined")})

@role_required("admin")
def admin_rent(request):
    payments = RentPayment.objects.select_related("lease__tenant", "lease__unit").order_by("-due_date")
    return render(request, "admin_zone/rent.html", {
        "payments": payments[:30],
        "paid": payments.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0,
        "pending": payments.filter(status="pending").aggregate(t=Sum("amount"))["t"] or 0,
        "overdue": payments.filter(status="overdue").aggregate(t=Sum("amount"))["t"] or 0,
    })

@role_required("admin")
def admin_maintenance(request):
    reqs = MaintenanceRequest.objects.select_related("unit__property", "tenant").order_by("-created_at")
    if request.method == "POST":
        req = get_object_or_404(MaintenanceRequest, id=request.POST.get("req_id"))
        req.status = request.POST.get("status"); req.owner_notes = request.POST.get("notes","")
        if req.status == "resolved": req.resolved_date = timezone.now()
        req.save()
        notify(req.tenant, "Maintenance Update", f"Request #{req.id} status: {req.status}", "info")
        messages.success(request, "Updated."); return redirect("admin_maintenance")
    return render(request, "admin_zone/maintenance.html", {"reqs": reqs})

@role_required("admin")
def admin_verify(request):
    return render(request, "admin_zone/verify.html", {
        "pending_owners": User.objects.filter(role="owner", is_active=True),
        "pending_leases": Lease.objects.filter(status="pending"),
    })

@role_required("admin")
def admin_announcements(request):
    anns = Announcement.objects.order_by("-created_at")
    if request.method == "POST":
        title = request.POST.get("title","").strip(); msg = request.POST.get("message","").strip()
        audience = request.POST.get("audience","all"); pinned = request.POST.get("is_pinned") == "on"
        Announcement.objects.create(title=title, message=msg, audience=audience, is_pinned=pinned, created_by=request.user)
        if audience == "tenants": targets = User.objects.filter(role="tenant")
        elif audience == "owners": targets = User.objects.filter(role="owner")
        else: targets = User.objects.exclude(id=request.user.id)
        for u in targets[:100]: notify(u, f"Announcement: {title}", msg[:200], "info")
        messages.success(request, "Published!"); return redirect("admin_announcements")
    return render(request, "admin_zone/announcements.html", {"announcements": anns})

@role_required("admin")
def admin_reports(request):
    payments = RentPayment.objects.all()
    return render(request, "admin_zone/reports.html", {
        "revenue_total": payments.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0,
        "maint_stats": MaintenanceRequest.objects.values("status").annotate(c=Count("id")),
        "top_props": Property.objects.annotate(unit_count=Count("units")).order_by("-unit_count")[:5],
        "total_payments": payments.count(), "paid_count": payments.filter(status="paid").count(),
        "overdue_count": payments.filter(status="overdue").count(),
    })

@role_required("owner")
def owner_dash(request):
    props = Property.objects.filter(owner=request.user)
    units = Unit.objects.filter(property__owner=request.user)
    payments = RentPayment.objects.filter(lease__owner=request.user)
    maint_open = MaintenanceRequest.objects.filter(unit__property__owner=request.user, status__in=["open","assigned","in_progress"])
    recent_complaints = Complaint.objects.filter(unit__property__owner=request.user).order_by("-created_at")[:5]
    open_complaints = Complaint.objects.filter(unit__property__owner=request.user, status__in=["open","under_review"]).count()
    return render(request, "owner/dashboard.html", {
        "props": props, "total_properties": props.count(), "occupied": units.filter(is_occupied=True).count(),
        "total_units": units.count(), "active_tenants": Lease.objects.filter(owner=request.user, status="active").count(),
        "revenue": payments.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0,
        "open_maint": maint_open.count(), "recent_payments": payments.order_by("-created_at")[:6],
        "recent_maint": maint_open.order_by("-created_at")[:5],
        "recent_complaints": recent_complaints, "open_complaints": open_complaints,
    })

@role_required("owner")
def owner_properties(request):
    props = Property.objects.filter(owner=request.user).prefetch_related("units")
    if request.method == "POST":
        action = request.POST.get("action", "add_property")
        if action == "add_unit":
            prop = get_object_or_404(Property, id=request.POST.get("property_id"), owner=request.user)
            unit_number = request.POST.get("unit_number","").strip()
            if not unit_number:
                messages.error(request, "Unit number is required."); return redirect("owner_properties")
            if Unit.objects.filter(property=prop, unit_number=unit_number).exists():
                messages.error(request, f"Unit {unit_number} already exists."); return redirect("owner_properties")
            Unit.objects.create(property=prop, unit_number=unit_number, floor=request.POST.get("floor","").strip(),
                bedrooms=int(request.POST.get("bedrooms",1)), area_sqft=int(request.POST.get("area_sqft",0)),
                monthly_rent=request.POST.get("monthly_rent",0), security_deposit=request.POST.get("security_deposit",0), is_occupied=False)
            prop.total_units = prop.units.count(); prop.save(update_fields=["total_units"])
            messages.success(request, f"Unit {unit_number} added!"); return redirect("owner_properties")
        total_units = int(request.POST.get("total_units",1))
        prop = Property.objects.create(owner=request.user, name=request.POST.get("name","").strip(),
            address=request.POST.get("address","").strip(), city=request.POST.get("city","").strip(),
            state=request.POST.get("state","").strip(), pincode=request.POST.get("pincode","").strip(),
            property_type=request.POST.get("property_type","apartment"), total_units=total_units)
        for i in range(1, total_units+1):
            Unit.objects.create(property=prop, unit_number=str(i), floor=str((i-1)//4+1),
                bedrooms=int(request.POST.get("bedrooms",1)), monthly_rent=request.POST.get("monthly_rent",0),
                security_deposit=request.POST.get("security_deposit",0), is_occupied=False)
        messages.success(request, f'Property "{prop.name}" added with {total_units} unit(s)!'); return redirect("owner_properties")
    return render(request, "owner/properties.html", {"props": props})

@role_required("owner")
def owner_tenants(request):
    return render(request, "owner/tenants.html", {"leases": Lease.objects.filter(owner=request.user, status="active").select_related("tenant","unit")})

@role_required("owner")
def owner_rent(request):
    payments = RentPayment.objects.filter(lease__owner=request.user).select_related("lease__tenant","lease__unit__property").order_by("-due_date")
    active_leases = Lease.objects.filter(owner=request.user, status="active").select_related("tenant","unit__property")
    if request.method == "POST":
        action = request.POST.get("action","mark_paid")
        # Fix 1i: Send payment due alert to tenant
        if action == "send_due_alert":
            lease = get_object_or_404(Lease, id=request.POST.get("lease_id"), owner=request.user, status="active")
            today = date.today()
            month_year = today.strftime("%B %Y")
            existing = RentPayment.objects.filter(lease=lease, month_year=month_year).first()
            if not existing:
                RentPayment.objects.create(
                    lease=lease, amount=lease.monthly_rent,
                    due_date=today.replace(day=10) if today.day < 10 else today + timedelta(days=5),
                    status="pending", month_year=month_year,
                )
            notify(lease.tenant,
                f"🔔 Rent Due Alert — {month_year}",
                f"Your owner has sent a payment reminder. Rent of ₹{lease.monthly_rent} for {month_year} is due. Please pay via the Rent section.",
                "warning")
            messages.success(request, f"Payment due alert sent to {lease.tenant.get_full_name() or lease.tenant.username}!")
            return redirect("owner_rent")
        payment = get_object_or_404(RentPayment, id=request.POST.get("pay_id"), lease__owner=request.user)
        payment.status="paid"; payment.paid_date=date.today()
        payment.payment_method=request.POST.get("method","cash"); payment.transaction_id=request.POST.get("txn_id","")
        payment.save()
        notify(payment.lease.tenant, "Rent Confirmed", f"{payment.month_year} rent confirmed by owner.", "success")
        messages.success(request, "Marked paid."); return redirect("owner_rent")
    return render(request, "owner/rent.html", {
        "payments": payments[:30],
        "paid": payments.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0,
        "pending": payments.filter(status="pending").aggregate(t=Sum("amount"))["t"] or 0,
        "active_leases": active_leases,
    })

@role_required("owner")
def owner_maintenance(request):
    reqs = MaintenanceRequest.objects.filter(unit__property__owner=request.user).select_related("unit","tenant").order_by("-created_at")
    if request.method == "POST":
        req = get_object_or_404(MaintenanceRequest, id=request.POST.get("req_id"), unit__property__owner=request.user)
        req.status=request.POST.get("status",req.status); req.owner_notes=request.POST.get("notes","")
        req.assigned_to=request.POST.get("assigned_to","")
        if req.status=="resolved": req.resolved_date=timezone.now()
        req.save()
        notify(req.tenant, "Maintenance Update", f"Request #{req.id} is now {req.status}.", "info")
        messages.success(request, "Updated."); return redirect("owner_maintenance")
    return render(request, "owner/maintenance.html", {"reqs": reqs})

@role_required("owner")
def owner_complaints(request):
    complaints = Complaint.objects.filter(unit__property__owner=request.user).select_related("tenant","unit__property").order_by("-created_at")
    if request.method == "POST":
        complaint = get_object_or_404(Complaint, id=request.POST.get("complaint_id"), unit__property__owner=request.user)
        complaint.status = request.POST.get("status", complaint.status)
        complaint.response = request.POST.get("response","").strip()
        complaint.save()
        notify(complaint.tenant, "Complaint Update", f"Your complaint '{complaint.title}' is now {complaint.get_status_display()}.", "info")
        messages.success(request, "Complaint updated."); return redirect("owner_complaints")
    stats = {
        "total": complaints.count(), "open": complaints.filter(status="open").count(),
        "under_review": complaints.filter(status="under_review").count(), "resolved": complaints.filter(status="resolved").count(),
    }
    return render(request, "owner/complaints.html", {"complaints": complaints, "stats": stats})

@role_required("owner")
def owner_leases(request):
    leases = Lease.objects.filter(owner=request.user).select_related("tenant","unit__property").order_by("-start_date")
    all_units = Unit.objects.filter(property__owner=request.user).select_related("property")
    vacant_units = all_units.filter(is_occupied=False)
    tenants = User.objects.filter(role="tenant")
    props = Property.objects.filter(owner=request.user)
    if request.method == "POST":
        action = request.POST.get("action","create_lease")
        if action == "terminate_lease":
            lease = get_object_or_404(Lease, id=request.POST.get("lease_id"), owner=request.user)
            lease.status="terminated"; lease.save()
            lease.unit.is_occupied=False; lease.unit.save()
            notify(lease.tenant, "Lease Terminated", f"Your lease for {lease.unit} has been terminated.", "warning")
            messages.success(request, f"Lease terminated."); return redirect("owner_leases")
        unit = get_object_or_404(Unit, id=request.POST.get("unit_id"), property__owner=request.user)
        tenant = get_object_or_404(User, id=request.POST.get("tenant_id"), role="tenant")
        Lease.objects.create(unit=unit, tenant=tenant, owner=request.user,
            start_date=request.POST.get("start_date"), end_date=request.POST.get("end_date"),
            monthly_rent=request.POST.get("monthly_rent") or unit.monthly_rent,
            security_deposit=request.POST.get("security_deposit", unit.security_deposit))
        unit.is_occupied=True; unit.save()
        notify(tenant, "New Lease Created", f"Your lease for {unit} at {unit.property.name} has been created.", "success")
        messages.success(request, f"Lease created!"); return redirect("owner_leases")
    return render(request, "owner/leases.html", {
        "leases": leases, "units": vacant_units, "all_units": all_units,
        "tenants": tenants, "props": props,
        "vacant_count": vacant_units.count(), "total_units": all_units.count(),
    })

@role_required("owner")
def owner_messages(request):
    my_leases = Lease.objects.filter(owner=request.user, status="active").select_related("tenant")
    tenants = [l.tenant for l in my_leases]; selected_id = request.GET.get("with")
    selected_user = None; chat = []
    if selected_id:
        selected_user = get_object_or_404(User, id=selected_id)
        chat = Message.objects.filter(Q(sender=request.user, receiver=selected_user)|Q(sender=selected_user, receiver=request.user)).order_by("created_at")
    if request.method == "POST" and selected_id:
        content = request.POST.get("content","").strip()
        if content:
            Message.objects.create(sender=request.user, receiver=selected_user, content=content)
            notify(selected_user, "New Message", f"{request.user.get_full_name()}: {content[:100]}", "info")
            return redirect(f"/owner/messages/?with={selected_id}")
    return render(request, "owner/messages.html", {"tenants": tenants, "chat": chat, "selected_user": selected_user})

@role_required("tenant")
def tenant_dash(request):
    lease = Lease.objects.filter(tenant=request.user, status="active").select_related("unit__property","owner").first()
    payments = RentPayment.objects.filter(lease__tenant=request.user).order_by("-due_date")[:6] if lease else []
    next_due = RentPayment.objects.filter(lease__tenant=request.user, status__in=["pending","overdue"]).order_by("due_date").first()
    maint = MaintenanceRequest.objects.filter(tenant=request.user).order_by("-created_at")[:3]
    notifs = Notification.objects.filter(user=request.user, is_read=False)[:5]
    announcements = Announcement.objects.filter(Q(audience="all")|Q(audience="tenants")).order_by("-is_pinned","-created_at")[:3]
    due_alert = Notification.objects.filter(user=request.user, is_read=False, title__icontains="Rent Due Alert").first()
    return render(request, "tenant/dashboard.html", {
        "lease": lease, "payments": payments, "next_due": next_due, "maint": maint,
        "notifs": notifs, "announcements": announcements, "due_alert": due_alert,
        "razorpay_key": getattr(settings, "RAZORPAY_KEY_ID",""),
    })

@role_required("tenant")
def tenant_rent(request):
    lease = Lease.objects.filter(tenant=request.user, status="active").first()
    payments = RentPayment.objects.filter(lease__tenant=request.user).order_by("-due_date")
    total_paid = payments.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0
    pending_count = payments.filter(status__in=["pending","overdue"]).count()
    if request.method == "POST" and lease:
        payment = get_object_or_404(RentPayment, id=request.POST.get("pay_id"), lease__tenant=request.user)
        payment.status="paid"; payment.paid_date=date.today()
        payment.payment_method=request.POST.get("method","upi")
        payment.transaction_id="".join(random.choices(string.ascii_uppercase+string.digits,k=12))
        payment.save()
        notify(request.user, "Payment Successful", f"{payment.month_year} paid. TXN:{payment.transaction_id}", "success")
        messages.success(request, "Payment successful!"); return redirect("tenant_rent")
    return render(request, "tenant/rent.html", {
        "lease": lease, "payments": payments, "total_paid": total_paid, "pending_count": pending_count,
        "razorpay_key": getattr(settings, "RAZORPAY_KEY_ID",""),
    })

@role_required("tenant")
def tenant_maintenance(request):
    reqs = MaintenanceRequest.objects.filter(tenant=request.user).order_by("-created_at")
    if request.method == "POST":
        lease = Lease.objects.filter(tenant=request.user, status="active").first()
        if lease:
            req = MaintenanceRequest.objects.create(unit=lease.unit, tenant=request.user,
                title=request.POST.get("title","").strip(), description=request.POST.get("description","").strip(),
                category=request.POST.get("category","other"), priority=request.POST.get("priority","medium"))
            notify(lease.owner, "New Maintenance Request", f"{request.user.get_full_name()} raised: {req.title}", "warning")
            notify(request.user, "Request Submitted", f"Request #{req.id} submitted.", "info")
            messages.success(request, "Request submitted!")
        return redirect("tenant_maintenance")
    return render(request, "tenant/maintenance.html", {"reqs": reqs})

@role_required("tenant")
def tenant_complaints(request):
    complaints = Complaint.objects.filter(tenant=request.user).order_by("-created_at")
    if request.method == "POST":
        lease = Lease.objects.filter(tenant=request.user, status="active").first()
        if lease:
            complaint = Complaint.objects.create(tenant=request.user, unit=lease.unit,
                title=request.POST.get("title","").strip(), description=request.POST.get("description","").strip())
            # Fix 1 & 5: Notify BOTH owner AND society admin
            notify(lease.owner, "New Complaint Filed",
                   f"{request.user.get_full_name() or request.user.username} filed a complaint: '{complaint.title}'. Check Complaints section.",
                   "warning")
            if lease.unit.property.society_admin:
                notify(lease.unit.property.society_admin, "New Complaint Filed",
                       f"{request.user.get_full_name() or request.user.username} at {lease.unit.property.name}: '{complaint.title}'.",
                       "warning")
            messages.success(request, "Complaint filed. Owner has been notified.")
        else:
            messages.error(request, "No active lease found.")
        return redirect("tenant_complaints")
    return render(request, "tenant/complaints.html", {"complaints": complaints})

@role_required("tenant")
def tenant_lease(request):
    lease = Lease.objects.filter(tenant=request.user, status="active").select_related("unit__property","owner").first()
    return render(request, "tenant/lease.html", {"lease": lease})

@role_required("tenant")
def tenant_history(request):
    payments = RentPayment.objects.filter(lease__tenant=request.user, status="paid").order_by("-paid_date")
    return render(request, "tenant/history.html", {"payments": payments})

@role_required("tenant")
def tenant_notifications(request):
    notifs = Notification.objects.filter(user=request.user).order_by("-created_at")
    unread_count = notifs.filter(is_read=False).count()
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, "tenant/notifications.html", {"notifs": notifs, "unread_count": unread_count})

@role_required("tenant")
def tenant_messages(request):
    lease = Lease.objects.filter(tenant=request.user, status="active").select_related("owner").first()
    chat = []
    if lease:
        chat = Message.objects.filter(Q(sender=request.user,receiver=lease.owner)|Q(sender=lease.owner,receiver=request.user)).order_by("created_at")
        if request.method == "POST":
            content = request.POST.get("content","").strip()
            if content:
                Message.objects.create(sender=request.user, receiver=lease.owner, content=content)
                notify(lease.owner, "Message from Tenant", f"{request.user.get_full_name()}: {content[:100]}", "info")
                return redirect("tenant_messages")
    return render(request, "tenant/messages.html", {"lease": lease, "chat": chat})

@role_required("tenant")
def tenant_profile(request):
    if request.method == "POST":
        u=request.user; u.first_name=request.POST.get("first_name",u.first_name)
        u.last_name=request.POST.get("last_name",u.last_name); u.phone=request.POST.get("phone",u.phone)
        u.email=request.POST.get("email",u.email); u.avatar_initials=""; u.save()
        messages.success(request, "Profile updated!"); return redirect("tenant_profile")
    return render(request, "tenant/profile.html")

@role_required("society_admin")
def sa_dash(request):
    props = Property.objects.filter(society_admin=request.user)
    units = Unit.objects.filter(property__in=props)
    leases = Lease.objects.filter(unit__property__in=props, status="active")
    maint = MaintenanceRequest.objects.filter(unit__property__in=props)
    open_maint = maint.filter(status__in=["open","assigned","in_progress"])
    announcements = Announcement.objects.filter(Q(audience="all")|Q(property__in=props)).order_by("-created_at")[:5]
    recent_complaints = Complaint.objects.filter(unit__property__in=props).order_by("-created_at")[:5]
    open_complaints = Complaint.objects.filter(unit__property__in=props, status__in=["open","under_review"]).count()
    return render(request, "society_admin/dashboard.html", {
        "props": props, "total_units": units.count(), "occupied": units.filter(is_occupied=True).count(),
        "active_tenants": leases.count(), "open_maint": open_maint.count(),
        "announcements": announcements, "open_maint_list": open_maint[:5],
        "recent_complaints": recent_complaints, "open_complaints": open_complaints,
    })

@role_required("society_admin")
def sa_maintenance(request):
    props = Property.objects.filter(society_admin=request.user)
    reqs = MaintenanceRequest.objects.filter(unit__property__in=props).select_related("unit","tenant").order_by("-created_at")
    return render(request, "society_admin/maintenance.html", {"reqs": reqs})

@role_required("society_admin")
def sa_announcements(request):
    props = Property.objects.filter(society_admin=request.user)
    announcements = Announcement.objects.filter(Q(audience="all")|Q(property__in=props)).order_by("-created_at")
    if request.method == "POST":
        prop_id = request.POST.get("property"); prop = props.filter(id=prop_id).first() if prop_id else None
        Announcement.objects.create(title=request.POST.get("title","").strip(), message=request.POST.get("message","").strip(),
            audience=request.POST.get("audience","all"), property=prop,
            is_pinned=request.POST.get("is_pinned")=="on", created_by=request.user)
        messages.success(request, "Published!"); return redirect("sa_announcements")
    return render(request, "society_admin/announcements.html", {"announcements": announcements, "props": props})

@role_required("society_admin")
def sa_community(request):
    props = Property.objects.filter(society_admin=request.user)
    leases = Lease.objects.filter(unit__property__in=props, status="active").select_related("tenant","unit")
    return render(request, "society_admin/community.html", {"leases": leases, "props": props})

@role_required("society_admin")
def sa_complaints(request):
    props = Property.objects.filter(society_admin=request.user)
    complaints = Complaint.objects.filter(unit__property__in=props).select_related("tenant","unit__property").order_by("-created_at")
    if request.method == "POST":
        complaint = get_object_or_404(Complaint, id=request.POST.get("complaint_id"), unit__property__in=props)
        complaint.status = request.POST.get("status", complaint.status)
        complaint.response = request.POST.get("response","").strip()
        complaint.save()
        notify(complaint.tenant, "Complaint Update",
               f"Your complaint '{complaint.title}' is now {complaint.get_status_display()}.", "info")
        messages.success(request, "Complaint updated."); return redirect("sa_complaints")
    stats = {
        "total": complaints.count(), "open": complaints.filter(status="open").count(),
        "under_review": complaints.filter(status="under_review").count(), "resolved": complaints.filter(status="resolved").count(),
    }
    return render(request, "society_admin/complaints.html", {"complaints": complaints, "stats": stats, "props": props})

@role_required("society_admin")
def sa_reports(request):
    props = Property.objects.filter(society_admin=request.user)
    units = Unit.objects.filter(property__in=props)
    maint = MaintenanceRequest.objects.filter(unit__property__in=props)
    return render(request, "society_admin/reports.html", {
        "props": props, "units": units, "open_maint": maint.filter(status="open").count(),
        "resolved_maint": maint.filter(status="resolved").count(),
        "occupied": units.filter(is_occupied=True).count(), "vacant": units.filter(is_occupied=False).count(),
    })

@role_required("society_admin")
def sa_users(request):
    props = Property.objects.filter(society_admin=request.user)
    leases = Lease.objects.filter(unit__property__in=props, status="active").select_related("tenant","unit")
    return render(request, "society_admin/users.html", {"leases": leases})

@role_required("society_admin")
def sa_verify(request):
    props = Property.objects.filter(society_admin=request.user)
    pending_leases = Lease.objects.filter(unit__property__in=props, status="pending").select_related("tenant","unit")
    return render(request, "society_admin/verify.html", {"pending_leases": pending_leases})

@login_required
def simulate_pay(request):
    if request.method != "POST": return JsonResponse({"error": "Invalid"}, status=405)
    try:
        data = json.loads(request.body); pay_id = data.get("pay_id"); method = data.get("method","upi")
        payment = get_object_or_404(RentPayment, id=pay_id, lease__tenant=request.user, status__in=["pending","overdue"])
        pfx = {"upi":"UPI","card":"CARD","netbanking":"NB","wallet":"WLT"}.get(method,"TXN")
        txn_id = pfx+"".join(random.choices(string.ascii_uppercase+string.digits,k=12))
        payment.status="paid"; payment.paid_date=date.today()
        payment.payment_method=method if method in ["upi","bank_transfer","cash","cheque","razorpay"] else "upi"
        payment.transaction_id=txn_id; payment.save()
        notify(request.user,"Rent Paid",f"{payment.month_year} rent paid via {method.upper()}. TXN:{txn_id}","success")
        notify(payment.lease.owner,"Rent Received",f"{request.user.get_full_name()} paid {payment.month_year}.","success")
        total_paid = RentPayment.objects.filter(lease__tenant=request.user,status="paid").aggregate(t=Sum("amount"))["t"] or 0
        return JsonResponse({"success":True,"txn_id":txn_id,"month_year":payment.month_year,"amount":str(payment.amount),"total_paid":str(total_paid),"pay_id":payment.id})
    except Exception as e:
        return JsonResponse({"success":False,"error":str(e)},status=500)

@login_required
def razorpay_create_order(request):
    if request.method != "POST": return JsonResponse({"error":"Invalid"},status=405)
    try:
        import razorpay
    except ImportError:
        return JsonResponse({"error":"Install razorpay: pip install razorpay"},status=500)
    try:
        data = json.loads(request.body); pay_id = data.get("pay_id")
        payment = get_object_or_404(RentPayment, id=pay_id, lease__tenant=request.user, status__in=["pending","overdue"])
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_paise = int((payment.amount+payment.late_fee)*100)
        order = client.order.create(data={"amount":amount_paise,"currency":"INR",
            "receipt":f"rent_{payment.id}_{payment.month_year}",
            "notes":{"tenant":request.user.get_full_name(),"month":payment.month_year,"pay_id":str(payment.id)}})
        payment.razorpay_order_id=order["id"]; payment.save(update_fields=["razorpay_order_id"])
        return JsonResponse({"order_id":order["id"],"amount":amount_paise,"currency":"INR",
            "key":settings.RAZORPAY_KEY_ID,"tenant_name":request.user.get_full_name() or request.user.username,
            "tenant_email":request.user.email,"tenant_phone":getattr(request.user,"phone",""),
            "month_year":payment.month_year,"pay_id":payment.id,"description":f"Rent for {payment.month_year}"})
    except Exception as e:
        return JsonResponse({"error":str(e)},status=500)

@login_required
@csrf_exempt
def razorpay_verify_payment(request):
    if request.method != "POST": return JsonResponse({"error":"Invalid"},status=405)
    try:
        import razorpay
    except ImportError:
        return JsonResponse({"error":"Install razorpay"},status=500)
    try:
        data = json.loads(request.body)
        rzp_order=data.get("razorpay_order_id",""); rzp_pay=data.get("razorpay_payment_id","")
        rzp_sig=data.get("razorpay_signature",""); pay_id=data.get("pay_id")
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({"razorpay_order_id":rzp_order,"razorpay_payment_id":rzp_pay,"razorpay_signature":rzp_sig})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"success":False,"error":"Signature mismatch"},status=400)
        payment = get_object_or_404(RentPayment, id=pay_id, lease__tenant=request.user)
        payment.status="paid"; payment.paid_date=date.today(); payment.payment_method="razorpay"
        payment.transaction_id=rzp_pay; payment.razorpay_order_id=rzp_order
        payment.razorpay_payment_id=rzp_pay; payment.razorpay_signature=rzp_sig; payment.save()
        notify(request.user,"Rent Paid via Razorpay",f"{payment.month_year} paid. TXN:{rzp_pay}","success")
        notify(payment.lease.owner,"Razorpay Rent Received",f"{request.user.get_full_name()} paid {payment.month_year}.","success")
        total_paid = RentPayment.objects.filter(lease__tenant=request.user,status="paid").aggregate(t=Sum("amount"))["t"] or 0
        return JsonResponse({"success":True,"txn_id":rzp_pay,"month_year":payment.month_year,"amount":str(payment.amount),"total_paid":str(total_paid),"pay_id":payment.id})
    except Exception as e:
        return JsonResponse({"success":False,"error":str(e)},status=500)
