# Database Change Policy

## 🚫 Direct Database Changes Prohibited

**Developers must NOT make direct changes to the database outside of Alembic migrations.**

### ✅ Correct Process:
1. Make changes to SQLAlchemy models in code
2. Run `alembic revision --autogenerate -m "description"`
3. Review and edit the generated migration if needed
4. Run `alembic upgrade head` to apply changes

### ❌ What NOT to do:
- Creating/deleting tables directly in database
- Modifying columns directly in database
- Using database GUI tools for schema changes
- Running raw SQL DDL statements outside migrations

### 🔧 If you find direct changes:
1. **Stop immediately** - don't apply the messy migration
2. **Use `alembic stamp head`** to sync migration state
3. **Create clean migrations** for any needed changes
4. **Document the incident** and discuss with team

### 📋 Migration Review Checklist:
- [ ] Migration only contains intended changes
- [ ] No unnecessary table drops
- [ ] Downgrade function is meaningful
- [ ] Migration tested on staging environment
- [ ] Team review completed

**Violation of this policy may result in database inconsistencies and deployment issues.**
