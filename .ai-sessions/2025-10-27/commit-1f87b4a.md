# Introspection: Canonical Introspection Format - Meta-Learning Focus

**Date**: 2025-10-27
**Type**: learning
**Focus**: Establish canonical introspection format across all repos

---

## Purpose

Standardize introspection format to focus on meta-learning (not task logging).
Goal: Improve efficiency/effectiveness across Human + Bot + System components.

---

## Challenges Encountered

**Challenge 1: Format Inconsistency Across Repos**
- Syra used "What/Why/How to Prevent" format
- StyleGuru used "Challenges/Mistakes/How to Avoid" format
- Inconsistency made validation complex and learning harder to aggregate

**Time wasted**: ~10 minutes discussing which format to use

**How resolved**: User clarified - use StyleGuru format (meta-learning focused, not task logging)

---

## Mistakes Made

**Mistake 1: Implemented Syra-specific format first**
- Created validation script with Syra format before checking StyleGuru
- Should have checked both repos first to identify inconsistency
- Assumed format was consistent across repos

**Why**: Didn't verify multi-repo consistency before implementing

**Correct approach**: Check all repos → identify canonical format → implement once

---

## How to Avoid Next Time

### What Human Could Have Done Differently
- Mentioned upfront: "StyleGuru format is canonical"
- Could have pointed to StyleGuru template as reference
- Clarified focus: "Meta-learning, not task logging"

### What Bot Could Have Done Differently
- Should have checked StyleGuru format BEFORE implementing Syra format
- Pattern: For multi-repo changes → check all repos for existing patterns first
- Should have asked: "Which format is canonical?" before proceeding
- Should have read StyleGuru's `.ai-session-template.md` upfront

### What System Could Have Done Differently
- CLAUDE.md should document: "For multi-repo standards, check all repos first"
- Canonical format should live in org-standards (now fixed)
- Template should be in org-standards (now added: `.ai-session-template.md`)
- Validation script should reference canonical sections (now updated)

---

## System Improvements Made

**Added to org-standards**:
1. `.ai-session-template.md` - Canonical introspection template
   - StyleGuru format (meta-learning focused)
   - Emphasizes Human/Bot/System component learning
   - Includes guided questions for each component

2. Updated `scripts/validate-introspection.py`:
   - Check canonical sections: Challenges/Mistakes/How to Avoid
   - Updated doc strings to emphasize meta-learning focus
   - Clear purpose: improve Human + Bot + System efficiency

**Impact**:
- Single source of truth for introspection format
- Automatic propagation to all repos (via org-standards)
- Targeted learning about each component (Human/Bot/System)

---

## Related Context

- **User Feedback**: "Use StyleGuru format - for learning (human + bot)"
- **User Feedback**: "Not task log - meta-learning on efficiency/effectiveness"
- **User Feedback**: "Targeted learning about various components"
- **Files Changed**:
  - org-standards/.ai-session-template.md (created)
  - org-standards/scripts/validate-introspection.py (updated)
