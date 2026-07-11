#!/usr/bin/env python
"""Quick user creation script"""

import os
import sys

# Add Django to path
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    import django
    django.setup()
    
    from usuarios.models import CustomUser
    
    # Try to create admin user
    try:
        if not CustomUser.objects.filter(username='admin').exists():
            user = CustomUser.objects.create_user(
                username='admin',
                password='password',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_staff=True,
                is_superuser=True,
            )
            print(f'✅ User admin created: {user.email}')
        else:
            print('⏭️  User admin already exists')
            
        # Try to create other users
        users = [
            {
                'username': 'estudiante',
                'password': 'password',
                'email': 'estudiante@example.com',
                'first_name': 'Estudiante',
                'last_name': 'User',
                'role': 'estudiante',
                'is_staff': False,
                'is_superuser': False,
            }
        ]
        
        for user_data in users:
            if not CustomUser.objects.filter(username=user_data['username']).exists():
                CustomUser.objects.create_user(**user_data)
                print(f"✅ User {user_data['username']} created")
            else:
                print(f"⏭️  User {user_data['username']} already exists")
                
    except Exception as e:
        print(f'❌ Error: {e}')
        sys.exit(1)
