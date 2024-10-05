from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for, flash
import lib.bwi_scraper as bwi_scraper
from lib.bwi_scraper import LoginFailureException
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def start():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])   
def login():
    if request.method == "POST":
        form_data = request.form
        username = form_data.get("username")
        password = form_data.get("password")

        session['BWI_username'] = username
        session['BWI_password'] = password

        if 'cookie_button_clicked' not in session:
            session['cookie_button_clicked'] = False

        try:
            bwi_scraper.login(username, password)
            return jsonify({"success": True})
        except LoginFailureException as e:
            return jsonify({"success": False, "error": str(e)})
    
@app.route("/home")
def home():
    if 'BWI_username' not in session and 'BWI_password' not in session:
        return redirect(url_for('start'))
    else:
        return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape(): 
    wine_url = "https://wine.databdn.com/#/app/database/allContinents/allCountries/wine_importer/allEntries/"
    form_data = request.form
    country = form_data.get("country")
    product_origin = form_data.get("productOrigin")
    result_count = form_data.get("resultCount")

    username = session.get("BWI_username")
    password = session.get("BWI_password")    

    bwi_scraper.login(username, password)
    excel_filepath = bwi_scraper.extract_wine_data(wine_url, country, product_origin, result_count)

    return jsonify({"file_path": excel_filepath})  

@app.route("/download/<path:excel_filepath>")
def download(excel_filepath):

    return send_file(excel_filepath, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('start'))

app.run("0.0.0.0", 8000, debug=True)