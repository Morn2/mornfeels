import os
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

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
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from fpdf import FPDF  # pip install fpdf
from kivy.uix.scatter import Scatter

# Import Tkinter for file dialog (works if Tkinter is installed)
from tkinter import Tk, filedialog

# Set a "phone-like" window size (portrait)
Window.size = (360, 640)

DATA_CSV = "mornfeels_data.csv"
SETTINGS_FILE = "settings.csv"
CHART_OUTPUT_DIR = "generated_charts"

# ---------------------- CSV and Settings Functions ----------------------------

def init_csv(file_path):
    """Create the CSV file with headers if it does not exist."""
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Date', 'Time', 'Value', 'Note'])


def save_entry(file_path, mood, note):
    """Save a new entry in the CSV file with the current date and time."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([date_str, time_str, mood, note])


def load_unique_dates_from_csv():
    """
    Read DATA_CSV and return a sorted list of unique dates (YYYY-MM-DD).
    """
    if not os.path.exists(DATA_CSV):
        print("DEBUG: DATA_CSV not found.")
        return []
    dates = set()
    with open(DATA_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader, None)
        for row in reader:
            if len(row) >= 3:
                dates.add(row[0])
    unique_dates = sorted(dates)
    print("DEBUG: Unique dates loaded:", unique_dates)
    return unique_dates


def filter_data_by_dates(start_date, end_date):
    """
    Filter data from DATA_CSV between start_date and end_date (inclusive).
    Assumes dates are in the format YYYY-MM-DD.
    Returns a list of rows.
    """
    data = []
    with open(DATA_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader, None)
        for row in reader:
            if len(row) >= 3:
                d = row[0]
                if start_date <= d <= end_date:
                    data.append(row)
    print(f"DEBUG: Filtered data count between {start_date} and {end_date}: {len(data)}")
    return data



def load_settings():
    """Load reminder times from SETTINGS_FILE as a list of (hour, minute) tuples."""
    if not os.path.exists(SETTINGS_FILE):
        return [(8, 0), (12, 0), (16, 0), (20, 0)]
    times = []
    with open(SETTINGS_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            if len(row) == 2:
                try:
                    hour = int(row[0])
                    minute = int(row[1])
                    times.append((hour, minute))
                except ValueError:
                    pass
    return sorted(times)


def save_settings(times):
    """Save the list of (hour, minute) tuples to SETTINGS_FILE."""
    with open(SETTINGS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for (hour, minute) in times:
            writer.writerow([hour, minute])


# ---------------------- Chart Generation  ----------------------------


def create_line_chart(filtered_data):
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)
    # Group data by date and calculate the average value
    day_values = {}
    for row in filtered_data:
        d = row[0]
        try:
            val = int(row[2])
        except ValueError:
            continue
        day_values.setdefault(d, []).append(val)
    dates = sorted(day_values.keys())
    averages = [sum(day_values[d]) / len(day_values[d]) for d in dates]
    plt.figure(figsize=(5, 3))
    plt.plot(dates, averages, marker='o', color="blue")
    plt.title("Daily Average Mood")
    plt.xlabel("Date")
    plt.ylabel("Average Mood")
    plt.xticks(rotation=45)
    out_path = os.path.join(CHART_OUTPUT_DIR, "line_chart.png")
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    return out_path


def create_daily_pie_charts(filtered_data):
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)

    color_mapping = {
        6: "lightgreen", 5: "darkgreen",
        4: "lightsalmon", 3: "darkred",
        2: "lightgrey",   1: "darkgrey",
        0: "black"
    }

    unique_dates = sorted(set(row[0] for row in filtered_data))
    paths = []
    for d in unique_dates:
        day_data = [row for row in filtered_data if row[0] == d]
        frequency = {}
        for row in day_data:
            try:
                val = int(row[2])
            except ValueError:
                continue
            frequency[val] = frequency.get(val, 0) + 1

        # Prepare data for pie
        labels, sizes, colors = [], [], []
        for val in sorted(frequency.keys(), reverse=True):
            labels.append(str(val))
            sizes.append(frequency[val])
            colors.append(color_mapping.get(val, "grey"))
        if not sizes:
            continue

        date_tag = d.replace("-", "")
        out_path = os.path.join(CHART_OUTPUT_DIR, f"pie_{date_tag}.png")

        # Ensure a white background
        plt.figure(figsize=(5, 3), facecolor="white")
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title(f"Pie Chart for {d}")
        plt.savefig(out_path, bbox_inches='tight', facecolor="white")
        plt.close()
        paths.append(out_path)
    return paths


def create_bar_chart(filtered_data):
    """Create a bar chart and return the PNG path."""
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)
    # Count frequencies overall
    frequency = {}
    for row in filtered_data:
        try:
            val = int(row[2])
        except ValueError:
            continue
        frequency[val] = frequency.get(val, 0) + 1
    # Sort keys (for example, in descending order)
    keys = sorted(frequency.keys(), reverse=True)
    values = [frequency[k] for k in keys]
    color_mapping = {
        6: "lightgreen",
        5: "darkgreen",
        4: "lightsalmon",
        3: "darkred",
        2: "lightgrey",
        1: "darkgrey",
        0: "black"
    }
    colors = [color_mapping.get(k, "grey") for k in keys]
    plt.figure(figsize=(5, 3))
    plt.bar([str(k) for k in keys], values, color=colors)
    plt.title("Bar Chart Example")
    out_path = os.path.join(CHART_OUTPUT_DIR, "bar_chart.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    return out_path


def create_summary_pie_chart(filtered_data):
    """Create a summary pie chart and return the PNG path."""
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)
    frequency = {}
    for row in filtered_data:
        try:
            val = int(row[2])
        except ValueError:
            continue
        frequency[val] = frequency.get(val, 0) + 1
    keys = sorted(frequency.keys(), reverse=True)
    sizes = [frequency[k] for k in keys]
    color_mapping = {
        6: "lightgreen",
        5: "darkgreen",
        4: "lightsalmon",
        3: "darkred",
        2: "lightgrey",
        1: "darkgrey",
        0: "black"
    }
    colors = [color_mapping.get(k, "grey") for k in keys]
    plt.figure(figsize=(5, 3))
    plt.pie(sizes, labels=[str(k) for k in keys], colors=colors, autopct='%1.1f%%')
    plt.title("Summary Pie Chart")
    out_path = os.path.join(CHART_OUTPUT_DIR, "summary_pie.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    return out_path


def generate_pdf_from_images(image_paths, output_pdf):
    """Combine the given PNG images into a PDF using FPDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    for img_path in image_paths:
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=180)
    pdf.output(output_pdf, "F")


# ---------------------- Popup Classes ----------------------------


class ReminderPopup(Popup):
    """Popup to add a new mood entry."""
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
            save_entry(self.file_path, mood, note)
        self.dismiss()


class SettingsPopup(Popup):
    """
    Popup for settings (reminder times).
    Top: "Reminder" label, below a text field for HH:MM with "Add Time" and "Delete Time" buttons.
    Bottom: ScrollView with a GridLayout (4 columns) displaying the times.
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
                        save_settings(self.main_screen.reminder_times)
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
                    save_settings(self.main_screen.reminder_times)
                    self.main_screen.schedule_daily_reminders()
                    self.update_times_grid()
            except ValueError:
                pass
        self.time_input.text = ""


class VisualizationResultsPopup(Popup):
    """
    Displays the generated charts in a scrollable, zoomable layout.
    Contains a "Save to PDF" button.
    """
    def __init__(self, image_paths, **kwargs):
        super().__init__(**kwargs)
        self.title = "Visualization Results"
        self.size_hint = (0.95, 0.9)

        # Main vertical layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Scrollable area for the images
        scroll_view = ScrollView(size_hint=(1, 0.85), do_scroll_x=False)
        # Use a vertical BoxLayout inside the ScrollView
        images_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        images_layout.bind(minimum_height=images_layout.setter('height'))

        for img_path in image_paths:
            # Wrap each image in a Scatter for zoom/drag functionality
            scatter = Scatter(size_hint=(1, None), height=300)
            # Use absolute path for the image
            image = Image(source=os.path.abspath(img_path),
                          size_hint=(None, None), size=(300, 300))
            scatter.add_widget(image)
            images_layout.add_widget(scatter)

        scroll_view.add_widget(images_layout)
        main_layout.add_widget(scroll_view)

        # Bottom buttons: "Save to PDF" and "Close"
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        pdf_btn = Button(text="Save to PDF")
        pdf_btn.bind(on_press=lambda x: self.on_save_pdf(image_paths))
        close_btn = Button(text="Close")
        close_btn.bind(on_press=self.dismiss)
        btn_layout.add_widget(pdf_btn)
        btn_layout.add_widget(close_btn)
        main_layout.add_widget(btn_layout)

        self.content = main_layout

    def on_save_pdf(self, image_paths):
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")])
        if save_path:
            generate_pdf_from_images(image_paths, output_pdf=save_path)
        root.destroy()


class VisualizePopup(Popup):
    """
    Popup to select the date range and desired chart types.
    The top row has the Start and End Date spinners,
    followed by a 2x2 grid with checkboxes (each next to its label),
    and at the bottom, the "Generate" and "Close" buttons side by side.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Visualize Mood"
        self.size_hint = (0.9, 0.8)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # Row 1: Date selection
        date_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        all_dates = load_unique_dates_from_csv()
        self.start_spinner = Spinner(text="Start Date", values=all_dates, size_hint=(0.5, 1))
        self.end_spinner = Spinner(text="End Date", values=all_dates, size_hint=(0.5, 1))
        date_layout.add_widget(self.start_spinner)
        date_layout.add_widget(self.end_spinner)
        main_layout.add_widget(date_layout)
        # Row 2: 2x2 grid for chart options
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
        # Row 3: Buttons "Generate" and "Close"
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
        filtered_data = filter_data_by_dates(start_date, end_date)
        image_paths = []
        if self.checkbox_line.active:
            image_paths.append(create_line_chart(filtered_data))
        if self.checkbox_daily_pie.active:
            image_paths.extend(create_daily_pie_charts(filtered_data))
        if self.checkbox_bar.active:
            image_paths.append(create_bar_chart(filtered_data))
        if self.checkbox_summary_pie.active:
            image_paths.append(create_summary_pie_chart(filtered_data))
        if image_paths:
            results_popup = VisualizationResultsPopup(image_paths)
            results_popup.open()


class MainScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_csv(DATA_CSV)
        self.reminder_times = load_settings()
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
        """Placeholder function for daily reminder scheduling."""
        print("Rescheduling daily reminders for:")
        for (hour, minute) in self.reminder_times:
            print(f"  - {hour:02d}:{minute:02d}")


class MornfeelsApp(App):
    def build(self):
        return MainScreen()


if __name__ == "__main__":
    MornfeelsApp().run()

