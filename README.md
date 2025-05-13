# **Flask-Based Keyword Search Rank Checker** 🔍📊

This project is a **Flask web application** that allows users to upload an **Excel file containing keywords** and fetches the **Google Search ranking** of a specified website using the **SerpAPI**. The application processes the file, checks the ranking of each keyword, and provides a downloadable **Excel report** with the ranking details.


## **Features 🚀**

* Upload an **Excel (.xlsx) file** with a column named `"Keywords"`.
* Filename format validation: must be in the format `companyname_description.xlsx`.
* Fetch Google Search ranking results using **SerpAPI**.
* Track keyword rankings for a specified **website URL**.
* Extract and display **page number and position** of the website for each keyword.
* Show the **remaining SerpAPI search quota** in real-time.
* Download a processed Excel file with **detailed rank data** using a structured filename:

  * Example: `ivista_results_2025_05.xlsx`.
* **Responsive design** with mobile-friendly layout following **W3C standards**.
* Includes **confirmation modals**, **loading indicators**, and **toast notifications** for better user experience.
* Multi-device support and smooth user interaction.



## **Tech Stack 🛠️**

* **Flask** – Backend web framework
* **Pandas** – For Excel file parsing and data processing
* **Requests** – HTTP calls to SerpAPI
* **SerpAPI** – For retrieving live Google search results
* **Gunicorn** – Production-ready WSGI server for deployment
* **Render** – Hosting the live demo (free tier used)
* **AWS S3** – Cloud file storage 


## **How It Works 📌**

1. User uploads an **Excel file** with a `"Keywords"` column.
2. Enters the **website URL** they want to check ranking for.
3. Enters their **SerpAPI key**.
4. System processes the file, queries Google Search for each keyword, and checks if the given domain appears in the results.
5. Once processed:

   * Results are available to **download** as an `.xlsx` file.
   * Remaining SerpAPI quota is updated and displayed.

---

## **Storage & Hosting**

* Currently hosted on **Render (Free Tier)**:
  👉 [https://keyword-search-rank-checker.onrender.com/](https://keyword-search-rank-checker.onrender.com/)

  * Note: On free tier, the app may experience **cold starts** (initial delay).
* Files are stored in **AWS S3 bucket**.

  

