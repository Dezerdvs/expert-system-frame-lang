# Frame-Based Expert System & Knowledge Base Engine

![CI](https://github.com/Dezerdvs/expert-system-frame-lang/actions/workflows/ci.yml/badge.svg)

A from-scratch implementation of a **frame-based knowledge representation system** (in the classic AI sense — think Minsky's "frames", the precursor to modern object-oriented modeling), plus a small natural-language search engine built on top of it.

## What it does

- **`frame_lang.py`** — the core language: `Frame`, `Slot`, and `Demon` (attached procedures that fire on get/set/call — similar to property getters/setters with side effects, plus inheritance between frames)
- **`kb.py`** — a `KnowledgeBase` that manages a collection of frames: create, destroy, look up, and query by type/inheritance
- **`rule_checker.py`** — validates logical rules/constraints over the knowledge base
- **`executor.py`** — runs procedures attached to frames
- **`domain_text_processing.py`** — builds a domain-specific frame structure out of raw text (tokenizing/parsing text into frames)
- **`search_engine.py`** — a `SearchEngine` + `Query` layer that lets you search over the populated knowledge base
- **`main_demo.py`** — wires everything together into a runnable demo, including lazy "parse on demand" logic via attached procedures and inheritance-aware attribute resolution

## Tech stack

Pure Python, using type hints (`typing`) for a clear internal API — no external dependencies.

## Running

```bash
python main_demo.py
```

## Why it matters

This reimplements a classic AI knowledge-representation paradigm (frames + slots + inheritance + attached procedures/"demons") from scratch, then applies it to a practical text-processing/search task — a good demonstration of both AI fundamentals and clean object-oriented Python design.
