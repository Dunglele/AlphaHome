import os

def main():
    path = 'requirements.txt'
    if os.path.exists(path):
        # Try reading with utf-16le
        try:
            with open(path, 'r', encoding='utf-16le') as f:
                content = f.read()
        except Exception:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Add gunicorn if not exists
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        has_gunicorn = any('gunicorn' in line.lower() for line in lines)
        if not has_gunicorn:
            lines.append('gunicorn')
            
        # Write back as UTF-8 (best for Railway/Git)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print("Successfully updated requirements.txt and converted to UTF-8!")
    else:
        print("requirements.txt not found!")

if __name__ == "__main__":
    main()
