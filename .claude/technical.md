# Technical Standards: Imports & Migration

## Dev/CI Environment Parity

**CRITICAL REQUIREMENT**: Devcontainer and CI/CD environments MUST be identical

### Symmetric Version Pinning Rule

**Both devcontainer AND CI/CD must use the same pinned Ubuntu version**

❌ **WRONG** (Asymmetric - causes drift):
```dockerfile
# .devcontainer/Dockerfile
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04  # Pinned
```
```yaml
# .github/workflows/ci.yml
runs-on: ubuntu-latest  # Unpinned - can change!
```

✅ **CORRECT** (Symmetric - drift-proof):
```dockerfile
# .devcontainer/Dockerfile
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04
```
```yaml
# .github/workflows/ci.yml
runs-on: ubuntu-24.04  # PINNED: Must match .devcontainer/Dockerfile
```

### Automated Verification

**Workflow**: `.github/workflows/verify-devcontainer-parity.yml`
- Runs on every push/PR that changes Dockerfile or workflows
- Extracts Ubuntu versions from both environments
- **Fails the build** if versions don't match
- **Fails the build** if CI/CD uses `ubuntu-latest`

### Why This Matters

**Problem**: `ubuntu-latest` is a moving target controlled by GitHub
- It WAS Ubuntu 22.04
- It IS NOW Ubuntu 24.04
- It WILL BE Ubuntu 26.04 in the future

**Impact of drift**:
- ❌ "Works on my machine" failures
- ❌ CI/CD fails but local tests pass
- ❌ Different package availability (e.g., libgl1-mesa-glx → libgl1)
- ❌ Loss of reproducibility

**Historic incident**: See `.ai-sessions/2025-10-21/introspection-devcontainer-ci-parity-broken.md`

### Update Process

When upgrading Ubuntu versions:
1. Update `.devcontainer/Dockerfile` FROM version
2. Update ALL `runs-on:` in `.github/workflows/*.yml`
3. Update system packages if needed (check deprecated packages)
4. Run `verify-devcontainer-parity.yml` to confirm
5. Rebuild local devcontainer
6. Verify tests pass locally AND in CI/CD

### References
- Verification workflow: `.github/workflows/verify-devcontainer-parity.yml`
- Root cause analysis: `.ai-sessions/2025-10-21/introspection-devcontainer-ci-parity-broken.md`

---

## Import Architecture Standards

### MANDATORY: Three-Tier Import Strategy

```python
# 1. STANDARD LIBRARY IMPORTS (always first)
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 2. THIRD-PARTY IMPORTS (always second)
import pytest
from unittest.mock import Mock, patch
import requests

# 3. PROJECT IMPORTS (always last)

# ✅ WITHIN COMPONENT: Relative imports
from .batch_processor import BatchProcessor
from .providers.openai_provider import OpenAIProvider
from ..utils.helpers import validate_image

# ✅ CROSS-COMPONENT: Absolute imports from project root
from src.shared.schemas.taxonomy import TaxonomyProvider
from src.components.crawler.policies.interfaces import PolicyResult
from src.shared.config_manager import ConfigManager
```

### Import Strategy Rules

1. **Within Component** (same package): Use relative imports
2. **Cross-Component** (different components): Use absolute imports from `src.`
3. **External Libraries**: Use standard imports

### Schema Import Pattern (Phase 2+)

**All Syra schemas centralized in `src/syra/schemas/`**:

```python
# ✅ CORRECT: Import from centralized location
from src.syra.schemas.artifacts import task_schema, report_schema
from src.syra.schemas.validation import validate_json_ld
from src.syra.schemas import load_context

# ✅ CORRECT: Load @context definitions
import json
with open('src/syra/schemas/@context/v1.0.0/bot-swarm.jsonld') as f:
    context = json.load(f)

# ❌ WRONG: Import from legacy scattered locations
from src.shared.universal_schema import ...  # Legacy (migrating to src/syra/schemas/legacy/)
from scripts.schemas.brd_schema import ...    # Wrong location (moved to src/syra/schemas/documents/)
```

**Schema Location Standards**:
- **Syra core schemas**: `src/syra/schemas/` (centralized)
- **@context definitions**: `src/syra/schemas/@context/v1.0.0/`
- **Bot swarm artifacts**: `src/syra/schemas/artifacts/`
- **Agent communication**: `src/syra/schemas/agents/`
- **Document schemas**: `src/syra/schemas/documents/` (BRD/PRD/ERD)
- **Legacy schemas**: `src/syra/schemas/legacy/` (migration from `src/shared/`)

**Why Centralized**:
- Single source of truth for all schemas
- No duplicates (no more `src/shared/` vs `shared/` confusion)
- Clear versioning (@context v1.0.0, v1.1.0)
- Easy discovery for future Claude sessions

**Details**: See [.claude/schema-standards.md](.claude/schema-standards.md)

### ❌ FORBIDDEN Import Patterns

```python
# ❌ FORBIDDEN: sys.path manipulation in production code
sys.path.insert(0, str(project_root))  # Only allowed in conftest.py

# ❌ FORBIDDEN: Complex relative imports across components
from ...src.batch_extract_fashion_info import main
from ..src.image_file_handler import iter_images
```

### Package Structure Requirements
Every directory must have `__init__.py`:
```
src/
├── __init__.py                    # Required
├── components/
│   ├── __init__.py               # Required
│   ├── extractor/
│   │   ├── __init__.py           # Required
│   │   ├── core/
│   │   │   └── __init__.py       # Required
│   │   └── tests/
│   │       └── __init__.py       # Required
├── shared/
│   └── __init__.py               # Required
└── scripts/
    └── __init__.py               # Required
```

## Strategy Pattern for Path Resolution

### MANDATORY: Use Strategy Pattern for Path Operations

All path resolution must use injectable PathResolver strategies to eliminate test brittleness.

**Generic PathResolver interface:**
```python
from abc import ABC, abstractmethod
from pathlib import Path

class PathResolver(ABC):
    """Abstract base class for path resolution strategies."""

    @abstractmethod
    def resolve_path(
        self,
        source_path: str,
        target_file: Path,
        base_dir: Path
    ) -> str:
        """Resolve source path relative to target file location."""
        pass
```

**Concrete implementations:**
- `RelativePathResolver`: Best practice for most scenarios
- `AbsolutePathResolver`: For deployment requiring absolute paths
- `BrokenPathResolver`: For testing broken path scenarios
- `DefaultPathResolver`: Combines best practices

**Dependency injection pattern:**
```python
def generate_html(
    results: List[Dict[str, Any]],
    images_dir: str,
    output_file: str,
    path_resolver: Optional[PathResolver] = None
) -> None:
    """Generate HTML with injectable path resolution strategy."""
    if path_resolver is None:
        path_resolver = DefaultPathResolver()

    image_src = path_resolver.resolve_path(
        image_path, Path(output_file), Path(images_dir)
    )
```

**Benefits:**
1. **Testability**: Inject specific strategies for deterministic testing
2. **Maintainability**: Add strategies without modifying existing code
3. **Flexibility**: Different environments use different strategies
4. **Separation of Concerns**: Path logic separated from business logic

## Migration Standards

### MANDATORY: Test-Driven Migration Process

**NO MIGRATION IS COMPLETE UNTIL ALL TESTS PASS**

1. **File-by-File Migration**: NEVER change multiple files simultaneously
2. **Immediate Validation**: Run tests after each file change
3. **Dependency Tracking**: Update all dependent files immediately
4. **Test Coverage**: All changed files must have passing tests

### Safe Migration Process

**ALWAYS COMMIT BEFORE MIGRATION**

1. **Pre-Migration Commit**: `git commit -m "Pre-migration checkpoint"`
2. **Batch Processing**: Process 3-5 files at a time
3. **AST-Based Changes**: Use `python scripts/ast_migration_tool.py`
4. **Batch Validation**: Validate entire batch before proceeding
5. **Commit Success**: `git commit -m "Migrate batch N: description"`
6. **Rollback on Failure**: `git reset --hard HEAD` if batch fails

### Migration Validation Gates

Every migration must pass:
1. **Syntax Validation**: `python -c "import ast; ast.parse(open('file.py').read())"`
2. **Import Resolution**: `python -c "import module"`
3. **Unit Test Validation**: `pytest src/module/tests/ -v`
4. **Integration Test Validation**: `pytest tests/integration/ -v`
5. **Full Test Suite**: `pytest --tb=short`

### Success Criteria

Migration is complete when:
- ✅ All syntax errors resolved
- ✅ All import errors resolved
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All dependent tests pass
- ✅ No test regressions introduced
- ✅ All pre-commit hooks pass
