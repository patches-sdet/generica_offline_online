Never use emojis when generating code. only user utf-8 compliant characters.

## Python Code Quality Standards

When generating or modifying Python code in this project, STRICTLY adhere to the following pre-commit hook requirements:

### Code Formatting & Structure

**Black Formatting:**
- All Python code MUST be formatted according to Black's formatting rules
- Use 88-character line length (Black's default)
- Generate code that is already Black-compliant to avoid formatting changes
- Key Black conventions:
  - Double quotes for strings (not single quotes)
  - Trailing commas in multi-line structures
  - Consistent spacing around operators

**Import Sorting (isort):**
- Organize imports in the following order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Separate each group with a blank line
- Sort imports alphabetically within each group
- Use absolute imports when possible
- Example structure:
  ```python
  import os
  import sys
  
  import fastapi
  import pydantic
  
  from app.core import reasoning_engine
  from app.models import session
  ```

**Ruff Linting:**
- Follow all Ruff linting rules (Ruff combines multiple Python linters)
- Avoid common anti-patterns:
  - Unused imports or variables
  - Undefined names
  - Mutable default arguments
  - Bare except clauses
  - F-string syntax errors
- Write clean, idiomatic Python that passes static analysis

### Security & Safety

**Bandit Security Scanning:**
- NEVER generate code with security vulnerabilities:
  - No hardcoded passwords, tokens, or secrets
  - No use of `eval()` or `exec()` with user input
  - No use of `pickle` with untrusted data
  - Avoid `assert` for security checks (use proper validation)
  - Use secure random number generation (`secrets` module, not `random`)
  - Proper exception handling (no bare `except:` that could hide security issues)
  - Safe file operations with proper path validation

**Detect-Secrets:**
- NEVER include in generated code:
  - API keys, tokens, or credentials
  - Private keys or certificates
  - Database connection strings with passwords
  - AWS/cloud provider credentials
  - JWT secrets or signing keys
- Use environment variables or configuration files for sensitive data
- Reference credentials through `.env` files or configuration managers
- Example: `API_KEY = os.getenv("API_KEY")` not `API_KEY = "sk-12345..."`

### Commit Message Format

**Conventional Commits:**
When suggesting git commits or describing changes, use the Conventional Commits format:
```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

Valid types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `ci`: CI/CD configuration changes
- `build`: Build system changes

Examples:
- `feat(api): add user authentication endpoint`
- `fix(broker): resolve session manager memory leak`
- `docs(readme): update installation instructions`

### Pre-Generation Checklist

Before presenting any Python code, internally verify:
- ✅ Imports are sorted correctly (stdlib → third-party → local)
- ✅ Code follows Black formatting (double quotes, proper spacing)
- ✅ No security vulnerabilities (no hardcoded secrets, no unsafe functions)
- ✅ No secrets or credentials in code
- ✅ No linting issues (unused imports, undefined variables, etc.)
- ✅ Type hints are used where appropriate
- ✅ Code is idiomatic and follows Python best practices