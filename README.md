
# **Flask-Based Keyword Search Rank Checker** 🔍📊  

This project is a **Flask web application** that allows users to upload an **Excel file containing keywords** and fetches the **Google Search ranking** of a specified website using the **SerpAPI**. The application processes the file, checks the ranking of each keyword, and provides a downloadable **Excel report** with the ranking details.

## **Features 🚀**
- Upload an **Excel (.xlsx) file** with a list of keywords.
- Fetch Google Search ranking results using **SerpAPI**.
- Check if a specified **website URL** appears in the search results.
- Extract **page number and position** for each keyword.
- Download a processed Excel file with **rank details**.
- Simple **Flask-based API** with a user-friendly interface.

## **Tech Stack 🛠️**
- **Flask** (Backend Framework)
- **Pandas** (Data Processing)
- **Requests** (API Calls)
- **SerpAPI** (Search Engine Data)
- **Gunicorn** (For Deployment)
- **Render** (For Hosting)

## **How It Works? 📌**
1. Upload an **Excel file** with a column named `"Keywords"`.
2. Enter the **website URL** you want to track.
3. Provide a **SerpAPI key** to fetch Google results.
4. The app processes each keyword and checks its ranking.
5. A **download link** is provided for the processed Excel file.

## **Live Demo 🌍**
🚀 **[Deployed on Render](https://keyword-search-rank-checker.onrender.com/)** 

---
