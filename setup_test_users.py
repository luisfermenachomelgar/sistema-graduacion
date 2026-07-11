#!/usr/bin/env python
"""
Create test users for development
Usage: python manage.py shell < setup_test_users.py
Or: python setup_test_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import CustomUser
from django.contrib.auth.hashers import make_password

def create_test_users():
    """Create test users with different roles"""
    
    test_users = [
        {
            'username': 'admin',
            'password': 'password',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'estudiante',
            'password': 'password',
            'email': 'estudiante@example.com',
            'first_name': 'Estudiante',
            'last_name': 'User',
            'role': 'estudiante',
            'is_staff': False,
            'is_superuser': False,
        },
    ]
    
    print('🔧 Creando usuarios de prueba...\n')
    
    for user_data in test_users:
        username = user_data['username']
        
        # Check if user exists
        if CustomUser.objects.filter(username=username).exists():
            print(f'⏭️  Usuario "{username}" ya existe, omitiendo...')
            continue
        
        # Create user
        try:
            user = CustomUser.objects.create_user(**user_data)
            print(f'✅ Usuario "{username}" creado exitosamente')
            print(f'   Email: {user.email}')
            print(f'   Role: {user.get_role_display()}')
            print(f'   Admin: {user.is_superuser}\n')
        except Exception as e:
            print(f'❌ Error al crear usuario "{username}": {str(e)}\n')
    
    # List all users
    print('\n📋 Usuarios actuales:')
    print('-' * 60)
    all_users = CustomUser.objects.all()
    if all_users.exists():
        for user in all_users:
            admin_badge = '👑' if user.is_superuser else '👤'
            print(f'{admin_badge} {user.username:15} | {user.email:25} | Role: {user.get_role_display()}')
    else:
        print('No hay usuarios registrados')
    
    print(f'\nTotal: {all_users.count()} usuarios')

if __name__ == '__main__':
    create_test_users()
