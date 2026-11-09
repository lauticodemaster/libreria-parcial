# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

See `_shared/skill-resolver.md` for the full resolution protocol.

Project: libreria-parcial (FastAPI async + SQLModel + SQLAlchemy 2 async + asyncpg + PostgreSQL 16 + Docker; Strict TDD). Recommended-but-not-installed skills (fastapi, fastapi-templates, python-testing-patterns, postgresql-table-design, postgresql-code-review, python-pro) are in .active-orchestrator-state.json under skills.recommended.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| build features / fix bugs test-first, red-green-refactor, integration tests | tdd | .claude/skills/tdd/SKILL.md |
| implement / continue tasks of an OpenSpec change ("opsx apply") | openspec-apply-change | .claude/skills/openspec-apply-change/SKILL.md |
| archive a completed change ("opsx archive") | openspec-archive-change | .claude/skills/openspec-archive-change/SKILL.md |
| think/investigate before a change ("opsx explore") | openspec-explore | .claude/skills/openspec-explore/SKILL.md |
| create a change with all artifacts ("opsx propose") | openspec-propose | .claude/skills/openspec-propose/SKILL.md |
| sync delta specs to main specs without archiving | openspec-sync-specs | .claude/skills/openspec-sync-specs/SKILL.md |
| revise planning artifacts of an existing change | openspec-update-change | .claude/skills/openspec-update-change/SKILL.md |
| run the Discovery phase before kb-creator (11-point checklist) | discovery-research | .claude/skills/discovery-research/SKILL.md |
| research a competitor from a URL (invoked by discovery-research) | web-scraper | .claude/skills/web-scraper/SKILL.md |
| create/generate knowledge base | kb-creator | .claude/skills/kb-creator/SKILL.md |
| generate CHANGES.md roadmap | roadmap-generator | .claude/skills/roadmap-generator/SKILL.md |
| generate AGENTS.md / CLAUDE.md | agents-md-generator | .claude/skills/agents-md-generator/SKILL.md |
| find/install skills | find-skills | .claude/skills/find-skills/SKILL.md |

Not applicable to this project (Android/Kotlin, video, replica packs, humanizer, skill-creator, testing-setup) are intentionally omitted.

Todas las skills viven en el proyecto (`.claude/skills/`); `skills-lock.json` registra el repo de origen y la huella de cada una. Para restaurarlas: `npx skills experimental_install`.

## Compact Rules

Pre-digested rules per skill. Delegators copy matching blocks into sub-agent prompts as `## Project Standards (auto-resolved)`.

### tdd
- Red before green: write the failing test first, then only enough code to pass; no speculative features.
- One vertical slice at a time (one seam, one test, one minimal impl); never write all tests first.
- Test behavior through public interfaces (HTTP endpoints / service API), not internals; tests must survive refactors.
- Agree the seams under test before writing tests (state them with a one-line note on what each catches/misses).
- Avoid anti-patterns: mocking internal collaborators, querying the DB as a side channel, tautological asserts (expected value recomputed like the code).
- Expected values come from independent sources (literals, spec scenarios).
- Refactoring belongs to review stage, not the red-green loop (Strict TDD mode still requires tests green after each refactor).

### openspec-apply-change
- Always run `openspec status --change "<name>" --json` and `openspec instructions apply --change "<name>" --json`; never guess state.
- Implement tasks in order from tasks.md; mark each `- [ ]` to `- [x]` only after real completion.
- Read the contextFiles (proposal, specs, design, tasks) before coding.
- Pause on errors, blockers or unclear requirements; do not guess.
- Never silently narrow, defer or drop specified behavior; surface added scope and ask.
- Keep code changes minimal and scoped to the task.
- Do not run `openspec init` or hand-create `openspec/`.

### openspec-archive-change
- Check artifact and task completion via `openspec status`; warn (and confirm) if incomplete.
- Assess delta spec sync state before archiving; offer sync first if deltas exist.
- Only ADDED requirements can create a new main spec; never invent a missing requirement for MODIFIED/RENAMED.
- Archive goes to `openspec/changes/archive/YYYY-MM-DD-<name>/`; do not infer completion from absence of tasks.

### openspec-explore
- Thinking partner only: NEVER write code or implement; point to /opsx:propose for implementation.
- May write OpenSpec artifacts only after naming the files and getting an explicit yes in a separate message.
- Inspect artifacts/source/tests before asking factual questions; ground recommendations in evidence.
- Resolve blocking decisions first; stop asking when the user has enough clarity.

### openspec-propose
- Planning artifacts only (proposal, design, specs deltas, tasks); do not edit project code or start implementation.
- Run `openspec context --json`, read openspec/config.yaml; create with `openspec new change "<kebab-name>"`.
- Build artifacts in dependency order using `openspec instructions <id> --change "<name>" --json`; follow its template; don't copy `context`/`rules` into files.
- Do not proceed without understanding what the user wants; ask if unclear.
- After artifacts are complete, stop and wait for an explicit apply request.

### openspec-sync-specs
- Merge delta specs (ADDED/MODIFIED/REMOVED/RENAMED) into main specs at `openspec/specs/<cap>/spec.md`.
- Use `openspec instructions specs --change "<name>" --json`; only sync paths in existingOutputPaths.
- Never invent missing requirements; stop and report on errors before writing any main spec.
- Spec path must resolve inside the real specs root (no symlink escape).

### openspec-update-change
- Revise only existing artifact files (`existingOutputPaths`); never create missing artifacts; never edit code.
- Keep proposal/design/specs/tasks coherent with each other; read dependencies from disk.
- Show revisions; if the user rejects one, leave that artifact unchanged.
- Do not hardcode artifact ids; take them from the schema via `openspec status --json`.

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| Discovery | discovery/discovery.md | 11-point discovery (problem, users, rules, risks) |
| Consigna | docs/consigna_parcial.pdf | Source document of the KB |
| CHANGES.md | CHANGES.md | Roadmap index: changes C-01..C-04, deps, governance |
| Knowledge base | knowledge-base/ | 12 files: vision, data model, business rules, architecture, container/deploy |
| OpenSpec root | openspec/ | specs and changes |
| Pytest config | pytest.ini | test runner config |
| Deploy notes | DEPLOY.md | Docker/deploy |
| Env template | env.example | .env is gitignored |

No AGENTS.md / CLAUDE.md at project level yet (agent-instruction step pending).

Read the convention files listed above for project-specific patterns and rules.
