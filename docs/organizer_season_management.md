# 📌 Organizer - Season Management - SkyScore

*Last updated: 2026-06-01*
*Validated by: Pierre LEGRENEUR*

---

## **🗓️ Season Management**

### **Season Types**
SkyScore manages seasons for different **ULM competition types and subtypes**.
The season name follows the format: **`{Type} {SubType} {Year}`** (e.g., `Paramotor Classic 2026`, `Microlight STOL 2026`).

---
### **Type and SubType Definitions**
   **Type**       | **SubType**       | **Description**                          |
 |----------------|-------------------|------------------------------------------|
 | Paramotor      | Classic           | Standard paramotor competitions.        |
 | Paramotor      | Slalom            | Paramotor slalom competitions.          |
 | Microlight     | Classic           | Standard microlight competitions.       |
 | Microlight     | STOL              | Short Take-Off and Landing competitions. |

---
### **Season Creation**
- **Name**:
  - Format: **`{Type} {SubType} {Year}`** (e.g., `Paramotor Classic 2026`).
- **Dates**:
  - Default: **January 1, YYYY** to **December 31, YYYY**.
  - The current date determines the **active season** (all others are archived).

---
### **Active Season and Administrator**
- Each **administrator** is associated with an **active season**.
- Upon login, the administrator's **active season** is automatically loaded, along with:
  - **Allowed event types** (e.g., only `Paramotor Classic` events for a `Paramotor Classic 2026` season).
  - **Associated competitors** (pilots registered for the active season).
  - **Active competitions and events** linked to the season.

- **Changing the Active Season**:
  - When the administrator switches the active season, the system updates:
    - The **available event types** (e.g., switching from `Paramotor Classic` to `Microlight STOL` changes the event options).
    - The **list of competitors** (only pilots registered for the new season are displayed).
    - The **active competitions and events** (only those belonging to the new season are accessible).

---
### **Season Listing**
- Display all seasons with their:
  - Name.
  - Start and end dates.
  - Status (**Active** or **Archived**).
  - Associated administrator (if applicable).

---
### **Permanent Ranking**
- **Automatic calculation** of pilots' rankings across all competitions in the **active season**.
- **Reset** at the start of a new season (January 1 of the new year).

---
---
## **📝 Additional Notes**
- **Active Season**: Only one season is active at a time for each administrator.
- **Archived Seasons**: All past seasons are automatically archived but remain accessible for reference.
- **Permanent Ranking**: Global ranking for all competitions in the active season.
- **Extensibility**: The `{Type} {SubType}` format allows easy addition of new competition types or subtypes in the future.
- **Automatic Loading**: All parameters (active season, events, competitors) are loaded automatically upon administrator login.