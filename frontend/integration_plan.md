# 🔄 Specialist Dashboard Integration & Testing Plan

## 📋 Overview
Step-by-step plan to integrate, test, and migrate to the new modular specialist dashboard.

---

## Phase 1: Pre-Integration Setup ✅

### Step 1.1: Verify File Structure
**Status:** ✅ Complete
- [x] All module files created
- [x] Hooks created
- [x] Shared components created
- [x] Layout components created
- [x] Routing updated

### Step 1.2: Check Dependencies
**Action:** Verify all imports are correct
```bash
# Check for any missing dependencies
npm install
# or
yarn install
```

**Files to verify:**
- [ ] `SpecialistDashboardContainer.jsx` - All module imports
- [ ] `AppointmentsModule.jsx` - All utility imports
- [ ] All hooks - API_URL imports
- [ ] Layout components - Icon imports

---

## Phase 2: Backend Endpoint Integration Testing 🧪

### Step 2.1: Test Overview Module
**Endpoint:** `GET /api/specialists/dashboard/stats`

**Test Actions:**
1. [ ] Login as approved specialist
2. [ ] Navigate to `/specialist-dashboard`
3. [ ] Verify Overview tab loads by default
4. [ ] Check if stats cards display:
   - [ ] Today's Appointments count
   - [ ] Active Patients count
   - [ ] Pending Reviews count
   - [ ] Forum Answers count
5. [ ] Verify Recent Activity section displays
6. [ ] Check dark mode toggle works
7. [ ] Wait 30 seconds, verify auto-refresh works

**Expected Response:**
```json
{
  "todays_appointments": 5,
  "active_patients": 20,
  "pending_reviews": 3,
  "forum_answers": 12,
  "recent_activities": [...]
}
```

**Error Handling:**
- [ ] If endpoint fails, shows error state with retry button
- [ ] If no data, shows appropriate message

---

### Step 2.2: Test Appointments Module
**Endpoints:**
- `GET /api/appointments/my-appointments`
- `POST /api/appointments/{id}/confirm-payment`
- `POST /api/appointments/{id}/reject-payment`
- `POST /api/appointments/{id}/complete`
- `PUT /api/appointments/{id}/cancel`

**Test Actions:**
1. [ ] Click "Appointments" tab in header
2. [ ] Verify appointments load and display
3. [ ] Test filters:
   - [ ] Click "All" - shows all appointments
   - [ ] Click "Pending" - shows only pending
   - [ ] Click "Scheduled" - shows only scheduled
   - [ ] Click "Completed" - shows only completed
   - [ ] Click "Cancelled" - shows only cancelled
4. [ ] Test search:
   - [ ] Search by patient name
   - [ ] Search by concern
   - [ ] Verify results filter correctly
5. [ ] Test sidebar filters:
   - [ ] Click each sidebar item (All, Pending, Scheduled, Completed, Cancelled)
   - [ ] Verify filter updates
6. [ ] Test appointment actions:
   - [ ] Find pending online appointment
   - [ ] Click "View Payment Details"
   - [ ] Verify payment modal opens
   - [ ] Test "Confirm Payment" button
   - [ ] Test "Reject Payment" button with reason
7. [ ] Test appointment completion:
   - [ ] Find scheduled appointment
   - [ ] Click "Mark as Completed"
   - [ ] Verify completion modal
   - [ ] Submit completion
8. [ ] Test refresh button
9. [ ] Verify real-time polling (wait 30s)

**Error Handling:**
- [ ] Network error shows error state
- [ ] Empty appointments shows empty state
- [ ] Payment confirmation errors handled

---

### Step 2.3: Test Patients Module
**Endpoint:** `POST /api/specialists/patients/filter`

**Test Actions:**
1. [ ] Click "Patients" tab in header
2. [ ] Verify patients list loads
3. [ ] Test sidebar filters:
   - [ ] Click "All Patients" - shows all
   - [ ] Click "New Patients" - shows status=new
   - [ ] Click "Active" - shows status=active
   - [ ] Click "Follow-up" - shows status=follow_up
   - [ ] Click "Discharged" - shows status=discharged
4. [ ] Test search:
   - [ ] Search by patient name
   - [ ] Search by email
   - [ ] Verify results update
5. [ ] Verify table displays:
   - [ ] Patient name and email
   - [ ] Status badge
   - [ ] Last session date
   - [ ] Total sessions count
6. [ ] Test pagination (if >20 patients):
   - [ ] Click "Next" button
   - [ ] Click "Previous" button
   - [ ] Verify page updates
7. [ ] Test refresh button
8. [ ] Verify auto-refresh (30s)

**Expected Request:**
```json
{
  "status": "active",
  "search_query": "",
  "page": 1,
  "size": 20
}
```

**Expected Response:**
```json
{
  "patients": [...],
  "page": 1,
  "total": 50
}
```

**Error Handling:**
- [ ] No patients shows empty state
- [ ] Network error shows error state with retry

---

### Step 2.4: Test Forum Module
**Endpoints:** (Placeholder - ready for integration)
- `GET /api/forum/questions`
- `POST /api/forum/questions/{id}/answers`
- `GET /api/forum/moderation/queue`
- `GET /api/forum/stats`

**Test Actions:**
1. [ ] Click "Forum" tab in header
2. [ ] Verify forum module loads
3. [ ] Check sidebar items:
   - [ ] Click "All Questions"
   - [ ] Click "My Answers"
   - [ ] Click "Moderation"
   - [ ] Click "Statistics"
4. [ ] Verify "Coming Soon" placeholder shows
5. [ ] Note: Full integration pending

**Status:** 🟡 Placeholder ready for future integration

---

### Step 2.5: Test Slots Module
**Endpoints:**
- `GET /api/specialists/slots`
- `GET /api/specialists/slots/availability-summary`
- `POST /api/specialists/slots/generate`
- `POST /api/specialists/slots/block`
- `POST /api/specialists/slots/unblock`

**Test Actions:**
1. [ ] Click "Availability" tab in header
2. [ ] Verify slots module loads
3. [ ] Check summary cards display:
   - [ ] Total Slots count
   - [ ] Available count
   - [ ] Booked count
   - [ ] Blocked count
4. [ ] Verify slots table loads:
   - [ ] Date & Time column
   - [ ] Duration column
   - [ ] Status badge
   - [ ] Actions column
5. [ ] Test sidebar navigation:
   - [ ] Click "Weekly Schedule"
   - [ ] Click "Generate Slots"
   - [ ] Click "Manage Slots"
   - [ ] Click "Summary"
6. [ ] Test "Generate Slots" button
7. [ ] Test refresh button
8. [ ] If no slots, verify empty state shows

**Expected Response (slots):**
```json
{
  "slots": [
    {
      "id": "uuid",
      "date": "2025-11-10",
      "start_time": "09:00",
      "duration_minutes": 30,
      "status": "available"
    }
  ]
}
```

**Expected Response (summary):**
```json
{
  "total_slots": 100,
  "available_slots": 60,
  "booked_slots": 35,
  "blocked_slots": 5
}
```

**Error Handling:**
- [ ] No slots shows empty state with "Generate Slots" button
- [ ] Network error shows error state

---

### Step 2.6: Test Profile Module
**Endpoints:**
- `GET /api/specialists/private/me`
- `GET /api/specialists/profile/completion-status`
- `PUT /api/specialists/profiles/{id}/interests`
- `PUT /api/specialists/profiles/{id}/professional-statement`
- `GET /api/specialists/document-status`
- `GET /api/specialists/{id}/reviews`

**Test Actions:**
1. [ ] Click "Profile" tab in header
2. [ ] Verify profile module loads
3. [ ] Check "View Profile" (default):
   - [ ] Profile avatar with initials
   - [ ] Name displays correctly
   - [ ] Email displays correctly
   - [ ] User type shows "Specialist"
   - [ ] Account status shows "Active"
4. [ ] Test sidebar navigation:
   - [ ] Click "View Profile"
   - [ ] Click "Edit Profile"
   - [ ] Click "Documents"
   - [ ] Click "Reviews"
5. [ ] Verify data from `specialistInfo` prop

**Status:** 🟡 Basic display ready, advanced features placeholder

---

## Phase 3: Cross-Module Testing 🔄

### Step 3.1: Navigation Testing
1. [ ] From Overview → Appointments
2. [ ] From Appointments → Patients
3. [ ] From Patients → Forum
4. [ ] From Forum → Slots
5. [ ] From Slots → Profile
6. [ ] From Profile → Overview
7. [ ] Verify sidebar resets on tab change
8. [ ] Verify data doesn't persist incorrectly
9. [ ] Check URL doesn't change (SPA behavior)

### Step 3.2: Dark Mode Testing
1. [ ] Toggle dark mode from any tab
2. [ ] Switch between all tabs
3. [ ] Verify dark mode persists
4. [ ] Check localStorage stores preference
5. [ ] Refresh page, verify dark mode persists
6. [ ] Test all modals in dark mode
7. [ ] Test all tables in dark mode

### Step 3.3: Responsive Testing
**Desktop (1920x1080):**
- [ ] All tabs render correctly
- [ ] Sidebar expands on hover
- [ ] Tables show all columns
- [ ] No horizontal scroll

**Tablet (768x1024):**
- [ ] Header tabs visible
- [ ] Sidebar functions
- [ ] Tables responsive
- [ ] Modals centered

**Mobile (375x667):**
- [ ] Header adapts
- [ ] Sidebar accessible
- [ ] Tables scroll horizontally
- [ ] Modals full-screen friendly

### Step 3.4: Authentication Testing
1. [ ] Test as unapproved specialist:
   - [ ] Should redirect to complete-profile
   - [ ] Should show error message
2. [ ] Test as pending approval:
   - [ ] Should redirect to pending-approval
3. [ ] Test as rejected:
   - [ ] Should redirect to application-rejected
4. [ ] Test with expired token:
   - [ ] Should redirect to login
5. [ ] Test as non-specialist user:
   - [ ] Should redirect to login or appropriate page

### Step 3.5: Real-time Polling Testing
1. [ ] Open Overview tab
2. [ ] Wait 30 seconds
3. [ ] Verify stats refresh (check network tab)
4. [ ] Switch to Appointments
5. [ ] Wait 30 seconds
6. [ ] Verify appointments refresh
7. [ ] Switch to Patients
8. [ ] Verify polling works
9. [ ] Close tab/window
10. [ ] Verify polling stops (no memory leaks)

---

## Phase 4: Performance Testing ⚡

### Step 4.1: Load Time Testing
- [ ] Measure initial dashboard load time
- [ ] Measure tab switch time
- [ ] Check for unnecessary re-renders
- [ ] Verify lazy loading (if implemented)
- [ ] Check bundle size impact

### Step 4.2: Network Testing
- [ ] Monitor API calls in Network tab
- [ ] Verify no duplicate requests
- [ ] Check request/response sizes
- [ ] Test with slow 3G network
- [ ] Test with offline mode

### Step 4.3: Memory Testing
- [ ] Open DevTools Performance tab
- [ ] Record while switching tabs
- [ ] Check for memory leaks
- [ ] Verify polling cleanup
- [ ] Test for 5-10 minutes continuous use

---

## Phase 5: Error Handling Testing 🚨

### Step 5.1: Network Errors
1. [ ] Disconnect internet
2. [ ] Try loading each module
3. [ ] Verify error states show
4. [ ] Reconnect internet
5. [ ] Click retry buttons
6. [ ] Verify data loads

### Step 5.2: API Errors
1. [ ] Test with 401 Unauthorized
   - [ ] Should redirect to login
2. [ ] Test with 403 Forbidden
   - [ ] Should show error message
3. [ ] Test with 404 Not Found
   - [ ] Should show appropriate error
4. [ ] Test with 500 Server Error
   - [ ] Should show error with retry
5. [ ] Test with timeout
   - [ ] Should show timeout error

### Step 5.3: Data Validation
1. [ ] Test with empty arrays
2. [ ] Test with null values
3. [ ] Test with malformed data
4. [ ] Test with very large datasets
5. [ ] Test with special characters

---

## Phase 6: User Acceptance Testing 👥

### Step 6.1: Specialist User Testing
**Scenario 1: Daily Workflow**
1. [ ] Login as specialist
2. [ ] Check today's appointments
3. [ ] Approve/reject pending appointments
4. [ ] View patient list
5. [ ] Check availability slots
6. [ ] Update profile

**Scenario 2: Appointment Management**
1. [ ] Confirm payment for online appointment
2. [ ] Mark appointment as completed
3. [ ] Cancel appointment
4. [ ] Search for specific appointment

**Scenario 3: Patient Management**
1. [ ] Filter patients by status
2. [ ] Search for specific patient
3. [ ] View patient details
4. [ ] Check session history

### Step 6.2: Compare with Old Dashboard
**Create comparison checklist:**
- [ ] All old features present in new dashboard
- [ ] All old data visible in new dashboard
- [ ] All old actions available in new dashboard
- [ ] New dashboard has better UX
- [ ] New dashboard is faster

---

## Phase 7: Migration Preparation 📦

### Step 7.1: Create Backup
```bash
# Backup old dashboard
cp mm/frontend/src/components/specialist/SpecialistDashboard.jsx mm/frontend/src/components/specialist/SpecialistDashboard.backup.jsx
cp mm/frontend/src/components/specialist/SpecialistDashboard.css mm/frontend/src/components/specialist/SpecialistDashboard.backup.css
```

### Step 7.2: Update Exports
**File:** `mm/frontend/src/components/specialist/index.js`

**Current:**
```javascript
export { default as SpecialistDashboard } from './SpecialistDashboard';
```

**Change to:**
```javascript
// Old dashboard (backup)
export { default as SpecialistDashboardOld } from './SpecialistDashboard';

// New modular dashboard
export { default as SpecialistDashboard } from './dashboard';
```

### Step 7.3: Add Feature Flag (Optional)
**If you want gradual rollout:**
```javascript
// In config
const USE_NEW_DASHBOARD = true; // or from env variable

// In routing
{USE_NEW_DASHBOARD ? (
  <SpecialistDashboardContainer />
) : (
  <SpecialistDashboardOld />
)}
```

---

## Phase 8: Final Migration 🚀

### Step 8.1: Remove Old Dashboard (After all tests pass)
```bash
# Remove old files
rm mm/frontend/src/components/specialist/SpecialistDashboard.jsx
rm mm/frontend/src/components/specialist/SpecialistDashboard.css
```

### Step 8.2: Clean Up Exports
**File:** `mm/frontend/src/components/specialist/index.js`
```javascript
// Remove old export
// Keep only new dashboard
export { default as SpecialistDashboard } from './dashboard';
```

### Step 8.3: Update Documentation
- [ ] Update README files
- [ ] Update API documentation
- [ ] Update user guides
- [ ] Update developer guides

### Step 8.4: Final Verification
- [ ] Test all routes still work
- [ ] Test all features still work
- [ ] No console errors
- [ ] No network errors
- [ ] Performance is good

---

## 📊 Testing Checklist Summary

| Module | Integration | Testing | Status |
|--------|-------------|---------|--------|
| Overview | ⬜ | ⬜ | Pending |
| Appointments | ⬜ | ⬜ | Pending |
| Patients | ⬜ | ⬜ | Pending |
| Forum | ⬜ | ⬜ | Pending |
| Slots | ⬜ | ⬜ | Pending |
| Profile | ⬜ | ⬜ | Pending |
| Navigation | ⬜ | ⬜ | Pending |
| Dark Mode | ⬜ | ⬜ | Pending |
| Responsive | ⬜ | ⬜ | Pending |
| Auth | ⬜ | ⬜ | Pending |
| Polling | ⬜ | ⬜ | Pending |
| Performance | ⬜ | ⬜ | Pending |
| Errors | ⬜ | ⬜ | Pending |

---

## 🐛 Bug Tracking Template

**Issue #:** [Number]
**Module:** [Overview/Appointments/Patients/etc.]
**Severity:** [Critical/High/Medium/Low]
**Description:** [What went wrong]
**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:** [What should happen]
**Actual Behavior:** [What actually happened]
**Screenshots:** [If applicable]
**Fix Status:** [To Do/In Progress/Fixed]

---

## 🎯 Success Criteria

✅ **Before Migration:**
- [ ] All 6 modules load without errors
- [ ] All backend endpoints respond correctly
- [ ] All user actions work as expected
- [ ] Dark mode works everywhere
- [ ] Responsive on all screen sizes
- [ ] Real-time polling works
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] Error handling works
- [ ] Old dashboard features replicated

✅ **After Migration:**
- [ ] No broken links or routes
- [ ] All features still functional
- [ ] No user complaints
- [ ] Performance improved or same
- [ ] Documentation updated

---

## 📞 Support Plan

**If issues found:**
1. Document in bug tracking template
2. Prioritize by severity
3. Fix critical bugs immediately
4. Test fix thoroughly
5. Deploy fix
6. Verify fix works

**Rollback Plan:**
If critical issues found and can't be fixed quickly:
1. Restore old dashboard from backup
2. Update routing to use old dashboard
3. Fix issues in new dashboard
4. Re-test completely
5. Try migration again

---

## ⏱️ Estimated Timeline

- **Phase 1:** 15 minutes (Setup verification)
- **Phase 2:** 2-3 hours (Endpoint testing)
- **Phase 3:** 1 hour (Cross-module testing)
- **Phase 4:** 30 minutes (Performance testing)
- **Phase 5:** 1 hour (Error handling)
- **Phase 6:** 1 hour (UAT)
- **Phase 7:** 30 minutes (Migration prep)
- **Phase 8:** 30 minutes (Final migration)

**Total:** ~7-8 hours of thorough testing

---

## 🚀 Ready to Start?

Begin with **Phase 1** and work through systematically. Check off items as you complete them.

Good luck! 🎉
