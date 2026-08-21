"""
Quick end-to-end smoke test — no server needed.
Tests: data loading → ML prediction → ranking → explanation
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, os.path.dirname(__file__))

from core.prediction_service import generate_preference_list

print("Running end-to-end smoke test...")
print("Student: percentile=95.5, category=GOPENH, district=Pune, branch=CE/IT")
print("-" * 70)

entries = generate_preference_list(
    percentile=95.5,
    category_code="GOPENH",
    preferred_districts=["Pune", "Mumbai"],
    preferred_branch_codes=["CE", "IT", "AIDS"],
    max_reach=3,
    max_match=5,
    max_safe=3,
)

for e in entries:
    print(f"  #{e.rank:2d} [{e.classification:5s}] {e.college_name[:40]:<40} | {e.branch_code:5} | Cutoff: {e.lower_bound:.1f}-{e.upper_bound:.1f}")

print(f"\nTotal: {len(entries)} entries")
reach = sum(1 for e in entries if e.classification == "Reach")
match = sum(1 for e in entries if e.classification == "Match")
safe  = sum(1 for e in entries if e.classification == "Safe")
print(f"Reach: {reach}  Match: {match}  Safe: {safe}")
print("\nExplanation for #1:")
print(" ", entries[0].explanation)
print("\nSMOKE TEST PASSED")
