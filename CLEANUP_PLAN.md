# TopKit Codebase Cleanup Plan

## 🧹 Conservative Cleanup Strategy

### **Phase 1: Obviously Obsolete Files** ✅ SAFE TO REMOVE

#### Backup Files (Replace with git history)
- `/app/backend/collaborative_models_backup.py`
- `/app/backend/collaborative_models_old.py` 
- `/app/backend/server_backup.py`
- `/app/backend/server_old_complex.py`

#### Orphaned Package Files
- `/app/backend/=6.10.0`
- `/app/backend/=7.4.0`
- `/app/backend/=2.8.0`
- `/app/backend/=10.0.0`
- `/app/=7.4.0`
- `/app/=2.8.0`
- `/app/=10.0.0`

#### Old Test Files (100+ files - keep only recent/relevant ones)
- Most files ending in `*_backend_test.py`
- Most files ending in `*_test.py`
- **KEEP ONLY:**
  - `test_result.md` (current testing protocol)
  - Recent deployment/validation tests
  - Current pydantic validation test

### **Phase 2: Code Cleanup**

#### Backend Cleanup
- Remove unused imports in `server.py`
- Remove commented/dead code sections
- Clean up unused API endpoints
- Remove obsolete environment variables

#### Frontend Cleanup  
- Remove unused imports in components
- Clean up commented code
- Remove unused utility functions
- Clean up obsolete state management

#### Database/Models Cleanup
- Remove unused Pydantic model fields
- Clean up obsolete enum values
- Remove unused validation functions

### **Phase 3: Structure Optimization**

#### File Organization
- Consolidate similar utility scripts
- Remove duplicate functionality
- Clean up uploads directory structure

## 🎯 **Conservative Approach Rules:**
1. Only remove files that are clearly obsolete/backup
2. Keep any file that might be referenced
3. Test after each phase
4. Document all removals

## 📊 **Estimated Impact:**
- **Files to remove:** ~150+ obsolete test files
- **Code lines to clean:** ~500-1000 lines
- **Disk space saved:** ~50MB+
- **Maintenance complexity:** Significantly reduced

Would you like me to proceed with Phase 1 (obvious file cleanup) first?