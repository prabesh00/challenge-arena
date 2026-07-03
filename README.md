# 🎯 Challenge Arena

An AI/ML Bootcamp Challenge & Leaderboard Platform built with **Streamlit + SQLite**.

**Instructors** create challenges (Classification, Regression, RAG, LLM, Code), upload ground truth, and students submit prediction CSVs to get automatically scored and ranked on a live leaderboard.

---

## 📋 Table of Contents

- [Features](#-features)
- [Challenge Types & Scoring](#-challenge-types--scoring)
- [Project Structure](#-project-structure)
- [Local Setup Guide](#-local-setup-guide)
- [Deployment Guide (GitHub + Streamlit Cloud)](#-deployment-guide-github--streamlit-cloud)
- [How to Use Challenge Arena](#-how-to-use-challenge-arena)
- [How to Shut Down the App](#-how-to-shut-down-the-app)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔬 **Classification** | Auto-scored: Accuracy, Precision, Recall, F1, AUC-ROC |
| 📈 **Regression** | Auto-scored: MSE, MAE, R², RMSE, MAPE |
| 📚 **RAG** | Auto-scored: Retrieval Precision@k, Recall@k, MRR, Semantic Similarity |
| 🤖 **LLM** | Auto-scored: Semantic Similarity + OpenRouter LLM-as-Judge |
| 💻 **Code Challenges** | Manual scoring with instructor feedback |
| 🏆 **Live Leaderboard** | Real-time rankings with tie-breaking (earlier submission wins ties) |
| 📤 **CSV Upload** | Validate, score, and rank automatically |
| 📱 **QR Code Login** | Scan to join — perfect for projecting in a classroom |
| 👥 **Cohort Tracking** | Group students by cohort/batch |
| 🗑️ **Submission Management** | Admin can delete individual submissions |

---

## 📊 Challenge Types & Scoring

### Classification
- **Submission CSV**: `image_id, predicted_label`
- **Ground Truth CSV**: `image_id, true_label`
- **Metrics**: Accuracy, Precision (macro+weighted), Recall (macro+weighted), F1 (macro+weighted), AUC-ROC (OVR)
- **Primary**: Accuracy (configurable)

### Regression
- **Submission CSV**: `id, predicted_value`
- **Ground Truth CSV**: `id, true_value`
- **Metrics**: MSE, RMSE, MAE, R², MAPE
- **Primary**: R² (configurable)

### RAG (Retrieval Augmented Generation)
- **Submission CSV**: `question_id, generated_answer, retrieved_doc_ids` (optional)
- **Ground Truth CSV**: `question_id, expected_answer, relevant_doc_ids` (optional)
- **Metrics**: Exact Match Rate, Normalized Match Rate, Semantic Similarity (sentence-transformers), Retrieval Precision@k, Recall@k, MRR
- **Primary**: Semantic Similarity (configurable)

### LLM Evaluation
- **Submission CSV**: `question_id, generated_answer, question_text` (optional)
- **Ground Truth CSV**: `question_id, expected_answer, question_text` (optional)
- **Metrics**: Exact Match Rate, Normalized Match Rate, Semantic Similarity, **LLM-as-Judge Score** (via OpenRouter), Combined Score
- **Primary**: Combined Score (configurable)

### Code Challenge
- **Submission**: CSV with code file paths or GitHub links
- **Scoring**: Manual — instructor reviews and assigns a score (0-100) with feedback

---

## 📁 Project Structure

```
challenge-arena/
├── app.py                        # Main entry point
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .streamlit/
│   └── config.toml               # Streamlit configuration
├── database/
│   ├── __init__.py
│   ├── db.py                     # SQLite database setup
│   └── models.py                 # All CRUD operations
├── auth/
│   ├── __init__.py
│   └── auth.py                   # Session-based authentication
├── scoring/
│   ├── __init__.py
│   ├── base.py                   # Abstract base scorer
│   ├── registry.py               # Scorer type registry
│   ├── classification.py         # Classification metrics
│   ├── regression.py             # Regression metrics
│   ├── rag.py                    # RAG metrics
│   ├── llm.py                    # LLM metrics + OpenRouter
│   └── manual.py                 # Manual code challenge scoring
├── pages/
│   ├── __init__.py
│   ├── login.py                  # Student registration
│   ├── challenges.py             # Active challenge list
│   ├── challenge_detail.py       # Challenge: upload, history, leaderboard
│   ├── admin_login.py            # Admin login
│   ├── admin_dashboard.py        # Admin: manage challenges
│   ├── admin_challenge_detail.py # Admin: ground truth, submissions, scoring
│   └── admin_qr.py               # QR code generation
├── utils/
│   ├── __init__.py
│   ├── validation.py             # CSV validation
│   └── helpers.py                # File storage, formatting
└── data/                         # Created automatically
    ├── challenges/               # Resource files
    ├── ground_truth/             # Ground truth CSVs (private)
    └── submissions/              # Student submissions
```

---

## 💻 Local Setup Guide

### Prerequisites
- Python 3.9 or higher installed
- A code editor (VS Code, PyCharm, etc.)
- Basic familiarity with the terminal/command prompt

### Step 1: Get the Code

```bash
# Clone the repository (or download the ZIP from GitHub)
git clone https://github.com/YOUR_USERNAME/challenge-arena.git
cd challenge-arena
```

### Step 2: Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This may take a few minutes as it downloads scikit-learn, sentence-transformers, and other libraries.

### Step 4: Set the Admin Password

**Windows (Command Prompt):**
```bash
set ADMIN_PASSWORD=my-secret-password
```

**Windows (PowerShell):**
```bash
$env:ADMIN_PASSWORD="my-secret-password"
```

**Mac/Linux:**
```bash
export ADMIN_PASSWORD=my-secret-password
```

### Step 5: Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Step 6: Access the App
- **Landing page**: `http://localhost:8501`
- **Admin login**: Click "Admin Login" on the landing page or go to `http://localhost:8501/admin_login`
- **Student login**: Click "Join Challenge" or go to `http://localhost:8501/login`
- **Admin password**: Use the password you set in Step 4

---

## ☁️ Deployment Guide (GitHub + Streamlit Cloud)

This guide walks you through deploying the app on **Streamlit Community Cloud** (free tier) using a **GitHub repository**.

### Step 1: Create a GitHub Account (if you don't have one)

1. Go to [github.com](https://github.com) and click **Sign up**
2. Enter your email, create a password, and choose a username
3. Verify your email address
4. You're now ready to create repositories!

### Step 2: Create a New Repository on GitHub

1. Click the **"+" icon** in the top-right corner → **"New repository"**
2. **Repository name**: `challenge-arena` (or any name you like)
3. **Description** (optional): "AI/ML Bootcamp Challenge & Leaderboard Platform"
4. **Visibility**: Select **Public** (required for Streamlit Community Cloud free tier)
5. **Initialize with**: DO NOT check any boxes (we'll upload files directly)
6. Click **"Create repository"**

### Step 3: Upload the Code to GitHub

There are two ways to do this:

#### Option A: Upload via GitHub Web Interface (Easiest)

1. On your new repository page, click **"Add file"** → **"Upload files"**
2. **On your computer**, create a folder called `challenge-arena` and copy ALL the project files into it:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `.streamlit/` (folder with `config.toml` inside)
   - `database/` (folder with all files inside)
   - `auth/`
   - `scoring/`
   - `pages/`
   - `utils/`
3. **Drag and drop** the entire `challenge-arena` folder OR all its contents into the GitHub upload area
4. Scroll down, add a commit message: `Initial commit`
5. Click **"Commit changes"**

#### Option B: Upload via Git Command Line

```bash
# Initialize git in your project folder
cd challenge-arena
git init
git add .
git commit -m "Initial commit"

# Connect to your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/challenge-arena.git

# Push the code
git branch -M main
git push -u origin main
```

> **Note**: Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 4: Verify Files are on GitHub

1. Go to your repository page: `https://github.com/YOUR_USERNAME/challenge-arena`
2. You should see all the files listed (app.py, requirements.txt, etc.)
3. If files are missing, go back and upload them again

### Step 5: Create a Streamlit Community Cloud Account

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in with GitHub"**
3. **Authorize** Streamlit to access your GitHub account
   - You'll be redirected to GitHub to approve the permissions
   - Click **"Authorize streamlit"**
4. You're now on the Streamlit Community Cloud dashboard

### Step 6: Deploy the App

1. On the Streamlit dashboard, click **"New app"**
2. Under **"Repository"**, select: `YOUR_USERNAME/challenge-arena`
3. **Branch**: `main`
4. **Main file path**: `app.py`
5. Click **"Deploy!"**

### Step 7: Wait for the Build

- Streamlit will now build and deploy your app
- This takes **2-5 minutes** the first time
- You'll see build logs — don't worry if you see warnings, as long as there are no errors
- Once done, you'll get a URL like: `https://challenge-arena.streamlit.app`

### Step 8: Set the Admin Password

1. Go to your app on Streamlit Cloud dashboard
2. Click **"Settings"** (gear icon)
3. Scroll to **"Secrets"** section
4. Add this (replace with your own password):

```toml
admin_password = "your-secure-password-here"
```

5. Click **"Save"**
6. The app will automatically restart with the new password

### Step 9: Set OpenRouter API Key (Optional — for LLM challenges)

If you plan to use LLM challenges with LLM-as-Judge scoring:

1. Go to [openrouter.ai](https://openrouter.ai) and sign up
2. Create an API key from the dashboard
3. In your Streamlit app settings → **Secrets**, add:

```toml
admin_password = "your-secure-password-here"
openrouter_api_key = "sk-or-v1-your-key-here"
openrouter_model = "openai/gpt-4o"
```

4. You can change the model to any model supported by OpenRouter (e.g., `anthropic/claude-3.5-sonnet`, `google/gemini-pro`, etc.)

### Step 10: Your App is Live! 🎉

- **Student URL**: `https://challenge-arena.streamlit.app/login`
- **Admin URL**: `https://challenge-arena.streamlit.app/admin_login`
- **QR Code Page**: `https://challenge-arena.streamlit.app/admin_qr`

---

## 🎮 How to Use Challenge Arena

### For Instructors (Admin)

1. **Login**: Go to `/admin_login` and enter your admin password
2. **Create a Challenge**:
   - Click "➕ New Challenge"
   - Enter title, description (supports Markdown), and select challenge type
   - Upload resource files (datasets, starter notebooks, etc.)
   - Set deadline (optional)
3. **Upload Ground Truth**:
   - Click "Manage →" on the challenge
   - Go to "📤 Ground Truth" tab
   - Upload the correct answers CSV
   - Pending submissions will be auto-scored
4. **Manage Submissions**:
   - View all submissions in "📊 Submissions" tab
   - For code challenges: enter manual scores and feedback
   - Delete submissions if needed
5. **Generate QR Code**:
   - Go to "📋 QR Code" page
   - Enter your app URL and cohort code
   - Project the QR code on screen for students to scan
6. **Download Leaderboard**: Go to "🏆 Leaderboard" tab → click "Download Leaderboard CSV"

### For Students

1. **Join**: Scan the QR code or go to the login URL
2. **Register**: Enter your name, email, and cohort code
3. **View Challenges**: See the list of open challenges
4. **Submit**: Click "View →" on a challenge, read the description, download resources, upload your CSV
5. **Check Results**: After uploading, see your scores, metrics, and rank on the leaderboard
6. **Re-submit**: You can upload again anytime before the deadline — only the latest counts

---

## 🛑 How to Shut Down the App

### Option A: Stop the App (Recommended — Keeps Data)

This pauses the app so students can't access it. All data is preserved.

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find your app in the dashboard
3. Click the **"⋮" (three dots)** menu → **"Stop app"**
4. The app is now paused. Students will see a "down" message
5. **To restart**: Click **"⋮"** → **"Start app"** — all data is restored

### Option B: Delete the App

This removes the app from Streamlit Cloud. Your GitHub repository stays intact.

1. In Streamlit dashboard → **"⋮"** → **"Delete app"**
2. Confirm deletion
3. **To redeploy later**: Just go through the deployment steps again — your GitHub code is still there
4. **⚠️ Warning**: All data on Streamlit's servers will be lost

### Option C: Make the GitHub Repository Private

The free tier of Streamlit Community Cloud **only serves apps from public repositories**. Making your repo private will stop the app from serving.

1. On GitHub, go to your repository → **Settings**
2. Scroll to **"Danger Zone"**
3. Click **"Change visibility"** → **"Make private"**
4. The Streamlit app will stop working (shows a 404)
5. **To re-enable**: Change visibility back to **Public**

### Option D: Delete the GitHub Repository (Permanent)

This permanently deletes everything — your code, app, and all data.

1. On GitHub, go to your repository → **Settings**
2. Scroll to **"Danger Zone"**
3. Click **"Delete this repository"**
4. Type the repository name to confirm
5. **⚠️ Warning**: This is irreversible. Download any important data first!

### Important Note About Data

- **SQLite data** (challenges, submissions, scores, student accounts) is stored on Streamlit's servers
- If you **stop** the app (Option A), data is preserved
- If you **delete** the app (Option B), **all data is lost**
- To save important data before deleting:
  - Go to each challenge → "🏆 Leaderboard" tab → Download Leaderboard CSV
  - There's no built-in database download, but the leaderboard CSVs capture the essential results

---

## 🔧 Troubleshooting

### "Module not found" errors on deployment
- Make sure `requirements.txt` has all dependencies listed
- Streamlit Cloud installs from requirements.txt automatically

### "Admin password not set" error
- You need to set the `admin_password` in Streamlit Secrets
- Go to Settings → Secrets → add `admin_password = "your-password"`

### App won't deploy / build fails
- Check the build logs in Streamlit dashboard
- Common issues:
  - Missing `requirements.txt` file
  - Typo in `app.py` path (should be just `app.py`, not `pages/app.py`)
  - Missing `__init__.py` files in Python packages

### "sentence-transformers" takes too long to load
- The first load downloads the embedding model (~80MB)
- Subsequent loads are cached and faster
- This is normal behavior

### OpenRouter API not working
- Make sure you've set `openrouter_api_key` in Secrets
- Check that your API key is still valid on openrouter.ai
- Try a different model (e.g., `google/gemini-pro` which is free)

### Students can't access the app
- Make sure the repository is **Public** (not Private)
- Check that the app is running (not stopped/paused)
- Verify the URL is correct

---

## ❓ FAQ

**Q: How many students can use this?**
A: Streamlit Community Cloud free tier has some limits, but for a classroom of 20-100 students it works perfectly.

**Q: Is my data safe?**
A: The app uses a local SQLite database. Data persists as long as the app is deployed. For production use, consider adding a cloud database. For a classroom tool, this is sufficient.

**Q: Can I customize the scoring?**
A: Yes! The scoring system is pluggable. Add a new scorer in the `scoring/` folder and register it in `scoring/registry.py`.

**Q: Do I need to install anything on students' computers?**
A: No. Everything runs in the browser. Students just need a CSV file to upload.

**Q: Can I export the leaderboard?**
A: Yes. As an admin, go to any challenge → "🏆 Leaderboard" tab → click "Download Leaderboard CSV".

**Q: What if a student uploads the wrong file?**
A: They can re-upload anytime before the deadline. Only their latest submission counts. You can also delete submissions as admin.

---

Built with ❤️ for AI/ML bootcamps.