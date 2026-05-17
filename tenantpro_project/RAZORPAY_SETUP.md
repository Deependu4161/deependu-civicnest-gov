# Razorpay Integration Setup Guide

## 1. Install the Razorpay Python SDK
```bash
pip install razorpay
```

## 2. Get Your Razorpay API Keys
- Sign up / Log in at https://dashboard.razorpay.com
- Go to Settings → API Keys
- Generate a **Test Key** (Key ID + Key Secret)
- For production, activate your account and use **Live Keys**

## 3. Update settings.py
Replace the placeholder values in `tenantpro/settings.py`:
```python
RAZORPAY_KEY_ID     = 'rzp_test_YOUR_KEY_ID'     # Your actual Key ID
RAZORPAY_KEY_SECRET = 'YOUR_KEY_SECRET'           # Your actual Key Secret
```

## 4. Run Migrations
```bash
python manage.py migrate
```

## 5. Test the Payment Flow
- Log in as a tenant
- Go to `/tenant/rent/`
- Click **Pay via Razorpay** on any pending payment
- Use test card: `4111 1111 1111 1111`, CVV: any 3 digits, Expiry: any future date

## New URLs Added
| URL | Purpose |
|-----|---------|
| `/razorpay/create-order/` | Creates Razorpay order (POST, AJAX) |
| `/razorpay/verify/` | Verifies payment signature (POST, AJAX) |

## Payment Flow
1. Tenant clicks **Pay via Razorpay**
2. A confirm modal shows payment details
3. Clicking **Proceed** calls `/razorpay/create-order/` → creates order in Razorpay
4. Razorpay Checkout popup opens (UPI / Card / NetBanking / Wallet)
5. On success, `/razorpay/verify/` validates the signature
6. `RentPayment` record is marked **Paid** with transaction ID saved
7. Notifications sent to both tenant and owner
