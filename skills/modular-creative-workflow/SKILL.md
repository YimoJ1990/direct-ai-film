---
name: modular-creative-workflow
description: A reusable, structured skill for planning, producing, reviewing, and delivering AI-assisted creative projects. Use when a request requires breaking a concept into stages, managing reusable assets, coordinating tools, checking consistency, and iterating toward a final deliverable.
---

# Modular Creative Workflow

## Purpose
Turn an open-ended creative request into a repeatable, reviewable production process. Keep planning, asset management, generation, quality review, and delivery separate so individual steps can be updated without redoing the entire project.

## Operating Principles
- Prioritize the user's explicit constraints over generic defaults.
- Separate confirmed requirements from assumptions. Ask only when a missing detail blocks execution; otherwise use reversible defaults and label them.
- Reuse approved assets, settings, and conventions to maintain consistency.
- Make each stage produce a concrete output that can be checked before the next stage.
- Automate repetitive operations; keep human review for subjective or high-impact decisions.
- Preserve a change log and avoid repeating failed attempts without adjusting the cause.
- Do not claim a task, generation, test, or delivery is complete unless verified.

## Workflow

### 1. Interpret the brief
Extract: objective, audience, deliverables, style, format, constraints, source assets, schedule, budget, and acceptance criteria. Create a short project brief. Do not invent specifics that the user did not supply.

### 2. Break the work into stages
Construct a dependency-aware plan:
1. Requirement confirmation
2. Reference and asset inventory
3. Structure and content planning
4. Reusable asset preparation
5. Production / generation
6. Quality assurance and revisions
7. Assembly and delivery

Identify which stages can run independently and which require approved outputs.

### 3. Build a reusable project structure
Organize assets by project, version, and stage. Use stable names and track origin, status, and intended use. Separate immutable source materials from derived assets. Do not overwrite approved masters.

Suggested directory structure:

```text
project/
  brief/
  sources/
  references/
  plans/
  assets/
  outputs/
  reviews/
  delivery/
```

### 4. Plan at the unit level
Divide the deliverable into small reviewable units. For each unit, record:
- Intent and essential content
- Inputs and required references
- Constraints and continuity requirements
- Selected tool or method
- Expected output
- Validation checks

Favor a table or structured manifest when multiple units must be managed.

### 5. Choose methods and tools
Match the method to the problem. Prefer the simplest reliable approach that meets quality, control, cost, and repeatability requirements. Where multiple approaches exist, compare them on expected quality, controllability, processing cost, and failure modes. Never imply a tool has been tested without evidence.

### 6. Produce iteratively
Start with a small representative sample. Verify the sample against the brief before scaling. Run only the necessary revisions, recording what changed and why. When appropriate, separate content preparation from execution so the same prepared assets can be reused.

### 7. Review quality
Inspect each unit for:
- Requirement coverage
- Visual and semantic coherence
- Consistency across units
- Technical defects
- Timing, transitions, or alignment where relevant
- Export format and completeness

Classify findings as blocking, important, or optional. Resolve blocking issues before delivery.

### 8. Assemble and deliver
Combine approved units into the final deliverable. Check ordering, naming, compatibility, and missing files. Deliver a concise handoff covering file locations, usage steps, editable inputs, known limitations, and any unresolved items.

## Output Format
When invoked, respond with:
1. **Brief:** objective, scope, constraints, and assumptions.
2. **Plan:** stages with inputs, outputs, and acceptance checks.
3. **Execution:** practical instructions or generated artifacts for the current stage.
4. **QA:** issues, fixes, and verification status.
5. **Handoff:** final deliverables and next actions.

Keep the response proportional to the task. For a simple request, compress stages without losing requirements. For production workflows, use structured manifests and clear naming conventions.

## Guardrails
- Do not copy proprietary examples, private references, or project-specific details into a reusable template.
- Do not introduce unrelated styles, subjects, settings, or tools.
- Do not hide uncertainty or present estimates as measured results.
- Do not perform destructive changes to existing assets without explicit authorization.
- Keep reusable instructions generic and project details in separate briefs.
