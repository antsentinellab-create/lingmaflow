## 1. README Structure Update

- [x] 1.1 Read current README.md content
- [x] 1.2 Backup original README.md
- [x] 1.3 Create new structure with 8 sections

## 2. Project Title & Problems Solved

- [x] 2.1 Write bilingual project title (LingmaFlow — Agentic development framework)
- [x] 2.2 Document three problems solved:
  - Agent gets lost after interruption
  - Cross-session progress disappears
  - Done conditions cannot be auto-verified

## 3. Installation Section

- [x] 3.1 Write git clone command
- [x] 3.2 Write pip install -e ".[dev]" command
- [x] 3.3 Add Python version requirement (3.11+)

## 4. CLI Commands Reference

- [x] 4.1 Document Task Management commands:
  - init / status / advance / block / resolve
- [x] 4.2 Document Skill commands:
  - skill list / skill find <keyword>
- [x] 4.3 Document AGENTS.md command:
  - agents generate
- [x] 4.4 Document Execution Engine commands:
  - prepare / verify / checkpoint
- [x] 4.5 Format as table with descriptions

## 5. Standard Workflow Section

- [x] 5.1 Write Step 1: lingmaflow init
- [x] 5.2 Write Step 2: lingmaflow prepare (generate task brief)
- [x] 5.3 Write Step 3: [Agent execution]
- [x] 5.4 Write Step 4: lingmaflow verify (check done conditions)
- [x] 5.5 Write Step 5: lingmaflow checkpoint (advance step)
- [x] 5.6 Add complete workflow example with output

## 6. Done Conditions Format

- [x] 6.1 Document file:PATH type with example
- [x] 6.2 Document pytest:PATH type with example
- [x] 6.3 Document func:MODULE.CLASS type with example
- [x] 6.4 Add markdown checkbox syntax explanation
- [x] 6.5 Explain verification mechanism

## 7. Architecture Section

- [x] 7.1 List core modules:
  - core/task_state.py
  - core/skill_registry.py
  - core/agents_injector.py
  - core/condition_checker.py
  - cli/lingmaflow.py
  - skills/*/SKILL.md
- [x] 7.2 Add one-line description for each module
- [x] 7.3 Include architecture diagram (optional)

## 8. Testing & License Sections

- [x] 8.1 Update test count to 153 tests
- [x] 8.2 Add pytest tests/ -v command
- [x] 8.3 Add MIT License section
- [x] 8.4 Add badge for test status (optional)

## 9. Review and Validation

- [ ] 9.1 Verify all links are working
- [ ] 9.2 Test all code examples are executable
- [ ] 9.3 Check bilingual consistency
- [ ] 9.4 Verify formatting matches existing style
- [ ] 9.5 Final proofread
