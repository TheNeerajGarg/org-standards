# Schema Standards & JSON-LD Architecture

**Status**: Active - Phase 2 Implementation
**Last Updated**: 2025-10-15

---

## Overview

All Syra core schemas use **JSON-LD format** (RDF-compatible) organized in `src/syra/schemas/` for semantic interoperability, A2A protocol compatibility, and future Neo4j integration (Phase 3).

**Key Decision**: Upgrade from plain JSON to JSON-LD for bot swarm artifacts while maintaining backward compatibility with fashion extraction schemas.

---

## Schema Organization

### Directory Structure

```
src/syra/schemas/
├── @context/
│   └── v1.0.0/                        # RDF context definitions
│       ├── syra-core.jsonld           # Core Syra ontology
│       ├── bot-swarm.jsonld           # Task, Report, Finding
│       └── introspection.jsonld       # Learning, prompt improvements
│
├── artifacts/                         # Bot swarm execution schemas
│   ├── task.schema.json               # JSON Schema (validation)
│   ├── report.schema.json             # JSON Schema (validation)
│   └── introspection.schema.json      # JSON Schema (validation)
│
├── agents/                            # Agent communication
│   ├── bot-config.schema.json         # Bot registry config
│   └── agent-message.schema.json      # A2A-compatible messages
│
├── documents/                         # BRD/PRD/ERD schemas
│   ├── brd.schema.json
│   ├── prd.schema.json
│   └── erd.schema.json
│
└── legacy/                            # Migrated from src/shared/
    ├── universal_schema.json          # Fashion extraction (plain JSON)
    └── taxonomy_schema.json           # Taxonomy config (plain JSON)
```

---

## Five Core Standards

### 1. Centralized Location
**Rule**: All Syra core schemas in `src/syra/schemas/` (not scattered in `src/shared/`, `scripts/schemas/`, etc.)

### 2. @context Versioning
**Rule**: @context files versioned separately in `@context/v1.0.0/`, `@context/v1.1.0/`, etc.

**Why**: @context changes are semantic breaking changes (require version bump)

### 3. Dual Schema Files
**Rule**: Every artifact has TWO files:
- `*.schema.json` - JSON Schema (validation rules)
- `*.jsonld` - Example JSON-LD (documentation + @context)

### 4. Schema $id URIs
**Rule**: All schemas have canonical URI $id:
```json
{
  "$id": "http://styleguru.ai/schemas/task-v1.json"
}
```

### 5. Git Versioning
**Rule**: Schema version = Git commit SHA (same as prompts)

**Tracking**:
```json
{
  "_version_info": {
    "version": "1.0.0",
    "commit_hash": "abc123def456",
    "github_url": "https://github.com/StyleGuru/StyleGuru/blob/.../task.schema.json"
  }
}
```

---

## JSON-LD vs Plain JSON

### When to Use JSON-LD

**Use JSON-LD for**:
- ✅ Bot swarm artifacts (Task, Report, Introspection)
- ✅ BRD/PRD/ERD documents (decision reasoning embedded)
- ✅ Agent communication (A2A compatibility)
- ✅ Knowledge graphs (Neo4j import Phase 3)

**Benefits**:
- Semantic meaning (RDF-compatible)
- Schema validation (JSON Schema + RDF validation)
- Graph queries ("Show all introspections → prompt improvements")
- A2A protocol compatibility (Google/Linux Foundation standard)

### When to Use Plain JSON

**Use Plain JSON for**:
- ⚠️ Fashion extraction outputs (Phase 2A: Add @context post-processing)
- ⚠️ Internal config files (taxonomy_config.json)

**Migration Strategy** (Phase 2A):
- Bots output plain JSON → Python adds @context → Save as JSON-LD
- No prompt changes needed
- Immediate RDF compatibility

---

## Bot Output Format

### All Bots Output JSON-LD (Not Markdown)

**Bad** (Old):
```python
result = crew.kickoff()
output_text = result.output  # Markdown string, requires parsing
```

**Good** (New):
```python
result = crew.kickoff()
report_jsonld = json.loads(result.output)  # Structured JSON-LD

# Validate against schema
validate_json_ld(report_jsonld, schema='report.schema.json')

# Save
with open(f'reports/report-{task_id}.json', 'w') as f:
    json.dump(report_jsonld, f, indent=2)
```

**Bot Prompt Template**:
```python
bot_prompt = """
Output format: JSON-LD Report

@context: http://styleguru.ai/schemas/@context/v1.0.0/bot-swarm.jsonld
@type: ["Report", "BotExecutionReport"]

Required fields:
- summary (confidence, findings_count)
- findings (each with severity, location, recommendation, decision reasoning)
- statistics (completeness_score)
- next_actions

IMPORTANT: Output ONLY valid JSON-LD (no markdown, no code blocks).
"""
```

---

## A2A Protocol Integration

### What is A2A?

**Agent2Agent Protocol**: Open standard for AI agent communication (Google/Linux Foundation, 100+ partners)

**Key Features**:
- Standards: HTTP, JSON-RPC, SSE
- Enterprise: Auth, webhooks, streaming
- Ecosystem: Microsoft, Salesforce, LangChain, etc.

### Phase 2: Design for A2A (Now)

**Strategy**: JSON-LD schemas are A2A-compatible (can wrap in JSON-RPC)

**Example**:
```json
{
  "jsonrpc": "2.0",
  "method": "agent.invoke",
  "params": {
    "task": {
      // Syra Task JSON-LD here
      "@context": "http://styleguru.ai/schemas/@context/v1.0.0/bot-swarm.jsonld",
      "@type": ["Task", "a2a:AgentTask"],
      ...
    }
  }
}
```

### Phase 3: Adopt A2A (Future)

**When**: After Neo4j integration proven
**Why**: Enable external agent interoperability (non-CrewAI agents)

---

## CrewAI + JSON-LD Integration

### Structured Task Creation

```python
from crewai import Agent, Task, Crew
import json

# Load Task JSON-LD
with open('task-uuid-123.json') as f:
    task_jsonld = json.load(f)

# Extract for CrewAI
task_description = f"""
Review document: {task_jsonld['input']['document_path']}
Objective: {task_jsonld['input']['objective']}

Output format: JSON-LD Report (schema at http://styleguru.ai/schemas/report-v1.json)
@context: {json.dumps(task_jsonld['@context'])}
"""

task = Task(
    description=task_description,
    agent=completeness_bot,
    expected_output='JSON-LD Report with @context'
)

# Execute
result = crew.kickoff()
report_jsonld = json.loads(result.output)

# Validate
validate_json_ld(report_jsonld, schema='report.schema.json')

# Save
with open(f'reports/report-{task_jsonld["id"]}.json', 'w') as f:
    json.dump(report_jsonld, f, indent=2)
```

**Benefits**:
- ✅ No regex parsing (programmatic access)
- ✅ Schema validation (catch malformed outputs)
- ✅ RDF conversion (Neo4j Phase 3)
- ✅ Decision traceability (every finding has reasoning)

---

## Universal Schema Migration

### Current State

- `universal_schema.json`: Plain JSON Schema (fashion items)
- Bots output plain JSON (no @context)
- Not RDF-compatible (can't import to Neo4j)

### Phase 2A: Hybrid (Current)

**Strategy**: Post-processing wrapper

```python
def add_jsonld_context(plain_json_output):
    """Add JSON-LD @context to plain JSON output."""
    with open('src/syra/schemas/@context/v1.0.0/fashion-item.jsonld') as f:
        context = json.load(f)

    return {
        "@context": context["@context"],
        "@id": f"http://styleguru.ai/data/items/{plain_json_output['id']}",
        "@type": "FashionItem",
        **plain_json_output
    }
```

**When**: Now (no prompt changes needed)

### Phase 2B: Native (Future)

**Strategy**: Update bot prompts to output JSON-LD directly

**When**: After Phase 3 (Neo4j import active and proven)

---

## Schema Validation

### Validation Pipeline

```python
from jsonschema import Draft7Validator
from rdflib import Graph

def validate_json_ld(doc: dict, schema_path: str):
    """Validate JSON-LD against JSON Schema and RDF."""

    # 1. JSON Schema validation
    with open(schema_path) as f:
        schema = json.load(f)

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        raise ValidationError(f"{len(errors)} schema errors: {errors}")

    # 2. RDF validation (optional, for Neo4j prep)
    g = Graph()
    g.parse(data=json.dumps(doc), format='json-ld')

    return True  # Valid
```

### Usage in Bot Executor

```python
def execute_bot(task_jsonld):
    # Execute bot
    result = crew.kickoff()
    report_jsonld = json.loads(result.output)

    # Validate
    try:
        validate_json_ld(report_jsonld, 'src/syra/schemas/artifacts/report.schema.json')
    except ValidationError as e:
        logger.error("Bot output validation failed", error=str(e))
        raise

    # Save
    report_path = f'.ai-sessions/{today}/reports/report-{uuid4()}.json'
    with open(report_path, 'w') as f:
        json.dump(report_jsonld, f, indent=2)

    return report_jsonld
```

---

## Anti-Patterns to Avoid

### AP-1: Scattered Schema Files
**Problem**: Schemas in `src/shared/`, `scripts/schemas/`, `shared/` (duplicates)

**Solution**: Centralize in `src/syra/schemas/`

### AP-2: Inline @context in Documents
**Problem**: Every document duplicates @context (maintenance nightmare)

**Solution**: Reference external @context:
```json
{
  "@context": "http://styleguru.ai/schemas/@context/v1.0.0/bot-swarm.jsonld",
  ...
}
```

### AP-3: Plain JSON for Bot Outputs
**Problem**: Requires regex parsing, no validation, no RDF compatibility

**Solution**: Bots output JSON-LD directly (include @context in prompt)

### AP-4: No Schema Validation
**Problem**: Malformed bot outputs accepted silently

**Solution**: Validate all bot outputs against JSON schemas

---

## Reference Documentation

**Full Architecture**:
- [syra-schema-architecture.md](../.ai-sessions/2025-10-15/syra-schema-architecture.md) - 35+ page deep dive
- [syra-schemas-implementation-summary.md](../.ai-sessions/2025-10-15/syra-schemas-implementation-summary.md) - Executive summary

**Phase 2 Decisions**:
- [phase2-architecture-decisions.md](../.ai-sessions/2025-10-15/phase2-architecture-decisions.md) - CrewAI, JSON-LD, ontology choices
- [phase2-implementation-ready.md](../.ai-sessions/2025-10-15/phase2-implementation-ready.md) - Implementation roadmap

**BRD/PRD/ERD Schemas**:
- [brd-json-ld-schema.md](../.ai-sessions/2025-10-15/brd-json-ld-schema.md) - BRD JSON-LD design
- [json-ld-explained.md](../.ai-sessions/2025-10-15/json-ld-explained.md) - What is JSON-LD?

**A2A Protocol**:
- Official: https://a2aprotocol.ai/
- Linux Foundation: https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project
- Google: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/

---

## Summary

**Key Principles**:
1. ✅ All Syra schemas use JSON-LD (RDF-compatible)
2. ✅ Centralized in `src/syra/schemas/` (not scattered)
3. ✅ @context versioned separately (semantic breaking changes)
4. ✅ Dual files: JSON Schema + Example JSON-LD
5. ✅ Git commit SHA versioning (same as prompts)
6. ✅ A2A-compatible (future external agent interop)

**Migration Path**:
- **Phase 2A** (Now): Fashion extraction uses post-processing wrapper
- **Phase 2B** (Future): Update prompts to output JSON-LD natively
- **Phase 3** (Future): Enable Neo4j import + A2A external agents

**Status**: Architecture complete, @context ready, JSON schemas next
