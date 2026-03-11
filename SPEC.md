# SPEC.md — agentic_memory Technical Specification

> **Project:** EnterpriseMem-Bench  
> **Series:** Enterprise AI Reliability Stack — Series #2 of 5  
> **Author:** Ravi Kumar Tummalapenta, Executive Director, AI Engineering @ JPMorgan Chase  
> **Status:** In Progress  

---

## 1. What This Project Is

A reproducible research benchmark that measures how different memory architectures affect AI agent performance on enterprise tasks.

**The core question:** Does memory make agents meaningfully better — and if so, when, by how much, and which kind of memory matters most?

**Why it matters:** Most enterprise AI deployments today are stateless. Every turn starts from zero. This project produces the first rigorous measurement of what that costs in accuracy across real enterprise workflows.

---

## 2. The Primary Claim Being Tested

> Memory-enabled agents outperform stateless agents on multi-turn enterprise tasks.  
> The performance gap is near-zero at turn 1 and grows with session depth.  
> On single-turn queries, memory provides no statistically significant benefit.

This non-linearity — memory matters only in context chains — is the core research finding and the Forbes hook.

---

## 3. Datasets

Three public data sources. No synthetic data, no IP concerns.

### 3.1 Northwind (Enterprise Sales)
- **Source:** github.com/jpwhite3/northwind-SQLite3
- **Schema:** Orders, OrderDetails, Customers, Products, Categories, Employees
- **Size:** 830 orders · 77 products · 91 customers
- **Why:** Canonical enterprise schema — instantly recognizable. Rich join complexity for multi-turn sessions.
- **Sessions:** 100 (T1: 30, T2: 40, T3: 30)

### 3.2 SEC EDGAR (Public Company Financials)
- **Source:** data.sec.gov/api/xbrl/companyfacts — free public API, no key required
- **Schema:** annual_financials, quarterly_financials, companies
- **Coverage:** 20 companies (Apple, Microsoft, JPMorgan, Nvidia, etc.) · 7 metrics · 10+ years
- **Metrics:** revenue, operating_income, net_income, total_assets, total_liabilities, eps, cash
- **Why:** Real data CFOs and analysts use. Strong Forbes angle. No IP issues — all public filings.
- **Sessions:** 120 (T1: 30, T2: 50, T3: 40)

### 3.3 BIRD Benchmark (Financial)
- **Source:** bird-bench.github.io — register for full download, or use auto-built proxy
- **Schema:** account, client, loan, trans, card, district (Czech bank data)
- **Size:** 682 loans · 5,369 clients · 1,057 transactions
- **Why:** Published academic benchmark — MBS results are peer-comparable. Evidence annotations map directly to semantic memory.
- **Sessions:** 80 (T1: 30, T2: 30, T3: 20)

### 3.4 Session Structure

| Tier | Sessions | Turns | Memory Critical | Description |
|---|---|---|---|---|
| T1 | 90 | 90 | 0% | Single-turn — control group. Memory should add zero benefit. |
| T2 | 120 | 480 | ~60% | 3-5 turns. Pronoun resolution, filter carry-forward. |
| T3 | 90 | 830 | ~85% | 6-10 turns. Full analyst sessions with entity chains. |
| **Total** | **300** | **1,400** | **~30%** | |

**Memory-critical turn:** A turn where the correct SQL requires context (entity, filter, or result) from a prior turn. Stateless agents fail these. Memory-enabled agents should not.

---

## 4. Agent Conditions

Four conditions. Identical LLM, identical prompt structure. Only the memory injection differs.

| Condition | Name | Memory Available | What It Has |
|---|---|---|---|
| A | Stateless | None | Baseline. Each turn is independent. |
| B | Working Memory | Last N turns in context | Sliding window of prior turns injected into prompt. |
| C | Episodic | Working + ChromaDB | Working window + vector retrieval of relevant prior context. |
| D | Full Stack | Working + Episodic + Semantic | C + schema docs and business glossary in semantic memory. |

**Condition A is the control.** All MBS scores are relative to A.

---

## 5. Memory Architecture

### 5.1 Working Memory (Redis)
- **What:** Last 5 turns of the active session stored in Redis list
- **Format:** `{turn_number, question, sql_generated, result_summary}`
- **Injection:** Formatted as "CONVERSATION HISTORY" block prepended to each prompt
- **TTL:** 24 hours per session
- **Used in:** Conditions B, C, D

### 5.2 Episodic Memory (ChromaDB)
- **What:** Vector embeddings of each completed turn
- **Retrieval:** Top-K cosine similarity search against current question
- **Injection:** "RELEVANT PRIOR CONTEXT" block in prompt, only when turn > window size
- **Embedding model:** text-embedding-3-small
- **Used in:** Conditions C, D

### 5.3 Semantic Memory (ChromaDB)
- **What:** Database schema, table descriptions, column definitions, business glossary
- **Loaded once** at agent initialization — does not change during a session
- **Retrieval:** Query-aware schema injection (fetch relevant tables, not all tables)
- **Used in:** Condition D only

### 5.4 Memory Stack by Experiment

| Experiment | Redis | ChromaDB | Pinecone | Neo4j |
|---|---|---|---|---|
| E0 Foundation | ✓ | ✓ | — | — |
| E1 Backend Benchmark | ✓ | ✓ | ✓ | ✓ |
| E2 Compression | ✓ | ✓ | — | — |
| E3 Retrieval Quality | ✓ | ✓ | ✓ | — |
| E4 Staleness & TTL | ✓ | — | — | — |
| E5 Multi-Agent | ✓ | ✓ | — | ✓ |

---

## 6. Evaluation

### 6.1 Primary Metric — SQL Result Match
Execute both ground truth SQL and generated SQL against the same database.  
Compare result sets — order-insensitive exact match.

```
is_correct = (sorted(gt_result_hashes) == sorted(gen_result_hashes))
```

No LLM-as-judge needed for core accuracy. This is why Text-to-SQL is the primary domain.

### 6.2 Named Metrics (4 total — designed for citation)

**Memory Benefit Score (MBS)** — Experiment 0
```
MBS = (Memory Accuracy − Stateless Accuracy) / Stateless Accuracy × 100
```
- Computed at each turn depth (1, 3, 5, 7, 10)
- Produces the Forbes hook curve: near-zero at T1, grows steeply, plateaus ~T7
- Primary research finding for Paper 1

**Information Retention Quotient (IRQ)** — Experiment 2
```
IRQ = Compressed Memory Accuracy / Full Memory Accuracy × 100
```
- Measures how much accuracy is preserved after context compression
- Target: IRQ > 85% at 70% token reduction

**Memory Freshness Score (MFS)** — Experiment 4
```
MFS = base_confidence × e^(−λ × days_since_update)
```
- λ = domain-specific decay rate (IT: 0.15, HR: 0.05, Legal: 0.02)
- Drives proactive memory refresh before MFS drops below threshold (0.40)

**Retrieval Contamination Rate (RCR)** — Experiment 5
```
RCR = injected_items_retrieved_by_non_injecting_agents / total_injected_items
```
- Measures cross-agent memory leakage in multi-agent architectures
- Target: RCR < 5% in role-scoped memory architecture

### 6.3 Secondary Evaluation
- LLM-as-judge (GPT-4o): synthesis turns, free-form answers — used sparingly to control cost
- Execution success rate: % of generated SQL that runs without error
- Latency: p50/p95 per condition per turn depth

---

## 7. Tech Stack

### LLMs
| Model | Role |
|---|---|
| gpt-4o-mini | Primary agent — all 4 conditions |
| gpt-4o | LLM-as-judge — synthesis turns only |
| text-embedding-3-small | Embeddings for ChromaDB and Pinecone |
| claude-sonnet-4-6 | Data generation assistance |

### Infrastructure
| Tool | Role | Port |
|---|---|---|
| Redis 7 (Docker) | Working memory, session KV, TTL management | 6379 |
| ChromaDB (Docker) | Episodic + semantic vector memory | 8000 |
| Langfuse (Docker) | Agent observability — traces every LLM call | 3000 |
| SQLite | Northwind, BIRD, results storage | — |

### Cloud (Free Tiers)
| Service | Role | Needed For |
|---|---|---|
| Pinecone | Cloud vector DB comparison | E1, E3 |
| Neo4j AuraDB | Knowledge graph memory | E1, E5 |
| Weights & Biases | Experiment tracking, MBS curves | All |

### Python Packages
```
openai, anthropic                     # LLM APIs
langchain, langchain-openai, langgraph # Orchestration
chromadb, redis, pinecone-client      # Memory backends
faker, sqlalchemy, sqlparse           # Data + SQL
python-dotenv, pyyaml, rich           # Config + CLI
pandas, scipy, numpy, matplotlib      # Analysis
pytest                                # Testing
```

---

## 8. Repository Structure

```
agentic_memory/
├── SPEC.md                          ← This file
├── PHASES.md                        ← Execution roadmap
├── README.md                        ← Quick start
├── requirements.txt
├── .env.example
├── docker-compose.yml               ← Redis + ChromaDB + Langfuse
│
├── data/
│   ├── northwind/
│   │   └── setup_northwind.py       ← Downloads + verifies Northwind
│   ├── sec_edgar/
│   │   └── setup_sec_edgar.py       ← Pulls 20 companies from SEC API
│   ├── bird/
│   │   └── setup_bird.py            ← BIRD financial subset / proxy
│   └── sessions/
│       └── build_sessions.py        ← Builds 300 multi-turn sessions
│
├── agents/
│   └── base_agent.py                ← Conditions A / B / C / D
│
├── memory/
│   ├── chromadb_store.py            ← Episodic + semantic memory
│   ├── redis_store.py               ← Working memory + TTL store
│   └── neo4j_store.py               ← Knowledge graph (E1, E5)
│
├── evaluation/
│   ├── sql_evaluator.py             ← Ground truth SQL comparison
│   └── mbs_calculator.py            ← MBS formula + turn-depth curve
│
├── experiments/
│   ├── exp0_foundation/
│   │   └── run_experiment.py        ← Main E0 runner
│   ├── exp1_backends/               ← (Phase 2)
│   ├── exp2_compression/            ← (Phase 3)
│   ├── exp3_retrieval/              ← (Phase 3)
│   ├── exp4_staleness/              ← (Phase 4)
│   └── exp5_multiagent/             ← (Phase 4)
│
├── config/
│   └── experiment_config.yaml       ← All experiment parameters
│
├── notebooks/                       ← Results analysis per experiment
└── scripts/
    └── verify_setup.py              ← Checks every component
```

---

## 9. Cost Estimates

| Scope | Sessions | Est. API Cost |
|---|---|---|
| E0 smoke test (5 sessions/tier) | 15 | ~$0.50 |
| E0 full run | 300 | ~$12 |
| E1–E5 combined | — | ~$80–120 |
| **Full series** | | **~$100–140** |

All GPT-4o-mini at $0.15/1M tokens. GPT-4o judge used sparingly.  
Cloud free tiers (Pinecone, Neo4j, W&B) are sufficient for all experiments.

---

## 10. Publication Output

| Experiment | Forbes Article | Medium Deep-Dive | Research Paper |
|---|---|---|---|
| E0 | Memory Systems #1 | Memory Systems #1 | MBS Metric (arXiv → IEEE/ACL) |
| E1 | Memory Systems #2 | Memory Systems #2 | — |
| E2 + E3 | Memory Systems #3 + #4 | Memory Systems #3 + #4 | IRQ + DTRR (arXiv → EMNLP/SIGIR) |
| E4 + E5 | Memory Systems #5 + #6 | Memory Systems #5 + #6 | MFS + RCR (arXiv → NeurIPS/ICLR) |

Open source benchmark release: **EnterpriseMem-Bench** — named benchmark drives citations.
