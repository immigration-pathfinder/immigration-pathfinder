# 📐 System Architecture

This document describes the full architecture of the **Immigration Pathfinder** multi-agent system.  
The project follows a modular, decoupled, and fully extensible design — optimized for Kaggle Agents Intensive 2025.

---

## 📂 Project Directory Structure

```text
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

### **1. Agent Layer**
Located in `/agents/`

- **profile_agent.py** → Extracts user profile & normalizes data  
- **match_agent.py** → Matches user profile with immigration criteria  
- **country_finder_agent.py** → Searches and ranks countries  
- **explain_agent.py** → Generates human-friendly explanations  
- **orchestrator.py** → Controls multi-step pipeline and agent coordination  

---

### **2. Rules Layer**
Located in `/rules/`

- `country_rules.json` → Contains structured immigration rules  
- `rules_engine.py` → Evaluates rules, scoring, eligibility logic  

---

### **3. Tools Layer**
Located in `/tools/`

- `search_tool.py` → Keyword lookup, filters, domain checks  
- `funds_gap_calculator.py` → Calculates missing financial requirements  

---

### **4. Memory Layer**
Located in `/memory/`

- `session_service.py` → Temporary session context for multi-step reasoning  

---

### **5. Test Layer**
Located in `/tests/`

Provides unit and integration tests:

- profile agent  
- match agent  
- country finder agent  
- full end-to-end pipeline  

---

### **6. Entry Point**
- `main.py` → Runs the orchestrator & all agents together  
- `requirements.txt` → Dependencies  
- `README.md` → Full documentation  

---

## ✅ Summary
This architecture ensures:

- Clean separation of responsibilities  
- High modularity  
- Easy debugging  
- Expandability for additional countries or new agents  
- 100% competition-ready quality  


