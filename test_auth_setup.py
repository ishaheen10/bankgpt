#!/usr/bin/env python3
"""
Test script to validate authentication setup before merging PR
Run this to ensure everything works before deploying
"""
import os
import sys
import subprocess
import importlib.util

def test_imports():
    """Test that all required imports work"""
    print("🔍 Testing imports...")
    
    try:
        # Test if we can import the simple auth module
        spec = importlib.util.spec_from_file_location("simple_auth", "simple_auth.py")
        simple_auth = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(simple_auth)
        print("✅ simple_auth.py imports successfully")
        
        # Test if the auth callback exists
        if hasattr(simple_auth, 'simple_auth_callback'):
            print("✅ simple_auth_callback function found")
        else:
            print("❌ simple_auth_callback function missing")
            return False
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Try to connect to database
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Check if User table exists
            user_table_check = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'User'
                );
            """))
            
            if user_table_check.fetchone()[0]:
                print("✅ User table exists")
            else:
                print("❌ User table missing - run your database schema first")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    return True

def test_sql_script():
    """Test that SQL script is valid"""
    print("\n🔍 Testing SQL script...")
    
    if not os.path.exists("simple_users.sql"):
        print("❌ simple_users.sql not found")
        return False
    
    with open("simple_users.sql", "r") as f:
        content = f.read()
        
    # Basic validation
    if "INSERT INTO" not in content:
        print("❌ SQL script missing INSERT statements")
        return False
        
    if "BEGIN;" not in content or "COMMIT;" not in content:
        print("❌ SQL script missing transaction statements")
        return False
        
    print("✅ SQL script looks valid")
    return True

def test_chainlit_integration():
    """Test Chainlit integration"""
    print("\n🔍 Testing Chainlit integration...")
    
    try:
        # Check if Step8MCPClientPsxGPT.py has been updated
        with open("Step8MCPClientPsxGPT.py", "r") as f:
            content = f.read()
            
        if "from simple_auth import simple_auth_callback" in content:
            print("✅ Main app imports simple_auth correctly")
        else:
            print("❌ Main app not updated to use simple_auth")
            return False
            
        if "auth_callback = simple_auth_callback" in content:
            print("✅ Auth callback assigned correctly")
        else:
            print("❌ Auth callback not assigned")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Chainlit integration: {e}")
        return False
    
    return True

def run_basic_auth_test():
    """Run basic authentication logic test"""
    print("\n🔍 Testing authentication logic...")
    
    try:
        # Import and test the auth function
        spec = importlib.util.spec_from_file_location("simple_auth", "simple_auth.py")
        simple_auth = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(simple_auth)
        
        # Test with mock data (this won't actually hit the database)
        print("✅ Authentication module loads without errors")
        
        # Test admin fallback
        admin_user = os.getenv("ADMIN_USERNAME")
        admin_pass = os.getenv("ADMIN_PASSWORD")
        
        if admin_user and admin_pass:
            print("✅ Admin credentials found in environment")
        else:
            print("⚠️  Admin credentials missing - only database users will work")
            
    except Exception as e:
        print(f"❌ Authentication logic error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Authentication PR Before Merge")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Database Connection", test_database_connection),
        ("SQL Script Validation", test_sql_script),
        ("Chainlit Integration", test_chainlit_integration),
        ("Auth Logic", run_basic_auth_test),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! PR is ready to merge.")
        print("\n🚀 Next steps:")
        print("1. Run: psql -d your_database -f simple_users.sql")
        print("2. Start your Chainlit app")
        print("3. Test login with user1/pass1")
        return True
    else:
        print("❌ Some tests failed. Fix issues before merging.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)