import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from django.contrib.auth import get_user_model


User = get_user_model()


username = os.environ.get("ADMIN_USERNAME")
email = os.environ.get("ADMIN_EMAIL")
password = os.environ.get("ADMIN_PASSWORD")


if not username or not password:
    print("ADMIN_USERNAME and ADMIN_PASSWORD are required.")
    raise SystemExit(1)


user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email or "",
        "is_staff": True,
        "is_superuser": True,
    },
)


if created:
    user.set_password(password)
    user.save()

    print(f"Admin user '{username}' created successfully.")

else:
    changed = False

    if email and user.email != email:
        user.email = email
        changed = True

    if not user.is_staff:
        user.is_staff = True
        changed = True

    if not user.is_superuser:
        user.is_superuser = True
        changed = True

    if changed:
        user.save()

    print(f"Admin user '{username}' already exists.")


print("Admin setup completed.")