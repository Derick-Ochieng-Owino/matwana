# test_settings_fix.py
import os
import sys
from pathlib import Path

# Add project to path
project_path = Path(__file__).resolve().parent
if str(project_path) not in sys.path:
    sys.path.append(str(project_path))

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("🔧 Testing Django Settings Fix")
print("=" * 50)

# Check environment variables
db_url = os.getenv('DATABASE_URL')
supabase_db_url = os.getenv('SUPABASE_DB_URL')

print(f"DATABASE_URL: {'✓' if db_url else '✗ Not found'}")
print(f"SUPABASE_DB_URL: {'✓' if supabase_db_url else '✗ Not found'}")

if db_url:
    print(f"   Using: {db_url.split('@')[1] if '@' in db_url else db_url}")
elif supabase_db_url:
    print(f"   Using: {supabase_db_url.split('@')[1] if '@' in supabase_db_url else supabase_db_url}")

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matwana.settings')

try:
    import django
    django.setup()
    
    print("\n✅ Django configured successfully")
    
    # Test database settings
    from django.conf import settings
    
    print("\n📋 Database Configuration:")
    db_settings = settings.DATABASES['default']
    
    # Mask password for security
    db_display = db_settings.copy()
    if 'PASSWORD' in db_display and db_display['PASSWORD']:
        db_display['PASSWORD'] = db_display['PASSWORD'][:3] + '***'
    
    for key, value in db_display.items():
        print(f"   {key}: {value}")
    
    # Test actual connection
    print("\n📊 Testing Database Connection...")
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to PostgreSQL!")
        print(f"   Version: {version}")
        
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"   Database: {db_info[0]}")
        print(f"   User: {db_info[1]}")
        
        print("\n🎉 All systems GO! Your Django is properly configured.")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    
    # More detailed error info
    import traceback
    print("\n🔍 Detailed traceback:")
    traceback.print_exc()