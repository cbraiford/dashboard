# Gifted Identification Dashboard (Streamlit)

A Streamlit app to explore subgroup equity across referral, testing, qualification, and placement pipelines for gifted & talented programs.

## Local Run

```bash
pip install -r requirements.txt
streamlit run integrated_gifted_dashboard_recommendations.py
```

## Deploy to Streamlit Community Cloud

1. Push these files to a **public GitHub repo** (e.g., `gifted-dashboard`):
   - `integrated_gifted_dashboard_recommendations.py`
   - `requirements.txt`
   - `README.md` (this file)

2. Go to https://share.streamlit.io (Streamlit Community Cloud), click **"New app"**.
3. Select your repo and branch.  
4. Set **Main file path** to: `integrated_gifted_dashboard_recommendations.py`
5. Click **Deploy**.

### Tips
- Use **Secrets** in Streamlit Cloud for credentials (if you later add databases or APIs).
- Put any sample data in the repo, or use the file uploader to provide your own at runtime.

## Hugging Face Spaces (Optional)

1. Create a Space → **Streamlit** template.  
2. Upload the same three files (`.py`, `requirements.txt`, `README.md`).  
3. Set the **App file** to `integrated_gifted_dashboard_recommendations.py`.  
4. The app will auto-build and launch.

## Expected CSV Schema

Columns like:
- `student_id`
- `school_year` (e.g., `2022-2023`)
- `grade`
- `gender`
- `race_ethnicity`
- `ell` (0/1)
- `iep` (0/1)
- `frl` (0/1)
- `referred` (0/1)
- `tested` (0/1)
- `qualified` (0/1)
- `placed` (0/1)

You can rename columns in the sidebar if your file uses different names.
