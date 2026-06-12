# Connect5 AI Arena

An interactive full‑stack application that pits humans and AI agents against each other in a custom Connect‑Five variant (9×10 board, 5‑in‑a‑row to win). The project combines classical game‑theory algorithms with modern neural network training and wraps everything in a polished web interface.

## 🎯 Why this project?
This project showcases a **complete AI + software engineering skill set**:

- **AI / Machine Learning** – Supervised deep learning (CNN) for state evaluation, Monte Carlo Tree Search, and classical minimax.
- **Game Theory** – Analysis of minimax values, exploitability, and approximate Nash equilibria (fictitious play / CFR).
- **Full‑stack Development** – React frontend, FastAPI backend, Docker deployment, real‑time WebSocket play.

Built from real game episodes, the entire pipeline—from raw data to a live, interactive demo—is covered.

---

## 📦 Features
- Play against three AI agents:
  - **Minimax** with alpha‑beta pruning
  - **Pure Monte Carlo Tree Search**
  - **Neural‑network‑guided MCTS** (lightweight AlphaZero style)
- Replay any game from the dataset with move‑by‑move commentary.
- Leaderboard with Elo ratings (humans + bots).
- Upload your own OpenSpiel episode logs to expand the training set.
- Real‑time two‑player mode (optional, via WebSockets).

---

## 🧠 Technical Stack
| Layer        | Technology                                   |
|--------------|----------------------------------------------|
| **Backend**  | Python, FastAPI, SQLAlchemy, ONNX Runtime    |
| **Frontend** | React, SVG canvas, Tailwind CSS (or plain CSS) |
| **AI Engine**| PyTorch (training), ONNX (inference), custom MCTS |
| **Database** | SQLite (dev), PostgreSQL (prod)              |
| **DevOps**   | Docker, Docker Compose, GitHub Actions (CI/CD) |

