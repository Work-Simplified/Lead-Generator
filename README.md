# POS Lead Generator SaaS

Scrapes Yelp for business leads, pushes them to Google Sheets, and includes an admin dashboard to manage users and view logs.

---

## 🚀 How to Run This App

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Set Up Environment
- Add your Google Service Account JSON and rename it to `google-creds.json`
- Create a Google Sheet and replace the spreadsheet ID in `app.py`

### 3. Create `users.json`
```json
{
  "admin": "you@example.com",
  "authorized_users": ["you@example.com"]
}
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
python app.py
```

Then open your browser:
- `/admin?admin=you@example.com` → Manage users
- `/admin/logs?admin=you@example.com` → Download scrape logs

---

## ✨ Features
- 🔐 Admin-controlled user access
- 📋 Google Sheets lead sync
- 🧾 Activity logging
- 🧠 Simple, extensible architecture

---

**Note:** Do **not** commit `google-creds.json` or real user logs!