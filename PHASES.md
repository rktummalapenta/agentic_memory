# PHASES.md — Execution Roadmap

> **Project:** agentic_memory / EnterpriseMem-Bench  
> **Total timeline:** 20 weeks  
> **Goal:** 6 Forbes articles · 6 Medium posts · 3 research papers · 1 open source benchmark  

---

## Status Overview

```
Phase 0 — Foundation         ▶  IN PROGRESS
Phase 1 — Experiment 0       ⬜  NEXT
Phase 2 — Experiments 1      ⬜  PLANNED
Phase 3 — Experiments 2 + 3  ⬜  PLANNED
Phase 4 — Experiments 4 + 5  ⬜  PLANNED
Phase 5 — Synthesis          ⬜  PLANNED
```

---

## Phase 0 — Foundation Setup
**Goal:** Everything running locally before writing a single line of experiment code.

### Checklist
- [x] OpenAI API key
- [x] Anthropic API key
- [x] Docker Desktop installed
- [x] Redis running (port 6379) — verified with `PONG`
- [x] ChromaDB running (port 8000) — verified with heartbeat
- [x] Pinecone free account + API key
- [ ] `pip install -r requirements.txt` — packages installed
- [ ] `.env` file complete with all keys
- [ ] Northwind database downloaded (`python data/northwind/load_northwind.py`)
- [ ] SEC EDGAR data pulled (`python data/sec_edgar/load_sec_edgar.py`)
- [ ] BIRD proxy built (`python data/bird/load_bird.py`)
- [ ] 300 sessions built (`python data/sessions/build_sessions.py`)
- [ ] E0 semantic memory seeded into ChromaDB (`python scripts/load_memory_backends.py --experiment e0`)
- [ ] Runtime memory reset flow verified (`python scripts/reset_runtime_memory.py --experiment e0`)
- [ ] Verify script all green (`python scripts/verify_setup.py`)

**Exit criteria:** source datasets are loaded, sessions are built, E0 semantic collections exist in ChromaDB, and `verify_setup.py` shows all critical checks green.

---

## Phase 1 — Experiment 0: Foundation
**Weeks 1–3 | Budget: ~$12 | Output: Forbes #2 + Medium #2 + arXiv Paper 1 draft**

### What We're Measuring
Does memory improve accuracy? By how much? At what turn depth does it start mattering?

### Steps

**Week 1 — Smoke test + validate pipeline**
- [ ] Reset Redis + per-run episodic collections before each run
- [ ] Seed semantic ChromaDB collections from schema + glossary artifacts
- [ ] Run smoke test: `python experiments/exp0_foundation/run_experiment.py --smoke-test`
- [ ] Verify MBS curve is printing correctly
- [ ] Fix any SQL execution errors on Northwind / SEC EDGAR / BIRD
- [ ] Confirm episodic memory starts empty and fills only from prior turns in-session
- [ ] Confirm agent conditions A/B/C/D all producing different results

**Week 2 — Full experiment run**
- [ ] Run Condition A (stateless baseline): `--conditions A`
- [ ] Run Condition B (working memory): `--conditions B`
- [ ] Run Condition C (episodic): `--conditions C`
- [ ] Run Condition D (full stack): `--conditions D`
- [ ] Save results to `experiments/exp0_foundation/results/`

**Week 3 — Analysis + writing**
- [ ] Generate MBS curve (turn 1 → 10) for all conditions
- [ ] Compute MBS by dataset (Northwind vs SEC EDGAR vs BIRD)
- [ ] Compute MBS by tier (T1 vs T2 vs T3)
- [ ] Write Forbes Article #2 (800 words, hook = MBS curve)
- [ ] Write Medium deep-dive #2 (full methodology + results)
- [ ] Draft arXiv Paper 1: "Memory Benefit Score: A Normalized Metric..."

### Expected Findings
| Turn | Stateless (A) | Full Stack (D) | MBS |
|---|---|---|---|
| 1 | ~85% | ~85% | ~0 |
| 3 | ~70% | ~82% | ~17 |
| 5 | ~55% | ~78% | ~42 |
| 7 | ~40% | ~80% | ~100 |
| 10 | ~35% | ~78% | ~123 |

*These are projections. Actual numbers replace these after the run.*

### Forbes Article Hook
"I ran 300 enterprise data analyst sessions through four versions of the same AI agent. At turn 1, memory made no difference. By turn 7, the stateless agent was wrong 60% of the time. The memory-enabled agent was wrong 20% of the time. That gap is not an edge case. That is every analyst session in your enterprise right now."

---

## Phase 2 — Experiment 1: Memory Backend Benchmark
**Weeks 4–6 | Budget: ~$25 | Output: Forbes #3 + Medium #3**

### What We're Measuring
Does it matter which memory backend you use? ChromaDB vs Pinecone vs Neo4j vs hybrid.

### Prerequisites Before Starting
- [ ] Pinecone index created (`enterprise-memory`, dim=1536, cosine)
- [ ] Weaviate sandbox created for E1 corpus loading
- [ ] Neo4j AuraDB instance created — URI + password in `.env`
- [ ] E0 results complete (need baseline accuracy to compare against)

### Steps
- [ ] Build E1 experiment runner (`experiments/exp1_backends/`)
- [ ] Generate one canonical chunked corpus for E1
- [ ] Load the identical corpus into ChromaDB, Pinecone, Weaviate, and Neo4j
- [ ] Validate corpus parity across backends (chunk count, IDs, metadata)
- [ ] Run 3,000 retrieval queries across all backends
- [ ] Measure: accuracy, latency (p50/p95), cost per query
- [ ] Compute Domain Transfer Retention Rate (DTRR) per backend
- [ ] Write Forbes #3 + Medium #3

### Key Metric: Domain Transfer Retention Rate (DTRR)
```
DTRR = accuracy on cross-domain queries / accuracy on same-domain queries × 100
```
Does a backend trained on IT queries handle HR queries well? This is the enterprise killer.

---

## Phase 3 — Experiments 2 + 3: Compression + Retrieval
**Weeks 7–12 | Budget: ~$40 | Output: Forbes #4 + #5 + Medium #4 + #5 + arXiv Paper 2 draft**

### Experiment 2 — Context Compression (Weeks 7–9)
**Question:** Can we compress session history by 70% and keep 85%+ accuracy?

- Compare 4 compression strategies: FIFO, static summary, entity-aware, importance-scored
- Build the compression benchmark dataset and canonical annotations
- Load full session histories into Redis and store compressed snapshots in ChromaDB
- Named metric: Information Retention Quotient (IRQ)
- Forbes angle: "Your AI is spending $0.40/session carrying context it doesn't need"

### Experiment 3 — Retrieval Quality (Weeks 10–12)
**Question:** Sparse vs dense vs re-ranking — which retrieval pipeline performs best?

- Pipelines: BM25, dense-only, hybrid, hybrid + cross-encoder, hybrid + LLM rerank
- Build the extended retrieval corpus once, then load the same chunks into dense stores
- Build BM25 lexical indexes from the same document IDs used in ChromaDB / Pinecone
- Named metric: DTRR (Domain Transfer Retention Rate)
- Forbes angle: "The retrieval pipeline is the memory system's bottleneck — and most teams are using the wrong one"

### arXiv Paper 2
"IRQ and DTRR: Metrics and Evaluation Framework for Context Compression and Retrieval Quality in Enterprise Memory Systems"
Target: EMNLP or SIGIR

---

## Phase 4 — Experiments 4 + 5: Staleness + Multi-Agent
**Weeks 13–18 | Budget: ~$40 | Output: Forbes #6 + #7 + Medium #6 + #7 + arXiv Paper 3 draft**

### Experiment 4 — Memory Staleness & TTL (Weeks 13–15)
**Question:** When does memory become a liability? How do you manage decay?

- 3 strategies: no management, fixed TTL, MFS decay
- Seed the temporal knowledge base into Redis and ChromaDB with timestamps and confidence metadata
- Reset the stores to the same T=0 state before evaluating each staleness strategy
- Named metric: Memory Freshness Score (MFS)
- Forbes angle: "Stale memory is worse than no memory — here's how to measure it"

### Experiment 5 — Multi-Agent Shared Memory (Weeks 16–18)
**Question:** Can agents share memory without contaminating each other?

- 4 architectures: isolated, shared flat, role-scoped, hierarchical controlled
- Load the shared workflow corpus into Neo4j and ChromaDB, then create Redis namespaces per role
- Inject contamination scenarios at runtime against the same base corpus for all architectures
- Named metric: Retrieval Contamination Rate (RCR)
- Forbes angle: "Multi-agent AI is the future. Shared memory is the landmine."

### arXiv Paper 3
"Temporal Confidence Decay and Contamination Isolation in Enterprise Multi-Agent Memory Systems"
Target: NeurIPS workshop or ICLR

---

## Phase 5 — Synthesis + Open Source Release
**Weeks 19–20 | Output: Forbes wrap-up + EnterpriseMem-Bench GitHub release**

### Steps
- [ ] Write synthesis Forbes article: "The Enterprise AI Memory Stack — What We Learned"
- [ ] Final README with all experiment results and MBS curves
- [ ] EnterpriseMem-Bench dataset release (all 300 sessions + ground truth SQL)
- [ ] Publish all 3 arXiv papers
- [ ] Submit to IEEE Access / ACL Findings / EMNLP / SIGIR

---

## Publication Calendar

| Week | Experiment | Forbes | Medium | arXiv |
|---|---|---|---|---|
| 1–3 | E0 Foundation | #2 Memory Systems | #2 | Paper 1 draft |
| 4–6 | E1 Backends | #3 Memory Systems | #3 | — |
| 7–9 | E2 Compression | #4 Memory Systems | #4 | Paper 2 draft |
| 10–12 | E3 Retrieval | #5 Memory Systems | #5 | — |
| 13–15 | E4 Staleness | #6 Memory Systems | #6 | Paper 3 draft |
| 16–18 | E5 Multi-Agent | #7 Memory Systems | #7 | — |
| 19–20 | Synthesis | Wrap-up | — | All 3 submitted |

---

## Decision Log

| Date | Decision | Reason |
|---|---|---|
| Week 0 | Use Northwind + SEC EDGAR + BIRD instead of synthetic data | Real data = more credible, peer-comparable results |
| Week 0 | Text-to-SQL as primary domain | Objective ground truth — no LLM judge needed for core accuracy |
| Week 0 | GPT-4o-mini as agent LLM | Cost control — full experiment series under $150 |
| Week 0 | Redis for working memory (not in-memory dict) | Mirrors real production architecture, feeds Series #3 observability |

---

## What Goes in Each Forbes Article

Every article must:
1. Reference Series #1 (LLM Gateways) — backward link
2. Reference the next experiment — forward hook
3. Include one named metric with a formula
4. Have one sentence that could be a LinkedIn pull quote
5. Stay 700–800 words

**The throughline across all 7 articles:**  
"You can't build reliable enterprise AI without understanding the reliability stack: gateway → memory → observability → orchestration → security. Each layer depends on the one before it."
