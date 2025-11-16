import os
import tkinter as tk
from tkinter import Canvas

from PIL import Image, ImageTk


class GeldGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Geld Drag & Drop")
        self.root.geometry("1400x800")

        # Canvas für die gesamte GUI
        self.canvas = Canvas(root, bg="lightgray", width=1400, height=800)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bilder speichern
        self.images = {}
        self.image_refs = []  # Verhindert Garbage Collection

        # Gezogene Objekte im mittleren Bereich
        self.dropped_items = []

        # Lade Bilder
        self.load_images()

        # Erstelle Layout
        self.create_layout()

        # Drag & Drop Variablen
        self.drag_data = {"item": None, "x": 0, "y": 0, "is_copy": False}

    def load_images(self):
        """Lädt alle Geldbilder"""
        geld_dir = "geld_png"

        # Münzen (Cent und Euro Münzen)
        self.coins = [
            ("1cent", "1cent.png"),
            ("2cent", "2cent.png"),
            ("5cent", "5cent.png"),
            ("10cent", "10cent.png"),
            ("20cent", "20cent.png"),
            ("50cent", "50cent.png"),
            ("1euro", "1euro.png"),
            ("2euro", "2euro.png"),
        ]

        # Scheine
        self.bills = [
            ("5euro", "5euro.png"),
            ("10euro", "10euro.png"),
            ("20euro", "20euro.png"),  # Falls vorhanden
            ("50euro", "50euro.png"),
            ("100euro", "100euro.jpg"),
            ("200euro", "200euro.png"),
            ("500euro", "500euro.png"),
        ]

        # Lade Münzbilder - kleinere Münzen mit unterschiedlichen Größen
        coin_sizes = {
            "1cent": 50,
            "2cent": 55,
            "5cent": 60,
            "10cent": 55,
            "20cent": 60,
            "50cent": 65,
            "1euro": 68,
            "2euro": 70,
        }

        for name, filename in self.coins:
            filepath = os.path.join(geld_dir, filename)
            if os.path.exists(filepath):
                img = Image.open(filepath)
                size = coin_sizes.get(name, 60)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                self.images[name] = ImageTk.PhotoImage(img)
                self.image_refs.append(self.images[name])

                # Lade Scheinbilder - alle in einheitlicher Anzeigegröße
        # Aber mit unterschiedlichen Skalierungsfaktoren basierend auf Originalbildgröße
        for name, filename in self.bills:
            filepath = os.path.join(geld_dir, filename)
            if os.path.exists(filepath):
                img = Image.open(filepath)
                # Proportionen des Originalbildes beibehalten
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                # Einheitliche Höhe, Breite proportional
                target_height = 77
                target_width = int(target_height * aspect_ratio)
                img = img.resize(
                    (target_width, target_height), Image.Resampling.LANCZOS
                )
                self.images[name] = ImageTk.PhotoImage(img)
                self.image_refs.append(self.images[name])

    def create_layout(self):
        """Erstellt das Layout mit Münzen links, Scheinen rechts und Mitte frei"""

        # Linke Seite: Münzen
        x_left = 50
        y_start = 100
        y_spacing = 90

        for i, (name, _) in enumerate(self.coins):
            if name in self.images:
                y = y_start + i * y_spacing
                item = self.canvas.create_image(
                    x_left, y, image=self.images[name], tags=("coin", name, "source")
                )

        # Rechte Seite: Scheine - mit angepasstem Abstand
        x_right = 1320
        y_start = 80
        y_spacing = 95

        for i, (name, _) in enumerate(self.bills):
            if name in self.images:
                y = y_start + i * y_spacing
                item = self.canvas.create_image(
                    x_right, y, image=self.images[name], tags=("bill", name, "source")
                )

        # Mittlerer Bereich - Markierung
        self.canvas.create_rectangle(
            200, 50, 1200, 750, outline="darkgray", width=2, dash=(5, 5)
        )

        # Bind Events
        self.canvas.tag_bind("source", "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)

    def on_drag_start(self, event):
        """Startet den Drag-Vorgang"""
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)

        if "source" in tags:
            # Erstelle eine Kopie des Quellobjekts
            coords = self.canvas.coords(item)
            image_name = None
            for tag in tags:
                if tag in self.images:
                    image_name = tag
                    break

            if image_name:
                new_item = self.canvas.create_image(
                    coords[0],
                    coords[1],
                    image=self.images[image_name],
                    tags=("draggable", image_name),
                )
                self.drag_data["item"] = new_item
                self.drag_data["is_copy"] = True
        elif "draggable" in tags:
            # Bewege existierendes Objekt
            self.drag_data["item"] = item
            self.drag_data["is_copy"] = False

        if self.drag_data["item"]:
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.canvas.tag_raise(self.drag_data["item"])

    def on_drag_motion(self, event):
        """Bewegt das Objekt während des Dragging"""
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag_release(self, event):
        """Beendet den Drag-Vorgang"""
        if self.drag_data["item"]:
            # Prüfe ob im mittleren Bereich (200-1200 x, 50-750 y)
            coords = self.canvas.coords(self.drag_data["item"])

            if coords and (200 <= coords[0] <= 1200 and 50 <= coords[1] <= 750):
                # Im gültigen Bereich
                if self.drag_data["is_copy"]:
                    self.dropped_items.append(self.drag_data["item"])
            else:
                # Außerhalb - lösche wenn es eine Kopie war
                if self.drag_data["is_copy"]:
                    self.canvas.delete(self.drag_data["item"])
                else:
                    # Wenn es ein bereits platziertes Item war, lösche es komplett
                    if self.drag_data["item"] in self.dropped_items:
                        self.dropped_items.remove(self.drag_data["item"])
                    self.canvas.delete(self.drag_data["item"])

        # Reset drag data
        self.drag_data = {"item": None, "x": 0, "y": 0, "is_copy": False}


def main():
    root = tk.Tk()
    app = GeldGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
