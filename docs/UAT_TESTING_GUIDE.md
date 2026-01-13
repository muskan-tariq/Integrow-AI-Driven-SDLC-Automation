# Integrow - User Acceptance Testing (UAT) Guide

## Overview

This guide provides comprehensive testing instructions for all Integrow features. Use this document to validate that the application meets user requirements and functions correctly in real-world scenarios.

---

## Pre-Requisites for Testing

Before starting UAT, ensure the following services are running:

- ✅ **Backend running**: `http://127.0.0.1:8000`
- ✅ **Frontend running**: `http://localhost:8888`
- ✅ **Redis running**: `docker ps --filter name=integrow-redis`
- ✅ **Database migrated**: Supabase tables created
- ✅ **Environment variables**: All `.env` files configured
- ✅ **GitHub OAuth**: App registered and credentials set
- ✅ **API Keys**: Groq API key valid

---

## 1. Authentication & User Management

### Feature 1.1: GitHub OAuth Login

**Test Steps**:
1. Launch the Integrow application
2. Click "Sign in with GitHub" button on login page
3. Authorize the application on GitHub
4. Return to application

**Expected Results**:
- ✅ Redirected to GitHub OAuth page
- ✅ After authorization, redirected back to application
- ✅ Automatically logged in to dashboard
- ✅ User profile displayed (GitHub username, avatar)
- ✅ JWT token stored securely in Electron auth store

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 1.2: Session Persistence

**Test Steps**:
1. Log in successfully
2. Close the Electron application completely
3. Reopen the application

**Expected Results**:
- ✅ User remains logged in
- ✅ No need to re-authenticate
- ✅ Dashboard loads immediately

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 1.3: Logout

**Test Steps**:
1. Click logout button in navigation
2. Verify logged out state
3. Try to access dashboard directly

**Expected Results**:
- ✅ Session cleared successfully
- ✅ Redirected to login page
- ✅ Cannot access protected routes without re-authentication

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 2. Project Management

### Feature 2.1: View Projects Dashboard

**Test Steps**:
1. Log in to application
2. View the dashboard page

**Expected Results**:
- ✅ All user projects displayed as cards
- ✅ Each project shows:
  - Project name
  - Description
  - GitHub repository info (if linked)
  - Creation date
  - Action buttons (Requirements Analyzer, Folder, GitHub link)
- ✅ "New Project" button visible

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 2.2: Create New Project

**Test Steps**:
1. Click "New Project" button
2. Fill in the form:
   - **Project Name**: "Test E-commerce App"
   - **Description**: "Online shopping platform for UAT testing"
   - **GitHub Repository** (optional): "username/repo-name"
3. Click "Create Project"

**Expected Results**:
- ✅ Project creation modal appears
- ✅ Form validation works (required fields)
- ✅ Project saved to database
- ✅ New project appears in dashboard
- ✅ Correct details displayed on project card

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 2.3: Link GitHub Repository

**Test Steps**:
1. Create a project with GitHub repository URL
2. Verify GitHub icon appears on project card
3. Click GitHub icon

**Expected Results**:
- ✅ GitHub icon visible on project card
- ✅ Clicking icon opens repository in browser
- ✅ Correct repository URL

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 3. Requirements Analyzer - Core Workflow

### Feature 3.1: Open Requirements Analyzer

**Test Steps**:
1. From dashboard, click "Requirements Analyzer" button (Sparkles ✨ icon) on any project card
2. Observe page transition

**Expected Results**:
- ✅ Navigate to Requirements Analyzer page
- ✅ Monaco Editor loads correctly
- ✅ Project name displayed in header
- ✅ Back arrow button visible (returns to dashboard)
- ✅ Analyze button visible
- ✅ Export button visible
- ✅ Chat sidebar visible on right

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 3.2: Write Requirements (Monaco Editor)

**Test Steps**:
1. In Monaco Editor, write a sample requirement:
```
The system should allow users to search for products.
Users can filter results by category and price range.
The search should be fast and return relevant results.
```
2. Test editor features:
   - Line numbers
   - Syntax highlighting
   - Copy/paste
   - Undo/redo

**Expected Results**:
- ✅ Editor responsive and smooth
- ✅ Text formatting works
- ✅ Line numbers visible
- ✅ Copy/paste functions correctly
- ✅ Undo/redo works

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 3.3: Auto-Save Requirements

**Test Steps**:
1. Type requirement in editor
2. Wait 2 seconds without typing
3. Check console for auto-save message
4. Refresh the page

**Expected Results**:
- ✅ "Auto-saving..." indicator appears after 2 seconds
- ✅ "Saved" confirmation message
- ✅ Console shows: `Auto-saving requirement: {text}`
- ✅ Requirement persists after page refresh
- ✅ No data loss

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 4. AI Analysis - Multi-Agent System

### Feature 4.1: Analyze Requirements

**Test Steps**:
1. Write a requirement in Monaco Editor
2. Click "Analyze" button
3. Wait for analysis to complete

**Expected Results**:
- ✅ Loading spinner appears
- ✅ "Analyze" button disabled during processing
- ✅ Analysis completes within 5-15 seconds
- ✅ Results display in "Analysis" tab
- ✅ No errors in console or UI

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 4.2: Parsed Entities

**Test Steps**:
1. After analysis completes, click "Parsed" tab
2. Review extracted entities

**Expected Results**:
- ✅ **Actors** correctly identified (e.g., "users", "system")
- ✅ **Actions** correctly identified (e.g., "search", "filter")
- ✅ **Objects** correctly identified (e.g., "products", "category", "price range")
- ✅ **Constraints** correctly identified (e.g., "fast", "relevant")
- ✅ Entities displayed in organized lists

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 4.3: Ambiguity Detection

**Test Steps**:
1. View "Ambiguity" section in Analysis panel
2. Review identified ambiguous terms

**Expected Results**:
- ✅ Vague terms flagged (e.g., "fast", "relevant")
- ✅ Specific suggestions provided:
  - "fast" → "< 2 seconds response time"
  - "relevant" → "ranked by keyword match score"
- ✅ Each issue has clear explanation
- ✅ Actionable recommendations provided

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 4.4: Completeness Check

**Test Steps**:
1. View "Completeness" section
2. Review missing requirements

**Expected Results**:
- ✅ Missing edge cases identified:
  - "What if no products match the search?"
  - "What if search query is empty?"
- ✅ Missing error handling identified:
  - "What if search service is down?"
- ✅ Missing constraints identified:
  - "Maximum results per page?"
  - "Pagination support?"
- ✅ Missing security considerations:
  - "Input validation for search query?"
  - "SQL injection prevention?"

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 4.5: Ethics Analysis

**Test Steps**:
1. View "Ethics" section
2. Review ethical concerns

**Expected Results**:
- ✅ Privacy issues flagged:
  - "Is user search history stored?"
  - "Is data encrypted?"
- ✅ Bias concerns identified:
  - "Search algorithm bias?"
  - "Filter fairness?"
- ✅ Accessibility considerations:
  - "Keyboard navigation support?"
  - "Screen reader compatibility?"
- ✅ Mitigation strategies suggested

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 4.6: Quality Score

**Test Steps**:
1. Check overall quality score in analysis panel
2. Note the score value and color

**Expected Results**:
- ✅ Score displayed (0-100)
- ✅ Color-coded:
  - Red: < 60 (Poor)
  - Yellow: 60-80 (Good)
  - Green: > 80 (Excellent)
- ✅ Score reflects analysis quality
- ✅ Score influences "Approve & Commit" button state

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 5. AI Chat Assistant (Real-time)

### Feature 5.1: WebSocket Connection

**Test Steps**:
1. Open Requirements Analyzer page
2. Check chat sidebar on right
3. Verify connection status

**Expected Results**:
- ✅ Chat sidebar visible
- ✅ "Connected" status with green pulsing dot
- ✅ WebSocket connected to backend
- ✅ Console shows: `Chat connected`
- ✅ Session ID displayed in console
- ✅ No WebSocket errors (ignore React Strict Mode warnings)

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 5.2: Send Chat Message

**Test Steps**:
1. Type in chat input box:
```
How can I make the search requirement more specific?
```
2. Press Enter or click Send button
3. Wait for AI response

**Expected Results**:
- ✅ User message appears immediately in chat
- ✅ Message displays with timestamp
- ✅ AI response streams in real-time (word by word)
- ✅ Response appears within 3-5 seconds
- ✅ Response formatted with markdown
- ✅ Response is relevant and helpful
- ✅ No errors displayed

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 5.3: Conversation Context

**Test Steps**:
1. Send first message: "What are the ambiguities in my requirement?"
2. Wait for response
3. Send follow-up: "What about performance requirements?"
4. Wait for response

**Expected Results**:
- ✅ AI remembers first question
- ✅ Second response references previous context
- ✅ Coherent multi-turn conversation
- ✅ Context maintained across messages

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 5.4: Chat Persistence

**Test Steps**:
1. Send several messages in chat
2. Refresh the browser page
3. Check if chat history is preserved

**Expected Results**:
- ✅ Chat messages remain visible after refresh
- ✅ Conversation history stored in Redis
- ✅ Can continue conversation where left off

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 5.5: New Chat

**Test Steps**:
1. Have an existing conversation
2. Click "New Chat" button (RefreshCw icon)
3. Confirm action

**Expected Results**:
- ✅ All previous messages cleared
- ✅ Chat input ready for new conversation
- ✅ Can start fresh conversation
- ✅ No errors

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 5.6: Chat Error Handling

**Test Steps**:
1. Stop Redis container: `docker stop integrow-redis`
2. Try to send a chat message
3. Observe error handling
4. Restart Redis: `docker start integrow-redis`
5. Try sending message again

**Expected Results**:
- ✅ Error message displayed when Redis is down
- ✅ User-friendly error (not technical jargon)
- ✅ Chat recovers after Redis restart
- ✅ Graceful degradation

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 6. Export Functionality

### Feature 6.1: Export as JSON

**Test Steps**:
1. Complete a requirement analysis
2. Click "Export" button
3. Select "JSON" format
4. Save the file
5. Open file in text editor

**Expected Results**:
- ✅ JSON file downloads successfully
- ✅ File contains:
  - `requirement_id`
  - `text` (original requirement)
  - `parsed` (entities)
  - `analysis` (ambiguity, completeness, ethics)
  - `quality_score`
- ✅ Valid JSON format (no syntax errors)

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 6.2: Export as YAML

**Test Steps**:
1. Click "Export" → Select "YAML"
2. Save and open file

**Expected Results**:
- ✅ YAML file downloads
- ✅ Human-readable format
- ✅ Contains all analysis data
- ✅ Valid YAML syntax

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 6.3: Export as Markdown

**Test Steps**:
1. Click "Export" → Select "Markdown"
2. Save and open file

**Expected Results**:
- ✅ Markdown file downloads
- ✅ Formatted with headers, lists, bold text
- ✅ Sections for:
  - Requirement text
  - Parsed entities
  - Ambiguity issues
  - Completeness gaps
  - Ethics concerns
- ✅ Readable in any text editor

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 6.4: Export as CSV

**Test Steps**:
1. Click "Export" → Select "CSV"
2. Save and open in Excel/Google Sheets

**Expected Results**:
- ✅ CSV file downloads
- ✅ Opens correctly in spreadsheet software
- ✅ Data organized in rows and columns
- ✅ Can be used for reporting/analysis

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 7. GitHub Integration - Approve & Commit

### Feature 7.1: Approve Requirement (Quality Check)

**Test Steps**:
1. Complete analysis with quality score < 60%
2. Try to click "Approve & Commit" button
3. Improve requirement and re-analyze
4. Get quality score > 60%
5. Click "Approve & Commit"

**Expected Results**:
- ✅ Button disabled when quality < 60%
- ✅ Tooltip explains why disabled
- ✅ Button enabled when quality ≥ 60%
- ✅ Modal opens with commit form

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 7.2: Commit to GitHub

**Test Steps**:
1. Ensure project has GitHub repository linked
2. Click "Approve & Commit" (with quality > 60%)
3. In modal:
   - Verify pre-filled commit message
   - Select branch (default: main)
   - Click "Commit" button
4. Wait for confirmation

**Expected Results**:
- ✅ Commit modal displays correctly
- ✅ Branch selection dropdown works
- ✅ Commit message editable
- ✅ "Committing..." loading state
- ✅ Success notification after commit
- ✅ File appears in GitHub repository
- ✅ Commit shows in GitHub history
- ✅ File format is YAML

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 7.3: GitHub Integration Error Handling

**Test Steps**:
1. Try to commit without GitHub repo linked
2. Try to commit with invalid credentials
3. Observe error messages

**Expected Results**:
- ✅ Clear error message if no repo linked
- ✅ Authentication errors handled gracefully
- ✅ User knows what went wrong
- ✅ Can retry after fixing issue

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 8. UI/UX Features

### Feature 8.1: Monaco Editor Annotations

**Test Steps**:
1. After analysis, check Monaco Editor
2. Look for visual indicators

**Expected Results**:
- ✅ Red squiggly lines under ambiguous terms
- ✅ Hover shows suggestion tooltip
- ✅ Visual feedback for issues
- ✅ Helps user identify problems

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 8.2: Responsive Design

**Test Steps**:
1. Resize application window
2. Test at different widths
3. Check layout adaptation

**Expected Results**:
- ✅ Layout adapts to window size
- ✅ No broken UI elements
- ✅ Content remains accessible
- ✅ Scrolling works correctly

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 8.3: Loading States

**Test Steps**:
1. Trigger analysis
2. Observe loading indicators
3. Send chat message
4. Observe streaming

**Expected Results**:
- ✅ Spinner visible during analysis
- ✅ Buttons disabled when processing
- ✅ Clear status indicators
- ✅ User knows system is working
- ✅ No ambiguity about state

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 8.4: Error Messages

**Test Steps**:
1. Trigger various errors:
   - Disconnect backend
   - Invalid input
   - Network failure
2. Read error messages

**Expected Results**:
- ✅ Clear, user-friendly error messages
- ✅ Not technical jargon
- ✅ Actionable guidance provided
- ✅ User understands what to do

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## 9. Performance & Reliability

### Feature 9.1: Analysis Speed

**Test Steps**:
1. Analyze short requirement (1-2 sentences)
2. Time the analysis
3. Analyze long requirement (5-10 sentences)
4. Time the analysis

**Expected Results**:
- ✅ Short requirement: < 10 seconds
- ✅ Long requirement: < 20 seconds
- ✅ Acceptable performance
- ✅ No timeouts

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 9.2: Chat Streaming Speed

**Test Steps**:
1. Send a chat message
2. Measure time to first response chunk
3. Measure time to complete response

**Expected Results**:
- ✅ First chunk within 1-2 seconds
- ✅ Complete response within 5 seconds
- ✅ Feels real-time
- ✅ Smooth streaming

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Feature 9.3: Auto-save Reliability

**Test Steps**:
1. Type requirement rapidly
2. Change tabs in browser
3. Return to Requirements page
4. Close and reopen app

**Expected Results**:
- ✅ No data loss during rapid typing
- ✅ Saves persist across tab changes
- ✅ Saves persist across app restarts
- ✅ Reliable auto-save

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## Complete UAT Scenarios

### Scenario 1: First-Time User Journey

**Steps**:
1. Launch application
2. Sign in with GitHub
3. Create first project: "Personal Blog"
4. Navigate to Requirements Analyzer
5. Write simple requirement:
```
Users should be able to create blog posts with title and content.
```
6. Click "Analyze"
7. Review analysis results
8. Ask chat: "What's missing from this requirement?"
9. Export as Markdown
10. Logout

**Expected Results**:
- ✅ Smooth onboarding experience
- ✅ Intuitive navigation
- ✅ All features work correctly
- ✅ User feels confident using the app

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Scenario 2: Complex Requirement Workflow

**Steps**:
1. Login to existing account
2. Open project "E-commerce Platform"
3. Write complex requirement:
```
The payment processing system must support multiple payment methods including credit cards, PayPal, and cryptocurrency. Transaction processing should complete within 3 seconds under normal load. The system must handle at least 1000 concurrent transactions. All payment data must be encrypted using AES-256. Failed transactions should be logged and retry attempted up to 3 times. Users should receive email confirmation of successful payments.
```
4. Analyze requirement
5. Review all analysis sections carefully
6. Use chat to discuss ambiguities:
   - "What is 'normal load'?"
   - "Should we specify which cryptocurrencies?"
7. Edit requirement based on chat suggestions
8. Re-analyze to verify improvements
9. Export as JSON for documentation
10. Approve and commit to GitHub

**Expected Results**:
- ✅ Handles complex requirements
- ✅ Identifies multiple issues
- ✅ Chat provides useful guidance
- ✅ Quality score improves after refinement
- ✅ Successful GitHub commit

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

### Scenario 3: Error Recovery & Edge Cases

**Steps**:
1. Start requirement analysis
2. Disconnect internet mid-analysis
3. Wait for error
4. Reconnect internet
5. Retry analysis
6. Stop Redis container
7. Try to send chat message
8. Observe error
9. Restart Redis
10. Verify chat works again
11. Try to approve requirement with quality < 60%
12. Verify button disabled

**Expected Results**:
- ✅ Network errors handled gracefully
- ✅ Can recover from failures
- ✅ Redis errors don't crash app
- ✅ Quality checks enforced
- ✅ User guidance provided for errors

**Pass/Fail**: ______

**Notes**: _______________________________________________

---

## Success Metrics

### Overall Application Quality

- [ ] **Feature Completeness**: 100% of features working
- [ ] **Bug Count**: < 5 critical bugs
- [ ] **User Satisfaction**: Intuitive and helpful
- [ ] **Performance**: Analysis < 15s, Chat < 3s
- [ ] **Reliability**: No crashes or data loss
- [ ] **Error Handling**: Graceful degradation
- [ ] **Documentation**: README sufficient for setup
- [ ] **Security**: OAuth and JWT working correctly

### Test Summary

| Category | Total Tests | Passed | Failed | Notes |
|----------|------------|--------|--------|-------|
| Authentication | 3 | | | |
| Project Management | 3 | | | |
| Requirements Analyzer | 3 | | | |
| AI Analysis | 6 | | | |
| Chat Assistant | 6 | | | |
| Export | 4 | | | |
| GitHub Integration | 3 | | | |
| UI/UX | 4 | | | |
| Performance | 3 | | | |
| **TOTAL** | **35** | | | |

---

## Issues Found During Testing

| # | Feature | Issue Description | Severity | Status |
|---|---------|------------------|----------|--------|
| 1 | | | High/Medium/Low | Open/Fixed |
| 2 | | | | |
| 3 | | | | |

---

## Tester Information

- **Tester Name**: ___________________________
- **Testing Date**: ___________________________
- **Application Version**: ___________________________
- **Environment**: Development / Staging / Production

---

## Sign-off

**Tester Signature**: ___________________________

**Date**: ___________________________

**UAT Status**: ☐ Passed  ☐ Passed with Minor Issues  ☐ Failed

**Recommendations**: _____________________________________________

_________________________________________________________________

_________________________________________________________________
