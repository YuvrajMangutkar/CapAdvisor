"""
core/explainer.py
-----------------
Generates human-readable explanations for each ranked college entry.

Two modes:
  1. Rule-based (default, no API key needed) — template-driven, always available.
  2. OpenAI-enhanced (optional) — richer context via LLM if OPENAI_API_KEY is set.

For the LLM path, we use a simple RAG pattern:
  - Retrieve placement/trend context from a static knowledge dict (no vector DB needed
    for MVP; can upgrade to pgvector later).
  - Inject into prompt → get back a polished explanation.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    from openai import OpenAI
    _groq_key = os.getenv("GROQ_API_KEY")
    _openai_key = os.getenv("OPENAI_API_KEY")
    if _groq_key:
        _llm_client = OpenAI(
            api_key=_groq_key,
            base_url="https://api.groq.com/openai/v1",
        )
        _llm_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    elif _openai_key:
        _llm_client = OpenAI(api_key=_openai_key)
        _llm_model = "gpt-4o-mini"
    else:
        _llm_client = None
        _llm_model = ""
    HAS_LLM = bool(_llm_client)
except ImportError:
    HAS_LLM = False
    _llm_client = None
    _llm_model = ""

# Static context snippets per college (RAG knowledge base — MVP version)
COLLEGE_CONTEXT = {
    "College of Engineering Pune (COEP)": "COEP is a premier Autonomous Institute under Savitribai Phule Pune University. Known for strong placements in CS/IT (avg 8–12 LPA). Highly competitive cutoffs — consistently among the top 2 in Maharashtra CAP.",
    "Veermata Jijabai Technological Institute (VJTI)": "VJTI Mumbai is one of Maharashtra's oldest and most prestigious engineering colleges. Located in Mumbai, it offers strong industry connections, avg placements 8–15 LPA for CS. Cutoffs are among the highest in the state.",
    "DJ Sanghvi College of Engineering": "DJ Sanghvi is a well-regarded Mumbai college affiliated to Mumbai University. Known for CS/IT with good placement records (avg 6–10 LPA). Popular among students preferring the Mumbai job market.",
    "KJ Somaiya College of Engineering": "KJ Somaiya is a strong Mumbai unaided college with a vibrant campus and good industry connect. CS/AIDS branches see high demand. Avg placements 5–9 LPA.",
    "Pune Institute of Computer Technology (PICT)": "PICT is a CS-focused college in Pune known for its strong alumni network and consistently good placements in product and service companies. Avg 7–11 LPA for CS/IT.",
    "Vishwakarma Institute of Technology (VIT Pune)": "VIT Pune is a well-established autonomous institute known for its research culture and good campus placements. Strong in CS/IT/ETE branches.",
    "Sardar Patel College of Engineering (SPCE)": "SPCE is a government-aided college in Mumbai with strong fundamentals programs. Good industry connect through alumni networks in Mumbai/Pune corridor.",
    "MIT College of Engineering Pune": "MIT Pune (not to be confused with MIT USA) is one of Pune's larger unaided colleges with broad branch offerings. Good placements, campus recruiters include TCS, Infosys, and startups.",
    "Walchand College of Engineering Sangli": "Walchand Sangli is a government-aided college known for its discipline and academic rigor. Good choice for students from Southern Maharashtra wanting quality education at lower cost.",
}


def _rule_based_explanation(entry) -> str:
    """
    Template-driven explanation. Always available, no API needed.
    """
    from core.classifier import SAFE_BUFFER

    tier = entry.classification
    pct  = entry.predicted_closing
    lo   = entry.lower_bound
    hi   = entry.upper_bound
    spct = round(entry.feasibility * 100, 0)  # rough admit probability

    if tier == "Safe":
        margin = round(entry.predicted_closing - entry.lower_bound + SAFE_BUFFER, 1)
        return (
            f"Your percentile comfortably exceeds the predicted cutoff range ({lo:.1f}–{hi:.1f}). "
            f"This is a Safe choice — very high probability of admission. "
            f"Listed here as a fallback in case Reach/Match options don't work out."
        )
    elif tier == "Match":
        return (
            f"Your percentile falls within the predicted cutoff range ({lo:.1f}–{hi:.1f} percentile). "
            f"This is a Match — you have a realistic chance, but admission isn't guaranteed. "
            f"Ordering this above your Safe options in the CAP list gives you the best shot."
        )
    elif tier == "Reach":
        gap = round(lo - entry.feasibility, 1)
        return (
            f"Your percentile is slightly below the optimistic cutoff estimate ({lo:.1f}). "
            f"This is a Reach — admission depends on competition being slightly lower than predicted. "
            f"Worth listing first; if the cutoff drops even modestly, you could get in."
        )
    return "See predicted cutoff range for details."


def _llm_explanation(entry, college_context: str = "") -> str:
    """Generate a richer explanation using the OpenAI API."""
    if not HAS_LLM or _llm_client is None:
        return _rule_based_explanation(entry)

    system_prompt = (
        "You are an expert advisor helping Indian engineering students fill their "
        "CAP round college preference list. Write concise, encouraging, and accurate "
        "explanations (2-3 sentences) for why a college was ranked at a particular "
        "position. Be specific about the percentile numbers. Avoid filler phrases."
    )

    user_prompt = f"""
College: {entry.college_name}
Branch: {entry.branch_name}
Student's Percentile: {entry.feasibility}
Predicted Cutoff Range: {entry.lower_bound:.1f}–{entry.upper_bound:.1f}
Classification: {entry.classification}
CAP List Rank: #{entry.rank}
College Context: {college_context or "A well-regarded Maharashtra engineering college."}

Write a 2-3 sentence explanation for why this college is ranked #{entry.rank} in the student's preference list.
""".strip()

    try:
        response = _llm_client.chat.completions.create(
            model=_llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=120,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return _rule_based_explanation(entry)


def explain(entry) -> str:
    """
    Main entry point: generate explanation for a CollegeEntry.
    Uses LLM if API key available, else rule-based.
    """
    college_ctx = COLLEGE_CONTEXT.get(entry.college_name, "")
    if HAS_LLM:
        return _llm_explanation(entry, college_ctx)
    return _rule_based_explanation(entry)


def explain_batch(entries: list) -> list:
    """Add explanations to a list of CollegeEntry objects (in-place)."""
    for entry in entries:
        entry.explanation = explain(entry)
    return entries
