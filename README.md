# Jev-Enhanced AI Chatbot: Complete Guide & Architecture

This document provides a complete technical breakdown of **Jev** (by TypeSafe AI), its core primitives, and how it is integrated into a real-time Streamlit and OpenAI application (`app.py`) as a high-speed "System One" decision engine.

---

## 1. What is Jev? (What, Why, Where, How)

### What is Jev?
Jev is a specialized **"System One" decision model** created by TypeSafe AI. Unlike traditional Large Language Models (like GPT-4 or Claude) that generate paragraphs of prose token-by-token, Jev is built strictly to **evaluate state and return fast, typed, probabilistic decisions** (choices, scores, and probabilities) in milliseconds.

### Why Use Jev?
* **Extreme Cost Efficiency:** Jev charges only for input tokens at an aggressive rate (roughly **$0.042 per 1 million tokens**), and **output tokens are completely free** because it returns typed structures rather than text generation. With a $5 budget, you can run roughly 300,000+ evaluations.
* **Instant Safety Guardrails:** It flags prompt injections, toxic text, or severe policy violations before expensive LLMs are ever invoked.
* **Smart Intent Routing:** It automatically categorizes user intent (e.g., billing, technical, general) and urgency so your application logic can dynamically branch or tune system prompts.

### Where is it Used?
Jev sits right at the **front door** of your LLM workflow or chatbot application as a pre-flight filter, intercepting user inputs before they hit downstream orchestration pipelines or generative language models.

### How Does It Work?
Your application passes unstructured text or data (`state`) alongside a dictionary of questions using Jev's primitives. Jev evaluates everything in a single, ultra-fast parallel pass ($\sim$100ms) and returns structured telemetry.

### Visual Explainer: Jev and LLMs Have Different Jobs

Jev is a decision engine, not a chatbot. It is designed to inspect an input once and return a typed result that application code can use immediately. Rather than generating a multi-step explanation, it can answer focused operational questions such as “Is this request unsafe?” or “Which department should receive this message?” with a probability, score, or selected category.

An LLM serves a complementary role. It is the better tool when the application needs open-ended text, creative writing, detailed explanations, code generation, or a conversational answer. Jev does not replace an LLM; it helps decide whether, when, and how an LLM should be used.

For example, for the query “Is this urgent?”, an LLM might produce a written explanation. Jev can instead return a structured urgency score, confidence value, or route selection that the application can act on directly. This supports a practical pattern: use Jev for fast decisions, then use an LLM for richer generation when it adds value.



#### 1. What is Jev?

Jev is not a chatbot. It is a decision engine that evaluates input and returns a result application code can use immediately. Put it at the front of an AI workflow when you need a quick decision before a generative model is involved.

**Highlight: Decision Engine, Not a Chatbot**

#### 2. What does it do?

Instead of writing an essay, Jev returns a typed, structured result: for example, a selected category, a probability, or a score. This gives the application a direct signal for routing, safety checks, and prioritization.

**Highlight: Typed Answers, Zero Fluff**

#### 3. How does it do it?

The application supplies the input state and a set of focused questions in one `system_one()` call. Jev evaluates the state and returns structured outputs without requiring a generated step-by-step explanation. The app then applies its own business rules to those outputs.

**Highlight: One Pass. One Shot.**

#### 4. Jev vs. an LLM: what is the difference?

An LLM is built to generate text: stories, explanations, conversations, code, and summaries. Jev is built to produce a direct operational answer, such as a safety probability, urgency score, or routing choice. One creates language; the other creates application-ready signals.

**Highlight: Story vs. Straight Answer**

#### 5. Will Jev replace an LLM?

No. Jev is not intended to replace creative or conversational generation. It is most valuable as a sidekick: it decides whether a request should be blocked, handled on a fast path, or sent to an LLM with useful context. Together, the two tools support faster, safer, and more deliberate AI workflows.

**Highlight: Sidekick, Not a Successor**

> **Real-world use cases:** safety guardrails, prompt-injection checks, intent routing, department triage, urgency detection, and priority scoring. Different strengths create bigger possibilities.

### Presenter Script: Five Jev Talking Points

Use the following expanded version as narration for a short video segment:

1. **What is Jev?** Jev is a decision engine rather than a chatbot. It is designed to turn an input into an application-ready signal, so the workflow can decide what to do next without first asking a generative model to write a response.
2. **What does it do?** It skips the essay and returns a typed result, such as a selected intent, a safety probability, or an urgency score. The result is concise because the application needs a decision, not conversational text.
3. **How does it do it?** The application submits the state and focused questions in a single `system_one()` call. Jev evaluates that input and returns structured outputs; your own application rules determine the next action.
4. **How is it different from an LLM?** An LLM writes a full answer. Jev gives the application the signal behind the answer: for example, “route this to billing” or “block this request.” The contrast is story versus straight answer, not better versus worse.
5. **Will it replace an LLM?** No. LLMs remain the right tool for writing, chatting, explaining, and creative reasoning. Jev is the sidekick that helps the application use the LLM more deliberately.

For a video, frame the pairing as **different strengths, bigger possibilities**: Jev handles fast operational decisions, while the LLM provides the human-readable voice. If you plan to mention a specific founder or researcher background, verify that attribution against an official TypeSafe AI source before recording.

### Comparison: Traditional LLM and Jev

| Dimension | Traditional LLM | Jev |
| --- | --- | --- |
| Primary purpose | Generates conversational, creative, and explanatory text | Produces structured decisions for application control |
| Output style | Free-form prose generated token by token | Typed values such as choices, scores, and probabilities |
| Execution pattern | May reason through a response before producing text | Evaluates the supplied state against focused questions in one decision pass |
| Best fit | Open-ended questions, code, summaries, and conversation | Safety checks, intent routing, classification, and scoring |
| Confidence handling | May express confidence in generated prose | Returns calibrated decision-oriented values that application code can inspect |
| Relationship | Provides the rich final answer | Decides whether, where, or how to invoke the LLM |

### Same Query, Two Worlds

Consider the user question: **“Is this urgent?”** The two systems can support different application outcomes.

| LLM World | Jev World |
| --- | --- |
| The application supplies context and asks the model to generate a written answer. | The application supplies the state and asks focused scoring or routing questions. |
| Useful when the user needs an explanation, detailed text, or a conversational follow-up. | Useful when the application needs a direct decision, such as an urgency score or department route. |
| More generated text can mean more tokens, more latency, and more cost depending on the model and prompt. | Typed output can provide a compact signal for downstream application logic. |
| Example result: an explanatory response about why the request appears urgent. | Example result: confidence score `0.92`, route `Finance`, and a typed decision. |

**Same question, different speed, different cost.** This is an architectural comparison, not a universal performance guarantee: actual latency and cost depend on the model, prompt, service configuration, and workload.

### Reference Architecture

The chatbot separates fast decision-making from rich text generation:

```text
User message
    |
    v
Jev System One evaluation
    |-- unsafe or simple fast-path --> block or direct response
    |
    +-- safe request requiring generation --> OpenAI chat model
                                             |
                                             v
                                      generated response
```

This structure lets Jev handle routing, safety, and simple decisions before the application incurs a generative-model request. The model response is still appropriate for complex questions, and the application can surface Jev telemetry alongside it.

### Cost Example

The following is an illustrative calculation using the pricing and approximate token count shown in the reference material. A request with approximately 350 input tokens at $0.042 per one million input tokens is estimated as:

$$
\left(\frac{350}{1{,}000{,}000}\right) \times \$0.042 = \$0.0000147
$$

This example assumes that the Jev request returns typed values rather than generated output text. Verify current pricing, token accounting, and service terms in TypeSafe AI documentation before using this figure in production planning or published material.

---

## 2. Core Jev SDK Primitives

The Python SDK (`typesafe_sdk`) relies on four main building blocks:

1. **`TypeSafeClient`**: The core API connection object initialized with your `TYPESAFE_API_KEY` that communicates with the Jev backend.
2. **`Choice` (Classification)**: Used to sort an input into one of several predefined categories or routing buckets, returning the selected choice along with confidence scores and probability distributions.
3. **`Noul` (Yes/No Probability)**: Used for binary checks (derived from null/boolean logic). It evaluates a statement and returns a probability score between `0.0` and `1.0` (e.g., checking for safety risks or jailbreaks).
4. **`Score` (Rubric Scaling)**: Used to place an input onto an ordered, descriptive scale or severity rubric (e.g., measuring user frustration or urgency levels).

| Primitive / Class | Core Purpose | Output Provided | Typical Use Case |
| --- | --- | --- | --- |
| **`TypeSafeClient`** | API connector | Network handler | Initializing a connection to the Jev model API |
| **`Choice`** | Multi-class sorting | Selected option and probabilities | Intent routing, department triage, categorization |
| **`Noul`** | Binary check | True/False probability from `0.0` to `1.0` | Safety guardrails, prompt-injection detection, policy checks |
| **`Score`** | Rubric scaling | Ordered level and continuous score | Urgency detection, priority scoring, sentiment evaluation |

---

## 3. Architecture & `app.py` Code Explanation

The `app.py` script integrates Streamlit, Jev, and OpenAI into an interactive chat interface. 

### Step-by-Step Workflow:
1. **User Input:** The user types a message into the Streamlit chat interface (`st.chat_input`).
2. **Jev Pre-Flight Evaluation:** The message is sent to `jev_client.system_one(...)`, where three questions are evaluated in parallel:
   * `is_safe` (Noul) -> Evaluates safety violation risk.
   * `intent` (Choice) -> Classifies intent as `billing`, `technical`, or `general`.
   * `urgency` (Score) -> Ranks urgency on a scale.
3. **Smart Control Logic / Branching:**
   * **Safety Guardrail:** If `safety_prob > 0.75`, the app blocks the request instantly without waking up OpenAI and returns a policy error.
   * **Fast-Path Greeting:** If the user types a pure, ultra-short greeting (e.g., "hi", "hello") with low urgency, it serves a fast hardcoded response.
   * **OpenAI Fallback:** Informational queries (like *"tell me about Patliputra"*) pass through to OpenAI (`gpt-4o-mini`), injecting Jev's intent and urgency metadata directly into the system prompt to tailor the AI's tone and depth.
4. **UI & Telemetry Display:** Streamlit maintains message history in `st.session_state` and renders an expandable UI section under each assistant response detailing Jev's exact metrics.

---

## 4. Complete `app.py` Source Code

```python
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
from streamlit.errors import StreamlitSecretNotFoundError

# 1. Page Configuration
st.set_page_config(
    page_title="Jev-Powered Smart Chatbot",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Jev-Enhanced AI Chatbot")
st.markdown("This chatbot uses **TypeSafe AI's Jev** as a high-speed System One decision engine for pre-flight safety screening and intent routing before hitting OpenAI.")

# 2. Load environment variables & initialize clients
load_dotenv()

# Load API keys from Streamlit secrets (Cloud) or environment variables (Local)
def get_config_value(name: str) -> str | None:
    try:
        return st.secrets.get(name) or os.getenv(name)
    except StreamlitSecretNotFoundError:
        return os.getenv(name)

openai_api_key = get_config_value("OPENAI_API_KEY")
typesafe_api_key = get_config_value("TYPESAFE_API_KEY")

if not openai_api_key:
    st.error("❗️ OPENAI_API_KEY not found. Please set it in your environment variables or Streamlit secrets.")
    st.stop()

if not typesafe_api_key:
    st.warning("⚠️ TYPESAFE_API_KEY not found. Ensure it is configured so Jev pre-flight checks can run.")

# Initialize Clients
jev_client = TypeSafeClient()  # Automatically reads TYPESAFE_API_KEY from environment
openai_client = OpenAI(api_key=openai_api_key)

# 3. Core Processing Function with Jev Integration
def process_chat_message(user_message: str):
    # ----------------------------------------------------
    # STEP 2: Jev "System One" Pre-Flight Check (Fast & Cheap)
    # ----------------------------------------------------
    try:
        jev_response = jev_client.system_one(
            state=user_message,
            questions={
                "is_safe": Noul(
                    instructions="Does this message contain severe abuse, hate speech, or dangerous jailbreak attempts?"
                ),
                "intent": Choice(
                    instructions="What is the primary intent of the user?",
                    criteria={
                        "billing": "Questions about payments, invoices, subscriptions, or refunds",
                        "technical": "Bugs, errors, code issues, or system outages",
                        "general": "General conversation, casual greetings, or basic inquiries"
                    }
                ),
                "urgency": Score(
                    instructions="How urgent or frustrated is the user?",
                    criteria=["Low", "Medium", "High"]
                )
            }
        )

        # Extract results from Jev's structured output
        safety_prob = jev_response.nouls["is_safe"].noul
        intent_choice = jev_response.answers["intent"].choice
        intent_confidence = jev_response.answers["intent"].confidence
        urgency_score = jev_response.scores["urgency"].score

    except Exception as e:
        # Fallback defaults if Jev service encounters an issue
        safety_prob = 0.0
        intent_choice = "general"
        intent_confidence = 1.0
        urgency_score = 0.0
        st.toast(f"Jev check warning: {e}", icon="⚠️")

    # Telemetry dictionary to display in the UI expander
    telemetry = {
        "safety_risk": safety_prob,
        "intent": intent_choice,
        "intent_confidence": intent_confidence,
        "urgency": urgency_score
    }

    # ----------------------------------------------------
    # STEP 3: Application Control Logic (Smart Branching)
    # ----------------------------------------------------
    
    # Condition A: Block unsafe inputs immediately without waking up OpenAI
    if safety_prob > 0.75:
        reply = "I'm sorry, but I cannot process requests that violate our safety policies."
        return reply, telemetry

    # Condition B: Only intercept true, ultra-short greetings for the fast path
    is_pure_greeting = user_message.lower().strip() in ["hi", "hello", "hey", "good morning", "good evening", "greetings"]
    if is_pure_greeting and urgency_score < 0.5:
        reply = "Hello! How can I help you today?"
        return reply, telemetry

    # ----------------------------------------------------
    # STEP 4: Fall back to OpenAI Chat LLM for full generation
    # ----------------------------------------------------
    system_prompt = (
        f"You are a helpful assistant. "
        f"The user's intent has been classified as '{intent_choice}' "
        f"with an urgency rating level of {urgency_score:.1f} out of 2. Tailor your tone and provide a complete, informative response."
    )

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )

    reply = completion.choices[0].message.content
    return reply, telemetry

# 4. Streamlit Chat Interface Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "telemetry" in message and message["role"] == "assistant":
            with st.expander("⚡ Jev Telemetry & Routing Details"):
                t = message["telemetry"]
                st.markdown(f"Safety Violation Risk: {t['safety_risk']:.2f}")
                st.markdown("")
                st.markdown(f"Classified Intent: {t['intent']} (Confidence: {t['intent_confidence']:.2f})")
                st.markdown("")
                st.markdown(f"Urgency Score (0-2): {t['urgency']:.2f}")

# Accept user chat input
if user_input := st.chat_input("Type your message here..."):
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process message through Jev + OpenAI pipeline
    with st.chat_message("assistant"):
        with st.spinner("⚡ Jev is evaluating safety and routing..."):
            response_text, telemetry_data = process_chat_message(user_input)
        
        st.markdown(response_text)
        
        # Show telemetry expander under the fresh message with exact custom formatting
        with st.expander("⚡ Jev Telemetry & Routing Details"):
            st.markdown(f"Safety Violation Risk: {telemetry_data['safety_risk']:.2f}")
            st.markdown("")
            st.markdown(f"Classified Intent: {telemetry_data['intent']} (Confidence: {telemetry_data['intent_confidence']:.2f})")
            st.markdown("")
            st.markdown(f"Urgency Score (0-2): {telemetry_data['urgency']:.2f}")

    # Append assistant response and telemetry to history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "telemetry": telemetry_data
    })
