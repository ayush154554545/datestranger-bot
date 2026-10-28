# OpenCode Universal Development OS

Welcome to your **OpenCode Universal Development OS**. This installation transforms OpenCode into a reusable, professional, low-token, production-oriented engineering system across web (React/TypeScript/Next.js/Vite), backend (Node/Express/Python/.NET), Android (Kotlin/Java/Gradle), desktop (Windows C#/.NET), databases, APIs, SaaS products, automation, and legacy codebases.

---

## 🏛 Architecture & Layered System

```
┌──────────────────────────────────────────────────────────────────┐
│                   Global Customization Layer                    │
│                 C:\Users\aman aryal\.gemini\config\              │
│  - AGENTS.md / GEMINI.md (Universal Engineering & Security)     │
│  - mcp_config.json (Playwright, DevTools, Supabase, ClickHouse)  │
│  - 17 Specialist Agents (specs/prompts)                          │
│  - 19 Universal Skills (SKILL.md runbooks)                       │
│  - 11 Reusable Commands                                          │
│  - env/.env.global.example & CREDENTIAL_CHECKLIST.md             │
└──────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Workspace Project Layer                        │
│                   .agents/ & Project Root                        │
│  - PROJECT_RULES.md (Codebase Invariants)                        │
│  - PRD.md, ARCHITECTURE.md, TECH_STACK.md, DATABASE.md           │
│  - API.md, UI_UX.md, TEST_PLAN.md, SECURITY.md, DEPLOYMENT.md     │
│  - ENVIRONMENT.md, MANUAL_SETUP.md, CHANGELOG.md, memory.md       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Available Specialist Agents (17)

1. **`orchestrator`**: Task decomposition, agent/skill assignment, verification, final synthesis.
2. **`architect`**: System boundaries, design patterns, database & API contracts.
3. **`frontend-engineer`**: React, TypeScript, Next.js, HTML/CSS, UI architecture, accessibility.
4. **`backend-engineer`**: Node.js, Express, Python, .NET APIs, services, controllers, queues.
5. **`android-engineer`**: Android apps, Kotlin, Java, Gradle, manifests, Android SDK.
6. **`desktop-engineer`**: Windows C#/.NET desktop applications, WPF, WinForms, native tooling.
7. **`ui-ux-engineer`**: Visual hierarchy, color systems, responsive layouts, loading/error states.
8. **`database-engineer`**: PostgreSQL, Supabase, Redis, schema migrations, query tuning.
9. **`debugger`**: Root-cause analysis, stack trace inspection, automated safe debugging.
10. **`qa-testing-engineer`**: Unit, integration, API, and component test execution.
11. **`browser-qa-engineer`**: Playwright browser automation, rendered UI validation, DOM testing.
12. **`security-reviewer`**: Secrets auditing, OWASP checks, input validation, dependency security.
13. **`performance-engineer`**: Profiling, bottleneck analysis, memory/bundle size optimization.
14. **`devops-engineer`**: Docker, CI/CD, hosting (Fly.io, Render, Vercel), container orchestration.
15. **`documentation-engineer`**: System documentation synchronization (PRD, API, Architecture).
16. **`code-reviewer`**: Code quality auditing, diff reviews, strict no-regression checks.
17. **`researcher`**: Web research, external documentation lookup, API specifications.

---

## 🧰 Universal Skills (19)

- `project-audit` • `architecture-planning` • `frontend-dev` • `backend-dev` • `android-dev`
- `desktop-dev` • `ui-ux-implementation` • `database-design` • `api-design` • `browser-testing`
- `automated-testing` • `debugging` • `security-review` • `performance-optimization` • `deployment`
- `documentation-generation` • `dependency-auditing` • `git-workflow` • `release-validation`

---

## 🚀 Commands (11)

- ` project-audit` - Audit codebase tech stack, coverage, dependencies, technical debt.
- ` architecture-audit` - Evaluate module boundaries and system architecture.
- ` test` - Execute targeted and regression test suites.
- ` debug` - Isolate test/build failures and apply minimal fixes.
- ` review` - Code review and no-regression check.
- ` ui-review` - Audit visual design, responsive layout, and accessibility.
- ` security-review` - Scan secrets, OWASP risks, and permissions.
- ` dependency-audit` - Scan outdated or vulnerable dependencies.
- ` build-verification` - Execute production build check.
- ` release-verification` - Validate release checklist and artifacts.
- ` doc-sync` - Synchronize system documentation with codebase state.

---

## ⚡ Low-Token Context Rules
- Never scan `node_modules`, `build`, `dist`, `bin`, or lockfiles.
- Rely on manifest files (`package.json`, `requirements.txt`, `csproj`, `build.gradle`).
- Use targeted symbol grep and slice range `view_file`.
- Summarize architecture into project documentation and reuse summaries.

---

## 🔄 Bootstrapping a New Project
To bootstrap any existing repository with this system without overwriting user files:
```bash
node "C:\Users\aman aryal\.gemini\antigravity-ide\brain\23118734-1c94-4cb5-94a3-a6b277475581\scratch\bootstrap_workspace.js"
```
Or run the `/project-audit` command.
