# 🧪 PR Testing Guide: Authentication Changes

## **Complete Testing Strategy Before Merge**

### **1. Pre-Merge Checklist**

**✅ Code Review**
- [ ] All files are present: `simple_auth.py`, `simple_users.sql`, `simple_credentials.txt`
- [ ] `Step8MCPClientPsxGPT.py` updated to import `simple_auth_callback`
- [ ] No complex authentication code left behind
- [ ] Basic passwords are simple (`pass1`, `pass2`, etc.)

**✅ File Validation**
- [ ] `simple_users.sql` has 10 INSERT statements
- [ ] `simple_credentials.txt` has all 10 user credentials
- [ ] No import errors when loading `simple_auth.py`

---

### **2. Local Testing Steps**

#### **Step A: Environment Check**
```bash
# 1. Verify environment variables
echo $DATABASE_URL
echo $ADMIN_USERNAME
echo $ADMIN_PASSWORD

# 2. Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"
```

#### **Step B: Database Setup**
```bash
# 1. Apply the SQL script
psql -d your_database -f simple_users.sql

# 2. Verify users were created
psql -d your_database -c "SELECT identifier, metadata->>'name' FROM \"User\";"
```

#### **Step C: Application Testing**
```bash
# 1. Start your Chainlit app
chainlit run Step8MCPClientPsxGPT.py

# 2. Test in browser:
# - Try logging in with user1/pass1
# - Try logging in with user5/pass5
# - Try logging in with your admin credentials
# - Try invalid credentials (should fail)
```

---

### **3. Specific Test Cases**

#### **🔐 Authentication Tests**

**Test 1: Database User Login**
- Username: `user1`
- Password: `pass1`
- Expected: ✅ Login successful

**Test 2: Different Database User**
- Username: `user10`
- Password: `pass10`
- Expected: ✅ Login successful

**Test 3: Admin Fallback**
- Username: Your `ADMIN_USERNAME`
- Password: Your `ADMIN_PASSWORD`
- Expected: ✅ Login successful

**Test 4: Invalid Credentials**
- Username: `user1`
- Password: `wrongpass`
- Expected: ❌ Login failed

**Test 5: Non-existent User**
- Username: `user99`
- Password: `pass99`
- Expected: ❌ Login failed

#### **🔧 Integration Tests**

**Test 6: Full Workflow**
1. Login with `user3/pass3`
2. Connect to MCP server
3. Ask a financial question
4. Verify response works normally
5. Expected: ✅ Everything works as before

---

### **4. Error Prevention Checklist**

#### **Common Merge Issues**

**❌ Import Errors**
- Check: `from simple_auth import simple_auth_callback` in main file
- Fix: Ensure `simple_auth.py` is in same directory

**❌ Database Connection Issues**
- Check: `DATABASE_URL` environment variable set
- Fix: Verify database is running and accessible

**❌ SQL Execution Errors**
- Check: User table exists in database
- Fix: Run `chainlit_schema_psx.sql` first if needed

**❌ Authentication Not Working**
- Check: `auth_callback = simple_auth_callback` in main file
- Fix: Ensure proper assignment

---

### **5. Production-Ready Testing**

#### **Staging Environment Test**
```bash
# 1. Deploy to staging environment
# 2. Run full test suite
# 3. Have team members test with their assigned credentials
# 4. Monitor logs for any errors
```

#### **Performance Testing**
- Test with multiple concurrent users
- Verify database connection pooling works
- Check response times are acceptable

---

### **6. Rollback Plan**

If something goes wrong after merge:

**Quick Rollback Steps:**
1. **Revert the main file:**
   ```python
   # In Step8MCPClientPsxGPT.py, replace:
   from simple_auth import simple_auth_callback
   auth_callback = simple_auth_callback
   
   # With original:
   ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
   ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
   
   @cl.password_auth_callback
   def auth_callback(username: str, password: str) -> Optional[cl.User]:
       if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
           return cl.User(identifier=username, metadata={"role": "admin"})
       return None
   ```

2. **Remove database users (if needed):**
   ```sql
   DELETE FROM "User" WHERE identifier LIKE 'user%';
   ```

---

### **7. Final Verification**

Before hitting "Merge":

**✅ Manual Testing Complete**
- [ ] All 10 users can login
- [ ] Admin fallback works
- [ ] Invalid logins are rejected
- [ ] Full application workflow works

**✅ Team Testing**
- [ ] At least 2 team members tested successfully
- [ ] No authentication errors in logs
- [ ] Performance is acceptable

**✅ Documentation**
- [ ] `SIMPLE_USERS_README.md` is accurate
- [ ] Team has access to `simple_credentials.txt`
- [ ] Rollback plan is documented

---

### **8. Post-Merge Monitoring**

After merge, monitor for:
- Authentication errors in logs
- Database connection issues
- User login failures
- Performance degradation

**Success Metrics:**
- 10 users can login successfully
- No authentication errors
- Application functions normally
- Team productivity improved

---

## **🚀 Quick Test Command**

```bash
# Run this complete test sequence:
echo "Testing authentication setup..."
psql -d your_database -f simple_users.sql
chainlit run Step8MCPClientPsxGPT.py &
sleep 5
echo "Visit http://localhost:8000 and test login with user1/pass1"
```

**If all tests pass → 🎉 Ready to merge!**
**If any tests fail → 🔧 Fix issues first**