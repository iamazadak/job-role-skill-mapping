import pandas as pd
import numpy as np
import json

df = pd.read_csv("processed_jobs.csv")

with open("skill_taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

skill_cols = taxonomy["skill_list"]
roles = df['standardized_role'].unique().tolist()

print("=== DEEP DATA ANALYST INSIGHTS ===")

# 1. Which Job Role Needs Which Skill Sets?
print("\n--- 1. ROLE VS SKILL BREAKDOWN (Top Skills per Role) ---")
role_skill_insights = {}
for role in sorted(roles):
    subset = df[df['standardized_role'] == role]
    skill_means = subset[skill_cols].mean() * 100
    top_skills = skill_means[skill_means > 0].sort_values(ascending=False).head(5)
    role_skill_insights[role] = {
        "job_count": len(subset),
        "total_vacancies": int(subset['vacancy_num'].sum()),
        "top_skills": top_skills.round(1).to_dict()
    }
    print(f"\n[Role: {role}] (Jobs: {len(subset)}, Vacancies: {subset['vacancy_num'].sum():,})")
    for s, pct in top_skills.items():
        print(f"  • {s}: {pct:.1f}%")

# 2. Compensation & Skill Premiums
print("\n--- 2. COMPENSATION BY ROLE ---")
sal_by_role = df.groupby('standardized_role')['monthly_salary'].agg(['count', 'median', 'mean', 'min', 'max'])
print(sal_by_role.round(0).to_string())

print("\n--- 3. SKILL PREMIUM (Median Salary WITH vs WITHOUT skill) ---")
skill_premiums = []
df_sal = df.dropna(subset=['monthly_salary'])
overall_median = df_sal['monthly_salary'].median()

for s in skill_cols:
    with_skill = df_sal[df_sal[s] == 1]['monthly_salary']
    without_skill = df_sal[df_sal[s] == 0]['monthly_salary']
    if len(with_skill) >= 5 and len(without_skill) >= 5:
        med_with = with_skill.median()
        med_without = without_skill.median()
        diff = med_with - med_without
        pct_diff = (diff / med_without) * 100
        skill_premiums.append({
            "skill": s,
            "jobs_with_skill": len(with_skill),
            "median_with": round(med_with, 0),
            "median_without": round(med_without, 0),
            "premium_rs": round(diff, 0),
            "premium_pct": round(pct_diff, 1)
        })

prem_df = pd.DataFrame(skill_premiums).sort_values(by="premium_rs", ascending=False)
print(prem_df.to_string(index=False))

# 4. Qualifications vs Roles
print("\n--- 4. QUALIFICATIONS PER ROLE (%) ---")
qual_role = pd.crosstab(df['standardized_role'], df['clean_qualification'], normalize='index') * 100
print(qual_role.round(1).to_string())

# Save insights to JSON
with open("deep_insights.json", "w", encoding="utf-8") as f:
    json.dump({
        "role_skills": role_skill_insights,
        "salary_by_role": sal_by_role.round(0).to_dict(orient="index"),
        "skill_premiums": skill_premiums
    }, f, indent=2)

print("\nInsights successfully saved to deep_insights.json")
