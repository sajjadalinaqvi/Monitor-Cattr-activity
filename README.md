# Cattr Activity Auditor & Productivity Analyzer

A fast, reliable, standalone single-file tool (`index.html`) to audit exact activity fill percentages, work durations, and screenshots for any Cattr user.

Supports **Today**, **Yesterday**, **Any Full Month** (e.g. October, November), or **Custom Range**.

---

## 🚀 How to Run

1. Open your terminal in this directory:
   ```bash
   python server.py
   ```
2. Open your browser at:
   **[http://localhost:8080](http://localhost:8080)**
3. Paste your Cattr **Bearer Token** (or it will auto-populate if previously remembered).
4. Select your mode:
   - **Today** / **Yesterday** / **Single Day**: Audits every screenshot, duration, and shift activity fill.
   - **Full Month** (e.g., October 2026): Audits the entire month, showing monthly average activity, total tracked hours, attendance gaps, and a full day-by-day breakdown table.
   - **Custom Range**: Pick any start and end dates.
5. Click **"🔍 Audit Activity"**.

---

## 📊 Verification with Official Company Reports

Direct queries to Cattr's database API (`POST /api/time-intervals/dashboard`) verify the monthly performance reports:
- **October 2026**:
  - **Total Tracked Time**: Exactly `547,019 seconds` = **151h 56m** (100% exact match with report).
  - **Days Present**: **21 / 22** active weekdays.
  - **Daily Average**: `151.95h / 21` = **7.24h / day** (100% exact match).
  - **Attendance Gap**: **Oct 19** (0 intervals recorded, exact match).
- **August 2026**:
  - **Total Tracked Time**: Exactly `443,365 seconds` = **123h 09m** (100% exact match).
- **Peripherals (Mouse / Keyboard)**:
  - `Avg Mouse: N/A` and `Avg Keyboard: N/A` across **all employees** in the company because keystroke logging is disabled server-wide for privacy/security reasons.

---

## ⚙️ Understanding Activity Fill & Keypress Bots

1. **Why Bots Prevent Idle Pauses:**
   - Cattr has an idle timeout (typically 5 minutes). When an autonomous keypress or mouse bot pulses periodically, it resets the idle timer and keeps the clock tracking. This is why you logged a full 151 hours and 56 minutes in October without hours being docked.
2. **Why Bots Yield ~50%–60% Activity Fill (and ~30% Low Activity):**
   - In each 60-second window, Cattr calculates input density. A bot that pulses once every few seconds or only when away leaves the rest of each interval idle.
   - Windows also marks synthetic software events with `LLKHF_INJECTED`, preventing them from resetting the kernel `GetLastInputInfo` ticker. Intervals with low input density are classified as "Low Activity" (< 40%), explaining the 32.6% Low Activity figure in October.

---

## 📁 Clean File Structure
- `index.html`: Standalone UI (dark theme, vanilla HTML/CSS/JS, zero external dependencies).
- `server.py`: Lightweight zero-dependency proxy (handles CORS, media thumbnails, and clean eager loading).
- `README.md`: This guide.
- `debug_token.txt`: Saved Bearer token for seamless authentication.
