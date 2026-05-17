from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_create_default_admin, sender=self)


def _create_default_admin(sender, **kwargs):
    """Auto-create the default admin user after migrations if none exists."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='Raja',
                email='admin@tenantpro.local',
                password='1234',
                first_name='Super',
                last_name='Admin',
                role='admin',
                phone='9000000001',
            )
            print("\n  ✅ Default admin created → username: Raja | password: 1234\n")
    except Exception:
        pass  # Table may not exist yet during initial migration
