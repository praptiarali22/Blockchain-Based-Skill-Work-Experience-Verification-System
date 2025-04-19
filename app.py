from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import bcrypt
from web3 import Web3
from datetime import datetime
import json
import os
from datetime import datetime

app = Flask(__name__)
# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Your MySQL username
app.config['MYSQL_PASSWORD'] = 'Rashmi@123'  # Your MySQL password
app.config['MYSQL_DB'] = 'BlockchainProject'
mysql = MySQL(app)
app.secret_key = os.urandom(24)

# Connect to local Ganache blockchain
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Check if connected
if not w3.is_connected():
    raise Exception("Web3 is not connected to Ganache")

# Your smart contract address deployed from Remix/Ganache
contract_address = Web3.to_checksum_address("0x99289B09Cc1d9a760F472261676838e4B98A23BA")

# Load ABI (replace with your actual ABI file path)
with open("certificate_abi.json") as f:
    contract_abi = json.load(f)

# Load contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Use the first Ganache account as the HR/admin
hr_account = w3.eth.accounts[0]

# Private key for hr_account (only use this in development!)
private_key = "0xc6a302112cee7730b17ede3e9a6c4742e36ebcd72a98584d5f35a34f8db31482"

@app.route("/")
def index():
    return render_template("index.html")

# Employee Signup
@app.route('/employee_signup', methods=['GET', 'POST'])
def employee_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        email = request.form['email']

        if password != confirm_password:
            flash("Passwords do not match!", 'danger')
            return render_template('employee_signup.html')
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO employees (username, password, name, email) VALUES (%s, %s, %s, %s)", 
                           (username, hashed_password, name, email))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            flash(f"Error during signup: {str(e)}", 'danger')
            return render_template('employee_signup.html')

        flash('Employee registered successfully', 'success')
        return redirect(url_for('login'))
    return render_template('employee_signup.html')

# HR Signup
@app.route('/hr_signup', methods=['GET', 'POST'])
def hr_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        company = request.form['company']
        name = request.form['name']
        email = request.form['email']
        
        if password != confirm_password:
            flash("Passwords do not match!", 'danger')
            return render_template('hr_signup.html')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO hr (username, password, name, email, company) VALUES (%s, %s, %s, %s, %s)", 
                           (username, hashed_password, name, email, company))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            flash(f"Error during signup: {str(e)}", 'danger')
            return render_template('hr_signup.html')

        flash('HR registered successfully', 'success')
        return redirect(url_for('login'))
    return render_template('hr_signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        try:
            cursor = mysql.connection.cursor()

            if user_type == 'employee':
                cursor.execute("SELECT * FROM employees WHERE username=%s", (username,))
            else:
                cursor.execute("SELECT * FROM hr WHERE username=%s", (username,))

            user = cursor.fetchone()

            if user:
                # Ensure you are comparing hashed password with the entered password
                stored_password = user[2]
                if stored_password:
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                        session['user_id'] = user[0]    
                        session['user_type'] = user_type
                        session['username'] = user[1]
                        return redirect(url_for(f'{user_type}_dashboard'))
                    else:
                        flash('Invalid credential', 'danger')
                        return redirect(url_for('login'))
                else:
                    flash('Invalid credentials', 'danger')
                    return redirect(url_for('login'))

        except Exception as e:
            flash(f"Error during login: {str(e)}", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Employee Dashboard
@app.route('/employee_dashboard')
def employee_dashboard():
    if 'user_id' not in session or session['user_type'] != 'employee':
        return redirect(url_for('login'))

    return render_template('employee_dashboard.html')


# HR Dashboard
@app.route('/hr_dashboard')
def hr_dashboard():
    if 'user_id' not in session or session['user_type'] != 'hr':
        return redirect(url_for('login'))

    return render_template('hr_dashboard.html')

# Forgot Password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("Passwords do not match!", 'danger')
            return render_template('forgot_password.html')

        try:
            # Check if the username and email match a record in the database
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM employees WHERE username=%s AND email=%s", (username, email))
            user = cursor.fetchone()

            if not user:
                cursor.execute("SELECT * FROM hr WHERE username=%s AND email=%s", (username, email))
                user = cursor.fetchone()
                user_type = 'hr'

            if user:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                if user_type == 'employee':
                    cursor.execute("UPDATE employees SET password=%s WHERE username=%s", (hashed_password, username))
                else:
                    cursor.execute("UPDATE hr SET password=%s WHERE username=%s", (hashed_password, username))
                flash("Password reset successfully", 'success')
                return redirect(url_for('login'))
            else:
                flash("Incorrect username or email", 'danger')
                return render_template('forgot_password.html')

        except Exception as e:
            flash(f"Error during password reset: {str(e)}", 'danger')
            return render_template('forgot_password.html')

    return render_template('forgot_password.html')

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session['user_type'] != 'hr':
        return redirect(url_for('login'))

    if request.method == 'POST':
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        skills_required = request.form['skills_required']
        location = request.form['location']

        try:
            cursor = mysql.connection.cursor()

            # Fetch company name for logged in HR
            cursor.execute("SELECT company FROM hr WHERE id = %s", (session['user_id'],))
            company_result = cursor.fetchone()

            if not company_result:
                flash("Company info not found", 'danger')
                return redirect(url_for('hr_dashboard'))

            company_name = company_result[0]

            cursor.execute("INSERT INTO jobs (company, job_title, job_description, skills_required, location, posted_by) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (company_name, job_title, job_description, skills_required, location, session['user_id']))
            mysql.connection.commit()
            cursor.close()

            flash("Job posted successfully!", "success")
            return redirect(url_for('hr_dashboard'))

        except Exception as e:
            flash(f"Error posting job: {str(e)}", "danger")
            return redirect(url_for('post_job'))

    return render_template('post_job.html')


@app.route('/create_certificate', methods=['GET', 'POST'])
def create_certificate():
    if 'user_id' not in session:
        flash("You must be logged in to issue a certificate", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            # Extracting form data
            employee_name = request.form["employee_name"]
            job_role = request.form["job_role"]
            skills = request.form["skills"]
            performance = request.form["performance"]
            employee_username = request.form["employee_username"]

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT company FROM hr WHERE id = %s", (session['user_id'],))
            company_result = cursor.fetchone()

            if not company_result:
                flash("Company info not found", 'danger')
                return redirect(url_for('hr_dashboard'))

            company_name = company_result[0]

            # Get the current certificate count to use as cert_id
            cert_id = contract.functions.totalCertificates().call()

            # Build the transaction for issuing the certificate
            txn = contract.functions.issueCertificate(
                employee_name, employee_username,company_name, job_role, skills, performance
            ).build_transaction({
                "from": hr_account,
                "gas": 3000000,
                "nonce": w3.eth.get_transaction_count(hr_account),
            })

            # Sign and send the transaction
            signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
            txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

            # Store certificate ID and username in MySQL
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO employee_certificates (employee_username, certificate_id) VALUES (%s, %s)",
                           (employee_username, cert_id))
            mysql.connection.commit()
            cursor.close()

            # Return the transaction hash to confirm certificate issuance
            return f"✅ Certificate issued! <br>Transaction Hash: {txn_hash.hex()}"

        except Exception as e:
            flash(f"Error issuing certificate: {str(e)}", 'danger')
            return redirect(url_for('create_certificate'))

    # GET request: render the certificate creation form
    return render_template('create_certificate.html')

@app.route('/view_certificate')
def view_certificate():
    if 'user_id' not in session or session['user_type'] != 'employee':
        return redirect(url_for('login'))

    try:
        username = session['username']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT certificate_id FROM employee_certificates WHERE employee_username = %s", (username,))
        cert_ids = cursor.fetchall()
        certificates = []

        for row in cert_ids:
            cert_id = row[0]
            total = contract.functions.totalCertificates().call()
            if cert_id < total:
                cert = contract.functions.getCertificate(cert_id).call()
                issue_date = datetime.fromtimestamp(cert[6]).strftime("%Y-%m-%d %H:%M:%S")
                certificates.append({
                    "cert_id": cert_id,
                    "employee_name": cert[0],
                    "employee_id": cert[1],
                    "company_name": cert[2],
                    "job_role": cert[3],
                    "skills": cert[4],
                    "performance": cert[5],
                    "issue_date": issue_date
                })

        return render_template('view_certificate.html', certificates=certificates)

    except Exception as e:
        flash(f"Error loading certificates: {str(e)}", 'danger')
        return render_template('view_certificate.html', certificates=[])
    

@app.route('/hr_view_certificate') 
def hr_view_certificate():
    if 'user_id' not in session or session['user_type'] != 'hr':
        return redirect(url_for('login'))

    try:
        # Fetch company name for logged-in HR
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT company FROM hr WHERE id = %s", (session['user_id'],))
        company_result = cursor.fetchone()

        if not company_result:
            flash("Company info not found", 'danger')
            return redirect(url_for('hr_view_certificate'))

        company_name = company_result[0]

        # Fetch total number of certificates issued
        total_certificates = contract.functions.totalCertificates().call()

        # Get the list of certificates issued by this HR (matching the company name)
        certificates = []
        for cert_id in range(total_certificates):
            cert = contract.functions.getCertificate(cert_id).call()

            # Check if the certificate's company name matches the logged-in HR's company
            if cert[2] == company_name:
                issue_date = datetime.fromtimestamp(cert[6]).strftime("%Y-%m-%d %H:%M:%S")
                certificates.append({
                    "cert_id": cert_id,
                    "employee_name": cert[0],
                    "employee_id": cert[1],
                    "company_name": cert[2],
                    "job_role": cert[3],
                    "skills": cert[4],
                    "performance": cert[5],
                    "issue_date": issue_date
                })

        return render_template('hr_view_certificate.html', certificates=certificates) 

    except Exception as e:
        flash(f"Error loading certificates: {str(e)}", 'danger')
        return redirect(url_for('hr_view_certificate'))


@app.route('/view_jobs')
def view_jobs():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT company, job_title, skills_required, location, job_description, posted_on FROM jobs")
    jobs = cursor.fetchall()
    cursor.close()

    # Format the timestamp
    formatted_jobs = []
    for job in jobs:
        formatted_posted_on = job[5].strftime('%Y-%m-%d %H:%M')  # You can customize this format
        formatted_jobs.append((job[0], job[1], job[2], job[3], job[4], formatted_posted_on))

    return render_template("view_jobs.html", jobs=formatted_jobs)


    
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
