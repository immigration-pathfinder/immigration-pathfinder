# Immigration Pathfinder
*A multi-agent system for immigration eligibility, scoring, and recommendations — built for the Google Agents Intensive Capstone (2025).*

---

## 🌍 Overview
**Immigration Pathfinder** is a fully modular **multi-agent system** designed to evaluate immigration eligibility, score countries, and generate human-friendly explanations.

The system uses:
- **ProfileAgent** – extract & normalize user data  
- **MatchAgent** – match profile to country rules  
- **CountryFinderAgent** – ranking & scoring using weighted factors  
- **ExplainAgent** – produce structured explanations  
- **Orchestrator** – manage the agent pipeline end-to-end  

Built for:
- **Kaggle Agents Intensive Capstone (2025)**
- Track: *Concierge Agents* or *Agents for Good*

---

## 🧠 System Architecture (4-Agent Pipeline)

1. ProfileAgent  
   ↳ Converts raw user text into structured UserProfile JSON

2. MatchAgent  
   ↳ Compares UserProfile against country rules → MatchResult[]

3. CountryFinderAgent  
   ↳ Computes weighted scores & ranking

4. ExplainAgent  
   ↳ Produces the final explanation for the user

➡️ Final Output: Best countries + reasoning + actionable next steps

Each component is fully decoupled and extendable.


---

## 📁 Project Structure

```text
immigration-pathfinder/
├── agents/
│   ├── profile_agent.py
│   ├── match_agent.py
│   ├── country_finder_agent.py
│   └── explain_agent.py
│
├── rules/
│   ├── rules_engine.py
│   └── country_rules.json
│
├── memory/
│   └── session_service.py
│
├── tools/
│   ├── search_tool.py
│   └── funds_gap_calculator.py
│
├── tests/
│   ├── test_profile_agent.py
│   ├── test_match_agent.py
│   ├── test_country_finder.py
│   └── test_end_to_end.py
│
├── docs/
│   └── architecture.md
│
├── main.py
├── requirements.txt
└── README.md
```
---

## 🧩 Agent Descriptions

### **1. ProfileAgent**

Extract raw text → structured JSON.

Example Output:

```
{
  "age": 27,
  "citizenship": "Iran",
  "education_level": "Bachelor",
  "field": "Electrical Engineering",
  "ielts": 6.5,
  "funds_usd": 18000,
  "work_experience_years": 3,
  "goal": "Study"
}

```
---

### **2. MatchAgent**
Compare UserProfile against country rules and output:

Example Output:

```
{
  "country": "Canada",
  "pathway": "Study",
  "status": "OK",
  "rule_gaps": [],
  "raw_score": 0.88
}
```

---

### **3. CountryFinderAgent**
Weighted scoring system:

| Factor | Weight |
|-------|--------|
| Eligibility | 30% |
| Language alignment | 15% |
| Financial capacity | 20% |
| Visa difficulty | 10% |
| Quality of life | 10% |
| Cost of living | 10% |
| Job market | 5% |

Takes MatchResults[] → Computes final scores & categories.

Example Output:
```
{
  "best_options": ["Canada", "Netherlands"],
  "acceptable": ["Germany", "Ireland"],
  "not_recommended": ["USA"],
  "scores": {
    "Canada": 92,
    "Netherlands": 87,
    "Germany": 74,
    "Ireland": 70,
    "USA": 48
  }
}
```

---

### **4. ExplainAgent**
Generate natural-language explanations based on the user profile and scoring results.

The agent provides:

Summary of the user profile

Recommended countries

Reasoning behind each score (high/low)

Strengths and gaps

Overall guidance

Example Output:
```
Based on your funds, language level, and study goal, Canada and the Netherlands are the strongest options.

• Canada: High eligibility due to strong finances and suitable study pathways  
• Netherlands: Good match with your academic background and English level  
• Germany: Possible but limited due to language gap

Strengths: Good financial capacity, Bachelor’s degree, clear study goal  
Gaps: Limited German proficiency, moderate work experience
```
---

## 🛠 Tools & Utilities
- **Google Search Tool (ADK/MCP)** – retrieve non-legal high-level info  
- **Funds Gap Calculator**  
- **Currency utilities**  

---

## 💾 Memory System
Session-based storage of:
- user profile  
- rankings  
- chat history  
- partial updates  

---

## 📊 Logging
Every agent call logs:
- timestamp  
- inputs/outputs summary  
- errors  
- tool usage  

Stored in `/logs`.

---

## 🧪 Testing
Includes:
- unit tests for each agent  
- pipeline test  
- 3–5 real-user profiles (student/worker/PR)  

---

## 🚀 How to Run
Install dependencies:
pip install -r requirements.txt

yaml
Copy code

Run locally:
python main.py

yaml
Copy code

---

## 📌 Notes & Limitations
- This system provides **high-level educational guidance**, not legal immigration advice.  
- Rules are simplified approximations.  
- External data tools follow Kaggle’s “reasonableness” standard.

---

## 🏆 Competition Details
Submitted for:
- **Google/Kaggle Agents Intensive Capstone 2025**
- Category: *Concierge Agents* or *Agents for Good*
- License: MIT (per Kaggle’s open-source requirement)

---

## 👥 Team
- Multi-agent architecture  
- Rules engineering  
- Backend engineering  
- Documentation & testing  

Contributions are welcome.

---
