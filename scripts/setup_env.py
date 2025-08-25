#!/usr/bin/env python3
"""
Environment setup script for EIA Storage Accrual Engine
Helps users configure their environment safely without exposing API keys
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and is properly configured"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    # Read .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Check for API key
    if 'EIA_API_KEY=' in content:
        lines = content.split('\n')
        for line in lines:
            if line.startswith('EIA_API_KEY='):
                key_value = line.split('=', 1)[1].strip()
                if key_value and key_value != 'your_eia_api_key_here':
                    print("✅ EIA_API_KEY is configured")
                    return True
                else:
                    print("⚠️  EIA_API_KEY is set to placeholder value")
                    return False
    
    print("❌ EIA_API_KEY not found in .env file")
    return False

def create_env_file():
    """Create .env file from template"""
    env_example = Path('env.example')
    env_file = Path('.env')
    
    if not env_example.exists():
        print("❌ env.example not found")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        return False
    
    # Copy env.example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env and add your EIA API key")
    return True

def check_git_ignore():
    """Check if .env is properly ignored by git"""
    gitignore_path = Path('.gitignore')
    
    if not gitignore_path.exists():
        print("❌ .gitignore file not found")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    if '.env' in content:
        print("✅ .env is in .gitignore")
        return True
    else:
        print("❌ .env is not in .gitignore")
        return False

def check_for_hardcoded_keys():
    """Check for hardcoded API keys in Python files"""
    print("\n🔍 Scanning for hardcoded API keys...")
    
    python_files = list(Path('.').rglob('*.py'))
    found_keys = []
    
    for file_path in python_files:
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for potential API keys (high entropy strings)
            import re
            # Pattern for potential API keys (alphanumeric, 20+ chars)
            pattern = r'["\']([a-zA-Z0-9]{20,})["\']'
            matches = re.findall(pattern, content)
            
            for match in matches:
                # Skip common false positives
                if match in ['your_eia_api_key_here', 'placeholder', 'example']:
                    continue
                found_keys.append((file_path, match))
                
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
    
    if found_keys:
        print("🚨 FOUND HARDCODED API KEYS:")
        for file_path, key in found_keys:
            print(f"   {file_path}: {key[:10]}...")
        return False
    else:
        print("✅ No hardcoded API keys found")
        return True

def main():
    """Main setup function"""
    print("🔧 EIA Storage Accrual Engine - Environment Setup")
    print("=" * 50)
    
    # Check current directory
    if not Path('env.example').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check .gitignore
    gitignore_ok = check_git_ignore()
    
    # Check/create .env file
    env_ok = check_env_file()
    if not env_ok:
        print("\n📝 Creating .env file...")
        create_env_file()
        env_ok = check_env_file()
    
    # Check for hardcoded keys
    keys_ok = check_for_hardcoded_keys()
    
    # Summary
    print("\n📊 Setup Summary:")
    print(f"   .gitignore configured: {'✅' if gitignore_ok else '❌'}")
    print(f"   .env file configured: {'✅' if env_ok else '❌'}")
    print(f"   No hardcoded keys: {'✅' if keys_ok else '❌'}")
    
    if not env_ok:
        print("\n🔧 Next Steps:")
        print("   For Local Development:")
        print("   1. Edit .env file and add your EIA API key")
        print("   2. Get your API key from: https://www.eia.gov/opendata/")
        print("   3. Run this script again to verify setup")
        print("\n   For CI/CD (GitHub Actions):")
        print("   1. Go to Repository Settings → Secrets and variables → Actions")
        print("   2. Add Repository Secret: EIA_API_KEY")
        print("   3. GitHub Actions will automatically use the secret")
    
    if not keys_ok:
        print("\n🚨 SECURITY ISSUE:")
        print("   Hardcoded API keys found. Please remove them immediately.")
        print("   See SECURITY.md for guidance.")
    
    if gitignore_ok and env_ok and keys_ok:
        print("\n🎉 Environment setup complete!")
        print("   You can now run the application safely.")

if __name__ == "__main__":
    main()
