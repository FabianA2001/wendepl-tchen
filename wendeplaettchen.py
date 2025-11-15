import tkinter as tk
from tkinter import ttk
import random
import math


class WendeplaettchenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wendeplättchen Werfen")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Anzahl der Plättchen
        self.anzahl = 10
        self.plaettchen = []
        self.animation_laueft = False
        
        # Titel
        titel = tk.Label(
            root, 
            text="Wendeplättchen", 
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0'
        )
        titel.pack(pady=20)
        
        # Steuerungsframe
        steuerung_frame = tk.Frame(root, bg='#f0f0f0')
        steuerung_frame.pack(pady=10)
        
        # Anzahl-Auswahl
        tk.Label(
            steuerung_frame, 
            text="Anzahl:", 
            font=('Arial', 12),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=5)
        
        self.anzahl_var = tk.StringVar(value="10")
        anzahl_spinbox = ttk.Spinbox(
            steuerung_frame,
            from_=1,
            to=50,
            textvariable=self.anzahl_var,
            width=10,
            font=('Arial', 12)
        )
        anzahl_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Werfen-Button
        werfen_button = tk.Button(
            steuerung_frame,
            text="Wendeplättchen werfen!",
            font=('Arial', 14, 'bold'),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            command=self.werfen,
            cursor='hand2'
        )
        werfen_button.pack(side=tk.LEFT, padx=20)
        
        # Statistik-Label
        self.statistik_label = tk.Label(
            root,
            text="",
            font=('Arial', 12),
            bg='#f0f0f0'
        )
        self.statistik_label.pack(pady=10)
        
        # Canvas für Plättchen
        self.canvas = tk.Canvas(
            root,
            bg='white',
            highlightthickness=1,
            highlightbackground='#ccc'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def prüfe_überlappung(self, x, y, radius, belegte_positionen):
        """Prüft ob eine Position mit bereits belegten Positionen überlappt"""
        min_abstand = radius * 2 + 5  # Mindestabstand zwischen Plättchen
        
        for pos in belegte_positionen:
            dx = x - pos['x']
            dy = y - pos['y']
            abstand = math.sqrt(dx * dx + dy * dy)
            
            if abstand < min_abstand:
                return True
        return False
    
    def finde_freie_position(self, radius, canvas_breite, canvas_hoehe, belegte_positionen, max_versuche=100):
        """Findet eine freie Position ohne Überlappung"""
        for _ in range(max_versuche):
            x = random.randint(radius + 10, canvas_breite - radius - 10)
            y = random.randint(radius + 10, canvas_hoehe - radius - 10)
            
            if not self.prüfe_überlappung(x, y, radius, belegte_positionen):
                return x, y
        
        # Fallback: Gebe Position zurück, auch wenn sie überlappt
        return (random.randint(radius + 10, canvas_breite - radius - 10),
                random.randint(radius + 10, canvas_hoehe - radius - 10))
    
    def werfen(self):
        # Verhindere mehrfaches Werfen während Animation
        if self.animation_laueft:
            return
            
        # Canvas leeren
        self.canvas.delete("all")
        self.plaettchen = []
        
        try:
            self.anzahl = int(self.anzahl_var.get())
            if self.anzahl < 1 or self.anzahl > 50:
                self.anzahl = 10
                self.anzahl_var.set("10")
        except ValueError:
            self.anzahl = 10
            self.anzahl_var.set("10")
        
        # Canvas-Größe ermitteln
        canvas_breite = self.canvas.winfo_width()
        canvas_hoehe = self.canvas.winfo_height()
        
        # Wenn Canvas noch nicht gerendert wurde
        if canvas_breite <= 1:
            canvas_breite = 760
            canvas_hoehe = 400
        
        # Plättchen-Größe basierend auf Anzahl
        if self.anzahl <= 10:
            radius = 40
        elif self.anzahl <= 20:
            radius = 30
        else:
            radius = 20
        
        # Zufällige Ziel-Positionen und Farben generieren
        anzahl_rot = 0
        anzahl_blau = 0
        belegte_positionen = []
        
        for i in range(self.anzahl):
            # Finde freie Zielposition ohne Überlappung
            ziel_x, ziel_y = self.finde_freie_position(radius, canvas_breite, canvas_hoehe, belegte_positionen)
            belegte_positionen.append({'x': ziel_x, 'y': ziel_y})
            
            # Startposition (oben außerhalb des Canvas)
            start_x = random.randint(radius + 10, canvas_breite - radius - 10)
            start_y = -radius - 20
            
            # Zufällige Farbe (rot oder blau)
            ist_rot = random.choice([True, False])
            farbe = '#E53935' if ist_rot else '#1E88E5'
            
            if ist_rot:
                anzahl_rot += 1
            else:
                anzahl_blau += 1
            
            # Plättchen erstellen (initial unsichtbar)
            kreis_id = self.canvas.create_oval(
                start_x - radius, start_y - radius,
                start_x + radius, start_y + radius,
                fill=farbe,
                outline='#333',
                width=2
            )
            
            # Plättchen-Daten speichern
            self.plaettchen.append({
                'id': kreis_id,
                'x': start_x,
                'y': start_y,
                'ziel_x': ziel_x,
                'ziel_y': ziel_y,
                'farbe': farbe,
                'radius': radius,
                'geschwindigkeit_y': 0,
                'geschwindigkeit_x': (ziel_x - start_x) / 30,
                'verzögerung': i * 2  # Verzögerte Starts für Welleneffekt
            })
        
        # Statistik aktualisieren
        self.statistik_label.config(
            text=f"Rot: {anzahl_rot} | Blau: {anzahl_blau} | Gesamt: {self.anzahl}"
        )
        
        # Animation starten
        self.animation_laueft = True
        self.animiere()
    
    def animiere(self):
        alle_fertig = True
        
        for plaettchen in self.plaettchen:
            # Verzögerung berücksichtigen
            if plaettchen['verzögerung'] > 0:
                plaettchen['verzögerung'] -= 1
                alle_fertig = False
                continue
            
            # Prüfe ob Plättchen bereits am Ziel ist
            if plaettchen['y'] >= plaettchen['ziel_y']:
                # Plättchen ist gelandet - kleine Bounce-Effekt
                if plaettchen.get('bounce', 0) < 5:
                    bounce_höhe = 5 - plaettchen.get('bounce', 0)
                    plaettchen['y'] = plaettchen['ziel_y'] - bounce_höhe
                    plaettchen['bounce'] = plaettchen.get('bounce', 0) + 1
                    alle_fertig = False
                else:
                    plaettchen['y'] = plaettchen['ziel_y']
                    plaettchen['x'] = plaettchen['ziel_x']
            else:
                # Plättchen fällt noch
                alle_fertig = False
                
                # Gravitation simulieren
                plaettchen['geschwindigkeit_y'] += 1.5
                plaettchen['y'] += plaettchen['geschwindigkeit_y']
                plaettchen['x'] += plaettchen['geschwindigkeit_x']
                
                # Dämpfung wenn nahe am Ziel
                if plaettchen['y'] > plaettchen['ziel_y']:
                    plaettchen['y'] = plaettchen['ziel_y']
                    plaettchen['geschwindigkeit_y'] = 0
            
            # Position aktualisieren
            radius = plaettchen['radius']
            self.canvas.coords(
                plaettchen['id'],
                plaettchen['x'] - radius,
                plaettchen['y'] - radius,
                plaettchen['x'] + radius,
                plaettchen['y'] + radius
            )
        
        # Nächster Frame oder Animation beenden
        if not alle_fertig:
            self.root.after(16, self.animiere)  # ~60 FPS
        else:
            self.animation_laueft = False


def main():
    root = tk.Tk()
    app = WendeplaettchenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
