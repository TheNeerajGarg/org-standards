# BRD/PRD/ERD Standards

## Abstract

**Purpose**: Define strict boundaries, size limits, and structure for requirements documents to prevent bloat and maintain focus. All documents MUST have 10% abstract at top so readers can decide if they need to read further.

**Key Rules**:
- **BRD**: <2 pages (~100 lines), business problem only, NO solution
- **PRD**: <6 pages (~300 lines), requirements only, NO code
- **ERD**: Detailed technical design with code
- **ALL docs**: Start with abstract (<10% of doc), clear sections for selective reading

---

## CRITICAL: Abstract Requirement (ALL Documents)

**EVERY document MUST start with an Abstract section (<10% of total doc)**

**Purpose**: Allow readers to decide if they need to read further and which sections to read.

**Abstract Requirements**:
- **Length**: <10% of document (BRD: 10 lines, PRD: 30 lines, ERD: 100 lines)
- **Content**: Problem/solution summary, key decisions, sections guide
- **Format**:
  ```markdown
  ## Abstract

  **Problem**: [1 sentence]
  **Solution**: [2-3 sentences]
  **Key Decisions**: [3-5 bullets]
  **Document Sections**: [List sections for selective reading]
  ```

**Agent Behavior**:
1. Read abstract first
2. Decide if full doc needed
3. If yes, read only relevant sections
4. NEVER read entire doc unless abstract unclear

---

## Document Scope Boundaries (CRITICAL - Prevents BRD Creep)

**Problem**: BRDs grow to 2000+ lines with ERD-level detail, violating document boundaries.

**Solution**: Strict size limits and content boundaries.

### Size Targets (STRICT)

| Document | Max Lines | Max Pages | Purpose |
|----------|-----------|-----------|---------|
| BRD | 100 | 2 | Business problem - "Why?" NO SOLUTION |
| PRD | 300 | 6 | Requirements - "What?" NO CODE |
| ERD | 1000 | 20 | Technical design - "How?" CODE OK |

**Red Flags**:
- BRD > 2 pages → STOP. Move content to PRD.
- PRD > 6 pages → STOP. Move content to ERD.
- PRD has code → STOP. Move to ERD.
- BRD mentions solution → STOP. Pure problem only.

### BRD: Business Requirements Document (<2 pages, ~100 lines)

**Purpose**: Answer "Why should we build this?" Business problem ONLY.

**MANDATORY Structure**:
1. **Abstract** (10 lines max) - Problem, impact, success criteria
2. **Customer & Problem** - Who is customer, current workarounds, success quote (NEW - see template)
3. **Problem Validation** - Problem-solution fit BEFORE any design (CRITICAL - see below)
4. **Business Problem** - What's broken? Evidence?
5. **Business Impact** - Cost of not solving? Revenue opportunity?
6. **Success Criteria** - How do we know it worked? (metrics only, business outcomes)
7. **Business Context** - Stakeholders, constraints
8. **Out of Scope** - What we're NOT doing
9. **Assumptions** - Explicit assumptions with confidence scores (minimum 5-10)

**Target Line Count**: 120-150 lines (complex problems may need up to 180, but >200 is a red flag)

**Problem Validation (CRITICAL - Must Come FIRST)**:

**Before writing ANY BRD, validate the problem** using [planning-checklist.md](planning-checklist.md):

**Step 1: Capture Pain Point** (user's exact words)
- ❓ What is the actual frustration/blocker?
- ❓ What behavior needs to change?
- ❓ Why do users behave the current way?

**Step 2: Distinguish Technical Root Cause from Actual Pain**
- Technical root cause: The measurable symptom (e.g., "tests take 2 min")
- Actual pain point: The frustration driving behavior (e.g., "developers feel punished for others' bugs")
- **Critical**: Solving technical root cause may NOT solve actual pain

**Step 3: Human Factors Analysis**
- Incentives: What motivates current behavior?
- Frustration: What causes users to work around the system?
- Time pressure: Are shortcuts taken due to deadlines?
- Attribution: Can users tell if problem is "their fault"?

**Example from Oct 17-18 incident**:
```
❌ Technical Root Cause: "Tests take 2 minutes, too slow"
   → Proposed Solution: pytest-xdist for parallel execution
   → Problem: Doesn't address why developers use `--no-verify`

✅ Actual Pain Point: "Developers bypass quality gates because they feel
   punished for 42 pre-existing failures they didn't cause ('not my problem')"
   → Proposed Solution: Baseline enforcement (allow pre-existing, block new)
   + civic duty system (file issues, don't block commits)
   → Result: Addresses attribution and collective punishment
```

**Red Flags** (stop and re-validate):
- "Users will just need to adapt" → Ignoring human factors
- "This is best practice" → Cargo cult without validation
- "It's technically correct" → May not address actual pain
- "We'll enforce with tooling" → Workaround for behavioral issue

**MUST be in BRD** ✅:
- Business pain points with evidence
- Impact (cost/revenue)
- Success metrics
- Stakeholder needs

**MUST NOT be in BRD** ❌:
- **NO SOLUTION** - Not even high-level ("we'll build X" is solution)
- **NO "DESIRED WORKFLOW"** - Specifies how solution should work (move to PRD user stories)
- **NO ARCHITECTURE** - Zero technical details
- **NO IMPLEMENTATION** - No task breakdowns
- **NO TEST STRATEGY**
- **NO API DESIGN**
- **NO CODE**
- **NO SCENARIOS** - "Current vs Desired Workflow" walkthroughs → PRD user stories
- **NO TECHNICAL ROOT CAUSES in detail** - Business impact only, tech details in PRD/ERD
- **NO FUNCTIONAL REQUIREMENTS** - "System must do X" → PRD
- API cost calculations (token-level math) → **PRD** (high-level only in BRD)
- Code examples, file paths, schemas → **ERD**
- Validation task plans → **PRD**
- Phase task lists with hour estimates → **PRD/ERD**
- Retry logic, timeouts, config values → **ERD**

**Common BRD Bloat Patterns** (DELETE these, move to PRD):
- ❌ Step-by-step workflow walkthroughs ("First developer does X, then Y...")
- ❌ "Desired Workflow" or "Ideal State" sections (solution thinking)
- ❌ Detailed baseline metrics tables (keep high-level in BRD, details in PRD)
- ❌ Root cause analysis with technical details (keep "what hurts", move "why technically" to PRD)
- ❌ Solution hints in success criteria ("hash stability", "incremental validation" are solutions)
- ❌ "Questions for Decision" planning sections (move to PRD)

---

### BRD Template (Copy This)

```markdown
# BRD: [Problem Name]

**Date**: YYYY-MM-DD
**Author**: [Name]
**Status**: Draft | Under Review | Approved
**Type**: Business Requirements Document
**Related**: [GitHub Issue #XX]
**PRD**: (To be created)

---

## Abstract

**Problem**: [1-2 sentences: What's broken? What behavior are we seeing?]

**Business Impact**: [1-2 sentences: Cost/revenue impact, velocity tax, morale issues]

**Success Criteria**: [1 sentence: Primary metrics baseline → target]

**Scope**: [1 sentence: Which projects/products affected]

---

## Customer & Problem

### Who is the Customer?

**INSTRUCTIONS**:
- If multiple customers: Use "Customer 1", "Customer 2" format below
- If single customer: Use "Primary" / "Secondary" format
- If zero customers (internal improvement): Use "Internal Stakeholder" and skip to "What's Wrong with Current Approach"

**Customer 1: [Customer Type/Role]**
- **Role**: [Who is this person/system? What do they do?]
- **Context**: [What environment/constraints do they operate in?]
- **Pain**: [What specific pain do they experience from this problem?]

**Customer 2: [Customer Type/Role]** (if applicable)
- **Role**: [Same format as Customer 1]
- **Context**: [Same format]
- **Pain**: [Same format]

[Add Customer 3, 4, etc. if needed. If >4 customers with different pains, scope is too broad]

**Common Profile Across Customers** (if multiple customers):
- [Key characteristic shared by all: constraints, context, motivations]
- [Another shared characteristic]

**OR (if single customer)**:

**Primary**: [Who is directly experiencing this problem? Be specific about role, context]
**Secondary**: [Who else is affected indirectly?]

**Customer Profile**:
- [Key characteristic 1: constraints, context, motivations]
- [Key characteristic 2]
- [Key characteristic 3]

**OR (if internal improvement only, no external customers)**:

**Internal Stakeholder**: [Team/role affected]
**Context**: [Why this matters internally: efficiency, maintenance, quality]
**Note**: This is an internal improvement - no external customer impact. Skip "Problem from Customer Perspective" and "Success Quote" sections.

### Problem from Customer Perspective

**INSTRUCTIONS**: If zero customers (internal improvement), skip this subsection.

**Customer says**: "[Direct quote or paraphrase of customer frustration in their words]"

**What they're trying to do**: [What outcome are they trying to achieve?]

**If multiple customers**: List each customer's perspective:
- **Customer 1 says**: "[Quote]"
- **Customer 2 says**: "[Quote]"
- **Common goal**: [What all customers are trying to achieve]

### How They're Doing It Today

**Current Workaround #1**: [How they currently solve/avoid the problem]
- Frequency: [How often? X% of time, Y times per day]
- Why they do it: [Root motivation for this workaround]
- Problems: [What's wrong with this workaround? Cost/impact?]

**Current Workaround #2**: [Second workaround if applicable]
- Frequency: [How often?]
- Why they do it: [Motivation]
- Problems: [What's wrong?]

[Add 2-4 workarounds total. If customers have >4 workarounds, problem is poorly scoped]

### What's Wrong with Current Approach

**From Customer Perspective**:
1. **[Pain Point 1]**: [Why this hurts from customer view, not technical view]
2. **[Pain Point 2]**: [Same format]
3. **[Pain Point 3]**: [Same format]
4. **[Pain Point 4]**: [Same format]

**Business Impact**: [High-level cost/revenue/morale impact]

### What Customer Will Say When Problem is Solved

**INSTRUCTIONS**:
- If zero customers (internal improvement): Skip this subsection, use metrics in Success Criteria section instead
- If multiple customers: Provide success quote for each OR a unified quote

**Success Quote** (target - what customer will say after solution):
> "[Verbatim quote from customer describing successful outcome. Make it specific, concrete, emotional. This is your north star.]"

**If multiple customers**:
- **Customer 1 quote**: "[Their success statement]"
- **Customer 2 quote**: "[Their success statement]"
- **OR Unified quote**: "[Combined success statement that represents all customers]"

**Behavior Change**:
- [Specific behavior that will change: metric before → after]
- [Another behavior change with metric]
- [Sentiment change: what they'll say/feel]

---

## Problem Validation

### Pain Point (User's Exact Words)

"[User quote describing frustration/blocker]"

### Technical Root Cause vs Actual Pain

**Technical Root Causes**:
- [Technical symptom 1]
- [Technical symptom 2]

**Actual Pain Points** (human factors):
- **Attribution**: [Who/what is blamed? "Not my problem" mentality?]
- **Collective punishment**: [Forced to fix others' issues?]
- **Lack of control**: [Can't predict outcomes?]
- **Time pressure**: [Deadlines causing shortcuts?]

**Critical Distinction**: Solving technical root cause may NOT solve actual pain if [reason].

### Human Factors Analysis

**Incentives**: [What motivates current behavior? Speed vs quality?]
**Frustration**: [What causes workarounds? Unpredictability? Forced context switching?]
**Time Pressure**: [Are shortcuts due to limited time/resources?]
**Attribution**: [Can users tell "my fault" vs "pre-existing"?]

---

## Business Problem

### Problem 1: [Name] ([Impact Metric])

[2-3 sentences describing pain, frequency, business impact. NO workflow walkthroughs. Focus on "what hurts" not "why technically".]

**Impact**: [Quantified: X% slower, $Y lost, Z incidents per month]

### Problem 2: [Name] ([Impact Metric])

[Same format as Problem 1]

[Add 3-5 problems total. If >5 problems, scope is too large - split into multiple BRDs]

---

## Business Impact

**[Impact Category 1]**: [1-2 sentences with metrics]

**[Impact Category 2]**: [1-2 sentences with metrics]

**Strategic Risk**: [How does this affect product/company strategy?]

**Revenue Impact**: [If applicable: delays, churn, opportunity cost]

---

## Success Criteria

**Primary Metrics** (baseline → target):
- [Metric 1]: [X] → [Y]
- [Metric 2]: [X] → [Y]
- [Metric 3]: [X] → [Y]
- [Metric 4]: [X] → [Y]
- [Metric 5]: [X] → [Y]

**Secondary Metrics**:
- [Qualitative or supporting metrics]

(Detailed baseline data and methodology in PRD Section 2: Current State)

---

## Business Context

### Why This Matters for [Product/Team]

**[Product] Mission**: [1 sentence]
**Impact on Product**: [2-3 sentences tying problem to product success/failure]

### Stakeholders

**Primary**: [Who is directly affected? Their needs?]
**Secondary**: [Who is indirectly affected?]

**Priority**: [If conflict arises between stakeholder needs, who wins?]

---

## Constraints

**Must Preserve**:
- [What we can't compromise on]
- [Core values/quality bars]

**Cannot Change**:
- [External constraints: processes, systems, regulations]

**Must Avoid**:
- [What would make problem worse]

---

## Out of Scope

**Not Solving** (separate problems, out of scope for this effort):
- [Problem/feature 1] - [Why out of scope]
- [Problem/feature 2] - [Why out of scope]

---

## Assumptions

**A1**: [Assumption statement]
**Confidence**: [0-100]% ([reasoning for confidence level])
**Validation Needed**: [How to verify this assumption]
**Risk if Wrong**: [What happens if assumption is false]

**A2**: [Same format for 5-10 assumptions total]

[List minimum 5-10 explicit assumptions. If you have <5, you're missing hidden assumptions.]

---

## Questions for Decision

1. **[Question 1]**: [What needs to be decided? What are the options?]
2. **[Question 2]**: [Same format]
3. **[Question 3]**: [Same format]

[Max 3-5 questions. If >5 questions, problem not well-defined yet.]

---

## Related Context

- **Issue**: [GitHub/Jira link]
- **Baseline Data**: [Link to detailed analysis]
- **Detailed Content**: [Link to PRD parking lot if applicable]
- **Review Feedback**: [Link to review consolidation]

---

## Next Steps

1. ✅ **[Completed step]** (YYYY-MM-DD): [What was done]
2. **[Next step]**: [What needs to happen]
3. **[Future step]**: [What comes after]

---

**BRD Complete**
**Status**: [Draft | Under Review | Approved]
**Line Count**: [X lines] ([X]× target of 100, [acceptable | needs compression])
**Next**: [What happens next: user review, PRD, etc.]
```

**Template Notes**:
- Target 120-150 lines total (with Customer section)
- Abstract should be ~10 lines (10% of document)
- Customer & Problem section should be ~40 lines (critical for customer empathy)
- Each problem should be 3-5 lines (compress, no workflows)
- Assumptions section mandatory (5-10 assumptions minimum)
- NO solution content anywhere (test: could you swap solutions and BRD still works?)
- Success Quote is your north star - everything should lead to making that quote real

---

### PRD: Product Requirements Document (<6 pages, ~300 lines)

**Purpose**: Answer "What are we building?" Requirements ONLY. NO CODE.

**Template**: [workflow/PRD_TEMPLATE.md](../workflow/PRD_TEMPLATE.md)

**MANDATORY Structure**:
1. **Abstract** (30 lines max) - Solution overview, features, phases
2. **Deployment Environments & Repository Specifications** - Where it will be deployed and tested
3. **Features & Requirements** - What must it do?
4. **User Stories (with E2E Test Requirements)** - Who needs what? How will we test end-to-end?
5. **Non-Functional Requirements** - Performance, scale, security
6. **Implementation Phases** - What's in each phase?
7. **Success Metrics** - Detailed metrics with targets

**CRITICAL - Deployment & Testing Requirements**:
- **Deployment Environments**: Specify Native Mac, Container on Mac, GitHub Actions, etc.
- **Repository Matrix**: For Syra/Org-standards work, specify which repos (org-standards, syra, StyleGuru, syra-playground)
- **E2E Test Requirements**: EVERY user story MUST have E2E test requirements for ALL appropriate environments
- **Deployment Matrix**: Environment × Repo × E2E Tests matrix required (see PRD template Section 2.3)

**MUST be in PRD** ✅:
- Feature descriptions (business terms)
- Requirements (functional + non-functional)
- User stories **WITH E2E test requirements**
- Success metrics
- Phases and scope
- **Deployment environment specifications**
- **Repository deployment matrix**
- **E2E test scenarios for each user story**

**MUST NOT be in PRD** ❌:
- **NO CODE** - Zero code examples
- **NO FILE PATHS** - No src/foo/bar.py
- **NO CLASS NAMES** - No FooValidator
- **NO FUNCTION SIGNATURES** - No def foo(x: int)
- **NO ALGORITHMS** - No implementation details
- **NO CONFIG VALUES** - No timeout=300s
- **NO TEST CASES** - Move to ERD (but E2E test requirements OK)

### ERD: Engineering Requirements Document (~1000 lines max)

**Purpose**: Answer "How do we build it?" Detailed technical design. CODE OK.

**MANDATORY Structure**:
1. **Abstract** (100 lines max) - Architecture, components, approach, risks
2. **Architecture** - Components, data flow, APIs
3. **Data Models** - Schemas, database design
4. **Implementation Tasks** - High-level breakdown (6-12 hour chunks)
5. **Testing Strategy** - Unit, integration, **E2E (CRITICAL)**
6. **E2E Test Implementation Plan** - MANDATORY mapping from PRD user stories to tests
7. **Error Handling** - Retry logic, timeouts
8. **Configuration** - File paths, env vars
9. **Deployment & Rollback** - How to deploy to all required environments × repos

**Note**: For complex ERDs (>3 components or >8 hours), create a separate **Execution Plan** after ERD approval. See [.claude/execution-plan-standards.md](.claude/execution-plan-standards.md).

**CRITICAL - E2E Test Requirements (From PRD)**:
- **EVERY user story in the PRD MUST have E2E tests implemented**
- **E2E tests must run in ALL appropriate environments** (Native Mac, Container, GitHub Actions)
- **E2E tests must validate deployment in ALL required repos** (org-standards, syra, StyleGuru, etc.)
- **ERD must include a mapping table**: PRD User Story → E2E Test Implementation → Test Files → Environments

**Example E2E Test Mapping Table** (MANDATORY in Section 6):
```markdown
## 6. E2E Test Implementation Plan

**CRITICAL**: This section maps all PRD user stories to E2E test implementations.

| PRD User Story | E2E Test ID | Test File Location | Environments | Repos | Status |
|----------------|-------------|-------------------|--------------|-------|--------|
| US-1: Developer can run quality gates locally | E2E-US-001 | tests/e2e/test_quality_gates_local.py | Native Mac, Container, GHA | org-standards, syra | ☐ Implemented |
| US-2: Workflow changes skip coverage gates | E2E-US-002 | tests/e2e/test_branch_policies.py | Native Mac, Container, GHA | org-standards, syra, StyleGuru | ☐ Implemented |
| US-3: Emergency bypass tracked and logged | E2E-US-003 | tests/e2e/test_emergency_bypass.py | Native Mac, Container, GHA | org-standards, syra | ☐ Implemented |

**E2E Test Details**:

### E2E-US-001: Developer can run quality gates locally

**Scenarios**:
1. **Happy Path**: All gates pass
   - Setup: Clean repo with passing code
   - Test: Run quality_gates.py on main branch
   - Verify: All gates execute, exit code 0
   - Environments: Native Mac, Container on Mac, GitHub Actions
   - Repos: org-standards (primary), syra (propagation test)

2. **Error Handling**: Gate failure with actionable message
   - Setup: Introduce linting error
   - Test: Run quality_gates.py
   - Verify: Linting gate fails with fix suggestion, exit code 1
   - Environments: All

3. **Branch Awareness**: Test branch exemptions
   - Setup: Switch to test/example branch
   - Test: Run quality_gates.py
   - Verify: Coverage/type-checking skipped
   - Environments: All

**Implementation**:
\`\`\`python
# tests/e2e/test_quality_gates_local.py

def test_us001_happy_path_all_gates_pass():
    """E2E-US-001 Scenario 1: All gates pass on main branch"""
    # Test implementation
    pass

def test_us001_gate_failure_actionable_message():
    """E2E-US-001 Scenario 2: Gate failure with clear error"""
    # Test implementation
    pass

def test_us001_branch_awareness_test_branch():
    """E2E-US-001 Scenario 3: Test branch exemptions work"""
    # Test implementation
    pass
\`\`\`
```

**MUST be in ERD** ✅:
- Code examples
- File paths, class names
- Config values (timeout=300s)
- Algorithms and implementation details
- Test cases
- API specifications
- Specific test cases with expected values
- Technical algorithms
- Retry logic with backoff strategies
- Database schemas with field types
- API endpoint specifications
- **E2E test implementation plan with mapping from PRD user stories**
- **Test files, scenarios, and implementation details for ALL PRD user stories**
- **Deployment instructions for all required environments × repos**

### Stop-Check Questions Before Adding Content

Before adding ANY section to a document, ask:

1. **For BRD**: "Would a CFO or executive need this to approve the project?"
   - If NO → Move to PRD or ERD

2. **For PRD**: "Is this about WHAT we're building or HOW we build it?"
   - If HOW → Move to ERD

3. **For ERD**: "Is this implementation detail or product feature?"
   - If product feature → Move to PRD

4. **Size Check**: "Does this push document over size target?"
   - BRD approaching 800 lines → Stop, move content to PRD
   - PRD approaching 1500 lines → Stop, move content to ERD

### Quality Bot Integration

**Update bot prompts to check document scope**:

**CompletenessBot** - Check required sections per doc type:
- BRD: Flag if missing business context, problem statement, stakeholders
- PRD: Flag if missing features, phases, budget breakdown
- ERD: Flag if missing architecture, test strategy, implementation tasks

**SimplicityBot** - Flag excessive detail for doc type:
- BRD: Flag ERD-level detail (file paths, config values, test cases, code examples)
- PRD: Flag ERD-level detail (class names, retry logic, algorithms)
- ERD: No limits on technical detail (this is where it belongs)

**DecompositionBot** - Flag task breakdowns in wrong document:
- BRD: Flag ANY task breakdowns (hours/days)
- PRD: Flag task breakdowns <12 hours (too granular, belongs in ERD)
- ERD: Expect 6-12 hour task chunks

---

## BRD Planning Anti-Patterns (Learned from Oct 17-18 Incident)

**Purpose**: Prevent token waste and wrong-direction planning based on $197 token spike analysis.

### Anti-Pattern #1: Solution-First Thinking

**Pattern**: User mentions problem → AI immediately proposes solution → writes detailed plan → user says "wrong direction"

**Example from Oct 17-18**:
```
User: "We had cascading test failures"
AI: Creates 29-hour marker implementation plan (15K tokens)
User: "Speed isn't the problem, attribution is"
Result: 15K tokens wasted on wrong direction
```

**Why It Happens**:
- AI pattern-matches to technical solutions
- Skips problem validation phase
- Assumes technical root cause = actual pain point

**Prevention**:
- ✅ Ask clarifying questions FIRST (Phase 1 of planning-checklist.md)
- ✅ Present 3-5 sentence outline before elaborating
- ✅ Validate pain point matches proposed solution

**Token Impact**: 15K tokens wasted → Could have caught in <1K with outline-first

### Anti-Pattern #2: Technical Root Cause ≠ Pain Point

**Pattern**: Focus on measurable technical symptom instead of actual frustration driving behavior

**Example from Oct 17-18**:
```
❌ Technical Root Cause: "Tests take 2 minutes"
   Solution: pytest-xdist (parallel execution)
   Problem: Doesn't stop developers from using `--no-verify`

✅ Actual Pain Point: "Developers feel punished by 42 pre-existing failures ('not my problem')"
   Solution: Baseline enforcement + attribution
   Result: Addresses the behavior-driving frustration
```

**Why It Happens**:
- Technical problems are easier to measure
- Human factors (frustration, incentives) are harder to quantify
- "Best practice" cargo cult without context validation

**Prevention**:
- ✅ Ask "Why do users behave this way?" (human factors)
- ✅ Distinguish symptom from cause
- ✅ Validate: "Will this solution change the behavior?"

**Token Impact**: 60K tokens on expert reviews for wrong problem

### Anti-Pattern #3: Open-Ended Expert Prompts

**Pattern**: Ask expert to "review this plan" without specific questions → 30K tokens of general commentary

**Example from Oct 17-18**:
```
❌ Bad Prompt: "Review this 29-hour marker implementation ERD"
   Result: 30K tokens per expert (60K total)
   Value: Found critical issues BUT token-inefficient

✅ Good Prompt: "Does baseline enforcement prevent `--no-verify` usage better than markers?"
   Expected: 5K tokens with focused answer
   Value: Same critical findings, 6× more efficient
```

**Why It Happens**:
- No specific question = expert reviews everything
- Large context = higher token cost
- Open-ended prompts encourage elaboration

**Prevention**:
- ✅ Ask specific questions, not "review everything"
- ✅ Provide 2-3 sentence context, not full ERD
- ✅ Request specific deliverable (e.g., "identify risks")

**Token Impact**: 60K tokens → Could have been 10K with focused prompts (6× savings)

### Anti-Pattern #4: Skipping Outline Approval

**Pattern**: Jump directly to detailed plan without direction confirmation

**Example from Oct 17-18**:
```
Without outline:
- Create marker plan (15K tokens)
- User corrects direction
- Create new plan (20K tokens)
- Total: 35K tokens for planning

With outline:
- Present 3-sentence outline (1K tokens)
- User confirms direction
- Elaborate (10K tokens)
- Total: 11K tokens for planning
```

**Prevention**:
- ✅ Always present outline FIRST (3-5 sentences)
- ✅ Wait for user approval before elaborating
- ✅ Saves 40-50K tokens when direction is wrong

**Token Impact**: 24K tokens saved per wrong direction (68% reduction)

### Anti-Pattern #5: Expert Opinion as Gospel

**Pattern**: Trust expert claims without independent validation

**Example from Oct 17-18**:
```
Distinguished Software Engineer: "$91 incident not documented"
AI: Trusted claim without verification
Reality: Checked CSV file → $98.87 WAS documented

Result: Made wrong assumptions based on unverified expert opinion
```

**Prevention**:
- ✅ Verify expert claims against primary sources
- ✅ Check CSV files, code, git history
- ✅ If experts conflict, compare assumptions

**Token Impact**: Prevented bad architectural decision based on false assumption

### Anti-Pattern #6: No Token Budget

**Pattern**: Create detailed plans without token efficiency consideration

**Example from Oct 17-18**:
```
Session without budget:
- Marker plan: 15K
- Expert reviews: 60K
- Pivot: 20K
- New plan: 25K
- Total: 120K tokens

Session with budget:
- Target: <50K total
- Forces outline-first approach
- Specific expert questions
- Would have saved 70K tokens (58% reduction)
```

**Prevention**:
- ✅ Set token budget upfront (<50K per session)
- ✅ Planning phase <20K, implementation <30K
- ✅ Stop and checkpoint if approaching limit

**Token Impact**: 70K tokens saved (58% reduction) with upfront budgeting

### Anti-Pattern #7: Hypothesis Stated as Fact

**Pattern**: Claim something is true without validation (related to ERD anti-patterns but applies to BRD too)

**Example**:
```
❌ Bad: "Markers will prevent cascading failures"
   (Stated as fact without validation)

✅ Good: "HYPOTHESIS: Markers may help categorize tests, but won't prevent
   developers from using `--no-verify` if they feel 'not my problem'.
   Need to validate if speed or attribution is the pain point."
```

**Prevention**:
- ✅ Prefix unvalidated claims with "HYPOTHESIS:"
- ✅ Add validation plan for each hypothesis
- ✅ Distinguish proven facts from assumptions

**Token Impact**: Prevents building wrong solution (saves entire implementation cost)

---

## MANDATORY: BRD/PRD/ERD Anti-Patterns Requirements

**When documenting requirements in BRDs, PRDs, or ERDs, you MUST include BOTH positive and negative requirements.**

### Required Structure for Requirements Documents

Every BRD/PRD/ERD must include:

1. **Positive Requirements** (what to do)
   - Clear, actionable requirements
   - Measurable success criteria
   - Implementation guidance

2. **Anti-Patterns to Avoid** (what NOT to do) ⚠️ **CRITICAL**
   - Based on past pain/failures
   - Why these patterns are harmful
   - How to recognize them
   - Link to Problem Registry IDs

3. **Link Requirements to Root Causes**
   - Show WHY each requirement exists
   - Reference specific past problems
   - Connect solutions to root causes

### Example Structure

```markdown
### Requirement BR-X: Testing Requirements

**Positive Requirements**:
1. ✅ Integration tests cover all critical paths
2. ✅ Mock external dependencies ONLY (not internal logic)
3. ✅ Coverage ≥80%
4. ✅ 70/20/10 split (unit/integration/system)

**Anti-Patterns to Avoid** (learned from past pain):
- ❌ **Excessive mocking** (P-001) - Mocking internal business logic defeats test purpose
  - Tests pass but code fails in production
  - 3-4 days wasted per incident
  - **Prevention**: Mock APIs/databases/file system ONLY, never validators/domain models
- ❌ **100% unit tests** (P-002) - No integration tests misses component interaction bugs
  - Unit tests pass, integration fails
  - 25% sprint capacity lost to rework
  - **Prevention**: Require 20% integration tests minimum
- ❌ **Tests verify mocks** (P-003) - Testing that mocks were called, not actual behavior
  - False confidence in test suite
  - Bugs slip through
  - **Prevention**: Tests must verify business logic outcomes

**Why These Requirements** (link to root causes):
- **Problem**: P-001, P-002, P-003 (see Problem Registry)
- **Root Cause**: Over-reliance on mocked unit tests without integration
- **Solution**: 70/20/10 strategy + mock external only
- **Prevents**: 3-4 day waste from false positive tests
```

### BRD/PRD Checklist Template

**Use this template before finalizing any BRD/PRD/ERD**:
- [.workflow-poc/templates/BRD-CHECKLIST.md](.workflow-poc/templates/BRD-CHECKLIST.md)

The checklist ensures:
- ✅ Anti-patterns section included
- ✅ Requirements linked to root causes
- ✅ Problem Registry referenced
- ✅ Context files updated (LATEST_CONTEXT.md, PROBLEM_REGISTRY.md)

### Common Anti-Pattern Categories

**Testing Anti-Patterns** (reference P-001, P-002, P-003):
- ❌ Excessive mocking of internal logic
- ❌ No integration tests
- ❌ Testing mock calls instead of behavior

**AI Safety Anti-Patterns** (reference P-004, P-005):
- ❌ Bulk modifications without validation
- ❌ No pre-execution approval gates
- ❌ AI bypassing quality gates

**Documentation Anti-Patterns** (reference D-001, D-002):
- ❌ No Definition of Done
- ❌ Missing anti-patterns in requirements
- ❌ Requirements not linked to root causes

**Process Anti-Patterns** (reference PR-001):
- ❌ Skipping BRD→PRD→ERD for significant work
- ❌ Claiming "done" without DoD verification

### Why Anti-Patterns Matter

**Problem**: When BRDs only list positive requirements ("do this"), teams repeat known mistakes.

**Example Failure**:
- BRD says: "Implement comprehensive test coverage"
- Team implements: 100% unit test coverage with extensive mocking
- Result: Tests pass, code fails in production (P-001, P-002)
- **What was missing**: Anti-pattern guidance ("DON'T mock internal logic")

**Solution**: Explicitly document what NOT to do, with links to past failures.

### References

- **Problem Registry**: [.ai-sessions/PROBLEM_REGISTRY.md](.ai-sessions/PROBLEM_REGISTRY.md)
- **Latest Context**: [.ai-sessions/LATEST_CONTEXT.md](.ai-sessions/LATEST_CONTEXT.md)
- **BRD Checklist**: [.workflow-poc/templates/BRD-CHECKLIST.md](.workflow-poc/templates/BRD-CHECKLIST.md)

## MANDATORY: ERD Pre-Flight Checklist

**Before finalizing ANY ERD, you MUST complete this 40-item checklist.**

**Purpose**: Prevent the 7 common ERD failure modes identified in introspection analysis (Oct 2025).

### Section 1: Context Validation (CRITICAL - Prevents Issue #4)

**Re-read CLAUDE.md sections AFTER writing each ERD section**:
- [ ] Re-read workflow context: single human + bot swarm, optimization targets
- [ ] Re-read Architecture Principles: "Simple over sophisticated", SRP, separation of concerns
- [ ] Re-read this checklist before claiming ERD is complete

**Context Applied Section (MANDATORY)**:
- [ ] ERD includes "## Context Applied" section
- [ ] Lists 3-5 CLAUDE.md principles used in this ERD
- [ ] For each principle: Quote from CLAUDE.md → How you applied it
- [ ] Verification: Optimization targets match CLAUDE.md priorities (calendar time + review bandwidth, NOT just API cost)

**Example Format**:
```markdown
## Context Applied

1. **Optimization Target** (workflow.md): "Bottleneck: Neeraj's review bandwidth (30-60 min/week)"
   → Applied: Designed stateless components for easy queue migration (reduces review cycles)

2. **Simple Over Sophisticated**: "No over-engineering"
   → Applied: Phase 1 uses batch processing (simple), deferred queues to Phase 2

3. **Separation of Concerns**: Single Responsibility Principle
   → Applied: File I/O abstraction separate from Batch Orchestrator
```

### Section 2: Assumptions and Questions (CRITICAL - Prevents Issues #1, #3, #6)

**Assumptions Made Section (MANDATORY)**:
- [ ] ERD includes "## Assumptions Made (Human Must Validate)" section
- [ ] Lists 10+ assumptions made while writing ERD
- [ ] For each assumption: Confidence score (1-10), Why didn't ask, Validation needed?
- [ ] Flagged all assumptions with confidence <7/10 for human validation
- [ ] **BEFORE flagging as needs validation**: Search project history for existing validation (see guidance below)

**Assumption Validation: Search Before Flagging** (Prevents re-asking validated questions):

When reviewing assumptions with confidence <7/10:

1. **Search for existing validation** before flagging as blocker:
   ```bash
   grep -r "{assumption topic}" .ai-sessions/
   grep -r "{assumption topic}" {project}/bots/
   grep -r "{assumption topic}" {project}/*.md
   ```

2. **If validation found**:
   - Update confidence score (e.g., 4/10 → 9/10)
   - Cite source: "Validated in Phase 0.5 (see {file})"
   - Don't flag as needs validation

3. **If no validation found**:
   - Then flag as needs human validation
   - Document search performed (show you looked)

**Example**:
```
❌ WRONG: "Headless Claude unvalidated (4/10)" → Flag as blocker
         (Didn't search for validation)

✅ RIGHT: Search finds "Phase 0.5 validated Headless Claude"
         → Update: "Headless Claude available (9/10) - Validated Phase 0.5"
```

**Why**: Prevents re-asking humans for information already validated in project history.

**Example Format**:
```markdown
## Assumptions Made (Human Must Validate)

| Assumption | Confidence | Why I Didn't Ask | Validation Needed? |
|------------|-----------|------------------|-------------------|
| LLM uses totality of evidence (not most reliable source) | 5/10 | Pattern-matched to ML approach | ✅ Yes - Critical design decision |
| Support OpenAI, Anthropic, Google only | 6/10 | Assumed "big three" providers | ✅ Yes - Budget impacts choice |
| Batch Orchestrator handles file I/O + batching | 7/10 | Common pattern | ⚠️ Maybe - Could separate |
| Budget enforcement needed in Phase 1 | 4/10 | Seemed complete | ✅ Yes - Adds complexity |
```

**Questions for Clarification Section (MANDATORY)**:
- [ ] ERD includes "## Questions for Clarification" section
- [ ] Lists 5-10 questions you would ask if you could pause now
- [ ] Questions cover: architecture decisions, phasing, provider choices, optimization targets

**Example Questions**:
```markdown
## Questions for Clarification

1. **Multi-Source Aggregation**: Does LLM pick "most reliable source" or synthesize from all sources?
2. **Provider Selection**: Should we support Hugging Face for cost optimization ($500 budget)?
3. **Debug Mode**: Do you need per-artifact extractions for debugging, or combined only?
4. **Optimization Target**: Confirm priority: calendar time > review bandwidth > API cost?
5. **Evolution Path**: What's the roadmap: Files → Browser Plugin → URL?
```

### Section 3: Hypothesis vs Fact (CRITICAL - Prevents Issue #2)

**Hypothesis Tagging (MANDATORY)**:
- [ ] Reviewed all claims/rationales in ERD
- [ ] Marked hypotheses with "HYPOTHESIS:" prefix
- [ ] Marked facts with "VALIDATED:" or citation
- [ ] Marked assumptions with "ASSUMPTION:" prefix
- [ ] No claims stated as facts without evidence

**Example Tagging**:
```markdown
❌ WRONG: "LLM is smarter than custom algorithms"
✅ CORRECT: "HYPOTHESIS: LLM may handle aggregation better than custom algorithms - we want to see how far LLM can go and will revisit based on Week 3 pilot results. VALIDATION PLAN: Manual review of 50 products, success threshold >80% accuracy."

❌ WRONG: "Multi-threading provides better performance"
✅ CORRECT: "VALIDATED: Python asyncio provides 4-8× throughput for I/O-bound tasks [Python docs]. For 500 products, expected time: 15 min (parallel) vs 60 min (sequential)."
```

**Validation Plan for Each Hypothesis**:
- [ ] For each "HYPOTHESIS:", added validation plan
- [ ] Validation plan includes: What we'll measure, Success criteria, Decision gate (when?)
- [ ] Identified experiments needed to validate hypotheses

### Section 4: Complexity Check - Phase 1 vs Future (CRITICAL - Prevents Issue #7)

**Phase Filtering (MANDATORY)**:
- [ ] For each component/feature, tagged as "Phase 1" or "Future"
- [ ] Applied "Is this needed for Week 3 pilot?" filter
- [ ] Removed over-engineering (moved to "Future" phase)
- [ ] For multi-threaded features, considered race conditions and complexity

**Phase 1 vs Future Table (MANDATORY)**:
```markdown
## Phase 1 vs Future Breakdown

| Component/Feature | Phase 1? | Rationale | If Deferred, When? |
|-------------------|---------|-----------|-------------------|
| Budget tracking (logging) | ✅ Phase 1 | Need to monitor spend | N/A |
| Budget enforcement (blocking) | ❌ Future | Multi-threading complexity, provider limits sufficient | Phase 2 (if needed) |
| Combined extraction | ✅ Phase 1 | Core functionality | N/A |
| Per-artifact extraction (debug) | ⚠️ Phase 1 (optional) | Helps debugging but expensive | Always available but default off |
```

**Simplicity Check**:
- [ ] Each component has ≤2 responsibilities (if >2, split it)
- [ ] No features added that aren't in PRD scope
- [ ] Applied "Simple over sophisticated" principle
- [ ] Questioned large buffers or "just in case" features

### Section 5: Architecture Questions (Prevents Issues #1, #5, #6)

**Multi-Source Systems**:
- [ ] How does system aggregate multi-source data? (Pick one? Synthesize all?)
- [ ] What's the aggregation strategy? (Max confidence? Agreement? Totality of evidence?)
- [ ] Does LLM receive sources sequentially or simultaneously?

**Input/Output Format**:
- [ ] What's the exact input format? (Single file? Batch? Set of related files?)
- [ ] How are related inputs grouped? (Directory structure? Prefix? Metadata?)
- [ ] Does order matter in inputs?
- [ ] What's the output schema? (Composition of component schemas?)

**Evolution Path**:
- [ ] What's the evolution: Current phase → 6 months → 1 year → 2 years?
- [ ] What downstream consumers exist? (Browser plugin? Crawler? API?)
- [ ] How will system change over time?

**Logging and Improvement**:
- [ ] What should we log for continuous improvement? (Provider, model, params, prompt version)
- [ ] How will we A/B test? (Need correlation IDs? Multiple extraction runs?)
- [ ] What experimentation is needed?

### Section 6: Provider Questions (Prevents Issue #3)

**Provider Selection**:
- [ ] What's the budget constraint? How does it affect provider choice?
- [ ] Should we support open-source providers? (Hugging Face, Ollama)
- [ ] Cost hierarchy: Which providers cheapest → most expensive?
- [ ] Fallback strategy: If budget runs low, what's the backup?

### Section 7: Component Design (Prevents Issue #6)

**Single Responsibility Principle**:
- [ ] Listed each component's responsibilities (aim for 1, max 2)
- [ ] If >2 responsibilities, split into separate components
- [ ] Will other components need this functionality? (Reusability check)

**Example Check**:
```
Component: Batch Orchestrator
Responsibilities: 1) File I/O, 2) Parallelism, 3) Progress tracking
Status: ❌ Too many (3 responsibilities)
Fix: Split File I/O into separate abstraction layer
```

**Component Boundaries**:
- [ ] Which component owns which data?
- [ ] Can components evolve independently?
- [ ] Are external schemas referenced (not embedded)?

### Section 8: Schema Design (Prevents 10 schema issues)

**IF ERD includes data schemas, answer these**:

**Entity IDs**:
- [ ] Do we need dual IDs? (Internal DB key + External correlation ID)
- [ ] Will we run multiple extractions on same entity with different configs? (If yes → Need external ID)

**Artifact Organization**:
- [ ] How are multiple files grouped for a single entity? (Directory? Prefix?)
- [ ] What's the file system organization strategy?
- [ ] Who constructs artifact IDs? (Batch Orchestrator? File I/O layer?)

**Schema Composition**:
- [ ] Is this schema composed of multiple component schemas?
- [ ] Marked composition: `_schema_composition: ["schema1", "schema2"]`
- [ ] Clear ownership: Which component owns which data?

**Operational Modes**:
- [ ] Do we need debug mode (per-artifact) vs production mode (combined only)?
- [ ] How do we control API costs? (Debug mode = expensive, production = cheap)
- [ ] What traceability needed? (Evidence arrays? Provenance?)

**Type System**:
- [ ] Are all attribute values strings? Or numbers/arrays too?
- [ ] Checked taxonomy for attribute types?
- [ ] Type validation strategy?

**External References**:
- [ ] Are external schemas embedded or referenced?
- [ ] If referenced, how do we version? (taxonomy_version, judge_schema_version)
- [ ] Can external schemas evolve independently?

**Evidence and Traceability**:
- [ ] For each attribute value, can we trace which artifacts supported it?
- [ ] Evidence array format: `[{artifact_id, confidence}, ...]`
- [ ] Overall confidence calculation?

### Section 8A: E2E Test Implementation (CRITICAL - MANDATORY)

**E2E Test Mapping from PRD** (MANDATORY - Feature NOT complete without this):
- [ ] Listed ALL user stories from PRD
- [ ] For each user story: Created E2E test ID (E2E-US-XXX format)
- [ ] For each user story: Specified test file location (tests/e2e/test_*.py)
- [ ] For each user story: Listed all environments where test must run (Native Mac, Container, GHA)
- [ ] For each user story: Listed all repos where test must pass (org-standards, syra, StyleGuru, etc.)
- [ ] Created E2E test mapping table (see ERD template Section 6 for format)

**E2E Test Scenarios**:
- [ ] For each E2E test: Documented 2-5 test scenarios (happy path, error cases, edge cases)
- [ ] For each scenario: Specified setup, action, expected outcome
- [ ] For each scenario: Listed which environments apply
- [ ] For each scenario: Included verification criteria

**E2E Test Implementation Details**:
- [ ] For each E2E test: Provided code skeleton or pseudocode
- [ ] For each E2E test: Specified test data/fixtures needed
- [ ] For each E2E test: Documented dependencies (other tests, external services)
- [ ] For each E2E test: Estimated execution time

**Deployment Matrix Integration**:
- [ ] Created deployment matrix: Environment × Repo × E2E Tests
- [ ] For each cell: Specified if test is required (☑ Required) or not applicable (☐ N/A)
- [ ] Verified ALL PRD user stories covered in matrix
- [ ] Verified matrix matches PRD Section 2.3 deployment matrix

**Example Checklist Items**:
```markdown
✅ US-1 mapped to E2E-US-001
✅ E2E-US-001 test file: tests/e2e/test_quality_gates_local.py
✅ E2E-US-001 environments: Native Mac, Container on Mac, GitHub Actions
✅ E2E-US-001 repos: org-standards, syra
✅ E2E-US-001 scenarios documented (3 scenarios: happy path, error handling, branch awareness)
✅ E2E-US-001 implementation skeleton provided
```

### Section 9: Optimization Targets (CRITICAL - Prevents Issue #4)

**Verify Optimization Priorities**:
- [ ] Primary optimization: Calendar time (weeks to complete)
- [ ] Secondary: Neeraj's review bandwidth (30-60 min/week)
- [ ] Tertiary: AI API cost (within budget constraint)
- [ ] NOT optimizing for: Team coordination, engineering capacity (no team!)

**Design Decisions Align with Priorities**:
- [ ] Stateless components (enables queue migration → reduces calendar time)
- [ ] Simple over sophisticated (reduces review time)
- [ ] Clear decision gates (respects review bandwidth)
- [ ] Budget tracking, not enforcement (simplicity)

### Section 10: Self-Review Questions

**Before finalizing ERD, ask yourself**:
- [ ] Did I re-read CLAUDE.md after each section? (Context application)
- [ ] Did I surface all assumptions? (10+ listed with confidence)
- [ ] Did I mark hypotheses? (No claims as facts without evidence)
- [ ] Did I filter Phase 1 vs Future? (Each feature tagged)
- [ ] Did I check component responsibilities? (≤2 per component)
- [ ] Did I ask about evolution? (6-month, 1-year roadmap)
- [ ] Did I verify optimization targets? (Match CLAUDE.md priorities)
- [ ] Did I list questions for clarification? (5-10 questions)

### Section 11: ERD Anti-Patterns to Avoid

**The 7 Common Failures** (from Oct 2025 introspection):

❌ **Over-Engineering** (Issue #7): Adding features not in PRD scope
- Fix: Tag everything as "Phase 1" or "Future" - be explicit
- Ask: "Is this needed for Week 3 pilot?"

❌ **No Clarifying Questions** (Issues #1, #3, #6): Filling gaps with assumptions
- Fix: List 5-10 questions you'd ask if you could stop now
- Ask: "What am I assuming that I should validate?"

❌ **Reading Context But Not Applying** (Issue #4): Instructions exist but not used
- Fix: Re-read CLAUDE.md after each section, add "Context Applied" section
- Ask: "Did I optimize for the right variables?"

❌ **Hypotheses Stated as Facts** (Issue #2): "LLM is smarter" vs "LLM may be smarter"
- Fix: Prefix with "HYPOTHESIS:" and add validation strategy
- Ask: "Is this proven or to be validated?"

❌ **No Evolution Thinking** (Issue #5): Designing for current scope only
- Fix: Add "Future Evolution" section for each component
- Ask: "What comes next? Browser plugin? Database migration?"

❌ **Over-Bundled Responsibilities** (Issue #6): Components doing 3+ things
- Fix: Apply Single Responsibility Principle (SRP)
- Ask: "Should file I/O be separate from orchestration?"

❌ **Missing Provider Options** (Issue #3): Only big three (OpenAI, Anthropic, Google)
- Fix: Consider budget constraints → Open-source providers
- Ask: "What's the cost hierarchy? Need Hugging Face?"

**The 10 Schema Failures** (from Oct 2025 introspection):

❌ **Single ID** (need dual: internal + external for correlation)
❌ **No artifact organization** (grouping strategy for multi-file products)
❌ **Monolithic schema** (should be composed of component schemas)
❌ **No debug mode** (per-artifact extractions for troubleshooting)
❌ **Embedded taxonomy** (should reference with version)
❌ **No evidence array** (can't trace which artifacts support each value)
❌ **Embedded judge schema** (should reference separate component)
❌ **Taxonomy suggestions in wrong component** (belongs to Taxonomy Improver)
❌ **Prompt improvements in LLM output** (needs human judgment, not LLM's job)
❌ **String-only values** (check taxonomy for numbers, arrays)

### Confidence Scoring

**For each major design decision, include**:
```markdown
### Decision: [Description]

**Confidence**: X/10

**Rationale**: [Why this approach]

**What Could Go Wrong**: [Risks]

**Validation Plan**: [How we'll know if this works]

**Decision Gate**: [When we decide if this was right]
```

**If confidence <7/10 → Flag for human validation before proceeding**

### Completion Criteria

**ERD is NOT complete until**:
- [ ] All 40+ checklist items verified (including Section 8A: E2E Test Implementation)
- [ ] "Context Applied" section present (3-5 principles)
- [ ] "Assumptions Made" section present (10+ assumptions)
- [ ] "Questions for Clarification" section present (5-10 questions)
- [ ] All hypotheses marked with "HYPOTHESIS:" + validation plan
- [ ] Phase 1 vs Future tagged for all components
- [ ] Optimization targets verified against CLAUDE.md
- [ ] Anti-patterns section present (what NOT to do)
- [ ] Low confidence decisions (<7/10) flagged for human review
- [ ] **E2E Test Implementation Plan complete** (CRITICAL):
  - [ ] E2E test mapping table created (all PRD user stories → E2E tests)
  - [ ] E2E test scenarios documented for each user story (2-5 scenarios per story)
  - [ ] E2E test implementation details provided (code skeletons, test data)
  - [ ] Deployment matrix: Environment × Repo × E2E Tests specified
  - [ ] All PRD user stories have corresponding E2E tests
- [ ] **Deployment & Rollback Plan complete**:
  - [ ] Deployment instructions for ALL required environments (Native Mac, Container, GitHub Actions)
  - [ ] Deployment instructions for ALL required repos (org-standards, syra, StyleGuru, etc.)
  - [ ] Rollback procedure documented with specific commands
  - [ ] Success criteria for deployment verification

**Present to human as DRAFT with questions, NOT as final ERD**

---

## Execution Plans: From ERD to Implementation

**Purpose**: After ERD approval, create detailed execution plans for complex implementations.

**When to create Execution Plans**:
- ✅ Complex ERDs (>3 components or >8 hours estimated)
- ✅ Multi-phase implementations
- ✅ High-risk changes (database, auth, payment)
- ✅ Migrations (data, architecture, dependencies)
- ❌ Simple bug fixes (<1 hour)
- ❌ Single-file changes
- ❌ Documentation-only updates

**What Execution Plans provide**:
- **Granular tasks**: <4 hour chunks with clear deliverables
- **Phase breakdown**: Time estimates per phase
- **Bash commands**: Copy-paste ready, no placeholders
- **Validation steps**: How to verify each step succeeded
- **Dependencies**: Explicit prerequisites and parallel opportunities
- **Rollback plans**: How to undo if things go wrong
- **Success criteria**: Measurable go/no-go checklist

**Workflow**:
1. **BRD** → Why build this? (business problem)
2. **PRD** → What to build? (requirements)
3. **ERD** → How to build? (technical design)
4. **Execution Plan** → Step-by-step implementation (detailed tasks)
5. **Implementation** → Execute tasks from plan

**Key Difference**:

| ERD | Execution Plan |
|-----|----------------|
| Architecture decisions | Step-by-step bash commands |
| Component design | Validation commands + expected output |
| High-level approach (6-12h tasks) | Granular tasks (<4 hours) |
| "We'll use X pattern" | "Run this command to implement X" |
| Risk identification | Risk mitigation with rollback steps |

**Example**: [marker-implementation-plan.md](../.ai-sessions/2025-10-22/marker-implementation-plan.md) - marked 1,428 tests in 2.5 hours with 96% accuracy

**Full Standard**: [.claude/execution-plan-standards.md](.claude/execution-plan-standards.md)
