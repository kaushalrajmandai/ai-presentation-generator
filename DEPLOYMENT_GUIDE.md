# Deployment & Zero-Setup Run Guide
**Project**: AI Presentation Content Generator  
**Student**: Kaushal Dinesh Rajmandai | Roll No: 150096725111 | Cohort: Sam Altman

---

## 🌟 Option 1: 100% Free Public Web Deployment (No Setup for Anyone)
You can deploy this on **Streamlit Community Cloud** with a public link that anyone (faculty, students, evaluators) can open directly from their phone or browser:

1. Create a free GitHub repository (e.g., `slidegen-project`).
2. Push the contents of the `slidegen/` folder to your GitHub repo.
3. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
4. Click **New app**:
   - Repository: `your-username/slidegen-project`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **Deploy!**
6. *Optional*: In Streamlit Cloud **App Settings -> Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your-api-key"
   ```
   *(Even without this, the app defaults smoothly to the offline mock mode, so anyone can test it with zero configuration!)*

---

## 💻 Option 2: 1-Click Launch on Anyone's Local Computer

### For macOS / Linux:
Double-click `start.sh` or run in terminal:
```bash
./start.sh
```
*It automatically initializes a virtual environment, installs dependencies, loads configuration, and launches the UI in the browser.*

### For Windows:
Double-click `start.bat`.

---

## ⚡ Option 3: Automated Folder Watcher (Zero-Click CLI Demo)
To showcase the background automation during evaluation:
```bash
python run.py watch
```
Drop any text brief (e.g. `samples/club_update.txt`) into `inbox/`. The pipeline automatically cleans the brief, checks for prompt injections, generates the presentation with speaker notes, logs the run into SQLite (`data/slidegen.db`), and outputs the `.pptx` in `output/`.

---

## 🧪 Option 4: Verification Suite
Run the 5 rubric test cases (plus edge cases):
```bash
pytest -v
```
