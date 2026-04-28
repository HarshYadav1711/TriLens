# TriLens — A Deterministic Reflection System

TriLens is a structured, deterministic reflection tool for understanding how someone showed up during their day.

It does not generate advice.
It does not interpret free text.
It does not rely on any model at runtime.

Instead, it encodes reflection into a decision tree.

The result is a system where:

* every question is intentional
* every answer is meaningful
* every path is traceable

Same inputs always produce the same outputs.

---

## What This Is Actually Solving

Most reflection tools fail in two ways:

They are either too open-ended, which makes reflection vague, or
they rely on AI, which makes the system unpredictable.

TriLens takes a different approach.

It removes ambiguity at the point of thinking.

Instead of asking the user to “reflect”, it presents a small set of carefully designed choices that represent different ways of responding, contributing, and perceiving.

The insight comes from choosing.

---

## The Core Structure

The system is built around three axes, explored in sequence:

**1. Locus (Agency)**
Did I act on what I could influence, or react to what happened?

**2. Orientation (Contribution)**
Was I focused on what I gave, or what I expected?

**3. Radius (Perspective)**
Was my thinking centered on myself, or did it include others?

Each axis narrows the lens and then expands it.

The conversation is short, but cumulative. By the end, the user has a clearer view of their own behavior across the day.

---

## How It Works

The product is the tree.

* Questions have fixed options only
* Each option leads to a known next step
* Decision nodes route deterministically
* Reflection nodes reframe without judging
* Signals are accumulated to produce a final summary

There is no scoring model.
There is no hidden logic.
There is no runtime inference.

Everything is visible in the data.

---

## What This Deliberately Does Not Do

These are design choices to protect clarity, auditability, and trust:

* No AI usage at runtime
* No free text input
* No probabilistic outputs
* No hidden logic

---

## Why Deterministic

Reflection requires trust.

If the same answers can produce different outputs, the system becomes difficult to rely on. If reasoning is hidden, it becomes difficult to question.

By keeping the system deterministic:

* every output is explainable
* every path is auditable
* every improvement can be made at the level of structure

This makes reflection something you can design and inspect, not guess at.

---

## Project Structure

/tree

* reflection-tree.json
* reflection-tree.tsv
* tree-diagram.md

/agent

* main.py
* web.html

/transcripts

* persona-1.md
* persona-2.md

write-up.md

---

## Running the Agent

CLI:

```
cd agent
python main.py
```

Web:

Open `web.html` in a browser.

No installation. No API keys. No external services.

---

## Design Decisions

* Fixed options instead of free text to remove ambiguity at the point of choice
* Sequential axes instead of independent sections to preserve psychological flow
* Reflection nodes instead of feedback to avoid judgment
* Minimal runtime logic to keep the system inspectable

Most of the effort went into designing the options, not the code.

---

## What I Paid Attention To

Whether a tired person at the end of the day would actually pause before choosing an answer.

If the options are too obvious, the system becomes a formality.
If they are too abstract, the system becomes friction.

The goal was to sit exactly in between.

---

## What I Would Improve

* Deeper branching for repeated behavioral patterns
* More nuanced summaries based on combined signals
* Real user testing to refine where people hesitate or rush
* Expansion of the third axis into system-level or customer impact

---

## Closing Note

This project is an attempt to take something inherently fuzzy — how a person thinks about their day — and make it structured without making it mechanical.

The constraint of determinism turned out to be useful.

It forces clarity at every step.

And once the structure is right, the reflection follows.
