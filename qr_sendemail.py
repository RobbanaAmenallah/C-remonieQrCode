import pandas as pd
import qrcode
import os
import smtplib
import uuid
from email.message import EmailMessage

# ✅ Identifiants Gmail (remplace avec tes infos)
EMAIL_ADDRESS = 'boukhdhirdhia@gmail.com'
EMAIL_PASSWORD = 'rjxm pmtg fjuc fjuy'  # mot de passe d'application Gmail

# ✅ Charger le fichier Excel des étudiants
df = pd.read_excel('./etudiants (3).xlsx')  # Le fichier doit avoir les colonnes: Prenom, Nom, Email, Niveau

# ✅ Dossier pour stocker les QR codes
os.makedirs('qr_codes', exist_ok=True)

# ✅ Création de la base de données CSV partagée
DB_FILE = 'qr_database.csv'
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        f.write("uuid,prenom,nom,email,niveau,scan_count\n")

# ✅ Fonction pour envoyer un e-mail avec pièce jointe
def send_email(to_email, subject, body, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)

    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
    msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print(f"✅ Email envoyé à {to_email}")

# ✅ Parcourir les étudiants
for index, row in df.iterrows():
    email = str(row['Email']).strip()

    # Vérification de l'adresse email
    if pd.isna(email) or '@' not in email:
        print(f"❌ Email invalide pour {row['Prenom']} {row['Nom']} - ignoré.")
        continue

    # Génération d’un identifiant unique
    unique_id = str(uuid.uuid4())
    qr_url = f"https://c-remonieqrcode.onrender.com/scan?code={unique_id}"
    qr = qrcode.make(qr_url)
    qr_filename = f"qr_codes/{row['Prenom']}_{row['Nom']}.png"
    qr.save(qr_filename)

    # Sauvegarde dans la base CSV
    with open(DB_FILE, 'a') as f:
        f.write(f"{unique_id},{row['Prenom']},{row['Nom']},{email},{row['Niveau']},0\n")

    # Corps de l'email
    subject = "🎓 Invitation à la cérémonie ESSSECT 2024"
    body = f"""
Bonjour {row['Prenom']} {row['Nom']},

Veuillez trouver ci-joint votre QR code personnel pour la cérémonie de fin d'année.

🔒 Ce code permet un maximum de 3 scans à l'entrée.

Cordialement,
Le Comité ESSSECT
"""

    # Envoi de l'email
    try:
        send_email(email, subject, body, qr_filename)
    except Exception as e:
        print(f"❌ Échec envoi à {email} : {e}")

print("✅ Tous les emails valides ont été traités.")

