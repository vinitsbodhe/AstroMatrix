# 👑 AstroAnalytics Engine: Raj Yog Scoring & Kundli Intelligence Platform

An end-to-end Python analytics engine and interactive dashboard that processes precision astronomical coordinates to calculate, score, and visualize Vedic **Raj Yog** alignments. Built with high-precision Swiss Ephemeris data, rule-based scoring algorithms, and dynamic North Indian chart rendering.

---

## 🚀 Live Demo & Repository
* 🌐 **Live Web Application:** [Access Live Streamlit App]([https://astromatrix.streamlit.app])

---

## 📌 Project Overview
Vedic horoscope analysis often relies on qualitative evaluation of planetary alignments. The **AstroAnalytics Engine** translates complex astrological combination rules into a quantitative **0–100 potency score** by computing real-time spatial planetary positions, house lordships, and combustion states.

### Key Features
* **Astronomical Precision Engine:** Uses `pyswisseph` (Swiss Ephemeris bindings) configured with Lahiri Ayanamsa (`SE_SIDM_LAHIRI`) to determine planetary coordinates and house cusps.
* **Automated Rule & Scoring Engine:** Evaluates multi-variable astrological rules:
  * **Kendra-Trikona Conjunctions:** Identifies relationships between quadrant (1, 4, 7, 10) and trine (1, 5, 9) lords.
  * **Special Yogas:** Detects *Gajakesari* (Jupiter-Moon alignment) and *Budhaditya* (Sun-Mercury conjunction) combinations.
  * **Combustion Adjustments:** Applies dynamic score penalties for planets within $6^\circ$ proximity to the Sun.
* **Global Geocoding & Time Normalization:** Leverages `GeoPy` to convert global city inputs into precise latitude/longitude coordinates and automates time-zone adjustments to UTC.
* **Custom Chart Visualization:** Programmatically renders North Indian diamond-style birth charts (*Kundli*) using `Matplotlib`.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology / Library | Description |
| :--- | :--- | :--- |
| **User Interface** | `Streamlit` | Interactive web frontend for user input & metric display |
| **Ephemeris Engine** | `pyswisseph` | Swiss Ephemeris bindings for planetary position calculations |
| **Spatial Processing** | `GeoPy` (Nominatim) | Geocoding city names to latitude/longitude coordinates |
| **Visualization** | `Matplotlib` | Custom vector geometry rendering for North Indian Kundli charts |
| **Core Language** | `Python 3.10+` | Modular business logic, metric normalization, and data processing |

---

## 🧠 Technical Workflow & Logic
