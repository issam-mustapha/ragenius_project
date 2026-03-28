# 🤝 Contributing to RAGenius

Thank you for considering contributing to RAGenius! This document outlines how to get involved, report issues, and submit pull requests.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Commit Convention](#commit-convention)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Issues](#reporting-issues)
- [Project Structure](#project-structure)

---

## 🧭 Code of Conduct

By participating in this project, you agree to maintain a respectful and constructive environment. Please:

- Be kind and inclusive in all interactions
- Accept constructive feedback gracefully
- Focus on what is best for the project and the community
- Avoid discriminatory, offensive, or harassing language

---

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork via GitHub UI, then:
git clone https://github.com/YOUR_USERNAME/ragenius_project.git
cd RAGenius
git remote add upstream https://github.com/issam-mustapha/ragenius_project.git
```

### 2. Set Up the Environment

```bash
# Backend (Python)
cd backend
docker-compose up --build

# Frontend (Node.js)
cd ../frontend
npm install
npm run dev
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your local credentials
```

### 4. Run the App Locally

```bash
# Start all services
docker-compose up --build


# Frontend
npm run dev
```

---

## 🛠️ How to Contribute

### Types of Contributions Welcome

| Type | Examples |
|---|---|
| 🐛 Bug fixes | Fix incorrect RAG retrieval, auth token issues |
| ✨ New features | New memory strategies, file format support |
| 📚 Documentation | Improve README, add docstrings, write tutorials |
| 🎨 UI/UX | Improve chat interface, accessibility |
| ⚡ Performance | Faster FAISS indexing, query optimization |
| 🧪 Tests | Unit tests, integration tests, CI improvements |
| 🌍 i18n | Add language support to the interface |

### Before You Start

- Check [open issues](https://github.com/issam-mustapha/RAGenius/issues) to avoid duplicate work
- For large features, **open an issue first** to discuss the approach
- For small fixes (typos, minor bugs), feel free to open a PR directly

---

## 🔀 Development Workflow

```
main          ← stable, production-ready
  └── dev     ← integration branch for features
        └── feature/your-feature-name   ← your work
        └── fix/issue-description
        └── docs/what-you-documented
```

### Step-by-step

```bash
# 1. Sync your fork with upstream
git fetch upstream
git checkout dev
git merge upstream/dev

# 2. Create your branch
git checkout -b feature/add-pdf-summarization

# 3. Make your changes
# ... write code ...

# 4. Run tests
cd backend && pytest
cd frontend && npm run test

# 5. Stage and commit
git add .
git commit -m "feat(rag): add multi-document summarization support"

# 6. Push and open PR
git push origin feature/add-pdf-summarization
```

---

## ✍️ Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
(): 
```

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructure without feature change |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `chore` | Build, CI, dependencies |

**Examples:**
```
feat(memory): add long-term preference extraction from conversations
fix(faiss): resolve per-user index isolation bug on concurrent uploads
docs(readme): add architecture diagram and setup instructions
test(api): add unit tests for PII detection middleware
```

---

## 📬 Pull Request Guidelines

- Target the `dev` branch (not `main`)
- Fill in the PR template completely
- Link any related issues with `Closes #123`
- Keep PRs focused — one feature or fix per PR
- Include screenshots for UI changes
- Ensure all checks pass before requesting review

### PR Template

```markdown
## Summary


## Changes
- [ ] Feature / Fix / Docs / Other

## Related Issue
Closes #

## Testing Done


## Screenshots (if UI change)

```

---

## 🐛 Reporting Issues

When filing a bug report, please include:

1. **Description** — what happened vs what you expected
2. **Steps to reproduce** — minimal example
3. **Environment** — OS, Python version, Node version, Docker version
4. **Logs** — paste relevant error output
5. **Screenshots** — if UI-related

Use the issue template provided in `.github/ISSUE_TEMPLATE/`.



## 💬 Questions?

Open a [GitHub Discussion](https://github.com/issam-mustapha/ragenius_project/discussions) or reach out via LinkedIn:
[linkedin.com/in/issamadoch](https://www.linkedin.com/in/issam-ai-engineer)

---

*Thank you for helping make RAGenius better! 🧠*
