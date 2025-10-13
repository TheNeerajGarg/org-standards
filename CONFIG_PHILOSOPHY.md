# Configuration Philosophy

**Source**: org-standards
**Date**: 2025-10-10
**Context**: Principles extracted from fashion-extract audit and workflow POC learnings

---

## The Core Distinction: Configuration vs Application Logic

The most important principle:

> **Configuration** changes HOW your application behaves.
> **Application Logic** defines WHAT your application does.

**The Test**:
- If changing it requires **understanding the business domain** → Application Logic (code/JSON in repo)
- If it's just **tuning runtime behavior** → Configuration (Dynaconf TOML)

---

## The Five Layers

```
┌─────────────────────────────────────────────────────┐
│ 1. Application Logic (JSON/Python in repo)          │
│    - Data models (schemas)                          │
│    - Domain knowledge (taxonomy, prompts)           │
│    - Business rules (validation logic)              │
└─────────────────────────────────────────────────────┘
         ↓ referenced by
┌─────────────────────────────────────────────────────┐
│ 2. Workflow Definitions (YAML in repo)              │
│    - State machines (document workflows)            │
│    - Approval requirements (who approves what)      │
│    - Bot orchestration (which bot does what)        │
└─────────────────────────────────────────────────────┘
         ↓ loaded at startup
┌─────────────────────────────────────────────────────┐
│ 3. Runtime Configuration (TOML/Dynaconf)            │
│    - Technical settings (timeouts, retries)         │
│    - Feature flags (enable_beta_feature)            │
│    - Environment-specific (dev/prod overrides)      │
└─────────────────────────────────────────────────────┘
         ↓ uses for execution
┌─────────────────────────────────────────────────────┐
│ 4. Task Queue (GitHub Issues/Projects)              │
│    - Dynamic tasks for bots                         │
│    - State tracking (labels, assignments)           │
│    - Coordination (projects, dependencies)          │
└─────────────────────────────────────────────────────┘
         ↓ accesses via
┌─────────────────────────────────────────────────────┐
│ 5. Secrets (Environment Variables)                  │
│    - API keys (ANTHROPIC_API_KEY)                   │
│    - Tokens (GITHUB_TOKEN)                          │
│    - Credentials (DATABASE_URL)                     │
└─────────────────────────────────────────────────────┘
```

---

## Layer 1: Application Logic (JSON/Python in repo)

**Purpose**: Domain knowledge and data models that define WHAT the application does

**Format**: JSON, Python classes, committed to Git

**Use for**:
- ✅ **Data schemas**: Output structure definitions
- ✅ **Domain knowledge**: Taxonomy of valid values
- ✅ **Prompt templates**: What the AI sees
- ✅ **Business rules**: Validation logic
- ✅ **Constants**: Domain-specific constants

**Example**: `src/shared/universal_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "main_category": {
      "type": "string",
      "enum": ["dress", "top", "bottom", "outerwear"]
    },
    "attributes": {
      "type": "object",
      "properties": {
        "color": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "value": {"type": "string"},
              "confidence": {"type": "number"}
            }
          }
        }
      }
    }
  }
}
```

**Example**: `src/shared/taxonomy_config.json`

```json
{
  "categories": {
    "dress": {
      "subcategories": ["cocktail", "maxi", "mini"],
      "attributes": ["neckline", "sleeve_length", "silhouette"]
    }
  },
  "attributes": {
    "neckline": {
      "values": ["v-neck", "round", "square", "off-shoulder"],
      "type": "single_select"
    }
  }
}
```

**Why NOT in Dynaconf**:
- ❌ Changing taxonomy requires **fashion domain expertise**
- ❌ Changing schema requires **understanding data model**
- ❌ These define the **core business logic** of the application
- ❌ Versioned with code (schema v2 works with code v2)

**Benefits of JSON in repo**:
- Version controlled with code
- Can be imported and validated by Python
- Type-checked and linted
- Easy to generate from (documentation, tests)

---

## Layer 2: Workflow Definitions (YAML in repo)

**Purpose**: Business process logic that defines state machines and orchestration

**Format**: YAML, committed to Git

**Use for**:
- ✅ **Document state machines**: drafting → review → approved
- ✅ **Approval requirements**: BRD needs PM + Engineering approval
- ✅ **Bot orchestration**: PM bot creates BRD → Architect bot creates ERD
- ✅ **Sequential dependencies**: BRD must be approved before PRD

**Example**: `config/workflows.yaml`

```yaml
document_types:
  brd:
    name: "Business Requirements Document"
    required_approvers: [pm, engineering]
    advisory_reviewers: [ux]
    next_document: prd

  prd:
    name: "Product Requirements Document"
    required_approvers: [engineering, pm]
    advisory_reviewers: [ux]
    next_document: erd

bot_orchestration:
  pm_bot:
    creates: [brd]
    reviews: [prd]

  architect_bot:
    creates: [erd]
    reviews: [prd, brd]

document_states:
  - drafting
  - ready_for_review
  - in_review
  - approved
  - rejected

transitions:
  - name: mark_ready_for_review
    from: drafting
    to: ready_for_review
    trigger: human_action
```

**Why NOT in Dynaconf**:
- ❌ Workflow logic is **business process knowledge**
- ❌ Changing approvers requires **understanding the domain**
- ❌ Platform-agnostic (same YAML works for GitHub/Linear/Database)

**Benefits**:
- Non-developers (PMs) can understand and propose changes
- Version controlled - audit trail of process changes
- Tool-friendly - generate diagrams, validate consistency

---

## Layer 3: Runtime Configuration (TOML/Dynaconf)

**Purpose**: Technical settings that change HOW the application behaves

**Format**: TOML files, loaded via Dynaconf

**Use for**:
- ✅ **API settings**: Endpoints, timeouts, retries
- ✅ **Feature flags**: `enable_experimental_bots = true`
- ✅ **Performance tuning**: Concurrency, batch sizes
- ✅ **Environment overrides**: Dev vs staging vs prod
- ✅ **Logging**: Log levels, output formats

**Example**: `config/default.toml`

```toml
[api]
anthropic_base_url = "https://api.anthropic.com"
timeout_seconds = 30
max_retries = 3
retry_delay_seconds = 1

[features]
enable_experimental_bots = false
enable_auto_merge = false
enable_preview_deployments = true

[bot_execution]
max_concurrent_bots = 5
container_timeout_seconds = 600
max_memory_mb = 2048

[observability]
log_level = "INFO"
enable_tracing = true
structured_logging = true
```

**Example**: `config/production.toml` (overrides)

```toml
[features]
enable_auto_merge = true  # Override: enable in prod

[bot_execution]
max_concurrent_bots = 20  # Override: more concurrency in prod

[observability]
log_level = "WARNING"  # Override: less verbose in prod
```

**Access in code**:

```python
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="SYRA",
    settings_files=['config/default.toml', 'config/production.toml'],
)

# Use configuration
timeout = settings.api.timeout_seconds
if settings.features.enable_experimental_bots:
    load_experimental_bots()
```

**Why NOT for application logic**:
- ❌ Don't put schemas here (use JSON in repo)
- ❌ Don't put taxonomy here (use JSON in repo)
- ❌ Don't put workflow logic here (use YAML)

---

## Layer 4: Task Queue (GitHub Issues/Projects)

**Purpose**: Dynamic task management and bot coordination

**Format**: GitHub Issues, Labels, Projects, Assignments

**Use for**:
- ✅ **Individual tasks**: Issues created by bots or humans
- ✅ **State tracking**: Labels (`bot-pending`, `bot-in-progress`, `bot-completed`)
- ✅ **Bot assignments**: Which bot is working on which issue
- ✅ **Visualization**: GitHub Projects kanban board

**Example**: GitHub Issue created by PM Bot

```markdown
Title: Create PRD for User Authentication
Labels: bot-task, architect-bot, prd-creation
Assignee: @architect-bot

## Context
BRD #123 has been approved. Create PRD based on requirements.

## Dependencies
- Depends on: #123 (BRD - Approved)

## Definition of Done
- [ ] PRD document created in docs/prd/
- [ ] All BRD requirements addressed
- [ ] Technical architecture outlined
- [ ] Security considerations documented
```

**Why GitHub for task queue**:
- ✅ Real-time (webhooks, no polling)
- ✅ Native UI (kanban, notifications)
- ✅ Audit trail (all actions logged)
- ✅ Integration (links, mentions, dependencies)

**Why NOT YAML files for tasks**:
- ❌ Requires polling (inefficient)
- ❌ Merge conflicts (multiple bots writing)
- ❌ No native UI (need custom viewer)
- ❌ No webhooks (can't trigger on changes)

---

## Layer 5: Secrets (Environment Variables)

**Purpose**: Sensitive credentials that never go in code or config files

**Format**: Environment variables, `.env` files (never committed)

**Use for**:
- ✅ **API keys**: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
- ✅ **Tokens**: `GITHUB_TOKEN`, `LINEAR_API_KEY`
- ✅ **Database credentials**: `DATABASE_URL`
- ✅ **Signing keys**: `JWT_SECRET_KEY`

**Example**: `.env` (gitignored, never committed)

```bash
# AI Provider Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# GitHub Integration
GITHUB_TOKEN=ghp_...
GITHUB_REPO=neerajgarg/syra-playground

# Database
DATABASE_URL=postgresql://user:pass@localhost/syra
```

**Access via Dynaconf**:

```python
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="SYRA",
    settings_files=['config/default.toml'],
)

# Environment variables override TOML
api_key = settings.ANTHROPIC_API_KEY  # From .env
timeout = settings.api.timeout_seconds  # From default.toml
```

---

## Decision Matrix: Which Layer?

| What are you storing? | Which Layer? | Format |
|----------------------|--------------|---------|
| Fashion category taxonomy | **Application Logic** | JSON in repo |
| Output schema definition | **Application Logic** | JSON in repo |
| Prompt templates | **Application Logic** | .txt in repo |
| "BRD needs PM approval" | **Workflow Definition** | YAML in repo |
| "After BRD, create PRD" | **Workflow Definition** | YAML in repo |
| API timeout (30 seconds) | **Runtime Config** | TOML (Dynaconf) |
| Enable beta feature flag | **Runtime Config** | TOML (Dynaconf) |
| "Create PRD for auth" task | **Task Queue** | GitHub Issue |
| Bot working on issue #42 | **Task Queue** | GitHub Assignment |
| Anthropic API key | **Secret** | ENV variable |
| Database password | **Secret** | ENV variable |

---

## Real-World Example: fashion-extract

### ✅ Correct Placement

**Application Logic** (JSON in repo):
- `src/shared/universal_schema.json` - Output data model
- `src/shared/taxonomy_config.json` - Fashion domain knowledge
- `src/extractor/prompts/System_Prompt.txt` - AI instructions

**Runtime Configuration** (Dynaconf TOML):
- `config/default.toml` - API timeouts, log levels
- `config/production.toml` - Production overrides

**Secrets** (ENV):
- `ANTHROPIC_API_KEY` - Never in code
- `OPENAI_API_KEY` - Never in code

### ❌ Anti-Pattern Example

```toml
# DON'T: Put taxonomy in Dynaconf
[taxonomy]
valid_categories = ["dress", "top", "bottom"]  # NO!
```

**Why wrong**: This is domain knowledge (application logic), not runtime configuration.

```json
// DON'T: Put API timeout in schema
{
  "api_timeout": 30,  // NO!
  "categories": ["dress", "top"]
}
```

**Why wrong**: Mixing runtime config with application logic.

---

## The "Understanding Test"

When deciding where something belongs, ask:

**"Who needs to understand this to change it safely?"**

- **Domain expert** (fashion designer, PM) → Application Logic (JSON/YAML)
- **Software engineer** → Workflow Definition (YAML)
- **DevOps engineer** → Runtime Config (TOML)
- **Security team** → Secrets (ENV)

**Example**: Changing `valid_necklines` from `["v-neck", "round"]` to `["v-neck", "round", "square"]`

- Requires **fashion domain knowledge** ✓
- Does NOT require understanding API timeouts ✗
- **Answer**: Application Logic (JSON in repo)

**Example**: Changing API timeout from 30s to 60s

- Does NOT require fashion knowledge ✗
- Just performance tuning ✓
- **Answer**: Runtime Config (TOML)

---

## Migration Checklist

When auditing a project for compliance:

### Application Logic Check
- [ ] Schema definitions in JSON files (not TOML)
- [ ] Taxonomy/domain data in JSON files (not TOML)
- [ ] Prompt templates in .txt files (not TOML)
- [ ] Business rules in Python code (not TOML)

### Workflow Definition Check
- [ ] State machines in YAML (not hardcoded in Python)
- [ ] Approval rules in YAML (not TOML)
- [ ] Bot orchestration in YAML (not scattered in code)

### Runtime Config Check
- [ ] API settings in TOML (not hardcoded)
- [ ] Feature flags in TOML (not env vars)
- [ ] Environment overrides in separate TOML files

### Secrets Check
- [ ] No API keys in TOML files
- [ ] No passwords in YAML files
- [ ] All secrets in .env (gitignored)
- [ ] .env.example provided (with dummy values)

---

## Summary

| Layer | Format | Version Control | Purpose |
|-------|--------|-----------------|---------|
| **Application Logic** | JSON/Python | Committed | WHAT the app does |
| **Workflow Definitions** | YAML | Committed | Business processes |
| **Runtime Config** | TOML | Committed | HOW the app behaves |
| **Task Queue** | GitHub | Dynamic | What needs doing |
| **Secrets** | ENV | Never committed | Credentials |

**Golden Rule**:
- Domain knowledge → **JSON/YAML in repo**
- Runtime tuning → **TOML (Dynaconf)**
- Credentials → **ENV variables**
- Tasks → **GitHub Issues**

---

**Related Docs**:
- [python/README.md](python/README.md) - Dynaconf setup guide
- [YAML_ARCHITECTURE.md](https://github.com/neerajgarg/fashion-extract/.workflow-poc/v2/config/YAML_ARCHITECTURE.md) - Workflow YAML design
