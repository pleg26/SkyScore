# 📌 Actors and Roles - SkyScore

*Last updated: 2026-06-01*
*Validated by: Pierre LEGRENEUR*

---

## **👥 Actors and Responsibilities**

### **🏆 Organizer**
- **Role**: Manages a **season** (defined period with start and end dates).
- **Responsibilities**:
  - Create and manage competitions **within a season**.
  - Calculate a **permanent ranking** across all competitions of the season.
  - **Reset** the permanent ranking at the start of each new season.

---

### **✈️ ULM Pilot**
- **Role**: Participates in competitions and monitors personal performance.
- **Responsibilities**:
  - View personal **participation history**.
  - Check **rankings**:
    - **Real-time** for **ongoing events** (with access to details: maps, scoring, penalties).
    - **Global** for each **finalized event** (only the overall scoring, without intermediate calculation details).

---

### **⚖️ Judge / Referee**
- **Role**: Oversees events and validates results.
- **Responsibilities**:
  - Create events.
  - Upload **GPS tracks**.
  - Score pilots (time, penalties).
  - Edit results.
  - **Archive** scoring details (including GPS tracks) at the end of each competition.

---
### **👀 Public**
- **Role**: Views results and live tracking.
- **Responsibilities**:
  - Consult **public results** (final rankings).
  - Access **live tracking** during events.

---
---
## **📝 Additional Notes**
- **Permanent ranking**: Calculated across all competitions in a season. Reset to zero for the next season.
- **Event details**:
  - For pilots: **Accessible only during the event** (maps, detailed scoring, penalties).
  - For judges: **Archived** at the end of each competition (GPS tracks + scoring details).