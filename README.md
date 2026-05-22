<p align="center">
  <h1 align="center">🏭 AI-Augmented TCP-Secured IoT Hub</h1>
  <p align="center">
    A real-time, multi-user Industrial IoT monitoring platform with SSL/TLS-secured TCP communication, an AI-powered predictive maintenance engine, and a live web dashboard.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/ML-RandomForest-orange?logo=scikit-learn" alt="ML">
    <img src="https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?logo=google" alt="Gemini">
    <img src="https://img.shields.io/badge/Transport-TCP%20%2B%20SSL%2FTLS-green?logo=letsencrypt" alt="SSL">
    <img src="https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit" alt="Streamlit">
    <img src="https://img.shields.io/badge/License-Academic-lightgrey" alt="Academic">
  </p>
</p>

---

## 📖 Overview

**AI-Augmented TCP-Secured IoT Hub** is an industrial-grade IoT monitoring system developed as a university project. It simulates a factory environment where multiple client machines (or operators) connect to a central server over a **SSL/TLS-encrypted TCP channel**, send real-time sensor telemetry, and receive instant AI-powered failure predictions.

### What we built

| Component | Description |
|-----------|-------------|
| **TCP Server** (`server.py`) | Multi-threaded SSL/TLS server that broadcasts messages between all connected clients and spawns the AI bot |
| **AI Maintenance Bot** (`ai_bot.py`) | Connects to the server as a special client; runs a trained **Random Forest** model on incoming telemetry and queries **Google Gemini** for natural-language Q&A |
| **Client GUI** (`client_gui.py`) | Tkinter desktop app: real-time sensor simulation, live charts (air temp, process temp, RPM, torque, tool wear), chat room, and AI analysis reports |
| **Web Dashboard** (`web_dashboard.py`) | Streamlit dashboard that reads the SQLite log database and renders interactive Plotly charts — auto-refreshes every 2 seconds |

### What we aimed for

- **Secure communication**: All data travels over an SSL/TLS-wrapped TCP socket — no plaintext sensor data on the wire.
- **Predictive maintenance**: A Random Forest classifier, trained on the *AI4I 2020 Predictive Maintenance Dataset*, predicts the type of machine failure (tool wear, heat dissipation, power failure, overstrain, or no failure) with ~98% accuracy.
- **AI chatbot integration**: Employees can ask the bot any question using `@ai` or `@bot` tags in the chat — responses are powered by Google Gemini.
- **Multi-user real-time monitoring**: Multiple factory floor operators can be connected simultaneously, see each other's sensor data, and communicate in the same secured chat room.
- **Automated alerting**: When a failure is predicted, the bot logs an emergency alert report and broadcasts a warning to all connected clients.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         TCP Server (server.py)                  │
│                    SSL/TLS  ·  Port 12345  ·  Multi-threaded    │
└──────────┬──────────────────────────────────┬───────────────────┘
           │  Broadcasts messages              │  Spawns subprocess
           │                                  ▼
┌──────────┴──────────┐              ┌─────────────────────────────┐
│   Client GUI        │              │      AI Maintenance Bot     │
│  (client_gui.py)    │              │       (ai_bot.py)           │
│                     │  TELEMETRY   │                             │
│  • Sensor Simulator ├─────────────►│  Random Forest Classifier   │
│  • Live Charts      │              │  ──────────────────────     │
│  • Chat Room        │  REPORT      │  Predicts failure type      │
│  • Analysis Tab     │◄─────────────┤  + confidence score         │
│                     │              │                             │
│  • @ai / @bot msgs  ├─────────────►│  Google Gemini LLM          │
│                     │◄─────────────┤  Answers in natural lang.   │
└─────────────────────┘              └──────────┬──────────────────┘
                                                │ Logs predictions
                                                ▼
                                     ┌─────────────────────────────┐
                                     │   SQLite Database           │
                                     │   (bakim_loglari.db)        │
                                     └──────────┬──────────────────┘
                                                │ Reads
                                                ▼
                                     ┌─────────────────────────────┐
                                     │   Web Dashboard             │
                                     │   (web_dashboard.py)        │
                                     │   Streamlit + Plotly        │
                                     │   Auto-refresh every 2s     │
                                     └─────────────────────────────┘
```

---

## ✨ Features

- 🔒 **SSL/TLS encrypted TCP communication** — self-signed cert support, Ngrok tunnel compatible
- 🤖 **Random Forest predictive maintenance** — trained on 10,000 industrial records
- 💬 **Gemini-powered AI chatbot** — ask maintenance questions in natural language via `@ai` or `@bot`
- 📊 **Live sensor charts** — temperature, RPM, torque, and tool wear plotted in real time
- 🚨 **Automated emergency reports** — written to file and broadcast to all clients on failure detection
- 🗄️ **SQLite logging** — all sensor readings and predictions are persisted
- 🌐 **Streamlit web dashboard** — interactive Plotly charts and styled prediction tables, auto-refreshing
- 👥 **Multi-user chat room** — employees communicate over the same secured channel

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.8+ |
| GUI | Tkinter + Matplotlib (TkAgg backend) |
| ML | Scikit-learn (RandomForestClassifier) |
| Data | Pandas, NumPy |
| LLM | Google Generative AI (Gemini) |
| Web Dashboard | Streamlit + Plotly |
| Database | SQLite3 |
| Networking | Python `socket` + `ssl` (TLS) |
| Dataset | AI4I 2020 Predictive Maintenance Dataset (UCI ML Repository) |

---

## 📁 Project Structure

```
AI-Augmented-TCP-Secured-IoT-Hub/
│
├── server.py               # SSL/TLS TCP server — entry point
├── ai_bot.py               # AI maintenance bot (ML + Gemini LLM)
├── client_gui.py           # Tkinter client with live sensor dashboard
├── web_dashboard.py        # Streamlit web dashboard
│
├── predictive_maintenance.csv  # Training dataset (AI4I 2020)
│
├── server.crt              # ⚠️ Self-signed SSL cert — generate your own (see below)
├── server.key              # ⚠️ SSL private key   — NOT committed to git
│
├── .env.example            # API key template — copy to .env and fill in
├── requirements.txt        # Python dependencies
└── README.md
```

> **Note:** Runtime-generated files (`bakim_loglari.db`, `ACIL_DURUM_RAPORU.txt`, `current_status.json`) and your `.env` file are excluded from version control via `.gitignore`.

---

## ⚙️ Prerequisites

- Python **3.8 or higher**
- `pip`
- OpenSSL (for generating the SSL certificate)

---

## 🚀 Setup & Run

### 1. Clone the repository

```bash
git clone https://github.com/sefasys/AI-Augmented-TCP-Secured-IoT-Hub.git
cd AI-Augmented-TCP-Secured-IoT-Hub
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # Linux / macOS
# venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key

The AI chatbot requires a Google Gemini API key. Get one free at [aistudio.google.com](https://aistudio.google.com/).

```bash
cp .env.example .env
# Then open .env and fill in your key:
# GEMINI_API_KEY=your_api_key_here
```

The bot will automatically load the `.env` file on startup.

### 5. Generate an SSL certificate

```bash
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt \
  -days 365 -nodes -subj "/CN=localhost"
```

### 6. Run the server

```bash
python server.py
```

The server starts on `127.0.0.1:12345` and automatically launches the AI bot as a subprocess.

### 7. Run the client (one or more instances)

```bash
python client_gui.py
```

Enter the server IP (`127.0.0.1`) and port (`12345`) when prompted.

### 8. (Optional) Run the web dashboard

```bash
streamlit run web_dashboard.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 Remote Access (Ngrok)

To expose the server over the internet for remote clients:

```bash
ngrok tcp 12345
```

Clients then connect using the Ngrok address (e.g., `0.tcp.eu.ngrok.io`) and the provided port.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes (for chatbot) | Your Google Gemini API key |

---

## 📊 Dataset

The machine learning model was trained on the **AI4I 2020 Predictive Maintenance Dataset** from the UCI Machine Learning Repository.

- **10,000 records** of synthetic industrial sensor data
- **Features:** machine type, air temperature (K), process temperature (K), rotational speed (RPM), torque (Nm), tool wear (min)
- **Target classes:** `No Failure`, `Tool Wear Failure`, `Heat Dissipation Failure`, `Power Failure`, `Overstrain Failure`, `Random Failures`

---

## 🤖 AI Model

| Property | Value |
|----------|-------|
| Algorithm | Random Forest Classifier |
| Estimators | 100 trees |
| Train/Test Split | 80% / 20% |
| Test Accuracy | ~98% |
| Framework | Scikit-learn |

The model is retrained from scratch every time the AI bot starts. No pre-serialized model file is needed.

---

## 📸 Screenshots

<table>
  <tr>
    <td align="center"><strong>Client GUI — Sensor Dashboard</strong></td>
    <td align="center"><strong>Client GUI — Analysis Reports</strong></td>
  </tr>
</table>

---

## 📝 Academic Use

This project was developed as a term project for the **Internet of Things** course at **Ankara Yıldırım Beyazıt University (AYBU)**, Computer Engineering Department, 2025–2026 Fall Semester.

Feel free to use it as a reference or learning resource. If you build on top of it, a star ⭐ or credit is appreciated!

---

## 📄 License

This project is released for **academic and educational purposes**. No warranties expressed or implied.
