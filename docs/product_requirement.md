# Product Requirements Document (PRD): "The Modern Sage"

## 1. Product Overview
**"The Modern Sage"** is a conversational AI assistant that provides holistic self-help advice by synthesizing wisdom from two distinct domains:
1.  **Modern Behavioral Science** (e.g., *Atomic Habits*, *Thinking, Fast and Slow*, *Ikigai*)
2.  **Timeless Spiritual Wisdom** (e.g., *The Bhagavad Gita*)

The goal is to offer users a balanced perspective—practical, actionable steps backed by science, grounded in deep spiritual or philosophical meaning.

## 2. Core Value Proposition
-   **Holistic Guidance**: Answers combine "The Why" (Wisdom) with "The How" (Tactics).
-   **Structured Dual-Perspective**: Every answer is explicitly split into a "Spiritual Perspective" (Gita) and a "Scientific Perspective" (Modern).
-   **Trust & Verifiability**: Strict citation quotas (2-3 Gita, 3-4 Modern) ensure the AI never hallucinates advice.

## 3. Key Features

### 3.1. The "Sage" Chat Interface
-   **Dynamic Research**: Users can ask natural language questions (e.g., "Why do I fail at my goals?"). The system performs detailed research using semantic search and query dissection.
-   **Streaming Responses**: Answers appear token-by-token for a responsive feel.

### 3.2. Knowledge Base (The "Library")
-   **Content Types**: Semantic Chunking of key texts.
-   **Domains**: 
    -   *Science/Strategy*: Atomic Habits, Thinking Fast and Slow, The 7 Habits of Highly Effective People, Ikigai.
    -   *Spirituality/Philosophy*: The Bhagavad Gita.

### 3.3. Response Structure (Strict V2)
The AI response enforces a rigid structure:
1.  **The Spiritual Perspective (Ancient Wisdom)**:
    -   Must cite *The Bhagavad Gita* (2-3 citations).
    -   Focus: Dharma, Detachment, Inner Peace.
2.  **The Scientific Perspective (Modern Strategy)**:
    -   Must cite Modern Texts (3-4 citations).
    -   Focus: Psychology, Habit Loops, Decision Making.

## 4. Success Metrics
-   **Citation Accuracy**: 100% of claims must have an inline citation `[Source: Book, Ch X]`.
-   **Recall**: The system must retrieve relevant chunks even for abstract queries (via Semantic Chunking & Query Fusion).
-   **Performance**: <4s time-to-first-token (achieved via Pinecone Serverless).



