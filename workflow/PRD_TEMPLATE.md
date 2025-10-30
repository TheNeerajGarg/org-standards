# PRD: [Feature/Product Name]

**Date**: YYYY-MM-DD
**Author**: [Name]
**Status**: Draft | Under Review | Approved
**Type**: Product Requirements Document
**Related BRD**: [Link to BRD]
**Related ERD**: (To be created)
**Related Issue**: [GitHub Issue #XX]

---

## Abstract

**Solution Overview**: [2-3 sentences: What are we building? High-level approach]

**Key Features**: [3-5 bullet points of main features]

**Success Criteria**: [Primary metrics with targets: X → Y]

**Implementation Phases**: [Brief phase breakdown: Phase 1 (3 weeks), Phase 2 (4 weeks)]

**Document Sections** (for selective reading):
- Section 2: Deployment Environments & Repo Specifications
- Section 3: Features & Requirements
- Section 4: User Stories (with E2E test requirements)
- Section 5: Non-Functional Requirements
- Section 6: Success Metrics

---

## 1. Solution Overview

### 1.1 Solution Approach

[3-5 sentences describing the overall solution approach. What are we building to solve the business problem defined in the BRD?]

**Links to BRD Requirements**:
- BRD Requirement BR-1: [Describe how this solution addresses it]
- BRD Requirement BR-2: [Describe how this solution addresses it]
- BRD Requirement BR-3: [Describe how this solution addresses it]

### 1.2 High-Level Architecture

[Describe the solution architecture at a business/logical level. NO code, class names, or technical implementation details. Use business terminology.]

**Components**:
1. **[Component 1 Name]**: [What it does from a business perspective]
2. **[Component 2 Name]**: [What it does from a business perspective]
3. **[Component 3 Name]**: [What it does from a business perspective]

---

## 2. Deployment Environments & Repository Specifications

### 2.1 Target Deployment Environments

**CRITICAL**: This section specifies where the solution will be deployed and tested. All environments must be validated before marking this work as "Done".

#### 2.1.1 Development Environments

**Native Mac** (local development)
- **Required**: ☐ Yes ☐ No
- **Purpose**: [Why this environment is needed]
- **Test Coverage**: [What types of tests run here: unit, integration, E2E]
- **Validation Criteria**: [How we verify it works in this environment]

**Container on Mac** (Docker/Podman locally)
- **Required**: ☐ Yes ☐ No
- **Purpose**: [Why this environment is needed]
- **Test Coverage**: [What types of tests run here]
- **Validation Criteria**: [How we verify it works in this environment]

**Devcontainer** (VS Code remote containers)
- **Required**: ☐ Yes ☐ No
- **Purpose**: [Why this environment is needed]
- **Test Coverage**: [What types of tests run here]
- **Validation Criteria**: [How we verify it works in this environment]

#### 2.1.2 CI/CD Environments

**GitHub Actions**
- **Required**: ☐ Yes ☐ No
- **Purpose**: [CI/CD validation, automated testing]
- **Test Coverage**: [Full test suite, coverage requirements]
- **Validation Criteria**: [All required checks must pass before merge]
- **Required Workflows**:
  - [ ] Linting (Ruff)
  - [ ] Type checking (MyPy)
  - [ ] Unit tests (pytest)
  - [ ] Integration tests
  - [ ] E2E tests (see Section 4)
  - [ ] Coverage check (≥80%)

#### 2.1.3 Production Environments

[Add production environments if applicable: AWS, GCP, Azure, on-prem, etc.]

### 2.2 Repository Deployment Matrix

**For work in Syra/Org-standards context**: Specify which repositories this work will be deployed to.

#### 2.2.1 Repository Scope

| Repository | Deployment Required | Purpose | Priority |
|------------|-------------------|---------|----------|
| **org-standards** | ☐ Yes ☐ No | [Why: shared standards, templates, configs] | High/Medium/Low |
| **syra** | ☐ Yes ☐ No | [Why: main product repository] | High/Medium/Low |
| **StyleGuru** | ☐ Yes ☐ No | [Why: related product] | High/Medium/Low |
| **syra-playground** | ☐ Yes ☐ No | [Why: experimental features] | High/Medium/Low |
| **[Other Repo]** | ☐ Yes ☐ No | [Why: purpose] | High/Medium/Low |

#### 2.2.2 Repository-Specific Requirements

**org-standards** (if applicable):
- **Files Modified**: [List key files: config/, python/, workflow/]
- **Propagation Strategy**: [How changes propagate to other repos: submodule update, copy, template]
- **Breaking Changes**: ☐ Yes ☐ No - [If yes, describe migration path]

**syra** (if applicable):
- **Files Modified**: [List key files or modules]
- **Dependencies**: [Any new dependencies or config changes]
- **Breaking Changes**: ☐ Yes ☐ No

**StyleGuru** (if applicable):
- **Files Modified**: [List key files or modules]
- **Dependencies**: [Any new dependencies or config changes]
- **Breaking Changes**: ☐ Yes ☐ No

### 2.3 Deployment Matrix: Definition of Done

**Feature is NOT "Done" until deployed and tested in ALL required environments × repos**

**Deployment Matrix**:

| Environment | org-standards | syra | StyleGuru | syra-playground | E2E Tests |
|-------------|--------------|------|-----------|----------------|-----------|
| Native Mac | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ Pass |
| Container on Mac | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ Pass |
| GitHub Actions | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ N/A ☐ Required | ☐ Pass |

**Definition of Done Criteria** (all must be true):
- [ ] Deployed to ALL repositories marked "Required" above
- [ ] Tested in ALL environments marked "Required" above
- [ ] E2E tests pass in ALL required environments
- [ ] All user stories (Section 4) have corresponding E2E tests
- [ ] No breaking changes without migration guide
- [ ] Documentation updated for all affected repos

---

## 3. Features & Requirements

### 3.1 Feature List

**Feature F1: [Feature Name]**
- **Description**: [What this feature does from user perspective]
- **Priority**: P0 (Must Have) | P1 (Should Have) | P2 (Nice to Have)
- **Links to BRD**: Addresses BR-X, BR-Y
- **User Stories**: US-1, US-2, US-3
- **Acceptance Criteria**:
  1. [Measurable criterion 1]
  2. [Measurable criterion 2]
  3. [Measurable criterion 3]

**Feature F2: [Feature Name]**
[Same format as F1]

**Feature F3: [Feature Name]**
[Same format as F1]

[List 3-7 features. If >7 features, scope too large - split into multiple PRDs]

### 3.2 Functional Requirements

**FR-1: [Requirement Name]**
- **Description**: System must [do what]
- **Rationale**: [Why this is needed - link to BRD pain point]
- **Acceptance Criteria**: [How we verify this works]
- **Related Features**: F1, F2

**FR-2: [Requirement Name]**
[Same format as FR-1]

[List 5-15 functional requirements. Keep concise - detailed implementation in ERD]

---

## 4. User Stories (with E2E Test Requirements)

**CRITICAL**: Every user story MUST have corresponding E2E tests implemented in ALL appropriate environments.

### 4.1 User Story Template

**US-[ID]: [Story Title]**

**As a** [user role/persona]
**I want** [goal/desire]
**So that** [benefit/value]

**Acceptance Criteria**:
1. [Given/When/Then scenario 1]
2. [Given/When/Then scenario 2]
3. [Given/When/Then scenario 3]

**E2E Test Requirements** (MANDATORY):

| Environment | Test Required | Test Location | Test ID | Status |
|-------------|--------------|---------------|---------|--------|
| Native Mac | ☐ Yes ☐ No | [tests/e2e/test_us_XX.py] | E2E-US-XX-MAC | ☐ Pass ☐ Fail ☐ N/A |
| Container on Mac | ☐ Yes ☐ No | [tests/e2e/test_us_XX.py] | E2E-US-XX-CONTAINER | ☐ Pass ☐ Fail ☐ N/A |
| GitHub Actions | ☐ Yes ☐ No | [.github/workflows/e2e-tests.yml] | E2E-US-XX-GHA | ☐ Pass ☐ Fail ☐ N/A |

**E2E Test Scenarios**:
1. **Scenario 1**: [End-to-end workflow description]
   - **Setup**: [Initial state]
   - **Action**: [User action]
   - **Expected Outcome**: [What should happen]
   - **Environments**: [Which environments this scenario applies to]

2. **Scenario 2**: [End-to-end workflow description]
   [Same format as Scenario 1]

**Definition of Done for This User Story**:
- [ ] All E2E tests implemented
- [ ] E2E tests pass in ALL required environments
- [ ] Test coverage for happy path + error cases
- [ ] Test data and fixtures documented

---

### 4.2 User Story Examples

**US-1: Developer can run quality gates locally**

**As a** developer
**I want** to run quality gates on my local machine before pushing
**So that** I can fix issues immediately without waiting for CI

**Acceptance Criteria**:
1. Given I have Python 3.11+ installed
   When I run `./org-standards/python/quality_gates.py`
   Then all configured gates execute locally
2. Given a gate fails
   When I view the output
   Then I see actionable error messages with fix suggestions
3. Given I'm on a test branch
   When quality gates run
   Then coverage and type checking gates are exempted

**E2E Test Requirements**:

| Environment | Test Required | Test Location | Test ID | Status |
|-------------|--------------|---------------|---------|--------|
| Native Mac | ☑ Yes | tests/e2e/test_us_001_local_gates.py | E2E-US-001-MAC | ☐ Pass |
| Container on Mac | ☑ Yes | tests/e2e/test_us_001_local_gates.py | E2E-US-001-CONTAINER | ☐ Pass |
| GitHub Actions | ☑ Yes | .github/workflows/e2e-quality-gates.yml | E2E-US-001-GHA | ☐ Pass |

**E2E Test Scenarios**:
1. **Happy Path - All Gates Pass**:
   - Setup: Clean repo with passing code
   - Action: Run `quality_gates.py` on main branch
   - Expected: All gates pass, exit code 0
   - Environments: All (Mac, Container, GitHub Actions)

2. **Error Handling - Gate Failure**:
   - Setup: Introduce linting error
   - Action: Run quality gates
   - Expected: Linting gate fails with actionable message, exit code 1
   - Environments: All

3. **Branch-Aware - Test Branch**:
   - Setup: Switch to test/example branch
   - Action: Run quality gates
   - Expected: Coverage/type-checking skipped, only linting runs
   - Environments: All

**US-2: [Another user story]**
[Same detailed format as US-1]

[List all user stories from Section 3.1 features. Each feature may have 1-3 user stories.]

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

**NFR-P1: [Performance Requirement]**
- **Metric**: [What we measure]
- **Target**: [Baseline → Target]
- **Rationale**: [Why this target]
- **Validation**: [How we test this]
- **E2E Test Coverage**: [Which E2E tests validate this]

### 5.2 Security Requirements

**NFR-S1: [Security Requirement]**
- **Description**: [What must be secured]
- **Threat Model**: [What we're protecting against]
- **Validation**: [How we verify security]
- **E2E Test Coverage**: [Which E2E tests validate this]

### 5.3 Scalability Requirements

**NFR-SC1: [Scalability Requirement]**
- **Description**: [What must scale]
- **Target Scale**: [Current → Future]
- **Validation**: [How we test scalability]
- **E2E Test Coverage**: [Which E2E tests validate this]

### 5.4 Reliability Requirements

**NFR-R1: [Reliability Requirement]**
- **Description**: [What must be reliable]
- **Target**: [Uptime, error rate, etc.]
- **Validation**: [How we measure reliability]
- **E2E Test Coverage**: [Which E2E tests validate this]

### 5.5 Maintainability Requirements

**NFR-M1: Code Coverage**
- **Target**: ≥80% test coverage
- **Validation**: `pytest --cov=src --cov-fail-under=80`
- **Applies To**: All repositories in deployment matrix

**NFR-M2: Type Safety**
- **Target**: All new functions have type hints
- **Validation**: `mypy src/` passes with no errors
- **Applies To**: All Python code

---

## 6. Implementation Phases

### 6.1 Phase Breakdown

**Phase 1: [Phase Name]** (Time: X weeks)
- **Scope**: [What's included in this phase]
- **Features**: F1, F2
- **User Stories**: US-1, US-2, US-3
- **Deliverables**:
  - [ ] Feature F1 deployed to [repos]
  - [ ] Feature F2 deployed to [repos]
  - [ ] E2E tests for US-1, US-2, US-3 passing in all environments
  - [ ] Documentation updated
- **Success Criteria**: [How we know Phase 1 is complete]
- **E2E Tests Required**: All user stories in this phase must have E2E tests

**Phase 2: [Phase Name]** (Time: X weeks)
[Same format as Phase 1]

**Phase 3: [Phase Name]** (Time: X weeks)
[Same format as Phase 1]

### 6.2 Dependencies Between Phases

**Phase 2 depends on Phase 1**:
- [Dependency 1: Why Phase 2 can't start before Phase 1]
- [Dependency 2]

**Phase 3 depends on Phase 2**:
- [Dependency 1]
- [Dependency 2]

---

## 7. Success Metrics (Detailed)

### 7.1 Primary Metrics

**From BRD - Detailed Measurement Plan**:

**Metric M1: [Metric Name]**
- **Baseline**: [Current value]
- **Target**: [Goal value]
- **Measurement Method**: [How we collect this data]
- **Frequency**: [How often we measure]
- **Validation**: [Which E2E tests validate this metric]
- **Decision Gate**: [When we evaluate success]

**Metric M2: [Metric Name]**
[Same format as M1]

### 7.2 Secondary Metrics

**Metric M3: [Supporting Metric]**
[Same format as M1]

### 7.3 Baseline Data

[Detailed current state measurements. This is the data that was high-level in BRD.]

**Current State Analysis**:
- [Measurement 1]: [Current value with evidence]
- [Measurement 2]: [Current value with evidence]
- [Measurement 3]: [Current value with evidence]

---

## 8. Technical Constraints

### 8.1 Technology Stack

**Required Technologies**:
- [Technology 1]: [Why required, version constraints]
- [Technology 2]: [Why required, version constraints]

**Prohibited Technologies**:
- [Technology X]: [Why not allowed]
- [Technology Y]: [Why not allowed]

### 8.2 Platform Constraints

**Operating Systems**:
- macOS: [Version requirements]
- Linux: [Distribution and version requirements]
- Windows: [If applicable]

**CI/CD Platform**:
- GitHub Actions: [Runner requirements, workflow constraints]

### 8.3 Integration Constraints

**Must Integrate With**:
- [System 1]: [Integration requirements]
- [System 2]: [Integration requirements]

**Must NOT Break**:
- [Existing System 1]: [Compatibility requirements]
- [Existing System 2]: [Compatibility requirements]

---

## 9. Dependencies

### 9.1 External Dependencies

**Dependency D1: [External System/Service]**
- **Type**: Service | Library | Tool
- **Purpose**: [Why we need this]
- **Risk if Unavailable**: [Impact]
- **Mitigation**: [Backup plan]

### 9.2 Internal Dependencies

**Dependency D2: [Internal Component]**
- **Owner**: [Team/Person]
- **Status**: Available | In Development | Planned
- **Required By**: [Which phase needs this]
- **Risk**: [What happens if delayed]

---

## 10. Risks & Mitigations

### 10.1 Technical Risks

**Risk R1: [Risk Description]**
- **Likelihood**: High | Medium | Low
- **Impact**: High | Medium | Low
- **Mitigation**: [How we reduce risk]
- **Contingency**: [What we do if risk occurs]

### 10.2 Schedule Risks

**Risk R2: [Risk Description]**
[Same format as R1]

### 10.3 Integration Risks

**Risk R3: [Risk Description]**
[Same format as R1]

---

## 11. Out of Scope

**Explicitly NOT included in this PRD**:
- [Feature/capability 1] - [Why out of scope, when it might be addressed]
- [Feature/capability 2] - [Why out of scope]
- [Feature/capability 3] - [Why out of scope]

---

## 12. Open Questions

1. **[Question 1]**: [What needs to be decided? Impact on implementation?]
2. **[Question 2]**: [What needs to be decided?]
3. **[Question 3]**: [What needs to be decided?]

[Max 5-7 questions. If >7, requirements not well-defined yet.]

---

## 13. Appendix

### 13.1 References

- **BRD**: [Link to Business Requirements Document]
- **Related Issues**: [GitHub issues, Jira tickets]
- **Design Docs**: [Links to supporting design documents]
- **Meeting Notes**: [Links to decision meetings]

### 13.2 Glossary

**[Term 1]**: [Definition]
**[Term 2]**: [Definition]
**[Term 3]**: [Definition]

---

## PRD Anti-Patterns to Avoid

**Based on past failures and lessons learned**:

❌ **No E2E Test Requirements** (P-ERD-001)
- **Problem**: User stories defined without E2E test specifications
- **Impact**: Features deployed but not fully validated, bugs slip through
- **Prevention**: MANDATORY E2E test requirements table in every user story

❌ **Missing Deployment Environment Specifications** (P-ERD-002)
- **Problem**: "Works on my machine" but fails in CI/container
- **Impact**: 2-3 days debugging environment-specific issues
- **Prevention**: MANDATORY deployment matrix (Section 2.3) with all environments

❌ **Vague "All Repos" without Specifics** (P-ERD-003)
- **Problem**: "Deploy to all repos" without repo-specific requirements
- **Impact**: Breaking changes propagate, unclear testing responsibilities
- **Prevention**: Repository deployment matrix (Section 2.2) with specific requirements per repo

❌ **No Environment × Repo Matrix** (P-ERD-004)
- **Problem**: Unclear which environments are needed for which repos
- **Impact**: Incomplete testing, production failures
- **Prevention**: Deployment matrix table (Section 2.3) specifying env × repo combinations

❌ **User Stories Without E2E Scenarios** (P-ERD-005)
- **Problem**: "User can do X" without specific test scenarios
- **Impact**: Incomplete test coverage, ambiguous acceptance criteria
- **Prevention**: Every user story MUST have E2E test scenarios (Section 4)

❌ **Code Examples in PRD** (P-PRD-001)
- **Problem**: PRD includes code, class names, function signatures
- **Impact**: Violates PRD/ERD boundary, causes document bloat
- **Prevention**: Move all code to ERD (business logic only in PRD)

❌ **Missing Links to BRD** (P-PRD-002)
- **Problem**: PRD requirements don't trace back to BRD pain points
- **Impact**: Building features that don't address business problems
- **Prevention**: Every feature must link to BRD requirement (Section 3.1)

---

## PRD Checklist

**Before finalizing this PRD, verify**:

### Deployment & Testing
- [ ] All deployment environments specified (Section 2.1)
- [ ] Repository deployment matrix complete (Section 2.2)
- [ ] Deployment matrix (env × repo × E2E) filled out (Section 2.3)
- [ ] Every user story has E2E test requirements (Section 4)
- [ ] E2E test scenarios documented for each user story
- [ ] Definition of Done includes deployment criteria

### Requirements
- [ ] All features link to BRD requirements (Section 3.1)
- [ ] Functional requirements are measurable (Section 3.2)
- [ ] Non-functional requirements have validation criteria (Section 5)
- [ ] Success metrics are detailed with baselines (Section 7)

### Scope & Boundaries
- [ ] Implementation phases are realistic (Section 6)
- [ ] Out of scope items documented (Section 11)
- [ ] Dependencies identified with owners (Section 9)
- [ ] Risks assessed with mitigations (Section 10)

### Quality
- [ ] NO code examples (move to ERD if present)
- [ ] NO implementation details (move to ERD if present)
- [ ] Anti-patterns section present
- [ ] Document size <300 lines (or justified if larger)

---

**PRD Complete**
**Status**: [Draft | Under Review | Approved]
**Line Count**: [X lines] ([acceptable | needs compression])
**Next**: Create ERD after PRD approval
