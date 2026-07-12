# Week 2 Learning Journal: Production LLM Engineering

This journal tracks my daily progress, code adjustments, architectural reflections, and technical breakthroughs during Week 2 of mastering prompt engineering and production AI patterns.

## 📅 Day 1 Reflection: Zero-Shot vs. Few-Shot Performance

### 1. Impact of Few-Shot Prompting on Output Quality

Observation: Transitioning from zero-shot to few-shot prompting produced a dramatic upgrade in output quality.

Key Improvements: By presenting the model with in-context examples, the generated explanations gained exceptional structural alignment, consistent technical tone, and highly predictable formatting. The model successfully bypassed generic, conversational filler and matched the exact level of granular detail specified in the examples.

### 2. Strategic Deployment: Zero-Shot vs. Few-Shot in Production

Zero-Shot Prompting: Ideal for low-friction, general-purpose tasks where instructions are explicit and strict formatting consistency is not a hard dependency. It is faster to design and minimizes input token consumption (saving costs).

Few-Shot Prompting: Essential for mission-critical production pipelines requiring high predictability, specialized domain styling, or strict schema adherence (e.g., structured data extraction, code explanation generation, and classification systems). The increase in input token overhead is a necessary investment for production-grade reliability.

## 📅 Day 2 Reflection: Prompt Engineering & API Limits

Key Learning: Investigated the power of Chain-of-Thought (CoT) prompting. Instructing the model to write down its logic inside <thinking> tags before outputting final answers significantly improves reasoning accuracy on complex tasks.

API Constraints: Experienced firsthand the strict rate limits and quotas associated with hitting advanced model APIs. This highlighted the immediate need for client-side resilience, cost controls, and rate-limit safety mechanisms in production scripts.

## 📅 Day 4 Reflection: File System Integration & Input Pipelines

Implementation: Upgraded the Resume Reviewer from a purely interactive input tool into a command-line utility with integrated file-handling logic.

Why it Matters: Real-world applications rarely rely on copy-pasting raw text into a terminal. Building an automated local file reader—with robust decoding try-except blocks to catch legacy encodings (like windows-1252)—makes the application incredibly durable and user-friendly.

## 📅 Day 5 Reflection: API Resilience & Cost Safeguards

Resilience: Implemented client-side exponential backoff to gracefully intercept and handle HTTP 429 Rate Limit errors. Instead of crashing the program, the script now automatically pauses, backs off, and heals the connection dynamically.

Pre-Flight Cost Controls: Created an estimation tool using client.models.count_tokens to calculate precise prompt token sizes and projected API costs prior to hitting the generator model. This prevents "runaway loop" charges and provides critical administrative insights before incurring costs.