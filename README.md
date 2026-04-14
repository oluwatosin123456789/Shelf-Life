# 🍏 Fresco
> *Know your fruit. Before the moment passes.*

Fresco is an AI-powered computer vision application that estimates fruit freshness and shelf life. Built for people who treat food as a lifestyle, it uses advanced image classification and kinetic rule-based modeling to provide an instant freshness verdict—and tells you exactly how many days you have left to consume it.

## ✨ Core Features

* **Instant Visual Assessment:** Scan any fruit with your device's camera to get an immediate freshness verdict (Fresh, Eat Soon, or Spoiled).
* **Dynamic Shelf-Life Engine:** Calculates remaining days based on your chosen storage method (Room Temperature, Fridge, or Freezer).
* **Smart Inventory:** A living, urgency-sorted tracker for your kitchen.
* **Ethylene Compatibility Check:** Alerts you if stored fruits will prematurely spoil each other.
* **Progressive Web App (PWA):** Installable on any mobile device for a native, full-screen camera experience.

## 🛠️ Tech Stack

Fresco utilizes a decoupled, modern architecture:

**Frontend (Client)**
* **Framework:** Next.js 14 (App Router)
* **Language:** TypeScript
* **Styling:** Custom CSS Variables (Design System)
* **Features:** MediaDevices API (Camera), next-pwa

**Backend (API & Logic)**
* **Framework:** FastAPI (Python 3.11+)
* **Database:** SQLite (Dev) / PostgreSQL (Prod) via SQLAlchemy 2.0
* **Architecture:** RESTful API with JWT Authentication

**AI & Machine Learning Layer**
* **Classification:** MobileNetV2 (Transfer learning via ImageNet/Food-101)
* **Freshness Assessment:** Custom CNN trained on freshness degradation datasets.
* **Predictive Engine:** Proprietary rule-based estimator combining base biological shelf-life with visual freshness scores.

---

## 🚀 Getting Started

### Prerequisites
* Node.js 18+
* Python 3.11+

### 1. Backend Setup
Clone the repository and set up your Python environment:

```bash
git clone [https://github.com/yourusername/fresco.git](https://github.com/yourusername/fresco.git)
cd fresco/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000




