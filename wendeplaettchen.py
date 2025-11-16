import math
import random
import tkinter as tk


class WendeplaettchenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wendeplättchen Werfen")
        self.root.geometry("900x800")
        self.root.configure(bg="#f0f0f0")

        # Anzahl der Plättchen
        self.anzahl = 0
        self.plaettchen = []
        self.animation_laueft = False
        self.zwanzigerfeld_zellen = []
        self.gezogenes_plaettchen = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.hat_bewegt = False

        # Initial keine Plättchen
        self.plaettchen_farben = []

        self.wurde_geworfen = False

        # Hauptframe für Zwanzigerfeld und Button
        haupt_frame = tk.Frame(root, bg="#f0f0f0")
        haupt_frame.pack(pady=20)

        # Zwanzigerfeld für Anzahl-Auswahl
        zwanzigerfeld_frame = tk.Frame(haupt_frame, bg="#f0f0f0")
        zwanzigerfeld_frame.pack(side=tk.LEFT, padx=10)

        # Canvas für Zwanzigerfeld (mit Kreisen)
        self.zwanzigerfeld_canvas = tk.Canvas(
            zwanzigerfeld_frame,
            width=540,
            height=120,
            bg="white",
            highlightthickness=2,
            highlightbackground="#999",
        )
        self.zwanzigerfeld_canvas.pack(padx=10, pady=5)

        # Zeichne Zwanzigerfeld mit Kreisen (2 Reihen x 10 Spalten, Lücke in der Mitte)
        kreis_radius = 20
        start_x = 40
        start_y = 30
        abstand_x = 50
        abstand_y = 60
        luecke = 20  # Zusätzliche Lücke in der Mitte

        for reihe in range(2):
            for spalte in range(10):
                nummer = reihe * 10 + spalte + 1
                x = start_x + spalte * abstand_x

                # Lücke nach der 5. Position hinzufügen
                if spalte >= 5:
                    x += luecke

                y = start_y + reihe * abstand_y

                # Kreis zeichnen
                kreis = self.zwanzigerfeld_canvas.create_oval(
                    x - kreis_radius,
                    y - kreis_radius,
                    x + kreis_radius,
                    y + kreis_radius,
                    fill="white",
                    outline="#666",
                    width=2,
                    tags=f"kreis_{nummer}",
                )

                self.zwanzigerfeld_zellen.append(
                    {"kreis": kreis, "nummer": nummer, "x": x, "y": y}
                )

                # Klick-Event (nur wenn noch nicht geworfen wurde)
                self.zwanzigerfeld_canvas.tag_bind(
                    f"kreis_{nummer}",
                    "<Button-1>",
                    lambda e, n=nummer: self.wähle_anzahl(n),
                )

        # Initial keine Felder markieren
        self.aktualisiere_zwanzigerfeld()

        # Initial 5 Felder markieren
        self.aktualisiere_zwanzigerfeld()

        # Button-Frame
        button_frame = tk.Frame(haupt_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.LEFT, padx=10)

        # Werfen-Button
        self.werfen_button = tk.Button(
            button_frame,
            text="Werfen!",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=20,
            command=self.werfen,
            cursor="hand2",
        )
        self.werfen_button.pack(pady=5)

        # Reset-Button
        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            font=("Arial", 14, "bold"),
            bg="#FF9800",
            fg="white",
            padx=30,
            pady=15,
            command=self.reset,
            cursor="hand2",
            state=tk.DISABLED,  # Initial deaktiviert
        )
        self.reset_button.pack(pady=5)

        # Canvas für Plättchen
        self.canvas = tk.Canvas(
            root, bg="white", highlightthickness=1, highlightbackground="#ccc"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        # Maus-Events für Plättchen
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def on_canvas_click(self, event):
        """Behandelt Klicks auf Plättchen"""
        if self.animation_laueft:
            return

        # Finde angeklicktes Plättchen
        for plaettchen in self.plaettchen:
            if plaettchen.get("id"):
                dx = event.x - plaettchen["x"]
                dy = event.y - plaettchen["y"]
                abstand = math.sqrt(dx * dx + dy * dy)

                if abstand <= plaettchen["radius"]:
                    # Plättchen wurde angeklickt
                    self.gezogenes_plaettchen = plaettchen
                    self.drag_offset_x = dx
                    self.drag_offset_y = dy
                    self.hat_bewegt = False
                    return

    def on_canvas_drag(self, event):
        """Behandelt das Ziehen von Plättchen"""
        if self.gezogenes_plaettchen and not self.animation_laueft:
            self.hat_bewegt = True  # Markiere als bewegt

            canvas_breite = self.canvas.winfo_width()
            canvas_hoehe = self.canvas.winfo_height()
            radius = self.gezogenes_plaettchen["radius"]

            # Neue Position berechnen
            neue_x = event.x - self.drag_offset_x
            neue_y = event.y - self.drag_offset_y

            # Begrenzung auf Canvas
            neue_x = max(radius, min(neue_x, canvas_breite - radius))
            neue_y = max(radius, min(neue_y, canvas_hoehe - radius))

            # Position aktualisieren
            self.gezogenes_plaettchen["x"] = neue_x
            self.gezogenes_plaettchen["y"] = neue_y
            self.gezogenes_plaettchen["ziel_x"] = neue_x
            self.gezogenes_plaettchen["ziel_y"] = neue_y

            # Canvas aktualisieren
            self.canvas.coords(
                self.gezogenes_plaettchen["id"],
                neue_x - radius,
                neue_y - radius,
                neue_x + radius,
                neue_y + radius,
            )

    def on_canvas_release(self, event):
        """Behandelt das Loslassen der Maus"""
        # Nur Farbe wechseln, wenn nicht gezogen wurde
        if self.gezogenes_plaettchen and not self.hat_bewegt:
            self.animiere_farbwechsel(self.gezogenes_plaettchen)

        self.gezogenes_plaettchen = None
        self.hat_bewegt = False

    def animiere_farbwechsel(self, plaettchen, schritt=0):
        """Animiert den Farbwechsel eines Plättchens mit Wende-Animation"""
        if schritt == 0:
            # Farbe wechseln
            if plaettchen["farbe"] == "#E53935":
                neue_farbe = "#1E88E5"
                plaettchen["farbe"] = neue_farbe
            else:
                neue_farbe = "#E53935"
                plaettchen["farbe"] = neue_farbe

            # Animations-Daten speichern
            plaettchen["animation_ziel"] = neue_farbe
            plaettchen["animation_start_x"] = plaettchen["x"]
            plaettchen["animation_start_y"] = plaettchen["y"]
            plaettchen["original_radius"] = plaettchen["radius"]

        total_schritte = 20

        # Animation durchführen
        if schritt < total_schritte:
            faktor = schritt / float(total_schritte)
            radius = plaettchen["original_radius"]
            x = plaettchen["animation_start_x"]
            y = plaettchen["animation_start_y"]

            # Drehanimation simulieren durch Breite/Höhe Änderung
            if schritt < total_schritte / 2:
                # Erste Hälfte: Plättchen wird schmaler (dreht sich zur Seite)
                breite_faktor = 1.0 - (schritt / (total_schritte / 2))
                hoehe_sprung = -10 * (
                    schritt / (total_schritte / 2)
                )  # Springt leicht hoch

                # Behalte alte Farbe
                if plaettchen["animation_ziel"] == "#1E88E5":
                    aktuelle_farbe = "#E53935"
                else:
                    aktuelle_farbe = "#1E88E5"
            else:
                # Zweite Hälfte: Plättchen wird wieder breiter (mit neuer Farbe)
                breite_faktor = (schritt - total_schritte / 2) / (total_schritte / 2)
                hoehe_sprung = -10 * (
                    1.0 - (schritt - total_schritte / 2) / (total_schritte / 2)
                )  # Fällt zurück

                # Zeige neue Farbe
                aktuelle_farbe = plaettchen["animation_ziel"]

            # Ellipse zeichnen (simuliert Drehung)
            breite = max(radius * breite_faktor, 3)  # Mindestbreite von 3 Pixel

            self.canvas.coords(
                plaettchen["id"],
                x - breite,
                y - radius + hoehe_sprung,
                x + breite,
                y + radius + hoehe_sprung,
            )
            self.canvas.itemconfig(plaettchen["id"], fill=aktuelle_farbe)

            self.root.after(
                25, lambda: self.animiere_farbwechsel(plaettchen, schritt + 1)
            )
        else:
            # Animation beendet, zurück zur normalen Form
            radius = plaettchen["original_radius"]
            x = plaettchen["animation_start_x"]
            y = plaettchen["animation_start_y"]

            self.canvas.coords(
                plaettchen["id"], x - radius, y - radius, x + radius, y + radius
            )
            self.canvas.itemconfig(plaettchen["id"], fill=plaettchen["farbe"])

            # Synchronisiere mit Zwanzigertafel
            self.synchronisiere_farben()

    def wähle_anzahl(self, anzahl):
        """Wählt die Anzahl der Plättchen über das Zwanzigerfeld"""
        # Nur erlaubt wenn noch nicht geworfen wurde
        if self.wurde_geworfen:
            return

        self.anzahl = anzahl

        # Erstelle zufällige Farbverteilung
        farben = []
        for _ in range(anzahl):
            farbe = random.choice(["#1E88E5", "#E53935"])
            farben.append(farbe)

        # Sortiere: erst blau, dann rot
        farben.sort(key=lambda f: 0 if f == "#1E88E5" else 1)
        self.plaettchen_farben = farben

        self.aktualisiere_zwanzigerfeld()

    def aktualisiere_zwanzigerfeld(self):
        """Aktualisiert die Darstellung des Zwanzigerfelds"""
        for i, zelle in enumerate(self.zwanzigerfeld_zellen):
            if i < self.anzahl:
                # Immer grau für ausgewählte Plättchen
                self.zwanzigerfeld_canvas.itemconfig(
                    zelle["kreis"], fill="#9E9E9E", outline="#666"
                )
            else:
                # Leerer Kreis (weiß für nicht ausgewählte)
                self.zwanzigerfeld_canvas.itemconfig(
                    zelle["kreis"], fill="white", outline="#666"
                )

    def synchronisiere_farben(self):
        """Synchronisiert Farben zwischen Plättchen und Zwanzigertafel"""
        # Zähle Farben in Plättchen
        blau_count = 0
        rot_count = 0

        for plaettchen in self.plaettchen:
            if plaettchen.get("farbe") == "#1E88E5":
                blau_count += 1
            elif plaettchen.get("farbe") == "#E53935":
                rot_count += 1

        # Erstelle sortiertes Farben-Array (erst blau, dann rot)
        self.plaettchen_farben = ["#1E88E5"] * blau_count + ["#E53935"] * rot_count

        # Aktualisiere Zwanzigertafel
        self.aktualisiere_zwanzigerfeld()

    def prüfe_überlappung(self, x, y, radius, belegte_positionen):
        """Prüft ob eine Position mit bereits belegten Positionen überlappt"""
        min_abstand = radius * 2 + 5  # Mindestabstand zwischen Plättchen

        for pos in belegte_positionen:
            dx = x - pos["x"]
            dy = y - pos["y"]
            abstand = math.sqrt(dx * dx + dy * dy)

            if abstand < min_abstand:
                return True
        return False

    def finde_freie_position(
        self, radius, canvas_breite, canvas_hoehe, belegte_positionen, max_versuche=100
    ):
        """Findet eine freie Position ohne Überlappung"""
        for _ in range(max_versuche):
            x = random.randint(radius + 10, canvas_breite - radius - 10)
            y = random.randint(radius + 10, canvas_hoehe - radius - 10)

            if not self.prüfe_überlappung(x, y, radius, belegte_positionen):
                return x, y

        # Fallback: Gebe Position zurück, auch wenn sie überlappt
        return (
            random.randint(radius + 10, canvas_breite - radius - 10),
            random.randint(radius + 10, canvas_hoehe - radius - 10),
        )

    def werfen(self):
        # Verhindere mehrfaches Werfen während Animation
        if self.animation_laueft:
            return

        # Markiere als geworfen
        self.wurde_geworfen = True

        # Deaktiviere Werfen-Button und aktiviere Reset-Button
        self.werfen_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)

        # Canvas leeren
        self.canvas.delete("all")
        self.plaettchen = []

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
            ziel_x, ziel_y = self.finde_freie_position(
                radius, canvas_breite, canvas_hoehe, belegte_positionen
            )
            belegte_positionen.append({"x": ziel_x, "y": ziel_y})

            # Startposition (oben außerhalb des Canvas)
            start_x = random.randint(radius + 10, canvas_breite - radius - 10)
            start_y = -radius - 20

            # Farbe aus Array nehmen (falls vorhanden) oder zufällig
            if i < len(self.plaettchen_farben):
                farbe = self.plaettchen_farben[i]
            else:
                ist_rot = random.choice([True, False])
                farbe = "#E53935" if ist_rot else "#1E88E5"
                self.plaettchen_farben.append(farbe)

            if farbe == "#E53935":
                anzahl_rot += 1
            else:
                anzahl_blau += 1

            # Plättchen erstellen (initial unsichtbar)
            kreis_id = self.canvas.create_oval(
                start_x - radius,
                start_y - radius,
                start_x + radius,
                start_y + radius,
                fill=farbe,
                outline="#333",
                width=2,
            )

            # Plättchen-Daten speichern
            self.plaettchen.append(
                {
                    "id": kreis_id,
                    "x": start_x,
                    "y": start_y,
                    "ziel_x": ziel_x,
                    "ziel_y": ziel_y,
                    "farbe": farbe,
                    "radius": radius,
                    "geschwindigkeit_y": 0,
                    "geschwindigkeit_x": (ziel_x - start_x) / 30,
                    "verzögerung": i * 2,  # Verzögerte Starts für Welleneffekt
                }
            )

        # Animation starten
        self.animation_laueft = True
        self.animiere()

        # Aktualisiere Zwanzigertafel nach dem Werfen
        self.synchronisiere_farben()

    def animiere(self):
        alle_fertig = True

        for plaettchen in self.plaettchen:
            # Verzögerung berücksichtigen
            if plaettchen["verzögerung"] > 0:
                plaettchen["verzögerung"] -= 1
                alle_fertig = False
                continue

            # Prüfe ob Plättchen bereits am Ziel ist
            if plaettchen["y"] >= plaettchen["ziel_y"]:
                # Plättchen ist gelandet - kleine Bounce-Effekt
                if plaettchen.get("bounce", 0) < 5:
                    bounce_höhe = 5 - plaettchen.get("bounce", 0)
                    plaettchen["y"] = plaettchen["ziel_y"] - bounce_höhe
                    plaettchen["bounce"] = plaettchen.get("bounce", 0) + 1
                    alle_fertig = False
                else:
                    plaettchen["y"] = plaettchen["ziel_y"]
                    plaettchen["x"] = plaettchen["ziel_x"]
            else:
                # Plättchen fällt noch
                alle_fertig = False

                # Gravitation simulieren
                plaettchen["geschwindigkeit_y"] += 1.5
                plaettchen["y"] += plaettchen["geschwindigkeit_y"]
                plaettchen["x"] += plaettchen["geschwindigkeit_x"]

                # Dämpfung wenn nahe am Ziel
                if plaettchen["y"] > plaettchen["ziel_y"]:
                    plaettchen["y"] = plaettchen["ziel_y"]
                    plaettchen["geschwindigkeit_y"] = 0

            # Position aktualisieren
            radius = plaettchen["radius"]
            self.canvas.coords(
                plaettchen["id"],
                plaettchen["x"] - radius,
                plaettchen["y"] - radius,
                plaettchen["x"] + radius,
                plaettchen["y"] + radius,
            )

        # Nächster Frame oder Animation beenden
        if not alle_fertig:
            self.root.after(16, self.animiere)  # ~60 FPS
        else:
            self.animation_laueft = False

    def reset(self):
        """Setzt das Spiel zurück"""
        # Zurücksetzen der Variablen
        self.wurde_geworfen = False
        self.animation_laueft = False

        # Canvas leeren
        self.canvas.delete("all")
        self.plaettchen = []

        # Buttons zurücksetzen
        self.werfen_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)

        # Erstelle neue zufällige Farbverteilung für die aktuelle Anzahl
        farben = []
        for _ in range(self.anzahl):
            farbe = random.choice(["#1E88E5", "#E53935"])
            farben.append(farbe)
        # Sortiere: erst blau, dann rot
        farben.sort(key=lambda f: 0 if f == "#1E88E5" else 1)
        self.plaettchen_farben = farben

        # Aktualisiere Zwanzigerfeld (zeigt wieder grau)
        self.aktualisiere_zwanzigerfeld()


def main():
    root = tk.Tk()
    app = WendeplaettchenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
