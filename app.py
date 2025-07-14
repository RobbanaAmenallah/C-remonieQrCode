from flask import Flask, request, render_template_string
import pandas as pd
import os
import io  # ✅ AJOUT OBLIGATOIRE

app = Flask(__name__)
DB_FILE = 'qr_database.csv'

HTML_TEMPLATE = """ 
... ton HTML ici inchangé ...
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
        # 🛠️ Lecture binaire puis décodage manuel avec latin1
        with open(DB_FILE, 'rb') as f:
            raw = f.read()
        content = raw.decode('latin1', errors='ignore')
        df = pd.read_csv(io.StringIO(content))  # ✅ fonctionne bien maintenant
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
        df.to_csv(DB_FILE, index=False, encoding='latin1')
        return render_template_string(
            HTML_TEMPLATE,
            message=f"✅ Bienvenue {prenom} {nom}",
            color="green",
            detail=f"Scan {scans}/3 effectué avec succès.",
            status_class="success fade-in",
            emoji="✅"
        )
    

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
        # 🛠️ Lecture binaire puis décodage manuel avec latin1
        with open(DB_FILE, 'rb') as f:
            raw = f.read()
        content = raw.decode('latin1', errors='ignore')  # ignore les erreurs éventuelles
        df = pd.read_csv(io.StringIO(content))
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
        df.to_csv(DB_FILE, index=False, encoding='latin1')  # ✅ cohérent
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
    return """ ... (garde ici ton HTML de la page d’accueil) ... """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)