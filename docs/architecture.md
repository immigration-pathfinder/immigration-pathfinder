# 📐 System Architecture

This document describes the full architecture of the **Immigration Pathfinder** multi-agent system.  
The design is modular, decoupled, and fully extensible for the Kaggle Agents Intensive 2025.

---

## 📂 Project Directory Structure

```
immigration-pathfinder/
│── agents/
│   ├── profile_agent.py
│   ├── match_agent.py
│   ├── country_finder_agent.py
│   ├── explain_agent.py
│   └── orchestrator.py
│
│── rules/
│   ├── rules_engine.py
│   └── country_rules.json
│
│── tools/
│   ├── search_tool.py
│   └── funds_gap_calculator.py
│
│── memory/
│   └── session_service.py
│
│── tests/
│   ├── test_profile_agent.py
│   ├── test_match_agent.py
│   ├── test_country_finder.py
│   └── test_end_to_end.py
│
│── docs/
│   └── architecture.md
│
│── main.py
│── requirements.txt
│── README.md
```

---

## 🧠 Architecture Overview

### 1. Agent Layer (located in `/agents/`)
- **profile_agent.py** — extracts and normalizes user data  
- **match_agent.py** — applies country rules and evaluates eligibility  
- **country_finder_agent.py** — performs searching and ranking  
- **explain_agent.py** — generates natural-language explanations  
- **orchestrator.py** — controls the multi-agent pipeline  

---

### 2. Rules Layer (located in `/rules/`)
- **country_rules.json** — structured immigration rules  
- **rules_engine.py** — scoring + logic for matching rules  

---

### 3. Tools Layer (located in `/tools/`)
- **search_tool.py** — query utilities  
- **funds_gap_calculator.py** — calculates missing financial requirements  

---

### 4. Memory Layer (located in `/memory/`)
- **session_service.py** — maintains session context between steps  

---

### 5. Test Layer (located in `/tests/`)
Contains unit and integration tests:
- Profile Agent  
- Match Agent  
- Country Finder Agent  
- End-to-end pipeline  

---

### 6. Entry Point
- **main.py** — runs orchestrator + all agents  
- **requirements.txt** — dependencies  
- **README.md** — usage guide  

---

# 🧩 Data Models (JSON Schemas)

### UserProfile Schema Example
```json
{
  "age": 30,
  "citizenship": "Iran",
  "marital_status": "single",
  "education_level": "master",
  "field": "computer_science",
  "ielts": 6.5,
  "german_level": "none",
  "french_level": "none",
  "funds_usd": 20000,
  "work_experience_years": 5,
  "goal": "Work",
  "preferred_region": ["Europe"]
}
```

---

### MigrationRule Schema Example
```json
{
  "country": "Germany",
  "pathway": "Work",
  "min_ielts": 6,
  "min_funds_usd": 15000,
  "min_degree": "bachelor",
  "age_max": 45,
  "notes": "Skilled worker route"
}
```

---

### MatchResult Schema Example
```json
{
  "country": "Germany",
  "pathway": "Work",
  "status": "OK",
  "raw_score": 0.82,
  "rule_gaps": {
    "missing_requirements": [],
    "risks": []
  }
}
```

---

### CountryRanking Schema Example
```json
{
  "best_options": [
    { "country": "Germany", "score": 0.82 }
  ],
  "acceptable": [
    { "country": "Austria", "score": 0.75 }
  ],
  "not_recommended": ["Japan"],
  "scores": {
    "Germany": 0.82,
    "Austria": 0.75,
    "Japan": 0.40
  }
}
```

---

# 🧪 Example User Profiles

### 1) Student profile
```json
{
  "age": 22,
  "citizenship": "Iran",
  "marital_status": "single",
  "education_level": "bachelor",
  "field": "computer_science",
  "ielts": 6.5,
  "german_level": "none",
  "french_level": "none",
  "funds_usd": 15000,
  "work_experience_years": 0.5,
  "goal": "Study",
  "preferred_region": ["Europe"]
}
```

### 2) Worker profile
```json
{
  "age": 32,
  "citizenship": "Iran",
  "marital_status": "married",
  "education_level": "master",
  "field": "data_science",
  "ielts": 7.0,
  "german_level": "b1",
  "french_level": "none",
  "funds_usd": 25000,
  "work_experience_years": 7,
  "goal": "Work",
  "preferred_region": ["Europe", "North America"]
}
```

### 3) PR applicant profile
```json
{
  "age": 38,
  "citizenship": "Iran",
  "marital_status": "married",
  "education_level": "bachelor",
  "field": "mechanical_engineering",
  "ielts": 7.5,
  "german_level": "none",
  "french_level": "b1",
  "funds_usd": 40000,
  "work_experience_years": 12,
  "goal": "PR",
  "preferred_region": ["Canada"]
}
```

---

# ✅ Summary

- Modular architecture  
- Clear separation of concerns  
- Extendable data models  
- Fully ready for multi-agent pipeline  
