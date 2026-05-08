# 🌙 Bedtime Story Generator — Frontend

The web interface for the Bedtime Story Generator, built with **React** and **Vite**.

## 🚀 Features

- **Dynamic Story Generation**: Interface to submit story preferences (genre, characters, setting, etc.).
- **Audit Trail Visualization**: Shows the multi-agent reasoning process in real-time.
- **Safety Summaries**: Highlights any safety rewrites (e.g., "Iron Man" → "Brave Robot") applied by the backend.
- **Responsive Design**: Polished, bedtime-themed UI that works on desktop and mobile.

## 🛠️ Tech Stack

- **React 18**
- **Vite** (for fast HMR and builds)
- **Vanilla CSS** (custom bedtime-themed styling)

## 🚦 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env` file in the `frontend` directory:

```bash
cp .env.example .env
```

Ensure `VITE_API_BASE_URL` points to your running FastAPI server (default: `http://localhost:8000`).

### 3. Run the Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

## 📖 Available Routes

- `/reviewer`: Technical evaluator view (default).
- `/kids`: Simple child/parent-friendly story view.

## 🏗️ Building for Production

To create a production bundle:

```bash
npm run build
```

The output will be generated in the `dist` folder.
