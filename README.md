# Prompt Engineering & Production LLM Automation (Week 2)

A collection of three professional-grade Python applications built while mastering LLM prompt engineering, structured JSON validation, API rate-limit resilience, and streaming user experiences during Week 2 of an LLM engineering deep dive.

All tools in this repository utilize the modern Google GenAI SDK (google-genai) and are styled using Rich to produce elegant, terminal-based dashboard interfaces.

# 🛠️ Global System Setup

To run any of the applications in this repository locally, follow these steps:

### 1. Clone the Repository

git clone [https://github.com/DanielBasaznew/prompt-engineering-week2.git](https://github.com/DanielBasaznew/prompt-engineering-week2.git)
cd prompt-engineering-week2


### 2. Configure Your Environment

Create a .env file in the root directory to store your credentials securely:

GEMINI_API_KEY=your_actual_api_key_here


(Note: .env is pre-configured in .gitignore to prevent leaking your private API keys to public repositories).

### 3. Install Dependencies

Install all required libraries using pip:

pip install google-genai pydantic python-dotenv rich instructor


## 🚀 Projects Overview

### Project 1: Chain-of-Thought (CoT) Code Explainer (explainer_cot.py)

A command-line tool that breaks down complex code snippets for junior developers. It forces the LLM to output its raw thinking process step-by-step before compiling the final explanation.

Core Tech: Chain-of-Thought System Prompting, Regex Parsing, Error-safe local file readers.

How to Run (Interactive Paste Mode):

python explainer_cot.py


How to Run (File Mode):

python explainer_cot.py explainer_cot.py


How to Run (Hide Reasoning Trace):

python explainer_cot.py --hide explainer_cot.py


### Project 2: Streaming Structured Resume Reviewer (resume_reviewer.py)

An automated resume screener designed for technical recruiters. It forces Gemini to conform to a strict Pydantic schema using the Instructor parsing engine, while progressively streaming the results to the terminal in real-time.

Core Tech: Pydantic Schemas, Instructor Partial Parsing, Rich Live Displays, Micro-throttled visual rendering (80ms).

How to Run:

python resume_reviewer.py my_cv.txt


### Project 3: Resilient Email Writer (email_writer.py)

An AI administrative assistant that generates structured, copy-paste-ready business emails. To prevent unexpected runtime costs, it estimates input token usage and financial cost before triggering the LLM. It also features a self-healing client-side retry mechanism with exponential backoff.

Core Tech: Pre-flight token counting (client.models.count_tokens), Gemini Pricing models, Client-side Exponential Backoff (HTTP 429 Interception).

How to Run (Normal Mode):

python email_writer.py


How to Run (Rate-Limit Fault Injection Simulation):

python email_writer.py --simulate


## 🧠 Core Learnings & LLM Fundamentals

During this week's sprint, I mastered the following key concepts in prompt engineering and production AI architecture:

Structured Outputs vs. Raw JSON Mode: Direct JSON mode can result in broken keys or conversational markdown prefixes. Using Pydantic combined with Instructor enforces mathematical type safety, ensuring our app never crashes during parsing.

Chain-of-Thought (CoT) Reasoning: Forcing a model to work out logical steps inside <thinking> tags before delivering a final answer dramatically increases reasoning quality for complex code analysis.

Function/Tool Calling Mechanics: The LLM never actually runs Python code directly. It acts as a router that returns a tool request schema which our local application catches, runs, and resolves.

Structured Partial Streaming: Normal JSON parsers fail on partial data streams. Using Instructor allows us to dynamically close unfinished braces in memory, letting us stream strict structured data seamlessly.

Fault-Tolerant Client Designs: Real-world networks drop connections and hit rate limits (HTTP 429). Implementing client-side exponential backoff ensures our application heals itself rather than crashing.

Prompt Injection Vulnerabilities: Recognizing that user input must always be isolated so it cannot override or hijack the core instructions established in our system prompts.