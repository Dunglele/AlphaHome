import os
import sys
import django
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alphahome.settings")
django.setup()

from django.core.management import call_command
from django.db import connections
from django.conf import settings

def main():
    print("=== START SQLITE TO POSTGRESQL DATA MIGRATION ===")
    
    # 1. Save current PostgreSQL config
    postgres_db = settings.DATABASES['default']
    
    # 2. Configure SQLite local connection
    print("[1/3] Connecting to local SQLite and dumping data...")
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(settings.BASE_DIR) / 'db.sqlite3',
    }
    connections['default'].close()
    
    dump_file = Path(settings.BASE_DIR) / 'datadump.json'
    
    with open(dump_file, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata', 
            indent=4, 
            stdout=f, 
            exclude=['contenttypes', 'auth.Permission']
        )
        
    print(f"-> Successfully dumped data to: {dump_file}")
    
    # 3. Restore PostgreSQL connection
    print("[2/3] Reconnecting to remote PostgreSQL on Railway...")
    settings.DATABASES['default'] = postgres_db
    connections['default'].close()
    
    # Load data to PostgreSQL
    print("[3/3] Loading data (loaddata) into PostgreSQL...")
    try:
        call_command('loaddata', str(dump_file))
        print("-> Successfully loaded data to PostgreSQL!")
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return
        
    # 4. Clean up temporary files
    if dump_file.exists():
        dump_file.unlink()
        print("-> Cleaned up temporary datadump.json.")
        
    print("=== DATA MIGRATION COMPLETED SUCCESSFULLY 100% ===")

if __name__ == "__main__":
    main()
