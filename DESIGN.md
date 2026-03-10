# DESIGN.md — Agentic Memory: Enterprise Memory Infrastructure for AI Agents

> **Research Series:** Memory Systems for AI Agents · Intelligence Layer · Series #2 of 5  
> **Author:** Executive Director, AI Engineering · JPMorgan Chase  
> **Companion Publications:** Forbes Technology Council · Medium · arXiv / IEEE / ACM  
> **Benchmark Suite:** EnterpriseMem-Bench (this repository)

---

## Table of Contents

1. [Research Premise](#1-research-premise)
2. [The Memory Taxonomy](#2-the-memory-taxonomy)
3. [Experiment Series Overview](#3-experiment-series-overview)
4. [Experiment 0 — Foundation: Stateless vs Memory-Enabled Agents](#4-experiment-0--foundation-stateless-vs-memory-enabled-agents)
5. [Experiment 1 — Memory Backend Benchmark](#5-experiment-1--memory-backend-benchmark)
6. [Experiment 2 — Context Window Compression](#6-experiment-2--context-window-compression)
7. [Experiment 3 — Retrieval Quality Pipelines](#7-experiment-3--retrieval-quality-pipelines)
8. [Experiment 4 — Memory Staleness & TTL](#8-experiment-4--memory-staleness--ttl)
9. [Experiment 5 — Multi-Agent Shared Memory](#9-experiment-5--multi-agent-shared-memory)
10. [Complete Tech Stack](#10-complete-tech-stack)
11. [Data Specification](#11-data-specification)
12. [Named Metrics](#12-named-metrics)
13. [Research Papers](#13-research-papers)
14. [Repository Structure](#14-repository-structure)
15. [Quickstart](#15-quickstart)

---

## 1. Research Premise

Most enterprise AI deployments treat memory as optional. They are wrong — but not uniformly so.

The central question this research series answers is:

> **What memory infrastructure is required for reliable AI agents in enterprise systems?**

Before answering *how* to implement memory, Experiment 0 first proves *whether* memory matters at all on the tasks enterprises actually run. This is a deliberate methodological choice. Jumping directly into architecture comparisons before establishing the foundational benefit produces tutorials, not research.

The series is structured as a dependency chain:

```
E0: Does memory produce measurable benefit?
    ↓ Yes — by how much and where?
E1: Which memory backend architecture produces that benefit most reliably?
    ↓ Hybrid wins — but what happens to context at scale?
E2: How do you preserve decision-relevant information through compression?
    ↓ IRQ metric defined — now what gets retrieved?
E3: What retrieval pipeline actually surfaces the right memory at the right time?
    ↓ Two-stage wins — but memory degrades over time
E4: When does memory become a liability rather than an asset?
    ↓ Staleness modeled — now coordinate across agents
E5: How do multiple agents share memory without contaminating each other?
```

Each experiment earns the right to the next one.

---

## 2. The Memory Taxonomy

This research uses a five-layer memory taxonomy as its conceptual framework. Each layer maps to a distinct storage technology and enterprise use case.

| Memory Type | Analogy | Storage Technology | Enterprise Use Case |
|---|---|---|---|
| **Working Memory** | RAM | Context window / LangGraph state | Active task reasoning, current conversation |
| **Episodic Memory** | Diary | Vector DB (ChromaDB / Pinecone) | Session recall, conversation history, user preferences |
| **Semantic Memory** | Encyclopedia | Knowledge graph (Neo4j) / RAG corpus | Domain facts, company policies, schema knowledge |
| **Procedural Memory** | Muscle memory | Fine-tuned weights / tool definitions | Recurring workflows, SQL patterns, SOPs |
| **Collective Memory** | Org wiki | Shared vector store (multi-agent) | Cross-agent coordination, shared enterprise knowledge |

> **Text-to-SQL Integration:** A Text-to-SQL agent is the primary enterprise use case throughout this series because it exercises all five memory layers simultaneously and has objective ground truth — generated SQL can be evaluated against correct SQL programmatically, without LLM-as-judge subjectivity.

---

## 3. Experiment Series Overview

| # | Experiment | Core Question | Named Metric | Forbes Hook |
|---|---|---|---|---|
| E0 | Stateless vs Memory-Enabled | Does memory produce measurable benefit? | **Memory Benefit Score (MBS)** | Memory matters — but only after turn 3 |
| E1 | Memory Backend Benchmark | Vector DB vs Graph DB vs Hybrid — which wins? | Domain Transfer Retention Rate | Hybrid beats pure vector by 28% |
| E2 | Context Compression | How do you preserve what matters at 70% token reduction? | **Information Retention Quotient (IRQ)** | Your agent is forgetting the wrong things |
| E3 | Retrieval Quality | Sparse vs dense vs re-ranking — what actually works? | Domain Transfer Retention Rate (DTRR) | The retrieval problem nobody talks about |
| E4 | Memory Staleness & TTL | When does memory become a liability? | **Memory Freshness Score (MFS)** | Your AI agent is living in the past |
| E5 | Multi-Agent Shared Memory | Coordination without contamination? | **Retrieval Contamination Rate (RCR)** | Shared memory fails 85% of injection tests |

**Total publication output:** 6 Forbes articles · 6 Medium deep-dives · 3 research papers · 1 open-source benchmark suite

---

## 4. Experiment 0 — Foundation: Stateless vs Memory-Enabled Agents

### Hypothesis

Memory-enabled agents measurably outperform stateless agents on multi-turn enterprise tasks, with the performance gap widening as task complexity and conversational depth increase — but providing negligible benefit on single-turn, context-independent queries.

### Why Text-to-SQL

Text-to-SQL is the ideal primary domain for this experiment for one specific reason: **ground truth exists**. You can write the correct SQL once and score generated SQL objectively. This eliminates LLM-as-judge subjectivity from the core accuracy metric.

The failure mode is also viscerally real for any enterprise data team:

```
User:   "Show me Q3 revenue by region"
Agent:  [Returns correct results]

User:   "Now filter that to the top 5 customers"
Stateless agent:  No context for "that" → wrong SQL or clarification request
Memory agent:     Retains prior query → applies filter → correct SQL
```

### Experimental Conditions

| Condition | Agent Type | Memory Configuration |
|---|---|---|
| A | Fully Stateless | No memory — each turn is independent |
| B | Working Memory Only | Last N turns in context window (sliding) |
| C | Working + Episodic | Full session history via ChromaDB |
| D | Full Stack | Working + Episodic + Semantic (schema + glossary) |

### Dataset

**Primary: Synthetic Enterprise SQLite Database**

```sql
-- Four interconnected tables
orders      (10,000 rows)  — order_id, customer_id, region, amount, date, status
customers    (2,000 rows)  — customer_id, segment, tier, account_manager
products       (500 rows)  — product_id, category, unit_price, cost
returns      (1,200 rows)  — return_id, order_id, reason, amount
```

**Query Session Dataset — 3 Complexity Tiers**

| Tier | Sessions | Turns | Description |
|---|---|---|---|
| Tier 1: Single-Turn | 60 | 1 | No context dependency. Control group. Memory should show ≈0% benefit. |
| Tier 2: Multi-Turn Simple | 80 | 3–5 | Pronoun resolution, filter accumulation across turns |
| Tier 3: Multi-Turn Complex | 60 | 6–10 | Full analyst session: cross-period comparison, entity tracking, joins |

**Secondary Domains**
- 50 IT helpdesk sessions (multi-turn ticket resolution)
- 50 HR policy Q&A sessions (role-based compliance queries)

### Key Metrics

```
Memory Benefit Score (MBS) = (Memory Accuracy − Stateless Accuracy) / Stateless Accuracy × 100

Measured at turn depths: 1, 3, 5, 7, 10
→ Produces the benefit curve: the Forbes hook
```

Additional metrics: SQL exact-match accuracy, context retention score, hallucination rate, cost per correct task completion.

### Tools

```
LangGraph         — stateful agent graph, 4 condition configurations
ChromaDB          — episodic + semantic memory (local)
Redis (Docker)    — working memory / session KV store
mem0              — memory lifecycle: add / search / update
SQLite            — synthetic enterprise database
SQLAlchemy        — SQL execution + ground truth validation
GPT-4o-mini       — agent LLM
Langfuse          — full agent tracing (feeds Series #3 Observability)
W&B Weave         — experiment tracking + reproducibility
```

---

## 5. Experiment 1 — Memory Backend Benchmark

### Hypothesis

A hybrid memory architecture (vector DB for semantic search + knowledge graph for relational context) outperforms either approach alone by ≥25% on enterprise retrieval tasks, while adding <20ms latency overhead.

### Why This Matters

After E0 proves memory matters, the next engineering question is: which memory backend? Vector DBs excel at semantic similarity but fail on relational queries. Knowledge graphs excel at traversal but require structured input. Hybrid architectures theoretically combine both — this experiment quantifies the actual tradeoff.

### Experimental Conditions

| Condition | Backend | Query Strategy |
|---|---|---|
| A | ChromaDB / Pinecone | Dense vector only |
| B | Weaviate | BM25 sparse + dense hybrid (built-in) |
| C | Neo4j AuraDB | Cypher graph traversal |
| D | Pinecone + Neo4j | Two-phase: vector retrieval → graph context enrichment |

### Dataset

**Enterprise Knowledge Corpus — 3 Domains**

| Domain | Documents | Content Type |
|---|---|---|
| IT Runbooks | 2,000 | Troubleshooting guides, incident playbooks, system docs |
| HR Policies | 1,500 | Policy documents, role-based rules, compliance guides |
| Legal / Compliance | 1,500 | Regulatory text, contract clauses, audit requirements |

- 1,000 labeled query-document pairs per domain (3,000 total)
- Neo4j schema: entities (Policy, Role, System, Team, Regulation) + typed relationships
- All synthetic — generated with Claude API, fully publishable

### Key Metrics

```
MRR@10             — Mean Reciprocal Rank
NDCG@10            — Normalized Discounted Cumulative Gain
Precision@K        — K = 1, 3, 5
Query Latency      — p50 / p95 / p99 ms
Cost per 1K Queries
Domain Transfer Delta — train on IT, test on HR (cross-domain degradation %)
```

### Tools

```
Pinecone (free tier)   — cloud vector DB, 1 index, 100K vectors
ChromaDB               — local vector DB baseline
Weaviate Cloud         — hybrid BM25 + vector search
Neo4j AuraDB (free)    — knowledge graph, Cypher, APOC plugins
RAGAS                  — retrieval evaluation framework
```

---

## 6. Experiment 2 — Context Window Compression

### Hypothesis

Progressive summarization with entity-aware compression retains >90% of decision-relevant information while reducing token consumption by 60–80% compared to naive truncation. The Information Retention Quotient (IRQ) metric quantifies this tradeoff precisely.

### Why This Matters

Every memory-enabled agent faces a token economics problem. Context windows are finite. The naive solution — FIFO truncation — destroys exactly the information that made memory valuable. This experiment tests four compression strategies and introduces IRQ: a single number measuring how much decision-relevant information survives compression.

### Compression Strategies

| Strategy | Method | Expected IRQ |
|---|---|---|
| FIFO Truncation | Drop oldest turns when limit reached | Low — destroys critical early context |
| Static Summarization | Summarize all old turns into one block | Medium — loses entity specificity |
| Entity-Aware Progressive | Extract + preserve named entities, compress narrative | High — proposed winner |
| Importance-Scored Retention | Score each turn by relevance, retain top K | High — dynamic but expensive |

### Named Metric

```
Information Retention Quotient (IRQ) =
    (Downstream Task Accuracy with Compressed Memory)
    ─────────────────────────────────────────────────  × 100
    (Downstream Task Accuracy with Full Memory)

IRQ = 100  →  lossless compression
IRQ < 70   →  compression is losing decision-critical information
```

The IRQ vs Token Reduction curve — plotted at 20%, 40%, 60%, 80% token reduction — is the Pareto frontier: where compression stops being worth it.

### Dataset

- 3 domains × 50 sessions × avg 15 turns = 2,250 conversation turns
- Each session has annotated decision-critical entities
- Downstream evaluation: 10 questions per session answerable only if key entities survived compression

### Tools

```
LangGraph     — stateful agent + compression hooks
mem0          — entity extraction + versioned memory updates
spaCy         — named entity recognition pipeline
tiktoken      — token counting and budget enforcement
GPT-4o-mini   — compression LLM + downstream evaluation
W&B Weave     — track IRQ, token counts, accuracy per strategy
```

---

## 7. Experiment 3 — Retrieval Quality Pipelines

### Hypothesis

A two-stage retrieval pipeline (dense retrieval + cross-encoder re-ranking with domain-adaptive thresholds) achieves F1 > 0.87 on enterprise memory retrieval, outperforming single-stage approaches by ≥18%.

### Pipeline Configurations

| # | Pipeline | Components |
|---|---|---|
| 1 | BM25 only | Sparse keyword retrieval baseline |
| 2 | Dense only | Pinecone embeddings, no re-ranking |
| 3 | Hybrid (BM25 + Dense) | RRF fusion, no re-ranking |
| 4 | Hybrid + Cross-Encoder | Pipeline 3 + Cohere Rerank / MiniLM |
| 5 | Hybrid + LLM Re-rank | Pipeline 3 + GPT-4o as re-ranker (cost ceiling benchmark) |

### Dataset

**100K Document Enterprise Corpus**

```
25,000  IT runbooks and incident reports
25,000  HR policy documents and onboarding guides
25,000  Legal and compliance documents
25,000  Financial reports and budget summaries
```

- 1,000 manually labeled query-document pairs (250 per domain)
- 200 cross-domain evaluation pairs (training domain ≠ test domain)

### Key Metrics

```
Precision@K (K=1,3,5,10)
Recall@K
MRR
NDCG@10
Domain Transfer Retention Rate (DTRR) = in-domain accuracy / cross-domain accuracy
Latency: p50 / p95 ms end-to-end
Cost per 1K queries (commercial vs open-source re-rankers)
```

### Tools

```
rank_bm25          — sparse first-stage retrieval
Pinecone           — dense first-stage retrieval
BGE-M3             — open-source embedding baseline (HuggingFace)
Cohere Rerank API  — commercial cross-encoder (1K/month free tier)
ms-marco-MiniLM    — local cross-encoder (free)
RAGAS              — full pipeline evaluation
```

---

## 8. Experiment 4 — Memory Staleness & TTL

### Hypothesis

Unmanaged memory staleness degrades agent decision quality by >40% after 30 days in dynamic enterprise domains. TTL-aware memory with confidence decay scoring reduces this degradation to <8%.

### Why This Matters

Memory without expiry is a liability. An agent that confidently cites 6-month-old org chart data, deprecated system names, or superseded policies can cause more damage than a stateless agent that admits uncertainty. This experiment measures degradation over time and tests three staleness management strategies.

### Temporal Simulation Design

```
T=0          Agent memory seeded with ground truth
T+7 days     30% of items modified (simulating enterprise knowledge drift)
T+14 days    Additional 30% modified
T+30 days    Another 30% modified
T+60 days    Final measurement point

Change velocity by domain:
  IT Systems:       High   — weekly changes (λ = 0.15)
  HR Policies:      Medium — monthly changes (λ = 0.05)
  Legal Compliance: Low    — quarterly changes (λ = 0.02)
```

### Named Metric

```
Memory Freshness Score (MFS) = base_confidence × e^(−λ × days_since_update)

Where:
  λ = domain-specific decay rate (calibrated empirically)
  base_confidence = initial confidence score at storage time

MFS < threshold → trigger selective refresh
MFS = 0 → memory item expired
```

### Staleness Management Strategies

| Strategy | Mechanism | Expected Outcome |
|---|---|---|
| A: None | Memory never expires | >40% accuracy drop by day 30 |
| B: Fixed TTL | Hard expiry by domain (IT=7d, HR=30d, Legal=90d) | Better — wastes still-valid memory |
| C: MFS Decay + Selective Refresh | Confidence decay scoring, refresh when MFS < threshold | Best — efficient and accurate |

### Tools

```
Redis (Docker)    — TTL-aware memory store, key-level expiry
mem0              — memory versioning + confidence tracking
ChromaDB          — episodic memory with creation_time metadata
LangGraph         — pre-retrieval MFS filter in agent loop
scipy.stats       — exponential decay curve fitting for λ calibration
```

---

## 9. Experiment 5 — Multi-Agent Shared Memory

### Hypothesis

A role-scoped shared memory architecture reduces inter-agent redundancy by >60% and improves multi-agent task completion rate by >35%, while maintaining memory isolation boundaries that prevent cross-role contamination — including adversarial injection.

### The Contamination Problem

Shared memory amplifies both intelligence and errors. If Agent A writes a wrong fact, Agent B can retrieve and act on it. In agentic enterprise workflows, this is not a minor inconvenience — it is a wrong business decision propagated across an automated workflow chain.

```
Fully isolated memory:   Low redundancy benefit, maximum safety
Fully shared flat pool:  Maximum redundancy benefit, critical contamination risk
Role-scoped shared:      Balanced — the hypothesis winner
```

### Agent System Design

**5-Agent Enterprise Workflow**

```
Planner      → Breaks down task, coordinates subtasks
Researcher   → Retrieves information from shared knowledge
Writer       → Generates content / reports
Reviewer     → Validates output against policy + quality standards
Coordinator  → Manages workflow state, handles exceptions
```

**Task Domains**
- Quarterly report generation (Finance)
- Technical RFP responses (Sales / Engineering)
- Compliance audit preparation (Legal / Operations)

### Memory Sharing Architectures

| # | Architecture | Access Model |
|---|---|---|
| A | Fully Isolated | No agent reads another's memory |
| B | Fully Shared Flat | All agents read/write same pool |
| C | Role-Scoped Shared | Read-all, write-own-scope only |
| D | Hierarchical + Access Controls | Role-scoped + approval gate for cross-scope writes |

### Named Metric

```
Retrieval Contamination Rate (RCR) =
    (Adversarially injected items successfully retrieved by non-injecting agents)
    ────────────────────────────────────────────────────────────────────────────
    (Total adversarially injected items)

RCR = 0%  →  perfect isolation
RCR = 85% →  fully shared flat pool (expected result)
```

**Contamination Test Suite:** 20 adversarial injection scenarios — deliberate false facts injected by one agent, measuring propagation across the remaining 4.

### Tools

```
LangGraph Multi-Agent  — 5-node agent graph with shared state
CrewAI                 — agent role definition + write-scope restriction
Neo4j AuraDB           — collective memory graph (role-tagged nodes/edges)
Redis                  — role-scoped working memory (namespaced keys)
ChromaDB               — shared episodic memory (collection-level access)
Langfuse               — multi-agent trace correlation (critical for Series #3)
```

---

## 10. Complete Tech Stack

### Memory Backend Layer

| Tool | Memory Type | Tier | Experiments |
|---|---|---|---|
| ChromaDB | Episodic + Semantic | Free / open source | E0, E1, E2, E3, E5 |
| Pinecone | Episodic (vector) | Free tier (1 index, 100K vectors) | E1, E3 |
| Weaviate Cloud | Episodic + hybrid | Free sandbox | E1 |
| Neo4j AuraDB | Semantic (graph) | Free tier (1 instance) | E1, E5 |
| Redis | Working memory / KV | Free (local Docker) | E0, E4, E5 |
| mem0 | Memory lifecycle mgmt | Open source | E0, E2, E4 |
| SQLite | SQL target / procedural | Free (stdlib) | E0 |

### LLM & Embedding Layer

| Model | Role | Cost Estimate |
|---|---|---|
| GPT-4o-mini | Agent reasoning + SQL generation | ~$0.15/1M tokens |
| GPT-4o | LLM-as-judge evaluation | ~$2.50/1M tokens |
| text-embedding-3-small | Memory encoding (primary) | ~$0.02/1M tokens |
| text-embedding-3-large | High-quality retrieval (E3) | ~$0.13/1M tokens |
| Claude Sonnet 3.5 | Synthetic data generation | Pay-per-use |
| BGE-M3 (HuggingFace) | Open-source embedding baseline | Free (local) |

> **Estimated total API cost to run all 6 experiments: $80–150 USD**

### Orchestration Layer

| Tool | Role |
|---|---|
| LangGraph | Stateful agent graph — primary framework (E0–E5) |
| LangChain | Retrieval chains + SQL agent |
| CrewAI | Multi-agent role coordination (E5) |
| SQLAlchemy | SQL execution + ground truth validation |

### Evaluation & Observability Layer

| Tool | Role |
|---|---|
| RAGAS | RAG + retrieval evaluation |
| Weights & Biases (Weave) | Experiment tracking + reproducibility |
| Langfuse (self-hosted) | Full agent tracing (feeds Series #3 Observability content) |
| scipy.stats | Statistical significance tests (Mann-Whitney U, t-test) |
| pytest | Experiment reproducibility harness |

---

## 11. Data Specification

All datasets are **synthetic** — purpose-built to replicate enterprise conditions without any real organizational data. Every dataset is generated programmatically and publishable as part of this benchmark suite.

### Primary Datasets

| Dataset | Size | Generator | Used In |
|---|---|---|---|
| Enterprise SQLite DB | 13,700 rows across 4 tables | Python Faker + domain templates | E0 |
| Query Session Dataset | 200 sessions, 3 complexity tiers | Claude API + hand-crafted ground truth SQL | E0 |
| IT/HR/Legal Corpus | 5,000 documents | Claude API, domain-specific prompts | E1, E3 |
| Extended Retrieval Corpus | 100,000 documents | Claude API + template expansion | E3 |
| Compression Session Dataset | 2,250 turns across 150 sessions | Claude API + entity annotation | E2 |
| Temporal Knowledge Base | 300 items × 3 domains with change schedule | Custom generator + temporal tags | E4 |
| Multi-Agent Task Suite | 50 workflow tasks × 3 domains | Hand-crafted + Claude API | E5 |
| Contamination Injection Set | 20 adversarial scenarios | Custom injection framework | E5 |

### Ground Truth Standard

Every primary evaluation dataset includes hand-crafted ground truth:

- **E0:** Correct SQL per query (enables objective accuracy scoring)
- **E1:** Relevance labels per query-document pair (0–3 graded)
- **E2:** Annotated decision-critical entities per conversation session
- **E3:** Same as E1 + cross-domain transfer pairs
- **E4:** Ground truth values at each time point T=0,7,14,30,60
- **E5:** Expected task output + contamination propagation map

---

## 12. Named Metrics

Four new metrics introduced across this series. Each is formulaic, cross-comparable, and designed for citation.

### Memory Benefit Score (MBS) — Experiment 0

```
MBS = (Memory-Enabled Accuracy − Stateless Accuracy) / Stateless Accuracy × 100

MBS = 0    →  memory provides no benefit (expected on single-turn queries)
MBS = 50   →  memory improves accuracy by 50% over stateless baseline
MBS curve  →  plotted by conversation turn depth (1,3,5,7,10)
```

### Information Retention Quotient (IRQ) — Experiment 2

```
IRQ = (Downstream Task Accuracy with Compressed Memory)
      ──────────────────────────────────────────────────  × 100
      (Downstream Task Accuracy with Full Memory)

IRQ = 100  →  lossless compression
IRQ = 85   →  acceptable for most enterprise use cases
IRQ < 70   →  compression is destroying decision-critical information
```

### Memory Freshness Score (MFS) — Experiment 4

```
MFS = base_confidence × e^(−λ × days_since_update)

Where λ (domain decay rate) is calibrated empirically:
  IT Systems:       λ ≈ 0.15  (weekly change velocity)
  HR Policies:      λ ≈ 0.05  (monthly change velocity)
  Legal Compliance: λ ≈ 0.02  (quarterly change velocity)
```

### Retrieval Contamination Rate (RCR) — Experiment 5

```
RCR = Injected items retrieved by non-injecting agents
      ──────────────────────────────────────────────────
      Total injected items

RCR = 0%   →  perfect isolation
RCR = 85%  →  expected for fully shared flat memory pool
RCR < 5%   →  target for role-scoped architecture
```

---

## 13. Research Papers

Three papers from six experiments, each making a distinct citable contribution.

### Paper 1 — Foundation (from E0)

**Title:** *Memory Benefit Score: A Normalized Metric for Evaluating Memory-Augmented Agent Performance on Enterprise Tasks*

**Target Venues:** arXiv (immediate) → IEEE Access or ACL Findings

**Core Contributions:**
1. MBS metric definition and cross-domain validation
2. First controlled benchmark of memory-enabled vs. stateless agents on enterprise Text-to-SQL
3. Evidence that memory benefit is task-complexity dependent — non-linear, not uniform

**Key Finding:** Memory provides <5% benefit on single-turn queries but >45% benefit on turn-7+ complex tasks.

---

### Paper 2 — Compression & Retrieval (from E2 + E3)

**Title:** *IRQ and DTRR: Metrics and Evaluation Framework for Context Compression and Retrieval Quality in Enterprise Memory Systems*

**Target Venues:** arXiv → EMNLP or SIGIR

**Core Contributions:**
1. IRQ + DTRR metric pair — compression quality and retrieval generalization measured together for the first time in enterprise agent context
2. Entity-aware progressive compression algorithm with formal definition
3. Pareto frontier analysis: IRQ vs token reduction across 3 enterprise domains

**Key Finding:** Entity-aware compression achieves IRQ >90 at 65% token reduction. FIFO truncation achieves IRQ <65 at the same reduction level.

---

### Paper 3 — Staleness & Multi-Agent (from E4 + E5)

**Title:** *Temporal Confidence Decay and Contamination Isolation in Enterprise Multi-Agent Memory Systems*

**Target Venues:** arXiv → NeurIPS workshop (Multi-Agent Systems) or ICLR

**Core Contributions:**
1. MFS decay model with domain-specific λ calibration methodology
2. RCR contamination metric + adversarial injection benchmark (first of its kind for enterprise agents)
3. First evaluation of memory contamination propagation across multi-agent enterprise workflows — quantifying the coordination overhead of role-scoped isolation

**Key Finding:** Fully shared memory fails 85% of adversarial injection tests. Role-scoped isolation reduces this to 5%, with a 23% coordination overhead — quantified here for the first time.

---

## 14. Repository Structure

```
agentic_memory/
│
├── DESIGN.md                          ← This document
├── README.md                          ← Project overview + quickstart
│
├── data/
│   ├── generate_enterprise_db.py      ← SQLite database generator (E0)
│   ├── generate_query_sessions.py     ← 200-session query dataset (E0)
│   ├── generate_corpus.py             ← 5K + 100K document corpus (E1, E3)
│   ├── generate_compression_data.py   ← 2,250-turn session dataset (E2)
│   ├── generate_temporal_kb.py        ← Temporal knowledge base (E4)
│   └── generate_multiagent_tasks.py   ← 50-task multi-agent suite (E5)
│
├── agents/
│   ├── stateless_agent.py             ← Condition A baseline
│   ├── working_memory_agent.py        ← Condition B
│   ├── episodic_memory_agent.py       ← Condition C
│   ├── full_memory_agent.py           ← Condition D
│   └── text_to_sql_agent.py           ← SQL generation + execution
│
├── memory/
│   ├── chromadb_store.py              ← Episodic + semantic (local)
│   ├── pinecone_store.py              ← Episodic (cloud vector)
│   ├── neo4j_store.py                 ← Semantic (graph)
│   ├── redis_store.py                 ← Working memory / KV
│   └── mem0_lifecycle.py              ← Memory add/search/update/expire
│
├── experiments/
│   ├── exp0_foundation/
│   │   ├── run_experiment.py
│   │   ├── evaluate_sql.py
│   │   └── compute_mbs.py
│   ├── exp1_backends/
│   ├── exp2_compression/
│   │   └── compute_irq.py
│   ├── exp3_retrieval/
│   ├── exp4_staleness/
│   │   └── compute_mfs.py
│   └── exp5_multiagent/
│       └── compute_rcr.py
│
├── evaluation/
│   ├── mbs_calculator.py              ← Memory Benefit Score
│   ├── irq_calculator.py              ← Information Retention Quotient
│   ├── mfs_calculator.py              ← Memory Freshness Score
│   ├── rcr_calculator.py              ← Retrieval Contamination Rate
│   ├── llm_judge.py                   ← GPT-4o as quality evaluator
│   ├── ragas_eval.py                  ← Retrieval evaluation pipeline
│   └── statistical_tests.py          ← Mann-Whitney U, t-test
│
├── notebooks/
│   ├── E0_results_analysis.ipynb
│   ├── E1_backend_comparison.ipynb
│   ├── E2_compression_pareto.ipynb
│   ├── E3_retrieval_pipeline.ipynb
│   ├── E4_staleness_curves.ipynb
│   └── E5_contamination_analysis.ipynb
│
├── config/
│   ├── experiment_config.yaml         ← Shared config: models, thresholds, budgets
│   └── domain_decay_rates.yaml        ← λ values per domain (E4)
│
├── docker-compose.yml                 ← Redis + Langfuse + ChromaDB local setup
├── requirements.txt
└── .env.example                       ← API key placeholders (never commit keys)
```

---

## 15. Quickstart

### Prerequisites

```bash
# Python 3.11+
python --version

# Docker (for Redis + Langfuse)
docker --version
```

### 1. Clone and Install

```bash
git clone https://github.com/rktummalapenta/agentic_memory.git
cd agentic_memory
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Add your keys:
# OPENAI_API_KEY=
# PINECONE_API_KEY=
# NEO4J_URI= (AuraDB free tier)
# NEO4J_PASSWORD=
# ANTHROPIC_API_KEY= (for synthetic data generation)
```

### 3. Start Local Infrastructure

```bash
docker-compose up -d
# Starts: Redis (port 6379) + Langfuse (port 3000) + ChromaDB (port 8000)
```

### 4. Generate Base Data (Start Here)

```bash
# Generate the enterprise SQLite database
python data/generate_enterprise_db.py

# Generate 200-session query dataset with ground truth SQL
python data/generate_query_sessions.py

# Verify setup
python -c "import sqlite3; c=sqlite3.connect('data/enterprise.db'); print('Tables:', c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall())"
```

### 5. Run Experiment 0

```bash
python experiments/exp0_foundation/run_experiment.py \
  --conditions A B C D \
  --tiers 1 2 3 \
  --sessions 200

# Results written to: experiments/exp0_foundation/results/
# MBS curve generated: notebooks/E0_results_analysis.ipynb
```

### 6. View Traces

Open Langfuse at `http://localhost:3000` to inspect full agent traces for every experiment run.

---

## Contributing

This is an active research repository. Experiment designs, metric definitions, and results will be updated as experiments complete. Issues and discussions welcome.

---

## Citation

If you use EnterpriseMem-Bench datasets, metrics, or evaluation frameworks in your research, please cite:

```bibtex
@misc{tummalapenta2025agenticmemory,
  author = {Tummalapenta, Ravi Kumar},
  title  = {EnterpriseMem-Bench: Memory Infrastructure Evaluation for Enterprise AI Agents},
  year   = {2025},
  url    = {https://github.com/rktummalapenta/agentic_memory}
}
```

---

## License

MIT License — see `LICENSE` for details.

---

*Memory Systems for AI Agents · Series #2 of 5 · Intelligence Layer*  
*Forbes Technology Council · Medium · arXiv / IEEE / ACM*
