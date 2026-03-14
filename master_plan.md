# MASTER_PLAN.md
# EnterpriseMem-Bench — Memory Systems for AI Agents

Project: agentic_memory  
Benchmark: EnterpriseMem-Bench  
Author: Ravi Kumar Tummalapenta

---

# 1. Vision

EnterpriseMem-Bench is a reproducible benchmark designed to measure how different memory architectures affect AI agent performance on enterprise workflows.

The project answers the central question:

> What memory infrastructure is required for reliable AI agents in enterprise systems?

This benchmark will produce:

- 6–7 Forbes Technology Council articles
- 6 Medium engineering deep dives
- 3 research papers
- EnterpriseMem-Bench open benchmark dataset
- Open-source memory infrastructure reference implementation

---

# 2. Enterprise AI Reliability Stack

This project is part of a broader research series.
Layer 1 — LLM Gateway
Layer 2 — Memory Systems
Layer 3 — Observability
Layer 4 — Agent Orchestration
Layer 5 — Governance / Safety


Series #1 covered LLM Gateways.

EnterpriseMem-Bench focuses on **Layer 2: Memory Systems**.

---

# 3. Core Research Questions

The series answers the following questions:

1. Do AI agents actually benefit from memory?
2. How much memory does an agent need?
3. Which memory backend works best?
4. How should memory be compressed?
5. What retrieval pipelines produce the best results?
6. When does memory become stale?
7. How do multi-agent systems share memory safely?

Each experiment answers one question.

---

# 4. Experiment Roadmap

## Experiment 0 — Memory vs Stateless

Question  
Do memory-enabled agents outperform stateless agents on enterprise workflows?

Conditions

| Condition | Description |
|----------|-------------|
A | Stateless baseline |
B | Working memory only |
C | Working + episodic |
D | Full memory stack |

Metric

Memory Benefit Score (MBS)
MBS = (memory_accuracy − stateless_accuracy) / stateless_accuracy

Expected finding

Memory benefit grows with session depth.

Outputs

- Forbes Article #2
- Medium Deep Dive #2
- Research Paper #1

---

## Experiment 0.5 — Memory Scaling

Question  
How much memory is actually required before returns diminish?

Test parameters

- episodic memory top-k (1, 3, 5, 10, 20)
- working memory window (2, 5, 10 turns)
- semantic memory chunk size

Metric

Memory Scaling Efficiency (MSE)
MSE = accuracy_gain / additional_memory_cost


Expected finding

Memory benefit saturates beyond moderate context size.

Outputs

- Forbes Article #3
- Research Paper #1 (combined with E0)

---

## Experiment 1 — Memory Backend Benchmark

Question  
Which backend architecture is best?

Backends

- ChromaDB
- Pinecone
- Weaviate
- Neo4j
- Hybrid

Metric

Domain Transfer Retention Rate (DTRR)
DTRR = cross_domain_accuracy / same_domain_accuracy


Outputs

- Forbes Article #4
- Medium Deep Dive #3

---

## Experiment 2 — Context Compression

Question  
How much context can be compressed without losing accuracy?

Methods

- FIFO truncation
- static summarization
- progressive summarization
- entity-aware compression

Metric

Information Retention Quotient (IRQ)
IRQ = compressed_accuracy / full_context_accuracy


Outputs

- Forbes Article #5
- Medium Deep Dive #4
- Research Paper #2

---

## Experiment 3 — Retrieval Quality

Question  
Which retrieval pipeline works best for memory-augmented agents?

Pipelines

- BM25
- dense embeddings
- hybrid retrieval
- reranked retrieval

Metrics

Precision@k  
Recall@k  
Domain Transfer Retention Rate

Outputs

- Forbes Article #6
- Medium Deep Dive #5
- Research Paper #2

---

## Experiment 4 — Memory Staleness

Question  
When does memory become harmful?

Strategies

- no refresh
- fixed TTL
- decay-based refresh
- confidence decay

Metric

Memory Freshness Score (MFS)
MFS = confidence × e^(−λ × time)


Outputs

- Forbes Article #7
- Medium Deep Dive #6
- Research Paper #3

---

## Experiment 5 — Multi-Agent Memory

Question  
How should multiple agents share memory?

Architectures

- isolated memory
- shared flat memory
- role-scoped memory
- hierarchical memory

Metric

Retrieval Contamination Rate (RCR)
RCR = contaminated_retrievals / total_retrievals


Outputs

- Forbes Article #8
- Medium Deep Dive #7
- Research Paper #3

---

# 5. Benchmark Dataset

EnterpriseMem-Bench uses three public datasets.

## Northwind

Enterprise sales database.

Tables

- customers
- orders
- order_details
- products
- employees

Purpose

Complex SQL joins.

Sessions

100

---

## SEC EDGAR

Public company financial filings.

Tables

- companies
- annual_financials
- quarterly_financials

Metrics

- revenue
- net_income
- total_assets
- liabilities
- EPS

Sessions

120

---

## BIRD Benchmark

Financial dataset used in Text-to-SQL research.

Tables

- account
- client
- loan
- transaction
- card
- district

Sessions

80

---

## Session Structure

| Tier | Sessions | Turns |
|-----|---------|------|
T1 | 90 | 1 |
T2 | 120 | 3–5 |
T3 | 90 | 6–10 |

Total sessions

300

Total turns

~1400

Memory-critical turns

~30%

---

# 6. Memory Architecture

Working memory

Redis session window

Episodic memory

ChromaDB / Pinecone vector store

Semantic memory

Schema documentation and glossary

Graph memory

Neo4j knowledge graph

---

# 7. Technology Stack

LLM

- OpenAI GPT-4o-mini
- Claude Sonnet

Embeddings

- text-embedding-3-small

Databases

- SQLite
- Redis
- ChromaDB
- Pinecone
- Neo4j

Observability

- Langfuse
- Weights & Biases

---

# 8. Repository Structure
agentic_memory/
│
├── MASTER_PLAN.md
├── SPEC.md
├── PHASES.md
│
├── data/
├── agents/
├── memory/
├── evaluation/
├── experiments/
├── config/
├── notebooks/
└── scripts/


---

# 9. Implementation Order

Phase 1  
Environment setup

Phase 2  
Dataset preparation

Phase 3  
Experiment 0

Phase 4  
Memory scaling experiment

Phase 5  
Backend benchmark

Phase 6  
Compression + retrieval experiments

Phase 7  
Staleness + multi-agent experiments

---

# 10. Estimated Cost

Experiment 0

~$12

Full experiment series

~$100–140

Using GPT-4o-mini.

---

# 11. Expected Contributions

EnterpriseMem-Bench will contribute:

1. Memory Benefit Score metric
2. Memory Scaling Efficiency metric
3. Retrieval Contamination Rate metric
4. Benchmark dataset for enterprise agent memory
5. Reference architecture for memory-enabled AI agents

---

# 12. Publication Plan

| Experiment | Forbes | Medium | Research |
|-----------|--------|--------|---------|
E0 | Article #2 | Deep Dive #2 | Paper 1 |
E0.5 | Article #3 | Deep Dive #3 | Paper 1 |
E1 | Article #4 | Deep Dive #4 | — |
E2 | Article #5 | Deep Dive #5 | Paper 2 |
E3 | Article #6 | Deep Dive #6 | Paper 2 |
E4 | Article #7 | Deep Dive #7 | Paper 3 |
E5 | Article #8 | Deep Dive #8 | Paper 3 |

---

# 13. Final Goal

Produce the first reproducible benchmark evaluating memory infrastructure for enterprise AI agents.

The final output is:

EnterpriseMem-Bench — an open benchmark suite for agent memory systems.
