from flask import Flask, request, render_template_string, send_from_directory
import pandas as pd
import os

app = Flask(__name__)
DB_FILE = 'qr_database.csv'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Contrôle QR - Cérémonie de remise des diplômes ESSECT</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 500px;
            margin: 40px auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        .success {
            background-color: #e8f5e9;
            border-left: 6px solid #43a047;
        }
        .error {
            background-color: #ffebee;
            border-left: 6px solid #e53935;
        }
        .warning {
            background-color: #fff3e0;
            border-left: 6px solid #fb8c00;
        }
        .fade-in {
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        img.logo {
            width: 100px;
            margin-bottom: 20px;
        }
        .icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        h1 {
            font-size: 24px;
            color: {{ color }};
            margin: 10px 0;
        }
        p {
            font-size: 18px;
            color: #333;
        }
        footer {
            margin-top: 20px;
            font-size: 12px;
            color: #aaa;
        }
    </style>
</head>
<body>
    <div class="container {{ status_class }}">
        <div class="icon">{{ emoji }}</div>
        <img src="/static/essect.png" alt="Logo ESSECT" class="logo">
        <h1>{{ message }}</h1>
        {% if detail %}
        <p>{{ detail }}</p>
        {% endif %}
        <footer>© 2025 ESSECT - QR Contrôle</footer>
    </div>
</body>
</html>
"""

@app.route('/scan')
def scan():
    code = request.args.get('code')
    if not code:
        return render_template_string(
            HTML_TEMPLATE,
            message="❌ Code manquant",
            color="red",
            detail="Le paramètre 'code' est requis.",
            status_class="error fade-in",
            emoji="❌"
        )

    try:
        df = pd.read_csv(DB_FILE)
    except Exception as e:
        return render_template_string(
            HTML_TEMPLATE,
            message="❌ Erreur serveur",
            color="red",
            detail=str(e),
            status_class="error fade-in",
            emoji="💥"
        )

    match = df[df['uuid'] == code]
    if match.empty:
        return render_template_string(
            HTML_TEMPLATE,
            message="❌ Code invalide",
            color="red",
            detail="Ce QR code ne correspond à aucun enregistrement.",
            status_class="error fade-in",
            emoji="❌"
        )

    scans = int(match.iloc[0]['scan_count'])
    nom = match.iloc[0]['nom']
    prenom = match.iloc[0]['prenom']

    if scans >= 3:
        return render_template_string(
            HTML_TEMPLATE,
            message="🚫 Accès refusé",
            color="orange",
            detail=f"{prenom} {nom} a déjà utilisé son QR code 3 fois.",
            status_class="warning fade-in",
            emoji="🚫"
        )
    else:
        scans += 1
        df.loc[df['uuid'] == code, 'scan_count'] = scans
        df.to_csv(DB_FILE, index=False)
        return render_template_string(
            HTML_TEMPLATE,
            message=f"✅ Bienvenue {prenom} {nom}",
            color="green",
            detail=f"Scan {scans}/3 effectué avec succès.",
            status_class="success fade-in",
            emoji="✅"
        )

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Serveur QR - ESSECT</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e0f7fa, #ffffff);
            text-align: center;
            padding: 50px;
            color: #333;
        }
        img {
            width: 100px;
            margin-bottom: 20px;
        }
        h2 {
            font-size: 28px;
            color: #00796b;
        }
        p {
            font-size: 18px;
            margin-top: 20px;
        }
        code {
            background-color: #f1f1f1;
            padding: 4px 8px;
            border-radius: 4px;
            color: #d84315;
            font-weight: bold;
        }
        footer {
            margin-top: 50px;
            font-size: 14px;
            color: #888;
        }
        .badge {
            background-color: #004d40;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            display: inline-block;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <img src="/static/essect.png" alt="Logo ESSECT">
    <h2>🚀 Bienvenue sur le Serveur QR Code de l'ESSECT</h2>
    <p>Scannez un QR code contenant une URL au format :</p>
    <p><code>/scan?code=...</code></p>
    <div class="badge">Créé par INFOLAB - 2025</div>
    <footer>
        &copy; ESSECT - Tous droits réservés
    </footer>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
