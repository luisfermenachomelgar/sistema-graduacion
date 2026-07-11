import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from usuarios.models import CustomUser

# Test si los usuarios existen, si no, crearlos
test_credentials = {
    "admin_test": ("test123", "admin"),
    "estudiante_test": ("test123", "estudiante"),
}

for username, (password, role) in test_credentials.items():
    # Usar get_or_create pero actualizar password SIEMPRE
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            "role": role,
            "is_staff": role == "admin",
            "is_active": True,
        }
    )
    # Siempre establecer la contraseña correctamente
    user.set_password(password)
    user.save()
    
    if created:
        print(f"✅ Created: {username:20} password={password:10} role={role}")
    else:
        print(f"✅ Updated: {username:20} password={password:10} role={user.role}")

print("\n📋 Current users:")
for u in CustomUser.objects.all():
    print(f"  {u.username:25} role={str(u.role):15} is_staff={u.is_staff} is_active={u.is_active}")
