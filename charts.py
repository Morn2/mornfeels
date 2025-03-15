# charts.py
import os
from datetime import datetime, timedelta
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.label import Label
from kivy.graphics import PushMatrix, PopMatrix, Rotate

class RotatedLabel(Label):
    def __init__(self, angle=90, **kwargs):
        super(RotatedLabel, self).__init__(**kwargs)
        self.angle = angle
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=self.angle, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.bind(pos=self.update_origin, size=self.update_origin)

    def update_origin(self, *args):
        self.rot.origin = self.center

class LineChartWidget(BoxLayout):
    def __init__(self, filtered_data, start_date_str, end_date_str, **kwargs):
        """
        filtered_data: Liste von Zeilen, z.B. [["2025-01-01", "12:00:00", "4", "Note"], ...]
        start_date_str, end_date_str: Strings im Format "YYYY-MM-DD"
        """
        super(LineChartWidget, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10

        # --------------------------------------------------------
        # (1) Titel hinzufügen
        # --------------------------------------------------------
        title_label = Label(
            text="Daily Average Mood",  # Diagramm-Titel
            size_hint=(1, None),
            height=40,
            font_size="16sp",
            bold=True
        )
        self.add_widget(title_label)

        # --------------------------------------------------------
        # (2) Datenverarbeitung
        # --------------------------------------------------------
        # Konvertiere Start- und End-Daten in datetime-Objekte
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # day_values sammelt pro Tag alle Mood-Werte
        day_values = {}
        for row in filtered_data:
            date_str = row[0]  # z.B. "2025-01-01"
            try:
                d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                val = int(row[2])
            except ValueError:
                continue
            # Nur Werte im gewünschten Zeitraum berücksichtigen
            if start_date <= d_obj <= end_date:
                day_values.setdefault(d_obj, []).append(val)

        # Erstelle eine vollständige Liste aller Tage von start_date bis end_date
        all_dates = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)

        # Baue aus day_values die Liste "averages" (tagesweise Durchschnitt oder None)
        averages = []
        for d in all_dates:
            if d in day_values and len(day_values[d]) > 0:
                avg = sum(day_values[d]) / len(day_values[d])
            else:
                avg = None  # Keine Daten für diesen Tag
            averages.append(avg)

        # --------------------------------------------------------
        # (3) Graph-Objekt erstellen
        # --------------------------------------------------------
        self.graph = Graph(
            size_hint=(1, 0.8),
            xlabel='Date',
            ylabel='Average Mood',
            x_ticks_minor=0,
            x_ticks_major=1,
            y_ticks_major=1,
            y_grid_label=True,
            x_grid_label=True,
            padding=10,
            x_grid=True,
            y_grid=True,
            draw_border=True,
            background_color=[1, 1, 1, 1],  # Weiß
            border_color=[0, 0, 0, 1],      # Schwarz
            tick_color=[0, 0, 0, 1],        # Schwarze Achsen
        )

        # --------------------------------------------------------
        # (4) Achsenbereiche anpassen
        # --------------------------------------------------------
        valid_values = [v for v in averages if v is not None]
        if valid_values:
            self.graph.xmin = 0
            self.graph.xmax = len(averages) - 1
            y_min = min(valid_values) - 0.5
            y_max = max(valid_values) + 0.5
            self.graph.ymin = min(0, y_min)  # mindestens 0
            self.graph.ymax = max(6, y_max)  # mindestens 6
        else:
            self.graph.xmin, self.graph.xmax = 0, 0
            self.graph.ymin, self.graph.ymax = 0, 6

        # --------------------------------------------------------
        # (5) Liniendiagramm + Punkte einfügen
        # --------------------------------------------------------
        # Linie
        line_plot = MeshLinePlot(color=[0, 0, 1, 1])
        line_plot.line_width = 2
        line_plot.points = [
            (i, avg if avg is not None else 0)
            for i, avg in enumerate(averages)
        ]
        self.graph.add_plot(line_plot)

        # Punkte
        points_plot = MeshLinePlot(color=[0, 0, 1, 1])
        points_plot.mode = 'points'
        points_plot.point_size = 5
        points_plot.points = [
            (i, avg)
            for i, avg in enumerate(averages)
            if avg is not None
        ]
        self.graph.add_plot(points_plot)

        # Graph dem Layout hinzufügen
        self.add_widget(self.graph)

        # --------------------------------------------------------
        # (6) X-Labels unten (rotierte Beschriftung)
        # --------------------------------------------------------
        if all_dates:
            label_layout = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=60,
                spacing=5
            )
            num_dates = len(all_dates)
            # Beschrifte alle ca. 7 Tage, plus den ersten und letzten Tag
            n = max(1, num_dates // 7)
            for i, d_obj in enumerate(all_dates):
                if i == 0 or i == num_dates - 1 or i % n == 0:
                    date_str = d_obj.strftime("%b-%d")
                else:
                    date_str = ""
                lbl = RotatedLabel(
                    text=date_str,
                    size_hint=(None, 1),
                    width=40,
                    font_size='12sp'
                )
                label_layout.add_widget(lbl)
            self.add_widget(label_layout)

