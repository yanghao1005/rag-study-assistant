# Frontend Implementation Plan: SmartStudy AI (RAG Study Assistant)

## Project Overview
Next.js 16+ TypeScript frontend for a RAG-based learning platform. Focus on clean component architecture, reusable UI components via Shadcn/ui, and seamless integration with FastAPI backend.

**Tech Stack:**
- Next.js 16+ (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- Shadcn/ui components
- React Context API or Zustand (TBD)
- Fetch API for HTTP requests
- ESLint + Prettier for code quality

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Initialize Next.js Project Structure
```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home/dashboard
│   │   ├── (auth)/             # Auth routes (if needed)
│   │   ├── (main)/             # Protected routes
│   │   │   ├── subjects/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── create/
│   │   │   ├── documents/
│   │   │   ├── study/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   └── dashboard/
│   │   ├── api/                # API routes (if needed for middleware)
│   │   └── not-found.tsx       # 404 page
│   ├── components/
│   │   ├── ui/                 # Shadcn/ui components & custom UI
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── select.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── badge.tsx
│   │   │   └── ...
│   │   ├── common/             # Shared/layout components
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Breadcrumb.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── subjects/
│   │   │   ├── SubjectGrid.tsx
│   │   │   ├── SubjectCard.tsx
│   │   │   ├── SubjectModal.tsx
│   │   │   └── SubjectForm.tsx
│   │   ├── documents/
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentCard.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── SummaryEditor.tsx
│   │   │   ├── DocumentStatusBadge.tsx
│   │   │   ├── DocumentTabs.tsx (PDF vs Summary)
│   │   │   └── ChapterList.tsx
│   │   ├── study/
│   │   │   ├── ScopeSelector.tsx (Subject/Document/Chapter/Summary)
│   │   │   ├── Flashcard.tsx
│   │   │   ├── FlashcardCarousel.tsx
│   │   │   ├── QuizQuestion.tsx
│   │   │   ├── QuizInterface.tsx
│   │   │   ├── SourceCitation.tsx
│   │   │   └── ContentGenerator.tsx
│   │   └── shared/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ConfirmDialog.tsx
│   │       └── Toast.tsx
│   ├── lib/
│   │   ├── api/                # API client & utilities
│   │   │   ├── client.ts       # Fetch wrapper with auth
│   │   │   ├── endpoints.ts    # API endpoint constants
│   │   │   ├── hooks.ts        # Custom hooks (useSubjects, useDocuments, etc.)
│   │   │   └── types.ts        # API response/request types
│   │   ├── context/            # React Context setup
│   │   │   ├── SubjectContext.tsx
│   │   │   └── DocumentContext.tsx
│   │   ├── store/              # Zustand stores (if using Zustand)
│   │   │   ├── subjectStore.ts
│   │   │   └── documentStore.ts
│   │   ├── utils/
│   │   │   ├── cn.ts           # Tailwind class merge
│   │   │   ├── format.ts       # Date, file size formatting
│   │   │   ├── validation.ts   # Input validation helpers
│   │   │   └── constants.ts    # App constants
│   │   └── hooks/
│   │       ├── useAsync.ts
│   │       ├── useLocalStorage.ts
│   │       └── useDebounce.ts
│   ├── styles/
│   │   └── globals.css         # Tailwind + global styles
│   ├── types/
│   │   ├── api.ts              # API request/response types
│   │   ├── models.ts           # Domain models (Subject, Document, etc.)
│   │   └── index.ts            # Re-exports
│   └── env.ts                  # Environment variable validation
├── public/
│   ├── icons/
│   ├── logos/
│   └── images/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── postcss.config.ts
├── .env.local                  # Local development
├── .env.example                # Template for env vars
├── .eslintrc.json
├── .prettierrc
├── .gitignore
└── README.md
```

### 1.2 Dependencies to Install
```
Core:
- next@16.x
- react@19.x
- react-dom@19.x
- typescript

Styling & UI:
- tailwindcss
- postcss
- autoprefixer
- class-variance-authority
- clsx
- tailwind-merge
- @radix-ui/* (dependencies for shadcn/ui)

State Management (choose one):
- zustand (preferred for simplicity)
  OR
- Context API + useReducer (built-in)

Utilities:
- axios OR native fetch wrapper
- zod (for validation)
- date-fns (date formatting)

Development:
- @types/react
- @types/react-dom
- @types/node
- eslint
- eslint-config-next
- prettier
- typescript-eslint

Optional (Phase 5):
- @testing-library/react
- @testing-library/jest-dom
- vitest
- playwright
```

### 1.3 Configuration Files Setup
- **tsconfig.json:** Strict mode enabled, path aliases (@/*)
- **next.config.ts:** Image optimization, env handling, CORS setup
- **tailwind.config.ts:** Custom theme colors, spacing, extensions
- **postcss.config.ts:** TailwindCSS + Autoprefixer
- **.env.local template:**
  ```
  NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
  NEXT_PUBLIC_APP_NAME=SmartStudy AI
  ```
- **src/env.ts:** Validate environment variables at build time

### 1.4 ESLint & Prettier Setup
- Use Prettier for consistent formatting
- ESLint rules: Next.js recommended + strict TypeScript rules
- Pre-commit hooks (optional, Phase 5)

---

## Phase 2: Core Architecture & Utilities

### 2.1 API Client Setup (lib/api/client.ts)
```typescript
// Features:
- Fetch wrapper with TypeScript types
- Error handling (400, 401, 403, 500, etc.)
- Request/Response interceptors
- Timeout handling (30s default)
- Retry logic for transient failures
- Loading state management
```

**Key Functions:**
```typescript
apiFetch<T>(endpoint, options): Promise<T>
- Handles errors consistently
- Validates response structure
- Provides type safety

apiUploadFile(endpoint, file, onProgress): Promise<T>
- For PDF/document uploads
- Progress callback for UI feedback

apiFormData(endpoint, formData): Promise<T>
- For multipart form data
```

### 2.2 Types Definition (types/api.ts & types/models.ts)

**API Types (Request/Response):**
```typescript
// Subjects
CreateSubjectRequest = { name, description, color }
SubjectResponse = { id, name, description, color, document_count, created_at }

// Documents
UploadDocumentRequest = { file: File, subject_id, document_type: 'pdf' }
CreateSummaryRequest = { subject_id, title, content, chapter_id? }
DocumentResponse = { id, filename, subject_id, document_type, status, total_pages?, content_text?, created_at }

// Chapters
CreateChapterRequest = { name, start_page, end_page }
ChapterResponse = { id, document_id, name, start_page, end_page, order_index }

// Generation
GenerateFlashcardsRequest = { scope: 'subject'|'document'|'chapter'|'summary', scope_id, count, query? }
FlashcardResponse = { front, back, source: SourceInfo }
GenerateQuizRequest = { scope, scope_id, count, difficulty? }
QuizQuestionResponse = { question, options, correct_answer, explanation, source: SourceInfo }

// Source info (for citations)
SourceInfo = { document, document_type: 'pdf'|'summary', page?, chapter? }

// Error response
ErrorResponse = { error: string, message: string, details?: object }
```

**Domain Models (types/models.ts):**
```typescript
Subject = { id, name, description, color, documents: Document[], created_at }
Document = { id, subject_id, filename, document_type, status, chapters?, total_pages?, content_text? }
Chapter = { id, document_id, name, start_page, end_page }
Flashcard = { front, back, source }
QuizQuestion = { question, options, correct_answer, explanation, source }
```

### 2.3 Custom Hooks for API (lib/api/hooks.ts)

**Query Hooks (for fetching):**
```typescript
useSubjects() - Fetch all subjects
useSubjectById(id) - Fetch single subject with documents
useDocuments(filters) - Fetch documents (optionally filtered by subject_id, document_type)
useDocumentStatus(id) - Poll document processing status
useChapters(documentId) - Fetch chapters for a document
```

**Mutation Hooks (for creating/updating):**
```typescript
useCreateSubject() - Create new subject
useUpdateSubject(id) - Update subject
useDeleteSubject(id) - Delete subject (with confirmation)

useUploadDocument(subjectId) - Upload PDF file (with progress)
useCreateSummary(subjectId) - Create text summary
useDeleteDocument(id) - Delete document

useGenerateFlashcards(scope, scopeId) - Generate flashcards (with loading state)
useGenerateQuiz(scope, scopeId) - Generate quiz questions

useCreateChapter(documentId) - Add chapter
useUpdateChapter(id) - Update chapter
useDeleteChapter(id) - Delete chapter
```

**State Management Hook:**
```typescript
useAsync<T>(asyncFn, dependencies) - Reusable async logic
- Handles loading, error, data states
- Automatic cleanup
```

### 2.4 State Management (Context or Zustand)

**Option A: React Context (simpler)**
```typescript
SubjectContext - Global subject list & selected subject
DocumentContext - Global document list & filters
NotificationContext - Toast notifications
LoadingContext - Global loading indicators
```

**Option B: Zustand (recommended)**
```typescript
useSubjectStore() - Subjects list, selected subject, CRUD operations
useDocumentStore() - Documents, filters, CRUD operations
useNotificationStore() - Toast management
useStudyStore() - Current study session (scope, generated content)
```

### 2.5 Utility Functions (lib/utils/)

**cn.ts** - Class merge utility (Tailwind classes)
**format.ts** - Date/file formatting
```typescript
formatFileSize(bytes) → "2.5 MB"
formatDate(date) → "Feb 3, 2026"
getDocumentTypeLabel(type) → "PDF" or "Summary"
```

**validation.ts** - Input validation
```typescript
validateSubjectName(name) → boolean
validatePdfFile(file) → boolean | string (error)
validateSummaryContent(content) → boolean
```

**constants.ts** - App constants
```typescript
API_BASE_URL
DOCUMENT_TYPES = { PDF: 'pdf', SUMMARY: 'summary' }
GENERATION_SCOPES = { SUBJECT, DOCUMENT, CHAPTER, SUMMARY }
DOCUMENT_STATUS = { PROCESSING, READY, ERROR }
MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
```

---

## Phase 3: Reusable UI Components (Shadcn/ui)

### 3.1 Install Shadcn/ui Components
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add progress
```

### 3.2 Custom Shared Components

**LoadingSpinner.tsx**
- Centered spinner with optional text
- Used in loading states

**ConfirmDialog.tsx**
- Reusable confirmation modal
- For delete operations

**Toast Notifications**
- Success, error, warning, info types
- Auto-dismiss after 5s

**Breadcrumb.tsx**
- Navigation breadcrumb for: Subject → Document → Chapter
- Links to each level

**SourceCitation.tsx**
- Display source info for flashcards/quiz
- Format: "Source: [Document], Chapter X, Page Y" (for PDFs)
- Format: "Source: [Summary Title]" (for summaries)
- Visual design: Small badge with icon

---

## Phase 4: Page & Component Structure

### 4.1 Root Layout (app/layout.tsx)
```typescript
- Root HTML setup
- Font imports (e.g., Inter from next/font)
- Metadata (title, description)
- Tailwind globals
- Provider wrappers (Context/Zustand, Toast)
- Navbar component
```

### 4.2 Authentication Sketch (if needed)
```
Routes:
- / → Home/Login (redirects to /dashboard if authenticated)
- /dashboard → Main dashboard
- /auth/login → Login page (if multi-user in Phase 2)
- /auth/signup → Signup (optional)

For MVP: Skip auth, use localStorage for user_id or hardcode for testing
```

### 4.3 Subject Management Pages

**Page: (main)/subjects (SubjectListPage)**
```
Components:
- Navbar
- Sidebar (navigation)
- Subject Grid:
  - SubjectCard component for each subject
  - Color-coded cards with subject name, document count
  - Actions: View, Edit, Delete
- Create Subject Button → SubjectModal

Interactions:
- Create: Modal form (name, description, color picker)
- Edit: Modal with pre-filled data
- Delete: Confirmation dialog, cascade to documents
- Click card: Navigate to /subjects/[id]
```

**Page: (main)/subjects/[id] (SubjectDetailPage)**
```
Components:
- Breadcrumb: Home > Subjects > [Subject Name]
- Subject Header: Name, description, color bar
- Tabs:
  - "All Documents" - DocumentList filtered by subject
  - "PDFs" - Only PDFs
  - "Summaries" - Only summaries
  - "Chapters" - Hierarchical view of all chapters from all PDFs

DocumentList features:
- Sort by: Created, Name, Type, Status
- Filter: Status (all/processing/ready/error)
- Cards showing: name, type badge, status, progress bar, created date
- Actions: View, Delete, (View Chapters if PDF)

Create Document Button → DocumentUploadModal (with tabs)
```

**Page: (main)/subjects/[id]/documents/[docId] (DocumentDetailPage)**
```
Components:
- Breadcrumb: Home > Subjects > [Subject] > Documents > [Document]
- Document Header: Name, type badge, status, file size, created date
- Content Section:
  - For PDFs: 
    - Chapter List component (expandable/collapsible)
    - Edit chapters button
  - For Summaries:
    - Content preview (first 500 chars, expandable)
    - Edit button

Study Button: Opens ScopeSelector for this document (pre-selected scope=document)
Delete Document Button: Confirmation, cascade deletion
```

### 4.4 Upload & Content Creation

**Component: DocumentTabs (tabs for upload vs summary)**
```
Tab 1: "Upload PDF"
- File input (drag-drop + click)
- Subject dropdown (required)
- Display filename, file size validation
- Progress bar during upload
- Error message if upload fails
- Success message with document ID

Tab 2: "Create Summary"
- Subject dropdown (required)
- Summary title input
- Rich textarea for content (or rich editor)
- Optional chapter association dropdown
- Character count display (min 100, max 50KB)
- Submit button
- Loading state, success/error handling
```

**Component: FileUpload.tsx**
```
- Drag-drop zone
- Click to browse
- File type validation (PDF only)
- File size validation (max 10MB)
- Show selected filename
- Disabled during upload
- Progress callback
```

### 4.5 Study Interface

**Page: (main)/study (StudyPage)**
```
Components:
- Breadcrumb: Home > Study
- ScopeSelector component:
  - Radio/dropdown to choose scope:
    1. Subject: Select from dropdown
    2. Document: Select PDF or Summary
    3. Chapter: Select document, then chapter
    4. Summary: Select from dropdown
  - Different UI for each scope type

- Content Generator component:
  - Flashcard generator:
    - Count input (1-20, default 5)
    - Optional query/focus textarea
    - Generate button
    - Loading spinner
    - Error message
  - Quiz generator:
    - Count input (1-20, default 5)
    - Difficulty selector (easy/medium/hard)
    - Generate button
    - Loading spinner
    - Error message

Content Display:
- Once generated, show Flashcard Carousel or Quiz Interface
- Store in state (can reset to generate more)
```

**Component: ScopeSelector.tsx**
```typescript
// Visual hierarchy for scope selection
// Icons for each scope type
// Conditional dropdowns based on selection
// Clear labeling: "Study what?"
// Displays selected scope summary

Types:
- Subject (icon: book) - "Study entire subject"
- Document (icons: pdf, notes) - "Study single document" + type badge
- Chapter (icon: bookmark) - "Study specific chapter" 
- Summary (icon: note) - "Study from summary"
```

**Component: FlashcardCarousel.tsx**
```
Features:
- Centered card with flip animation
- Front side (question), back side (answer)
- Click/tap to flip, auto-flip after 5s (configurable)
- Progress indicator: "Card 3 of 5"
- Navigation buttons: Previous, Next, Shuffle, Reset
- Source citation badge below card (SourceCitation component)
- Full-screen button (optional)
- Export to PDF/image (Phase 5)
- Keyboard navigation (arrows)

Animations:
- Flip on Y-axis
- Smooth transitions
- Fade-in on card change
```

**Component: QuizInterface.tsx**
```
Features:
- Question number: "Question 2 of 5"
- Question text
- 4 radio button options (A, B, C, D)
- Submit answer button
- After submit:
  - Show correct/incorrect
  - Highlight correct answer in green
  - Show explanation
  - Show source citation (SourceCitation component)
  - Next button to proceed

At end:
- Score display: "You scored 4/5 (80%)"
- Option to retake quiz
- Option to go back to scope selector
- Performance breakdown (% by difficulty)

Progress:
- Progress bar showing completion
- Visual feedback on answered vs unanswered
```

**Component: SourceCitation.tsx**
```
Display formats:
For PDF:
┌─────────────────────────────────┐
│ 📄 Document Name                │
│ Chapter 5: Title | Page 42       │
└─────────────────────────────────┘

For Summary:
┌─────────────────────────────────┐
│ 📝 Summary: Title                │
└─────────────────────────────────┘

Props:
- source: SourceInfo
- variant: 'inline' | 'badge' | 'expanded'
- clickable: boolean (links to document?)
```

---

## Phase 5: Dashboard & Navigation

### 5.1 Dashboard Page (app/(main)/dashboard)
```
Components:
- Welcome message: "Welcome back, [User]"
- Quick stats cards:
  - Total subjects
  - Total documents
  - Recently studied
- Recent documents section:
  - Last 5 documents (across all subjects)
  - With thumbnails/type badges
  - Quick actions: View, Study

- Recently generated content:
  - Last 5 flashcard sets or quizzes
  - With scope info and date
  - Quick actions: Study, Delete

- CTA buttons:
  - "Create New Subject"
  - "Upload Document"
  - "Start Studying"
```

### 5.2 Layout Components

**Navbar.tsx**
```
Left side:
- Logo/app name
- (Optional) Home link

Center:
- Navigation links:
  - Subjects
  - Study
  - Dashboard

Right side:
- (Optional) User menu dropdown
- (Optional) Settings
- (Optional) Help/About

Mobile:
- Hamburger menu toggle
```

**Sidebar.tsx** (Optional, for secondary navigation)
```
- Collapsible sidebar
- Links to main sections
- Current subject quick select
- Quick access to recent documents
- Dark mode toggle (optional)
```

---

## Phase 6: Error Handling & Loading States

### 6.1 Error Boundaries
```typescript
RootErrorBoundary
- Catches all errors in app
- Shows friendly error message
- Reset button

PageErrorBoundary
- For individual pages
- More specific error handling
```

### 6.2 Error States in Components
```
For each async operation:
- Loading state: Spinner + disabled buttons
- Error state: Error message with retry button
- Empty state: "No documents found" + CTA
- Success state: Confirm message + redirect/reset
```

### 6.3 Error Display
```typescript
// Consistent error format
<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    {error.message}
    {error.details && <code>{JSON.stringify(error.details)}</code>}
    <Button onClick={retry}>Retry</Button>
  </AlertDescription>
</Alert>
```

---

## Phase 7: Form Handling

### 7.1 Subject Form (SubjectForm.tsx)
```
Fields:
- Name (required, max 100 chars, unique?)
- Description (optional, max 500 chars)
- Color picker (predefined options: 6-8 colors)

Validation:
- Real-time validation feedback
- Submit disabled if errors
- Show error message below each field

Actions:
- Submit button: "Create Subject" or "Update Subject"
- Cancel button: Close modal/return

Form library: react-hook-form + Zod validation
```

### 7.2 Document Upload Form
**PDF Upload (see DocumentTabs)**
- File input, validation, progress

**Summary Form (see DocumentTabs)**
- Title, content, optional chapter
- Character count feedback
- Word count display

### 7.3 Content Generation Form
**Flashcard Generator**
- Count slider (1-20)
- Optional query textarea
- Generate button

**Quiz Generator**
- Count slider (1-20)
- Difficulty selector
- Generate button

---

## Phase 8: Styling & Theme

### 8.1 Tailwind Configuration
```
Colors (using Shadcn defaults + custom):
- Primary: Blue (#3B82F6)
- Secondary: Slate gray
- Destructive: Red
- Subject colors: 6-8 predefined colors for cards

Spacing:
- Use Tailwind defaults (4px grid)
- Consistent padding: 16px, 24px, 32px

Typography:
- Headings: H1 (32px), H2 (24px), H3 (18px)
- Body: 16px (regular), 14px (small)
- Font: Inter (Google Fonts)
```

### 8.2 Component Styling Patterns
```
- Use Shadcn/ui components as base
- Extend with Tailwind for layout
- Use CSS modules only for complex animations
- Consistent spacing and alignment
- Accessible color contrast
- Responsive design (mobile-first)
```

### 8.3 Dark Mode (Optional, Phase 5)
```
- Tailwind dark mode support
- Toggle in navbar/settings
- Persist to localStorage
- Shadcn components support dark mode by default
```

---

## Phase 9: Responsive Design

### 9.1 Breakpoints
```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px

Key responsive changes:
- Navigation: Hamburger on mobile, horizontal on desktop
- Grids: 1 column (mobile) → 2 columns (tablet) → 3+ columns (desktop)
- Sidebar: Collapse to hamburger on mobile
- Modals: Full-screen on mobile, centered on desktop
- Study mode: Stack controls vertically on mobile
```

### 9.2 Mobile UX
```
- Touch-friendly button sizes (min 44px)
- Swipe to navigate flashcards
- Vertical scrolling for long content
- Bottom action bars instead of top
- Optimize image sizes for mobile bandwidth
```

---

## Phase 10: API Integration Testing

### 10.1 Mock API Server (Optional)
```typescript
// For development without backend
// Mock responses using MSW (Mock Service Worker) or similar
// Or use hardcoded mock data in development

// Mock data structure matches backend API exactly
// Update mocks as backend API evolves
```

### 10.2 API Contract
```
Ensure frontend requests/responses match backend API spec (Section 6 of master_prompt):
- Endpoint paths
- Request body structure
- Response body structure
- Error response format
- Status codes (200, 400, 404, 500, etc.)

Validation:
- Types in lib/types/api.ts must match backend Pydantic schemas
- Error handling matches backend error response format
```

---

## Implementation Phases (Detailed Breakdown)

### **Phase 1: Setup & Core (Week 1)**
- [ ] Initialize Next.js project with TypeScript, Tailwind, Shadcn/ui
- [ ] Set up project structure (folders, tsconfig, env vars)
- [ ] Create types (API types, models)
- [ ] Create API client with fetch wrapper
- [ ] Create custom hooks for API calls
- [ ] Set up state management (Context or Zustand)
- [ ] Create utility functions (validation, formatting)
- [ ] Root layout and basic navigation
- [ ] Error boundaries and error handling middleware

**Deliverable:** Fully configured Next.js project with working API client

---

### **Phase 2: UI Components & Common (Week 1-2)**
- [ ] Install all required Shadcn/ui components
- [ ] Create shared components (Navbar, Sidebar, Breadcrumb, LoadingSpinner)
- [ ] Create SourceCitation component
- [ ] Create Toast notification system
- [ ] Create ConfirmDialog component
- [ ] Create custom form components (with validation)
- [ ] Tailwind theme setup and constants
- [ ] Responsive grid/layout utilities

**Deliverable:** Reusable component library ready for all pages

---

### **Phase 3: Subject Management (Week 2)**
- [ ] Subject list page (SubjectGrid, SubjectCard)
- [ ] Create subject modal/form
- [ ] Subject detail page with document tabs
- [ ] Edit/delete subject functionality
- [ ] Connect to backend API (useSubjects, useCreateSubject, etc.)
- [ ] Loading/error states
- [ ] Filtering & sorting (optional)

**Deliverable:** Fully functional subject management

---

### **Phase 4: Document Management (Week 3)**
- [ ] Upload modal with PDF file upload (FileUpload component)
- [ ] Summary creation form
- [ ] Document list/grid view
- [ ] Document detail page
- [ ] Chapter list display (for PDFs)
- [ ] Chapter creation/edit modal
- [ ] Upload progress tracking
- [ ] Document status polling
- [ ] Delete document with confirmation
- [ ] Connect to backend API

**Deliverable:** PDF and summary upload, management, and chapter handling

---

### **Phase 5: Study Interface (Week 4)**
- [ ] Scope selector component (all 4 scope types)
- [ ] Content generator (flashcard + quiz forms)
- [ ] Flashcard carousel with flip animation
- [ ] Quiz interface with scoring
- [ ] Source citations on study content
- [ ] Error handling for insufficient context
- [ ] Study session state management
- [ ] Connect to backend generation API

**Deliverable:** Complete study workflow

---

### **Phase 6: Dashboard & Polish (Week 5)**
- [ ] Dashboard page with stats and quick access
- [ ] Recent content section
- [ ] Smooth page transitions
- [ ] Loading states across all pages
- [ ] Empty states with helpful CTAs
- [ ] Responsive design for all breakpoints
- [ ] Mobile-optimized UI
- [ ] Dark mode (optional)
- [ ] Accessibility audit (ARIA labels, contrast, keyboard nav)

**Deliverable:** Polished MVP frontend

---

### **Phase 7: Testing & Optimization (Week 5-6)**
- [ ] Unit tests for utility functions (vitest)
- [ ] Component tests for key components (React Testing Library)
- [ ] E2E tests for main workflows (Playwright)
- [ ] Performance optimization (code splitting, image optimization)
- [ ] Lighthouse audit and fixes
- [ ] Security review (XSS, CSRF, input validation)
- [ ] Browser compatibility testing

**Deliverable:** Tested and optimized frontend

---

### **Phase 8: Documentation & Deployment (Week 6)**
- [ ] Component storybook (optional)
- [ ] API integration documentation
- [ ] Deployment setup (Vercel)
- [ ] Environment configuration for staging/production
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] README with setup instructions
- [ ] Contribution guidelines

**Deliverable:** Production-ready frontend

---

## Key Implementation Details & Best Practices

### 10.1 Component Composition
```typescript
// Prefer composition over large monolithic components
// Example structure for a Document Card:

DocumentCard.tsx (Presentational)
├── Receives props: document, onView, onDelete, etc.
├── Handles rendering only
└── No API calls

DocumentCardContainer.tsx (Container)
├── Manages state
├── Calls API
├── Passes data to DocumentCard
└── Handles errors/loading

// Or use hooks:
useDocument() → Returns document data + actions
DocumentCard.tsx → Uses hook, simpler component
```

### 10.2 API Error Handling Strategy
```typescript
try {
  const data = await apiClient.get('/endpoint');
  setState(data);
} catch (error) {
  if (error instanceof FetchError) {
    if (error.status === 400) {
      // Validation error - show to user
    } else if (error.status === 500) {
      // Server error - retry
    }
  }
  setError(error.message);
}
```

### 10.3 Loading & Optimistic Updates
```typescript
// Show loading state immediately
// For mutations (create, update, delete):
// 1. Update UI optimistically
// 2. Make API call
// 3. If fails, revert UI
// For queries (fetch):
// 1. Show skeleton/spinner
// 2. Fetch data
// 3. Update UI with data
```

### 10.4 Form Validation with Zod
```typescript
// Define schema once, use everywhere
const SubjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/)
});

type Subject = z.infer<typeof SubjectSchema>;

// In form component:
const { register, errors } = useForm<Subject>({
  resolver: zodResolver(SubjectSchema)
});
```

### 10.5 Environment Variables
```typescript
// src/env.ts - Validate at build time
const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api',
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? 'SmartStudy AI'
};

export default env;

// Use in components:
import env from '@/env';
const response = await fetch(`${env.apiBaseUrl}/subjects`);
```

### 10.6 Keyboard Navigation
```typescript
// All interactive elements keyboard accessible
// Tab navigation for forms
// Arrow keys for carousels/selects
// Enter for buttons/submit
// Escape to close modals
// Implement in Flashcard carousel:
onKeyDown={(e) => {
  if (e.key === 'ArrowRight') nextCard();
  if (e.key === 'ArrowLeft') prevCard();
  if (e.key === ' ') flipCard();
}}
```

### 10.7 Image Optimization
```typescript
// Use Next.js Image component
import Image from 'next/image';

<Image
  src="/icon.svg"
  alt="Descriptive text"
  width={24}
  height={24}
  priority={true} // For above-fold images
/>

// Avoid <img> tag for optimization
```

### 10.8 Type Safety Across Layers
```
API Response → types/api.ts
  ↓
Custom hooks (lib/api/hooks.ts)
  ↓
Components (receive typed props)
  ↓
State management (store/context typed)
  ↓
UI display

// Entire pipeline is type-safe
// No 'any' types unless absolutely necessary
```

---

## Decision Points (Choices to Make)

1. **State Management:** React Context API (simpler, no dependencies) vs Zustand (lightweight, more powerful)
   - **Recommendation:** Zustand for better performance and debugging

2. **HTTP Client:** Native Fetch vs Axios
   - **Recommendation:** Fetch with custom wrapper (built-in, no dependencies)

3. **Form Library:** React Hook Form (recommended) vs Formik
   - **Recommendation:** react-hook-form (lightweight + Zod integration)

4. **Testing Library:** Vitest + RTL (recommended) vs Jest + Enzyme
   - **Recommendation:** Vitest (faster, ESM support)

5. **Animation Library:** Framer Motion vs TailwindCSS animations vs CSS
   - **Recommendation:** TailwindCSS for simple animations (flip card, fade), Framer Motion for complex (optional)

6. **Auth:** Implement now vs Phase 2
   - **Recommendation:** Skip for MVP, add in Phase 2 (use hardcoded user_id now)

7. **Rich Text Editor for Summaries:** Simple textarea vs TipTap/Slate editor
   - **Recommendation:** Start with textarea, upgrade to TipTap in Phase 5 if needed

---

## File Size & Performance Targets

- **Initial bundle size:** < 150KB (gzipped)
- **Largest route (study):** < 200KB
- **LCP (Largest Contentful Paint):** < 2.5s
- **FCP (First Contentful Paint):** < 1.5s
- **Cumulative Layout Shift:** < 0.1

**Strategies:**
- Code splitting by route (automatic in Next.js)
- Lazy load heavy components (Suspense + React.lazy)
- Image optimization (next/image)
- Compress SVGs
- Tree-shake unused Shadcn components

---

## Summary Timeline

**Total estimated time:** 5-6 weeks for MVP

- Week 1: Setup + Core architecture (Phase 1-2)
- Week 2-3: Subject & Document management (Phase 3-4)
- Week 4: Study interface (Phase 5)
- Week 5: Dashboard & Polish (Phase 6)
- Week 6: Testing, optimization, deployment (Phase 7-8)

**Parallel work:** Backend can be developed simultaneously using API spec from master_prompt

---

## Next Steps

1. **Finalize decisions** (state management, HTTP client, etc.)
2. **Initialize Next.js project** with chosen stack
3. **Create base directory structure** and configuration files
4. **Start Phase 1:** Set up API client and types
5. **Implement core components** (Navbar, Layout, Error boundaries)
6. **Begin Phase 3:** Subject management pages
7. **Iterate with backend team** on API endpoints

---

## Questions to Finalize

Before starting implementation, decide on:

1. ✅ Zustand or Context API? (Recommend Zustand)
2. ✅ Auth implementation now or Phase 2? (Recommend Phase 2)
3. ✅ Rich text editor for summaries? (Recommend textarea → TipTap upgrade)
4. ✅ Dark mode support? (Recommend Phase 5)
5. ✅ Animation library? (Recommend Tailwind only for MVP)
6. ✅ Backend deployment URL for development?
7. ✅ Any specific design/branding guidelines beyond master_prompt?

---

**This plan is comprehensive and ready to execute. Proceed to Phase 1 when ready.**
