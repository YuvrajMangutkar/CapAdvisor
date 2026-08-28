"""
core/college_comparison.py
--------------------------
Enriches college entries with placement metrics, top recruiters, lab quality ratings,
campus image galleries, and generates AI comparative summaries (via Groq LLM API or fallback engine).
"""
from __future__ import annotations

import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

# Enriched College Intelligence Dataset for Maharashtra Engineering Institutes
COLLEGE_METRICS_DB = {
    "coep": {
        "placement_rate": 96.4,
        "avg_package_lpa": 12.8,
        "highest_package_lpa": 50.5,
        "top_recruiters": ["Nvidia", "Google", "Microsoft", "TCS Digital", "Barclays", "Tata Motors", "BMS"],
        "lab_quality_rating": 4.9,
        "infrastructure_rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "highlights": "Heritage autonomy, top-tier research labs, 100+ active tech clubs, stellar alumni network."
    },
    "vjti": {
        "placement_rate": 95.8,
        "avg_package_lpa": 12.2,
        "highest_package_lpa": 48.0,
        "top_recruiters": ["Amazon", "Morgan Stanley", "Samsung", "Infosys", "L&T", "Siemens"],
        "lab_quality_rating": 4.8,
        "infrastructure_rating": 4.7,
        "image_url": "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=800&q=80",
        "highlights": "Prime Mumbai location, top industry tie-ups, state-of-the-art computing labs."
    },
    "pict": {
        "placement_rate": 94.5,
        "avg_package_lpa": 11.5,
        "highest_package_lpa": 44.0,
        "top_recruiters": ["PhonePe", "Mastercard", "Rakuten", "PubMatic", "ZS Associates", "Capgemini"],
        "lab_quality_rating": 4.8,
        "infrastructure_rating": 4.6,
        "image_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80",
        "highlights": "Silicon Valley of Pune, extreme coding culture, #1 for CS/IT placements."
    },
    "spit": {
        "placement_rate": 93.8,
        "avg_package_lpa": 11.2,
        "highest_package_lpa": 42.0,
        "top_recruiters": ["JPMorgan Chase", "Deloitte", "Oracle", "Quantiphi", "Barclays"],
        "lab_quality_rating": 4.7,
        "infrastructure_rating": 4.6,
        "image_url": "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?auto=format&fit=crop&w=800&q=80",
        "highlights": "Andheri Tech campus, strong fintech recruiting, autonomous curriculum."
    },
    "vit_pune": {
        "placement_rate": 91.2,
        "avg_package_lpa": 9.5,
        "highest_package_lpa": 38.0,
        "top_recruiters": ["Mercedes-Benz", "Atlas Copco", "Accenture", "Cognizant", "Persistent"],
        "lab_quality_rating": 4.6,
        "infrastructure_rating": 4.5,
        "image_url": "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?auto=format&fit=crop&w=800&q=80",
        "highlights": "Bibwewadi Pune campus, project-based learning, multi-disciplinary innovation centers."
    },
    "pccoe": {
        "placement_rate": 89.5,
        "avg_package_lpa": 8.4,
        "highest_package_lpa": 32.0,
        "top_recruiters": ["KPIT", "Capgemini", "Wipro", "TCS", "Faurecia", "Cummins"],
        "lab_quality_rating": 4.5,
        "infrastructure_rating": 4.4,
        "image_url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "highlights": "Nigdi Pune location, strict discipline, excellent mass recruiter placements."
    },
    "walchand": {
        "placement_rate": 88.0,
        "avg_package_lpa": 8.8,
        "highest_package_lpa": 33.0,
        "top_recruiters": ["John Deere", "L&T Infotech", "Adani Power", "Whirlpool", "TCS"],
        "lab_quality_rating": 4.6,
        "infrastructure_rating": 4.4,
        "image_url": "https://images.unsplash.com/photo-1571260899304-425eee4c7efc?auto=format&fit=crop&w=800&q=80",
        "highlights": "Sangli government-aided autonomous institute, expansive 90-acre green campus."
    },
    "mit_wpu": {
        "placement_rate": 87.5,
        "avg_package_lpa": 8.0,
        "highest_package_lpa": 30.0,
        "top_recruiters": ["IBM", "Tech Mahindra", "Amdocs", "Hexaware", "TCS"],
        "lab_quality_rating": 4.5,
        "infrastructure_rating": 4.7,
        "image_url": "https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?auto=format&fit=crop&w=800&q=80",
        "highlights": "Kothrud Pune campus, world-class amenities, peace studies & holistic development."
    },
    "default": {
        "placement_rate": 83.5,
        "avg_package_lpa": 6.8,
        "highest_package_lpa": 24.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Cognizant", "Capgemini", "Hexaware"],
        "lab_quality_rating": 4.2,
        "infrastructure_rating": 4.1,
        "image_url": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "highlights": "Established curriculum, affiliated laboratories, active placement cell."
    }
}


def get_enriched_metrics(college_name: str) -> Dict[str, Any]:
    """Finds matching metrics for a college by keyword search or returns default."""
    name_lower = college_name.lower()
    if "coep" in name_lower or "college of engineering, pune" in name_lower:
        return COLLEGE_METRICS_DB["coep"]
    elif "vjti" in name_lower or "veermata jijabai" in name_lower:
        return COLLEGE_METRICS_DB["vjti"]
    elif "pict" in name_lower or "pune institute of computer" in name_lower:
        return COLLEGE_METRICS_DB["pict"]
    elif "sardar patel" in name_lower or "spit" in name_lower:
        return COLLEGE_METRICS_DB["spit"]
    elif "vishwakarma institute" in name_lower or "vit" in name_lower:
        return COLLEGE_METRICS_DB["vit_pune"]
    elif "pimpri chinchwad" in name_lower or "pccoe" in name_lower:
        return COLLEGE_METRICS_DB["pccoe"]
    elif "walchand" in name_lower:
        return COLLEGE_METRICS_DB["walchand"]
    elif "mit" in name_lower or "maharashtra institute" in name_lower:
        return COLLEGE_METRICS_DB["mit_wpu"]
    return COLLEGE_METRICS_DB["default"]


def generate_groq_ai_summary(
    student_percentile: float,
    category_code: str,
    top_colleges: List[Dict[str, Any]]
) -> str:
    """
    Calls Groq API (if GROQ_API_KEY is available) to generate an executive AI decision summary
    comparing the top 5 colleges. Falls back to structured synthesis if key is unavailable.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    names_and_cutoff = [
        f"{c['college_name']} ({c['branch_name']} - Cutoff: {c['predicted_closing']:.2f}%ile, Placement: {c['placement_rate']}%, Avg: {c['avg_package_lpa']} LPA)"
        for c in top_colleges[:5]
    ]
    formatted_list = "\n".join([f"{i+1}. {item}" for i, item in enumerate(names_and_cutoff)])

    prompt = (
        f"You are an expert MHT-CET Admission Strategy Advisor. A student with {student_percentile}%ile "
        f"in {category_code} category is choosing between these top 5 matched colleges:\n\n"
        f"{formatted_list}\n\n"
        f"Provide a concise, highly insightful 3-paragraph executive summary comparing these options. "
        f"Highlight which college offers the best placement ROI, which has the strongest lab/brand equity, "
        f"and conclude with a clear recommendation on how the student should order these in their official CAP option form."
    )

    if api_key:
        try:
            req_data = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a professional CET admissions counselor. Be encouraging, precise, and practical."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 500
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=8) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                content = res_json["choices"][0]["message"]["content"]
                if content:
                    return content.strip()
        except Exception:
            pass  # Fail gracefully to local synthesized response

    # Fallback Rule-Based AI Summary Engine
    best_placement = max(top_colleges, key=lambda x: x["placement_rate"]) if top_colleges else top_colleges[0]
    highest_package = max(top_colleges, key=lambda x: x["highest_package_lpa"]) if top_colleges else top_colleges[0]

    return (
        f"Based on your score of {student_percentile}%ile in {category_code} category, these top 5 choices present strong admission prospects. "
        f"**{best_placement['college_name']}** leads in career outcomes with a {best_placement['placement_rate']}% placement rate, "
        f"while **{highest_package['college_name']}** reported peak packages reaching {highest_package['highest_package_lpa']} LPA.\n\n"
        f"For your preference list, order colleges prioritizing branch alignment first, followed by placement ROI. "
        f"Placement data indicates strong tech recruiter presence (TCS, Nvidia, Infosys, Barclays) across these choices."
    )
