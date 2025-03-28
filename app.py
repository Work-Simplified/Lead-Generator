# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import csv
import datetime

app = Flask(__name__, template_folder='templates')
CORS(app)

# Load authorized users
USERS_FILE = 'users.json'
LOG_FILE = 'usage_log.csv'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {"admin": "", "authorized_users": []}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def log_usage(email, keyword, location):
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now().isoformat(), email, keyword, location])

user_data = load_users()
authorized_users = user_data.get("authorized_users", [])
admin_email = user_data.get("admin", "")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("YOUR_SPREADSHEET_ID").sheet1  # Replace with your actual spreadsheet ID

@app.route('/scrape', methods=['POST'])
def scrape_yelp():
    data = request.json
    email = data.get('email')

    if not email or email not in authorized_users:
        return jsonify({"error": "Unauthorized access"}), 403

    keyword = data['keyword']
    location = data['location']
    leads = []

    log_usage(email, keyword, location)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for page in range(0, 20, 10):  # Two pages (change as needed)
        url = f"https://www.yelp.com/search?find_desc={keyword}&find_loc={location}&start={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        listings = soup.find_all("div", class_="container__09f24__21w3G")
        for biz in listings:
            try:
                name_tag = biz.find("a", class_="css-1egxyvc")
                if not name_tag:
                    continue
                name = name_tag.text.strip()
                link = "https://www.yelp.com" + name_tag['href']
                address = biz.find("address").text.strip() if biz.find("address") else "N/A"
                phone = biz.find("p", class_="css-8jxw1i").text.strip() if biz.find("p", class_="css-8jxw1i") else "N/A"

                lead = {"Name": name, "Address": address, "Phone": phone, "Link": link}
                leads.append(lead)

                # Push to Google Sheets
                sheet.append_row([name, address, phone, link])

            except:
                continue

    return jsonify(leads)

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('admin') != admin_email:
            return "Admin access required", 403

        email = request.form.get('email')
        action = request.form.get('action')

        if action == 'add' and email not in user_data['authorized_users']:
            user_data['authorized_users'].append(email)
        elif action == 'remove' and email in user_data['authorized_users']:
            user_data['authorized_users'].remove(email)

        save_users(user_data)
        return redirect(url_for('admin_dashboard', admin=admin_email))

    if request.args.get('admin') != admin_email:
        return "Admin access required", 403

    return render_template("admin.html", admin=admin_email, users=authorized_users)

@app.route('/admin/logs', methods=['GET'])
def download_logs():
    if request.args.get('admin') != admin_email:
        return "Admin access required", 403

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Email', 'Keyword', 'Location'])

    return send_file(LOG_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
