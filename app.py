import io
import pandas as pd
import requests
from flask import Flask, request, send_file, render_template,session,jsonify,redirect,url_for
from datetime import datetime
import os
from pymongo import MongoClient
import certifi
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI,tlsCAFile = certifi.where())
db = client["KeywordSearch"]
collection = db["users"]

ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def search_site_rank(query, site_url, serp_api_key, num_results=100):
    url = 'https://serpapi.com/search.json'
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {
        'api_key': serp_api_key,  
        'q': query,
        'num': num_results,  
        'google_domain': 'google.co.in',
        'hl': 'en',
        'gl': 'in',
        'filter': 0
    }

    response = requests.get(url, params=params, headers=headers)
    results = response.json()

    if "organic_results" in results:
        for idx, result in enumerate(results["organic_results"], start=1):
            link = result['link']
            if site_url in link:
                page_number = (idx - 1) // 10 + 1
                position_on_page = idx % 10 if idx % 10 != 0 else 10
                return page_number, position_on_page
    return None, None

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def authenticate():
    data= request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = collection.find_one({"email":email })
  
    if user and check_password_hash(user["password"], password):
        session["user"] = email  
        return jsonify({"message": "Login successful", "redirect": url_for("upload_file")}), 200
    else:
        print("error")
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route('/upload')
def upload_file():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "File is required."}), 400
    if 'siteUrl' not in request.form or not request.form['siteUrl'].strip():
        return jsonify({"error": "Site URL is required."}), 400
    if 'apiKey' not in request.form or not request.form['apiKey'].strip():
        return jsonify({"error": "API Key is required."}), 400

    file = request.files['file']
    site_url = request.form['siteUrl'].strip()
    serp_api_key = request.form['apiKey'].strip()

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Please upload an Excel (.xlsx) file."}), 400

    try:
        file_content = file.read()
        df = pd.read_excel(io.BytesIO(file_content))

        expected_columns = {'Keywords'}
        actual_columns = set(df.columns)

        if not expected_columns.issubset(actual_columns):
            return jsonify({"error": "The file must contain a 'Keywords' column."}), 400
        if len(actual_columns) > 1:
            return jsonify({"error": "The file must contain only the 'Keywords' column."}), 400

        result_df = pd.DataFrame(columns=['Keyword', 'Page', 'Position'])

        for keyword in df['Keywords'].dropna():
            page, position = search_site_rank(keyword, site_url, serp_api_key)
            new_row = pd.DataFrame([{
                'Keyword': keyword,
                'Page': page if page else 'Not Found',
                'Position': position if position else 'Not Found'
            }])
            result_df = pd.concat([result_df, new_row], ignore_index=True)

        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = io.BytesIO()
        result_df.to_excel(result_file, index=False)
        result_file.seek(0)

        download_name = f"processed_results_{current_datetime}.xlsx"
        return send_file(result_file, as_attachment=True, download_name=download_name, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500

@app.route('/error')
def errorpage():
    return render_template('error.html')
if __name__ == '__main__':
    app.run(debug=True)
