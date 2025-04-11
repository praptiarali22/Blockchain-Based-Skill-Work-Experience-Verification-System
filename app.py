from flask import Flask, render_template, redirect, url_for
from routes.certificates import cert_routes

app = Flask(__name__, template_folder='templates')  # Ensure Flask knows where templates are
app.register_blueprint(cert_routes)

@app.route('/')
def home():
    return redirect(url_for('cert_routes.dashboard'))  # dashboard instead of my_certificates

if __name__ == '__main__':
    app.run(debug=True)
