# Planning Checklist

**Purpose**: Token-efficient planning that validates problem-solution fit BEFORE detailed design

**When to Use**: Before creating ANY implementation plan (BRD, PRD, ERD) for non-trivial work (>5 lines of code)

**Token Budget**: Aim for <10K tokens in planning phase (outline + validation)

---

## Phase 1: Understanding (Before Solutions)

**Goal**: Understand the problem WITHOUT proposing solutions yet

### 1.1 Problem Validation

**Ask these questions** (capture user's exact words):

- ❓ **Pain Point**: What is the actual frustration/blocker?
  - Not: "What needs to be built?"
  - But: "What behavior are you trying to change?"

- ❓ **Current Behavior**: What do users do now?
  - Example: "Developers use `--no-verify` to bypass pre-commit"

- ❓ **Why That Behavior**: What drives current behavior?
  - Human factors: Incentives, frustration, time pressure
  - Technical factors: Speed, complexity, reliability
  - **Critical**: Technical root cause ≠ Actual pain point

- ❓ **Desired Behavior**: What should users do instead?
  - Example: "Developers commit frequently without bypassing checks"

### 1.2 Success Criteria

**Define measurable outcomes**:

- What changes in behavior would indicate success?
- What metrics would validate the solution works?
- What timeline is realistic?

### 1.3 Stakeholder Context

**Who is affected**:

- Primary users (who experiences the pain?)
- Secondary stakeholders (who else is impacted?)
- Decision makers (who approves the approach?)

---

## Phase 2: Solution Design (After Validation)

**Goal**: Explore solutions that address the validated problem

### 2.1 Outline-First Approach (Token Efficiency)

**BEFORE writing detailed plans**:

1. **Draft 3-5 sentence outline** of proposed direction:
   ```
   Example:
   "The root cause is attribution (developers can't tell which failures
   are theirs). Solution: baseline enforcement (ratcheting) that allows
   pre-existing failures but blocks new ones. Combine with civic duty
   system where issues are filed but don't block commits."
   ```

2. **Present to user** for direction confirmation

3. **Wait for approval** before elaborating

4. **Benefits**:
   - Catches wrong directions in <1K tokens
   - Prevents 40-50K token waste on detailed plans
   - Allows user to correct misunderstandings early

**Example from Oct 17-18 incident**:
- ❌ Without outline: 15K tokens on marker plan before realizing wrong direction
- ✅ With outline: Would have caught in <1K tokens that speed wasn't the problem

### 2.2 Solution Options

**If multiple approaches exist**:

- Present 2-3 options as brief summaries (not detailed designs)
- Include trade-offs for each
- Recommend one with rationale
- Let user choose before elaborating

### 2.3 Problem-Solution Fit Validation

**Before detailed design, verify**:

- ✅ Will this solution change the behavior identified in Phase 1?
- ✅ Does it address human factors (not just technical factors)?
- ✅ Is the investment justified by the pain level?
- ✅ Have we validated assumptions (not just accepted them)?

**Red Flags** (stop and re-validate):
- "Users will just need to adapt" (ignores human factors)
- "This is best practice" (cargo cult, not validated for context)
- "It's technically correct" (but doesn't address actual pain)
- "We'll enforce with tooling" (workaround for behavioral issue)

---

## Phase 3: Expert Review (If Complex)

**When to involve experts**:

- Solution affects core architecture
- High investment (>10 hours)
- High risk (security, data loss, production impact)
- Multiple conflicting approaches exist

### 3.1 Expert Prompt Structure

**Token-efficient expert consultation**:

1. **Context** (2-3 sentences):
   - What is the problem (validated pain point)
   - What solution is proposed (outline)

2. **Specific Question** (not open-ended):
   - ❌ Bad: "Review this plan"
   - ✅ Good: "Will baseline enforcement prevent `--no-verify` usage?"

3. **Constraints** (if any):
   - Budget, timeline, existing architecture

4. **Expected Output**:
   - Specific deliverable (not general commentary)
   - Example: "Identify risks and suggest mitigation"

### 3.2 Expert Conflict Resolution

**If experts disagree**:

- Create comparison table (point-by-point)
- Identify where they agree (common ground)
- Analyze WHY they disagree (different assumptions?)
- Recommend approach with rationale
- Present to user for final decision

**Example from Oct 17-18 incident**:
- Principal Engineer: Fast markers (3.5h)
- Test Architect: Infrastructure first (15h)
- Resolution: Test Architect's deeper analysis won (found pytest.ini already had 12 markers)

---

## Phase 4: Checkpoint (Before Execution)

**Before starting implementation**:

### 4.1 Documentation Requirements

**Create checkpoint document** if:

- Session approaching token limit (>40K used)
- Complex multi-phase plan
- User requests pause/resume capability

**Checkpoint must include**:

- Problem statement (validated pain point)
- Solution summary (outline)
- Architectural decisions (with rationale)
- What we're NOT doing (and why)
- File structure (where code will live)
- Success metrics
- Next steps

### 4.2 Context Preservation

**Update LATEST_CONTEXT.md** if:

- Major architectural decisions made
- File structure changes planned
- New patterns/standards established

### 4.3 Final Pre-Flight Check

**Before writing code**:

- [ ] Problem validated with user
- [ ] Solution addresses the actual pain point
- [ ] Outline approved by user
- [ ] Expert reviews complete (if needed)
- [ ] Token budget reasonable (<50K for implementation)
- [ ] Success criteria defined
- [ ] Checkpoint created (if complex)

---

## Anti-Patterns (What NOT to Do)

### Anti-Pattern 1: Solution-First Thinking

❌ **Bad Flow**:
1. User mentions problem
2. Immediately propose solution
3. Write detailed plan
4. User says "that doesn't address the real issue"

✅ **Good Flow**:
1. User mentions problem
2. Ask clarifying questions (Phase 1)
3. Validate pain point
4. Present outline (Phase 2.1)
5. Get approval, THEN elaborate

### Anti-Pattern 2: Expert Opinion as Gospel

❌ **Bad**: "Expert said X, so we must do X"

✅ **Good**: "Expert said X because of assumption Y. Let's validate Y first."

**Example from Oct 17-18**: Distinguished Software Engineer claimed "$91 incident not documented" → Verified against CSV → Found $98.87 WAS documented

### Anti-Pattern 3: Technical Correctness ≠ Right Solution

❌ **Bad**: "Adding markers is technically correct best practice"

✅ **Good**: "Will markers prevent developers from using `--no-verify`? No, because the problem is attribution, not categorization."

### Anti-Pattern 4: Open-Ended Expert Prompts

❌ **Bad**: "Review this 40-page ERD" (costs 30K tokens)

✅ **Good**: "Does the baseline enforcement approach prevent collective punishment?" (costs 5K tokens)

### Anti-Pattern 5: Skipping Outline Approval

❌ **Bad**: User says "fix the tests" → Write 20-page marker plan → Wrong direction

✅ **Good**: User says "fix the tests" → Ask "why are developers bypassing?" → 3-sentence outline → Approve → Elaborate

---

## Token Efficiency Guidelines

**Target budgets by phase**:

- Phase 1 (Understanding): 2-5K tokens
  - Ask questions, capture exact words, validate pain point

- Phase 2 (Solution Design): 3-5K tokens
  - Outline (1K) + approval + elaboration (2-4K)

- Phase 3 (Expert Review): 5-10K per expert
  - Specific questions, not open-ended reviews

- Phase 4 (Checkpoint): 2-3K tokens
  - Summary, not full transcript

**Total Planning Target**: <20K tokens

**Implementation Target**: <30K tokens

**Session Target**: <50K total

---

## Examples from Oct 17-18 Incident

### What Happened (Token Inefficient)

```
1. User: "We had cascading test failures" (Oct 17-18)
2. AI: Read base class, found missing markers
3. AI: Created detailed 29-hour marker plan (15K tokens)
4. User: "Speed isn't the problem, attribution is"
5. AI: Pivoted to new solution
6. AI: Got expert reviews (60K tokens)
7. User: "This still doesn't address token efficiency"
8. AI: Created token optimizer bot plan (20K tokens)

Total: 120K tokens used
```

### What Should Have Happened (Token Efficient)

```
1. User: "We had cascading test failures" (Oct 17-18)
2. AI: "What is the pain point? Speed or something else?" (validate)
3. User: "Developers bypass because 'not my problem'"
4. AI: "Outline: Baseline enforcement (allow pre-existing failures,
   block new ones) + civic duty (file issues, don't block). Proceed?" (1K)
5. User: "Yes, but also think about token efficiency"
6. AI: "Add token optimizer bot for batching mechanical fixes. Proceed?" (1K)
7. User: "Yes"
8. AI: Create detailed plan (10K)
9. AI: Implement (20K)

Total: 35K tokens used
```

**Savings**: 85K tokens (71% reduction) by validating problem first and using outline-first approach

---

## Lessons from Oct 17-18 Session

### What Worked Well

1. **Root cause validation**: Checked if shared state was actually the problem (it wasn't)
2. **Expert reviews**: Got deeper analysis from Test Architect vs Principal Engineer
3. **Pivoting when corrected**: User said "attribution not speed" → immediately pivoted
4. **Checkpoint creation**: Preserved 120K token context for resumption
5. **Self-introspection**: Analyzed what went wrong to prevent future waste

### What Didn't Work Well

1. **False start on markers**: 15K tokens before validating if speed was the actual problem
2. **Open-ended expert prompts**: 30K tokens per expert (could have been 5K with specific questions)
3. **No outline approval**: Jumped to detailed plans without direction confirmation
4. **Late token optimization consideration**: Should have been part of initial planning
5. **Trusted expert claims without verification**: "$91 not documented" → was actually documented

### Key Insight

> "When someone fixes one test and breaks another, it is the problem of **not having a full plan**"
> - User feedback that reframed entire approach

**The real problem wasn't technical (markers, speed, shared state)**

**The real problem was process (lack of planning, no attribution, collective punishment)**

---

## When to Use This Checklist

### MUST Use (Required)

- Any BRD, PRD, or ERD creation
- Significant architecture decisions (>10 hours investment)
- User reports repeated pain point
- Previous solution attempts failed

### SHOULD Use (Recommended)

- Non-trivial features (>5 lines of code)
- Refactoring that affects multiple components
- Process improvements
- Quality gate changes

### MAY Skip (Optional)

- User says "skip the docs"
- Emergency hotfix (<1 hour)
- Trivial changes (typo fixes, formatting)
- Following existing documented pattern

### NEVER Skip (Always Required)

- Phase 1 problem validation (even for small tasks)
- Outline-first approach (when >10K token plan expected)
- Expert review conflict resolution (when experts disagree)

---

## Summary

**The One Rule**: Validate the problem BEFORE designing the solution

**The One Technique**: Outline-first (3-5 sentences) before elaboration

**The One Metric**: Token efficiency (planning <20K, total <50K)

**The One Question**: "Will this solution change the behavior we identified in Phase 1?"
