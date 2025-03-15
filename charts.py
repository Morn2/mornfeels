import os
from datetime import datetime
from fpdf import FPDF


# charts.py (Ergänzung oder in einer neuen Datei chart_widgets.py)

from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import Graph, MeshLinePlot
from datetime import datetime

class LineChartWidget(BoxLayout):
    def __init__(self, filtered_data, **kwargs):
        """
        filtered_data: Liste von Zeilen, z. B. [["2025-01-01", "12:00:00", "4", "Note"], ...]
                      Diese Daten sollen hier in ein Liniendiagramm umgewandelt werden.
        """
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # 1) Tagesdurchschnitt berechnen
        day_values = {}
        for row in filtered_data:
            date_str = row[0]  # z.B. "2025-01-01"
            try:
                d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                val = int(row[2])
            except ValueError:
                continue
            day_values.setdefault(d_obj, []).append(val)

        # 2) Sortieren und Durchschnitts-Liste anlegen
        sorted_dates = sorted(day_values.keys())
        averages = [sum(day_values[d]) / len(day_values[d]) for d in sorted_dates]

        # Für das Plotten mit Kivy Garden Graph:
        #    x-Achse = Indizes (0, 1, 2, ...)
        #    y-Achse = Durchschnittswerte
        # Später können wir manuell Labels anlegen.

        # 3) Graph-Objekt erstellen
        self.graph = Graph(
            xlabel='Date',
            ylabel='Average Mood',
            x_ticks_minor=0,
            x_ticks_major=1,
            y_ticks_major=1,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            draw_border=True,
            background_color=[1, 1, 1, 1],  # Weißer Hintergrund
            border_color=[0, 0, 0, 1],      # Schwarzer Rand
            tick_color=[0, 0, 0, 1]         # Schwarze Achsen-Beschriftungen
        )

        # 4) Achsen-Bereiche dynamisch anpassen
        if averages:
            # x von 0 bis len(averages)-1
            self.graph.xmin = 0
            self.graph.xmax = len(averages) - 1
            # y z. B. von min(averages) - 0.5 bis max(averages) + 0.5
            y_min = min(averages) - 0.5
            y_max = max(averages) + 0.5
            # oder fest: self.graph.ymin, self.graph.ymax = 0, 6
            self.graph.ymin = min(0, y_min)
            self.graph.ymax = max(6, y_max)
        else:
            # Fallback, falls keine Daten
            self.graph.xmin, self.graph.xmax = 0, 0
            self.graph.ymin, self.graph.ymax = 0, 6

        # 5) Plot (Linie mit Punkten)
        plot = MeshLinePlot(color=[0, 0, 1, 1])  # Blau
        plot.points = [(i, avg) for i, avg in enumerate(averages)]
        self.graph.add_plot(plot)

        # 6) Graph dem Layout hinzufügen
        self.add_widget(self.graph)

        # Optional: Manuelle Labels für das X-Achsen-Raster
        #           Da Graph() standardmäßig nur Zahlen anzeigt,
        #           könntest du z. B. unten eigene Label-Widgets hinzufügen.
        #           (siehe "Optionale X-Labels" unten)

#----------------------------------------------------------------------------------------
def generate_pdf_from_images(image_paths, output_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    for img_path in image_paths:
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=180)
    pdf.output(output_pdf, "F")

