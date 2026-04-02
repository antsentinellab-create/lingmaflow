## 1. Brainstorming Skill Content

- [x] 1.1 Create YAML frontmatter for brainstorming (name, version, triggers, priority: high)
- [x] 1.2 Write core principles section (clarify requirements before implementation)
- [x] 1.3 Write questioning techniques section (guide users to clarify goals)
- [x] 1.4 Write design options analysis section (trade-offs and decisions)
- [x] 1.5 Add workflow checklist (proposal.md before implementation)

## 2. Writing Plans Skill Content

- [x] 2.1 Create YAML frontmatter for writing-plans (name, version, triggers, priority: high)
- [x] 2.2 Write task breakdown principles (2-5 minutes per task)
- [x] 2.3 Write done condition definition guidelines
- [x] 2.4 Write progress tracking with checkbox syntax
- [x] 2.5 Add storage convention (docs/plans/YYYY-MM-DD-<name>.md)

## 3. Test-Driven Development Skill Content

- [x] 3.1 Create YAML frontmatter for test-driven-development (name, version, triggers, priority: high)
- [x] 3.2 Write RED-GREEN-REFACTOR cycle explanation
- [x] 3.3 Write TDD disciplines (write failing test first)
- [x] 3.4 Add forbidden practices (no tests-after-code)
- [x] 3.5 Include example workflow

## 4. Systematic Debugging Skill Content

- [x] 4.1 Create YAML frontmatter for systematic-debugging (name, version, triggers, priority: normal)
- [x] 4.2 Write problem reproduction steps
- [x] 4.3 Write error message reading guidelines
- [x] 4.4 Write scope reduction techniques
- [x] 4.5 Add verification after fix (tests must pass)

## 5. Subagent-Driven Skill Content

- [x] 5.1 Create YAML frontmatter for subagent-driven (name, version, triggers, priority: normal)
- [x] 5.2 Write TASK_STATE.md reading procedure
- [x] 5.3 Write task completion update workflow
- [x] 5.4 Write done condition checking (all must be met before advancing)
- [x] 5.5 Add BLOCKED handling (stop and wait)

## 6. Validation and Testing

- [x] 6.1 Run `lingmaflow skill list` and verify 5 skills shown
- [x] 6.2 Run `lingmaflow skill find brainstorm` and verify matching
- [x] 6.3 Run `lingmaflow skill find pytest` and verify matching
- [x] 6.4 Run `lingmaflow agents generate --force` and verify all skills included
- [x] 6.5 Verify all YAML frontmatter is parseable by SkillRegistry.scan()

## 7. Documentation Update

- [x] 7.1 Update TASK_STATE.md to PHASE-3-done
- [x] 7.2 Verify done conditions: 5 SKILL.md files exist with content
- [x] 7.3 Prepare for openspec-archive-change
