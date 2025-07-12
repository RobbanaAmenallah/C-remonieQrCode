from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import pandas as pd

DB_FILE = "qr_database.csv"

class QRScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.label = Label(text="Entrez le code QR (UUID)")
        self.input = TextInput(multiline=False)
        self.button = Button(text="Scanner le code")
        self.result = Label(text="")

        self.button.bind(on_press=self.verify_qr)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.input)
        self.layout.add_widget(self.button)
        self.layout.add_widget(self.result)

        return self.layout

    def verify_qr(self, instance):
        code = self.input.text.strip()
        try:
            df = pd.read_csv(DB_FILE)
        except Exception as e:
            self.result.text = f"Erreur lecture base : {e}"
            return

        match = df[df['uuid'] == code]

        if match.empty:
            self.result.text = "❌ Code invalide."
            return

        scans = int(match.iloc[0]['scan_count'])
        nom = match.iloc[0]['nom']
        prenom = match.iloc[0]['prenom']

        if scans >= 3:
            self.result.text = f"🚫 {prenom} {nom} - Invitation déjà utilisée 3 fois."
        else:
            scans += 1
            df.loc[df['uuid'] == code, 'scan_count'] = scans
            df.to_csv(DB_FILE, index=False)
            self.result.text = f"✅ Bienvenue {prenom} {nom} - Scan {scans}/3 autorisé."

if __name__ == '__main__':
    QRScannerApp().run()

