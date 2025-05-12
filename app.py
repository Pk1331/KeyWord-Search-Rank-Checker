from flask import Flask, request, render_template, session, jsonify, redirect, url_for
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi
from werkzeug.security import check_password_hash
import pandas as pd
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["KeywordSearch"]
collection = db["users"]



# AWS S3 Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION") 

# Login Page
@app.route('/')
def login():
    return render_template('login.html')

# Authenticating  Credentials in MongoDB
@app.route('/login', methods=['POST'])
def authenticate():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = collection.find_one({"email": email})
  
    if user and check_password_hash(user["password"], password):
        session["user"] = email
        return jsonify({"message": "Login successful", "redirect": url_for("upload_file")}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# Upload Page
@app.route('/upload')
def upload_file():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template('upload.html')

# Handle File Upload and Processing
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
    session['serp_api_key'] = serp_api_key 
    

    try:
        file_content = file.read()
        df = pd.read_excel(io.BytesIO(file_content))
        expected_columns = {'Keywords'}
        if not expected_columns.issubset(df.columns):
            return jsonify({"error": "The file must contain a 'Keywords' column."}), 400

        keywords = df['Keywords'].dropna().unique()

        result_list = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_keyword_result, keyword, site_url, serp_api_key) for keyword in keywords]
            for future in as_completed(futures):
                result_list.append(future.result())

        result_df = pd.DataFrame(result_list)

        original_filename = secure_filename(file.filename) or "others_file.xlsx"
        name, ext = os.path.splitext(original_filename)
        if not name:
            name = "result"
        if not ext:
            ext = ".xlsx"
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = io.BytesIO()
        result_df.to_excel(result_file, index=False)
        result_file.seek(0)

        download_name = f"{name}_{current_datetime}{ext}"
        
        client_name = name.split("_")[0]
        year = datetime.now().strftime("%Y")
        month = datetime.now().strftime("%B")
        
        s3_path = f"{client_name}/{year}/{month}/{download_name}"
        file_url = upload_to_s3(result_file, AWS_S3_BUCKET, s3_path)
        
        if file_url:
            return jsonify({"message": "File processed and uploaded", "s3_url": file_url}), 200
        else:
            return jsonify({"error": "Failed to upload to S3"}), 500
        
    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500
    
# Fetch keyword,Page and Position
def fetch_keyword_result(keyword, site_url, serp_api_key):
    page, position = search_site_rank(keyword, site_url, serp_api_key)
    return {
        'Keyword': keyword,
        'Page': page if page else 'Not Found',
        'Position': position if position else 'Not Found'
    }
  
# SERP API Function
def search_site_rank(query, site_url, serp_api_key, num_results=100):
    url = 'https://serpapi.com/search.json'
    params = {
        'api_key': serp_api_key,
        'q': query,
        'num': num_results,
        'google_domain': 'google.co.in',
        'hl': 'en',
        'gl': 'in',
        'filter': 0
    }

    response = requests.get(url, params=params)
    results = response.json()

    if "organic_results" in results:
        for idx, result in enumerate(results["organic_results"], start=1):
            link = result.get('link', '')
            if site_url in link:
                page_number = (idx - 1) // 10 + 1
                position_on_page = idx % 10 if idx % 10 != 0 else 10
                return page_number, position_on_page
    return None, None

# Upload file to S3
def upload_to_s3(file, bucket_name, file_path):
    try:
        # Create an S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url='https://s3.ap-south-2.amazonaws.com',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION,
        )

        # Upload the file to S3
        s3_client.upload_fileobj(file, bucket_name, file_path)

        # Generate the file URL after upload
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_path}"
        return s3_url

    except FileNotFoundError:
        print("Error: The file was not found.")
        return None
    except NoCredentialsError:
        print("Error: Credentials not available.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Results Page
@app.route('/results')
def s3_browser_ui():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template('results.html')

# Download file from S3
@app.route('/browse-s3', methods=['GET'])
def browse_s3():
    prefix = request.args.get('prefix', '')

    s3_client = boto3.client(
        's3',
        endpoint_url='https://s3.ap-south-2.amazonaws.com',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )

    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        result = paginator.paginate(Bucket=AWS_S3_BUCKET, Prefix=prefix, Delimiter='/')

        folders = []
        files = []


        for page in result:
            if 'CommonPrefixes' in page:
                for cp in page['CommonPrefixes']:
                    folders.append(cp['Prefix'])

            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    if key != prefix:
                        url = s3_client.generate_presigned_url('get_object',
                            Params={'Bucket': AWS_S3_BUCKET, 'Key': key},
                            ExpiresIn=3600
                        )
                        files.append({
                            'filename': key.split('/')[-1],
                            'url': url
                        })

        return jsonify({
            'prefix': prefix,
            'folders': folders,
            'files': files
        })

    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not found."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 404 Error Page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Search Limit
@app.route('/remaining-searches', methods=['GET'])  
def remaining_searches():
    if "user" not in session:
        return redirect(url_for("login"))

    serp_api_key = session.get("serp_api_key")
    serp_api_url = f'https://serpapi.com/account?api_key={serp_api_key}'

    response = requests.get(serp_api_url)
    data = response.json()
    if "error" in data:
        return jsonify({"error": data["error"]}), 400

    return jsonify({"total_searches_left": data.get("total_searches_left")}), 200


# Logout Page
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
