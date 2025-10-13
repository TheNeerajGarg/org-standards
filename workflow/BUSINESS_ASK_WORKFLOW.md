# Business Ask Workflow

**Last Updated**: 2025-10-13
**Status**: Standard

## Workflow Structure

```
Business Ask (Container Issue)
│   - 2-3 lines high-level description
│   - Label: business-ask
│
├── Task: Create BRD → Human works with AI
│   └── BRD Document Issue
│       - Full business requirements
│       - Label: brd-ready-for-review
│       - Review Process: PM, Eng, UX bots
│       - Result: brd-approved
│
├── Task: Create PRD → PM works with AI
│   └── PRD Document Issue
│       - Product requirements
│       - Label: prd-ready-for-review
│       - Review Process: PM, Eng, UX bots
│       - Result: prd-approved
│
└── Task: Create ERD → Eng works with AI
    └── ERD Document Issue
        - Engineering design
        - Label: erd-ready-for-review
        - Review Process: PM, Eng, UX bots
        - Result: erd-approved
```

## Step-by-Step Process

### Step 1: Create Business Ask Container

**Human Action**:
```bash
gh issue create --title "Business Ask: [Feature Name]" \
  --body "High-level description (2-3 lines)" \
  --label "business-ask"
```

**Result**: Container issue created (e.g., #53)

**System Action**: Workflow creates child task "Create BRD for #53", assigns to human

---

### Step 2: Create BRD Document

**Human Action**:
1. Work with interactive AI shell to create BRD
2. Create BRD issue:
   ```bash
   gh issue create --title "BRD: [Feature Name]" \
     --body "$(cat brd.md)" \
     --label "brd-ready-for-review"
   ```
3. Link to parent: Add "Parent: #53" in issue body

**Result**: BRD document issue created (e.g., #54)

**System Action**:
- Orchestrator detects `brd-ready-for-review` label
- Creates 3 child review tasks (Eng, UX, PM)
- Bots review and post feedback
- Collator synthesizes feedback
- If approved: adds `brd-approved` label
- If needs clarification: creates human task

---

### Step 3: Address BRD Feedback (if needed)

**Human Action**:
1. Check `human-input-needed` tasks
2. Update BRD issue content with answers
3. Close human task issue

**System Action**:
- Detects BRD update
- Re-triggers review cycle
- Repeats until `brd-approved`

---

### Step 4: Create PRD Document

**Trigger**: BRD gets `brd-approved` label

**System Action**: Creates task "Create PRD for #53", assigns to PM

**PM Action**:
1. Work with AI to create PRD
2. Create PRD issue:
   ```bash
   gh issue create --title "PRD: [Feature Name]" \
     --body "$(cat prd.md)" \
     --label "prd-ready-for-review"
   ```
3. Link to parent: "Parent: #53"

**System Action**: Same review process as BRD → `prd-approved`

---

### Step 5: Create ERD Document

**Trigger**: PRD gets `prd-approved` label

**System Action**: Creates task "Create ERD for #53", assigns to Eng

**Eng Action**:
1. Work with AI to create ERD
2. Create ERD issue:
   ```bash
   gh issue create --title "ERD: [Feature Name]" \
     --body "$(cat erd.md)" \
     --label "erd-ready-for-review"
   ```
3. Link to parent: "Parent: #53"

**System Action**: Same review process → `erd-approved`

---

### Step 6: Implementation

**Trigger**: ERD gets `erd-approved` label

**System Action**: Business Ask #53 marked as `ready-for-implementation`

**Human Decision**: Assign to dev team, break into tasks, etc.

---

## Label Convention Standards

### State Labels (Applied by Humans)

**Container**:
- `business-ask` - High-level feature container

**Document Creation States**:
- `brd-ready-for-review` - BRD document ready for bot review
- `prd-ready-for-review` - PRD document ready for bot review
- `erd-ready-for-review` - ERD document ready for bot review

### Status Labels (Applied by Bots)

**Review Status**:
- `in-review` - Bots currently reviewing
- `needs-clarification` - Bot has questions, human input needed
- `brd-approved` - BRD approved by all reviewers
- `prd-approved` - PRD approved by all reviewers
- `erd-approved` - ERD approved by all reviewers
- `ready-for-implementation` - All artifacts approved

**Human Tasks**:
- `human-input-needed` - Action required from human

**Reviewer Assignment** (on child review tasks only):
- `engineering-pending` - Waiting for engineering bot
- `ux-pending` - Waiting for UX bot
- `pm-pending` - Waiting for PM bot

---

## Issue Naming Convention

**Format**: `[Type]: [Feature Name]`

**Examples**:
- Business Ask: `Business Ask: Real-time Collaboration`
- BRD: `BRD: Real-time Collaboration`
- PRD: `PRD: Real-time Collaboration`
- ERD: `ERD: Real-time Collaboration`
- Review Task: `Engineering Review: BRD Real-time Collaboration`

---

## Parent-Child Linking

**In Document Issue Body** (BRD/PRD/ERD):
```markdown
**Parent**: #53
```

**In Review Task Body**:
```markdown
**Parent BRD**: #54
**Container**: #53
```

This allows:
- Tracing from artifact back to Business Ask
- Finding all artifacts for a Business Ask
- Understanding review task context

---

## Workflow Queries

### For Humans

**My tasks**:
```bash
gh issue list --label "human-input-needed" --assignee @me
```

**Business Asks in progress**:
```bash
gh issue list --label "business-ask" --state open
```

**Documents needing my review** (if you're a reviewer):
```bash
gh issue list --label "brd-ready-for-review,prd-ready-for-review,erd-ready-for-review"
```

**Approved and ready for implementation**:
```bash
gh issue list --label "ready-for-implementation"
```

### For Bots

**Documents ready for review**:
```bash
gh issue list --label "brd-ready-for-review" --state open
gh issue list --label "prd-ready-for-review" --state open
gh issue list --label "erd-ready-for-review" --state open
```

**Review tasks for specific reviewer**:
```bash
gh issue list --label "engineering-pending,review-task" --state open
gh issue list --label "ux-pending,review-task" --state open
gh issue list --label "pm-pending,review-task" --state open
```

---

## Definition of Done: Documentation Updates

**When implementing workflow changes**:

- [ ] Update BUSINESS_ASK_WORKFLOW.md with new process
- [ ] Update CURRENT_STATE.md to reflect changes
- [ ] Update workflow YAML files in `.github/workflows/`
- [ ] Update bot code in `.workflow-poc/phase1/`
- [ ] Test complete workflow end-to-end
- [ ] Document breaking changes in CHANGELOG

**Rule**: Workflow changes are NOT done until documentation reflects current reality.

---

## Current Workflow vs Standard

### What Needs to Change

**Orchestrator** (`.github/workflows/orchestrator.yml`):
- ✅ Already accepts `business-ask` label
- ⚠️  Change: Accept `brd-ready-for-review` instead of checking for `business-ask` on BRD documents
- ⚠️  Change: Accept `prd-ready-for-review` and `erd-ready-for-review`

**Reviewer Bots** (`.github/workflows/reviewer-bots.yml`):
- ✅ Already use `engineering-pending`, `ux-pending`, `pm-pending` on review tasks
- No changes needed

**Bot Code** (`.workflow-poc/phase1/bot_reviewer_github.py`):
- Verify it looks for `*-ready-for-review` labels
- Update if using old label names

**Documentation**:
- ⚠️  Update CURRENT_STATE.md with this workflow
- ⚠️  Update HUMAN_WORKFLOW.md to reflect label changes
- ⚠️  Create this file (BUSINESS_ASK_WORKFLOW.md)

---

## Examples

### Example: Real-time Collaboration Feature

**Issue #100**: Business Ask: Real-time Collaboration
- Label: `business-ask`
- Body: "Enable multiple users to edit documents simultaneously"

**Issue #101**: BRD: Real-time Collaboration
- Label: `brd-ready-for-review`
- Body: Full BRD document + "Parent: #100"
- After review: Label becomes `brd-approved`

**Issue #105**: PRD: Real-time Collaboration
- Label: `prd-ready-for-review`
- Body: Full PRD document + "Parent: #100"
- After review: Label becomes `prd-approved`

**Issue #110**: ERD: Real-time Collaboration
- Label: `erd-ready-for-review`
- Body: Full ERD document + "Parent: #100"
- After review: Label becomes `erd-approved`

**Issue #100** updated with: `ready-for-implementation`

---

## Migration from Current V1

**Phase 1** (This Week):
1. Document current workflow (this file)
2. Define label standards
3. Update orchestrator to accept new labels
4. Keep backward compatibility with old labels

**Phase 2** (Next Week):
5. Test with new Business Ask
6. Verify all workflows trigger correctly
7. Document any issues

**Phase 3** (Following Week):
8. Remove old label support
9. Update all documentation
10. Mark as stable

---

**Status**: Standard (as of 2025-10-13)
**Next Review**: After first complete workflow test
