import pandas as pd
import numpy as np
import re
import json

def process_data(input_csv="job-list.csv", output_csv="processed_jobs.csv"):
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} raw job rows.")

    # 1. Clean Vacancy
    df['vacancy_num'] = pd.to_numeric(df['vacancy'], errors='coerce').fillna(1).astype(int)
    # If vacancy was 0, assume at least 1 opening
    df['vacancy_num'] = df['vacancy_num'].apply(lambda x: max(1, x))

    # 2. Standardize Role
    def categorize_role(job_name, desc="", resp="", qual=""):
        text = f"{str(job_name)} {str(desc)} {str(resp)} {str(qual)}".lower()
        if any(k in text for k in ['forklift', 'flt', 'reach truck', 'rt operator', 'aflt', 'bopt', 'stacker', 'pallet truck']):
            return "Material Handling & Heavy Equipment"
        elif any(k in text for k in ['picker', 'packer', 'picking', 'packing', 'warehouse', 'store', 'inventory', 'dispatch', 'sorter', 'loading', 'unloading']):
            return "Warehouse, Logistics & Fulfillment"
        elif any(k in text for k in ['quality inspector', 'qa', 'qc', 'quality control', 'quality assurance', 'inspector', 'inspection', 'testing', 'quality audit']):
            return "Quality Assurance & Inspection"
        elif any(k in text for k in ['welder', 'welding', 'fitter', 'fabricat', 'electrician', 'maintenance', 'tool & die', 'tool and die']):
            return "Welding, Fitting & Technical Trades"
        elif any(k in text for k in ['cnc', 'vmc', 'lathe', 'miller', 'turner', 'machinist', 'press operator', 'molding', 'machine operator', 'machine operating']):
            return "CNC & Machine Operation"
        elif any(k in text for k in ['trainee', 'apprentice', 'naps', 'nats', 'training']):
            return "Industrial & Apprentice Trainee"
        elif any(k in text for k in ['sales', 'marketing', 'telecaller', 'customer', 'retail', 'promoter', 'cashier']):
            return "Sales, Retail & Commercial"
        elif any(k in text for k in ['supervisor', 'engineer', 'lead', 'manager', 'incharge']):
            return "Engineering & Supervision"
        elif any(k in text for k in ['assembly', 'production', 'operator', 'helper', 'line operator', 'manufacturing']):
            return "Assembly & Production Associate"
        else:
            return "General Production & Support"

    df['standardized_role'] = df.apply(
        lambda r: categorize_role(r['job_name'], r['job_description'], r['job_responsibilities'], r['highest_qualifications']),
        axis=1
    )

    # 3. Clean Qualifications
    def standardize_qualification(val):
        if pd.isnull(val):
            return "Not Specified"
        s = str(val).lower()
        if any(k in s for k in ['b. tech', 'btech', 'b.e', 'engineering', 'graduate', 'degree']):
            return "Graduate / B.Tech / BE"
        elif 'diploma' in s:
            return "Diploma (Polytechnic)"
        elif any(k in s for k in ['i.t.i', 'iti']):
            return "I.T.I (Vocational)"
        elif any(k in s for k in ['12th', 'hsc', 'puc']):
            return "Higher Secondary (12th)"
        elif any(k in s for k in ['10th', 'ssc']):
            return "Secondary (10th)"
        elif '8th' in s:
            return "Below 10th (8th Standard)"
        else:
            return "General / Other"

    df['clean_qualification'] = df['highest_qualifications'].apply(standardize_qualification)

    # 4. Clean Salary
    def parse_num_or_range(val):
        if pd.isnull(val):
            return None
        s = str(val).replace(',', '').replace('₹', '').strip()
        nums = re.findall(r'(\d+(?:\.\d+)?)', s)
        if not nums:
            return None
        valid_nums = [float(n) for n in nums if float(n) > 500]
        return np.mean(valid_nums) if valid_nums else None

    def extract_salary(row):
        for col in ['gross_pay', 'stipend', 'net_take_home_pay']:
            parsed = parse_num_or_range(row[col])
            if parsed and parsed > 1000:
                return parsed
        
        ctc = parse_num_or_range(row['ctc'])
        if ctc and ctc > 1000:
            return round(ctc / 12, 1) if ctc > 60000 else ctc

        st = str(row['stipend_tiers'])
        if pd.notnull(st) and '₹' in st:
            matches = re.findall(r'₹\s*(\d+)', st)
            if matches:
                nums = [float(m) for m in matches if float(m) > 1000]
                if nums:
                    return np.mean(nums)
                    
        match_title = re.search(r'rs\.?\s*(\d{4,6})', str(row['job_name']), re.IGNORECASE)
        if match_title:
            return float(match_title.group(1))

        return np.nan

    df['monthly_salary'] = df.apply(extract_salary, axis=1)

    def salary_tier(sal):
        if pd.isnull(sal):
            return "Undisclosed / Negotiable"
        elif sal < 14000:
            return "Entry Level (< ₹14k)"
        elif sal <= 18000:
            return "Standard (₹14k - ₹18k)"
        elif sal <= 22000:
            return "Skilled (₹18k - ₹22k)"
        else:
            return "Specialized (> ₹22k)"

    df['salary_tier'] = df['monthly_salary'].apply(salary_tier)

    # 5. Clean Experience
    def clean_experience(val):
        if pd.isnull(val):
            return "Fresher / Entry Level"
        s = str(val).lower().strip()
        if any(k in s for k in ['nil', 'fresher', 'freshar', 'no', '0', 'nr', 'na', 'none']):
            return "Fresher / Entry Level"
        elif any(k in s for k in ['0-1', '1 yr', '1yr', '1 year', '1']):
            return "0 - 1 Year"
        elif any(k in s for k in ['1-2', '2 yr', '2yr', '2 years', '2']):
            return "1 - 2 Years"
        elif any(k in s for k in ['2-3', '3 yr', '3 year', '3-5', '4', '5']):
            return "2 - 5 Years"
        else:
            return "Fresher / Entry Level"

    df['clean_experience'] = df['experience'].apply(clean_experience)

    # 6. Clean Age Limits
    def parse_age(val):
        if pd.isnull(val):
            return 18, 35
        s = str(val).strip()
        nums = [int(n) for n in re.findall(r'\d+', s)]
        if len(nums) >= 2:
            return min(nums), max(nums)
        elif len(nums) == 1:
            if nums[0] <= 21:
                return nums[0], 30
            else:
                return 18, nums[0]
        return 18, 35

    ages = df['age_limit'].apply(parse_age)
    df['min_age'] = [a[0] for a in ages]
    df['max_age'] = [a[1] for a in ages]

    # 7. Clean Gender Preference
    def clean_gender(val):
        if pd.isnull(val):
            return "Any"
        s = str(val).capitalize().strip()
        return s if s in ["Any", "Male", "Female"] else "Any"

    df['clean_gender'] = df['gender_preference'].apply(clean_gender)

    # 8. Clean State & Industry
    df['clean_state'] = df['state'].fillna("Not Specified").str.strip()
    df['clean_industry'] = df['industry_sector'].fillna("General Manufacturing / Other").str.strip()

    # 9. Skill Taxonomy & Extraction
    SKILL_TAXONOMY = {
        # Equipment & Machining
        "CNC Operation": r"\b(cnc|computer numerical control|fanuc|siemens|turner|miller|machining center)\b",
        "VMC Operation": r"\b(vmc|vertical machining)\b",
        "Lathe & Milling Machine": r"\b(lathe|milling|drill press|boring)\b",
        "Grinding & Polishing": r"\b(grind|grinder|grinding|buffing|polishing)\b",
        "Press & Stamping": r"\b(press machine|power press|hydraulic press|stamping|punching)\b",
        "Injection Molding": r"\b(injection mold|moulding|plastic injection|die casting)\b",
        "Machine Setup & Tooling": r"\b(machine setup|tool setting|clamping|fixture|tool change)\b",
        
        # Logistics & Material Handling
        "Forklift Operation (FLT)": r"\b(forklift|flt|counterbalance)\b",
        "Reach Truck Operation (RT)": r"\b(reach truck|rt operator|high reach)\b",
        "Articulated Forklift (AFLT)": r"\b(aflt|articulated forklift)\b",
        "BOPT & Pallet Truck": r"\b(bopt|pallet truck|hand pallet|stacker)\b",
        "Order Picking & Packing": r"\b(pick|picking|packer|packing|carton packing|bundling)\b",
        "Inventory & Stock Auditing": r"\b(inventory|stock count|stock audit|cycle count|replenishment)\b",
        "Loading & Unloading": r"\b(loading|unloading|dock|inward|outward|dispatch|dispatching)\b",
        "Barcode Scanning & WMS": r"\b(barcode|rf scanner|wms|warehouse management|system entry)\b",

        # Quality & Metrology
        "Vernier Caliper & Micrometer": r"\b(vernier|caliper|micrometer|dial gauge|height gauge|bore gauge)\b",
        "Dimensional Measurement": r"\b(dimensional|measurement|tolerance|inspection|gauge|gauges)\b",
        "Blueprint & Drawing Reading": r"\b(blueprint|drawing|engineering drawing|specifications)\b",
        "Visual Quality Inspection": r"\b(visual inspection|defect|burr|scratch|rejection|sorting)\b",
        "5S & Workplace Organization": r"\b(5s|5-s|kaizen|housekeeping|workplace organization)\b",
        
        # Technical Trades & Fabrication
        "Welding (MIG/TIG/Arc)": r"\b(weld|welder|welding|mig|tig|arc welding|spot weld)\b",
        "Fitting & Mechanical Assembly": r"\b(fitter|fitting|mechanical assembly|bench work)\b",
        "Electrical Maintenance & Wiring": r"\b(electric|electrical|wiring|panel|circuit|multimeter)\b",
        "Preventive Maintenance": r"\b(preventive maintenance|maintenance|lubrication|troubleshoot)\b",
        
        # Safety & Commercial
        "PPE & Industrial Safety": r"\b(ppe|safety shoes|helmet|goggles|safety gear|safety procedures|hazard)\b",
        "Material Traceability & Reporting": r"\b(traceability|log sheet|report|checklist|documentation|sop)\b",
        "Customer Service & Retail Sales": r"\b(customer|sales|selling|cashier|billing|merchandise)\b"
    }

    df['combined_text'] = (
        df['job_name'].fillna('') + " " +
        df['job_description'].fillna('') + " " +
        df['job_responsibilities'].fillna('') + " " +
        df['highest_qualifications'].fillna('') + " " +
        df['specializations'].fillna('') + " " +
        df['industry_sector'].fillna('')
    ).str.lower()

    skill_names = list(SKILL_TAXONOMY.keys())
    for skill_name, pattern in SKILL_TAXONOMY.items():
        regex = re.compile(pattern, re.IGNORECASE)
        df[skill_name] = df['combined_text'].apply(lambda x: 1 if regex.search(x) else 0)

    # Calculate skill counts per job
    df['total_skills_tagged'] = df[skill_names].sum(axis=1)

    # Save processed dataframe
    df.to_csv(output_csv, index=False)
    print(f"Enriched dataset saved to {output_csv} with {len(df.columns)} columns.")

    # Save skill taxonomy metadata for Streamlit
    with open("skill_taxonomy.json", "w", encoding="utf-8") as f:
        json.dump({
            "categories": {
                "Machining & Equipment": [
                    "CNC Operation", "VMC Operation", "Lathe & Milling Machine", 
                    "Grinding & Polishing", "Press & Stamping", "Injection Molding", "Machine Setup & Tooling"
                ],
                "Material Handling & Logistics": [
                    "Forklift Operation (FLT)", "Reach Truck Operation (RT)", "Articulated Forklift (AFLT)",
                    "BOPT & Pallet Truck", "Order Picking & Packing", "Inventory & Stock Auditing",
                    "Loading & Unloading", "Barcode Scanning & WMS"
                ],
                "Quality & Metrology": [
                    "Vernier Caliper & Micrometer", "Dimensional Measurement", "Blueprint & Drawing Reading",
                    "Visual Quality Inspection", "5S & Workplace Organization"
                ],
                "Technical Trades & Maintenance": [
                    "Welding (MIG/TIG/Arc)", "Fitting & Mechanical Assembly",
                    "Electrical Maintenance & Wiring", "Preventive Maintenance"
                ],
                "Safety & Operations": [
                    "PPE & Industrial Safety", "Material Traceability & Reporting", "Customer Service & Retail Sales"
                ]
            },
            "skill_list": skill_names
        }, f, indent=2)

if __name__ == "__main__":
    process_data()
