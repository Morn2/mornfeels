import os
from datetime import datetime
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from tkinter import Tk, filedialog
from charts import LineChartWidget
from utils import save_widget_as_image

import data
import charts

# Setze die Fenstergröße (Portrait)
Window.size = (360, 640)

DATA_CSV = data.DATA_CSV
SETTINGS_FILE = data.SETTINGS_FILE

# ---------------------- Popup Klassen ----------------------------

class ReminderPopup(Popup):
    """Popup zum manuellen Hinzufügen eines Mood-Eintrags."""
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.title = "Reminder"
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = False

        layout = FloatLayout()
        label = Label(text="How are you feeling?", pos_hint={'center_x': 0.5, 'top': 0.95}, size_hint=(None, None))
        layout.add_widget(label)
        self.mood_spinner = Spinner(
            text="Select Mood",
            values=["1", "2", "3", "4", "5", "6"],
            size_hint=(0.8, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 0.85}
        )
        layout.add_widget(self.mood_spinner)
        note_label = Label(text="Additional Note (optional)", pos_hint={'center_x': 0.5, 'top': 0.65}, size_hint=(None, None))
        layout.add_widget(note_label)
        self.note_input = TextInput(
            hint_text="Note", multiline=False, size_hint=(0.8, None),
            height=40, pos_hint={'center_x': 0.5, 'top': 0.55}
        )
        layout.add_widget(self.note_input)
        save_btn = Button(text="Save", size_hint=(0.3, None), height=40, pos_hint={'center_x': 0.3, 'top': 0.3})
        save_btn.bind(on_press=self.save_data)
        layout.add_widget(save_btn)
        cancel_btn = Button(text="Cancel", size_hint=(0.3, None), height=40, pos_hint={'center_x': 0.7, 'top': 0.3})
        cancel_btn.bind(on_press=self.dismiss)
        layout.add_widget(cancel_btn)
        self.content = layout

    def save_data(self, instance):
        mood = self.mood_spinner.text.strip()
        note = self.note_input.text.strip()
        if mood != "Select Mood":
            data.save_entry(self.file_path, mood, note)
        self.dismiss()

class SettingsPopup(Popup):
    """
    Popup für Einstellungen (Erinnerungszeiten).
    """
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.title = "Settings"
        self.size_hint = (0.9, 0.8)
        self.auto_dismiss = False

        layout = FloatLayout()
        reminder_label = Label(text="Reminder", size_hint=(None, None), size=(300, 40),
                               pos_hint={'center_x': 0.5, 'top': 0.95})
        layout.add_widget(reminder_label)
        values_label = Label(text="Values", size_hint=(None, None), size=(300, 40),
                             pos_hint={'center_x': 0.5, 'top': 0.55})
        layout.add_widget(values_label)
        self.time_input = TextInput(
            hint_text="HH:MM", multiline=False, size_hint=(0.5, None),
            height=40, pos_hint={'center_x': 0.5, 'top': 0.8}
        )
        layout.add_widget(self.time_input)
        add_btn = Button(text="Add Time", size_hint=(0.3, None), height=40,
                         pos_hint={'right': 0.48, 'top': 0.68})
        add_btn.bind(on_press=self.add_time)
        layout.add_widget(add_btn)
        delete_btn = Button(text="Delete Time", size_hint=(0.3, None), height=40,
                            pos_hint={'x': 0.52, 'top': 0.68})
        delete_btn.bind(on_press=self.delete_time)
        layout.add_widget(delete_btn)
        self.scroll_view = ScrollView(
            size_hint=(0.9, 0.35),
            pos_hint={'center_x': 0.5, 'top': 0.5},
            do_scroll_x=False,
            do_scroll_y=True
        )
        layout.add_widget(self.scroll_view)
        self.times_grid = GridLayout(cols=4, size_hint_y=None)
        self.times_grid.bind(minimum_height=self.times_grid.setter('height'))
        self.scroll_view.add_widget(self.times_grid)
        close_btn = Button(text="Close", size_hint=(0.2, None), height=40,
                           pos_hint={'center_x': 0.5, 'y': 0.05})
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)
        self.content = layout
        self.update_times_grid()

    def update_times_grid(self):
        self.times_grid.clear_widgets()
        for (hour, minute) in self.main_screen.reminder_times:
            time_str = f"{hour:02d}:{minute:02d}"
            label = Label(text=time_str, size_hint=(None, None))
            self.times_grid.add_widget(label)
        self.times_grid.height = self.times_grid.minimum_height

    def add_time(self, instance):
        time_str = self.time_input.text.strip()
        if time_str:
            try:
                hour, minute = time_str.split(":")
                hour = int(hour)
                minute = int(minute)
                if 0 <= hour < 24 and 0 <= minute < 60:
                    if (hour, minute) not in self.main_screen.reminder_times:
                        self.main_screen.reminder_times.append((hour, minute))
                        self.main_screen.reminder_times.sort()
                        data.save_settings(self.main_screen.reminder_times)
                        self.main_screen.schedule_daily_reminders()
                        self.update_times_grid()
            except ValueError:
                pass
        self.time_input.text = ""

    def delete_time(self, instance):
        time_str = self.time_input.text.strip()
        if time_str:
            try:
                hour, minute = time_str.split(":")
                hour = int(hour)
                minute = int(minute)
                if (hour, minute) in self.main_screen.reminder_times:
                    self.main_screen.reminder_times.remove((hour, minute))
                    data.save_settings(self.main_screen.reminder_times)
                    self.main_screen.schedule_daily_reminders()
                    self.update_times_grid()
            except ValueError:
                pass
        self.time_input.text = ""


class VisualizationResultsPopup(Popup):
    def __init__(self, filtered_data, **kwargs):
        super().__init__(**kwargs)
        self.title = "Visualization Results"
        self.size_hint = (0.95, 0.9)

        # Hauptlayout für den Inhalt
        main_layout = BoxLayout(orientation='vertical')

        # Das Diagramm-Widget (hier z.B. das Liniendiagramm)
        self.chart_widget = LineChartWidget(filtered_data)
        main_layout.add_widget(self.chart_widget)

        # Button-Layout am unteren Rand
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10, padding=10)

        pdf_btn = Button(text="Save to PDF")
        pdf_btn.bind(on_press=self.save_as_pdf)
        btn_layout.add_widget(pdf_btn)

        close_btn = Button(text="Close")
        close_btn.bind(on_press=self.dismiss)
        btn_layout.add_widget(close_btn)

        main_layout.add_widget(btn_layout)
        self.content = main_layout

    def save_as_pdf(self, instance):
        # Zunächst das Widget als Bild speichern
        import tempfile
        from tkinter import Tk, filedialog
        # Erstelle einen temporären Dateipfad
        temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        save_widget_as_image(self.chart_widget, temp_img)

        # Wähle über einen Dateidialog den Speicherort für das PDF
        root = Tk()
        root.withdraw()
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")])
        if save_path:
            # Verwende die vorhandene Funktion zum Erzeugen des PDFs
            # Hier wird nur ein Bild in das PDF eingefügt
            from charts import generate_pdf_from_images
            generate_pdf_from_images([temp_img], output_pdf=save_path)
        root.destroy()



class VisualizePopup(Popup):
    """
    Popup zur Auswahl des Datumsbereichs und der gewünschten Chart-Typen.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Visualize Mood"
        self.size_hint = (0.9, 0.8)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        date_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        all_dates = data.load_unique_dates_from_csv()
        self.start_spinner = Spinner(text="Start Date", values=all_dates, size_hint=(0.5, 1))
        self.end_spinner = Spinner(text="End Date", values=all_dates, size_hint=(0.5, 1))
        date_layout.add_widget(self.start_spinner)
        date_layout.add_widget(self.end_spinner)
        main_layout.add_widget(date_layout)

        grid = GridLayout(cols=2, size_hint=(1, 0.3), spacing=10)
        box1 = BoxLayout(orientation='horizontal', spacing=5)
        self.checkbox_line = CheckBox(size_hint=(None, None), size=(40, 40))
        box1.add_widget(self.checkbox_line)
        box1.add_widget(Label(text="Line Chart", halign="left"))
        grid.add_widget(box1)
        box2 = BoxLayout(orientation='horizontal', spacing=5)
        self.checkbox_daily_pie = CheckBox(size_hint=(None, None), size=(40, 40))
        box2.add_widget(self.checkbox_daily_pie)
        box2.add_widget(Label(text="Daily Pie Charts", halign="left"))
        grid.add_widget(box2)
        box3 = BoxLayout(orientation='horizontal', spacing=5)
        self.checkbox_bar = CheckBox(size_hint=(None, None), size=(40, 40))
        box3.add_widget(self.checkbox_bar)
        box3.add_widget(Label(text="Bar Chart", halign="left"))
        grid.add_widget(box3)
        box4 = BoxLayout(orientation='horizontal', spacing=5)
        self.checkbox_summary_pie = CheckBox(size_hint=(None, None), size=(40, 40))
        box4.add_widget(self.checkbox_summary_pie)
        box4.add_widget(Label(text="Summary Pie Chart", halign="left"))
        grid.add_widget(box4)
        main_layout.add_widget(grid)

        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        generate_btn = Button(text="Generate", size_hint=(0.5, 1))
        generate_btn.bind(on_press=self.on_generate)
        btn_layout.add_widget(generate_btn)
        close_btn = Button(text="Close", size_hint=(0.5, 1))
        close_btn.bind(on_press=self.dismiss)
        btn_layout.add_widget(close_btn)
        main_layout.add_widget(btn_layout)
        self.content = main_layout

    def on_generate(self, instance):
        start_date = self.start_spinner.text
        end_date = self.end_spinner.text
        if not start_date or not end_date or start_date == "Start Date" or end_date == "End Date":
            return
        filtered_data = data.filter_data_by_dates(start_date, end_date)
        image_paths = []
        if self.checkbox_line.active:
            results_popup = VisualizationResultsPopup(filtered_data)
            results_popup.open()
        if self.checkbox_daily_pie.active:
            image_paths.extend(charts.create_daily_pie_charts(filtered_data))
        if self.checkbox_bar.active:
            image_paths.append(charts.create_bar_chart(filtered_data))
        if self.checkbox_summary_pie.active:
            image_paths.append(charts.create_summary_pie_chart(filtered_data))
        if image_paths:
            results_popup = VisualizationResultsPopup(image_paths)
            results_popup.open()

class MainScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        data.init_csv(DATA_CSV)
        self.reminder_times = data.load_settings()
        add_entry_btn = Button(
            text="Add Entry Manually",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        add_entry_btn.bind(on_press=lambda x: ReminderPopup(DATA_CSV).open())
        self.add_widget(add_entry_btn)
        settings_btn = Button(
            text="Settings",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'center_x': 0.5, 'top': 0.75}
        )
        settings_btn.bind(on_press=lambda x: SettingsPopup(self).open())
        self.add_widget(settings_btn)
        visualize_btn = Button(
            text="Visualize Mood",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'center_x': 0.5, 'top': 0.6}
        )
        visualize_btn.bind(on_press=lambda x: VisualizePopup().open())
        self.add_widget(visualize_btn)

    def schedule_daily_reminders(self):
        print("Rescheduling daily reminders for:")
        for (hour, minute) in self.reminder_times:
            print(f"  - {hour:02d}:{minute:02d}")

class MornfeelsApp(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    MornfeelsApp().run()

