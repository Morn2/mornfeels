import os
import csv
from datetime import datetime, timedelta

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

# Force a "phone-like" window size (portrait).
Window.size = (360, 640)

CSV_FILE = "mornfeels_data.csv"
SETTINGS_FILE = "settings.csv"

def init_csv(file_path):
    """Create the main CSV file (for mood entries) with headers if it does not exist."""
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Date', 'Time', 'Value', 'Note'])

def save_entry(file_path, mood, note):
    """Save a new entry in the main CSV file with the current date and time."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([date_str, time_str, mood, note])

def load_settings():
    """
    Load reminder times from SETTINGS_FILE (settings.csv).
    Each row is expected to have hour;minute.
    Returns a list of (hour, minute) tuples.
    """
    if not os.path.exists(SETTINGS_FILE):
        # Return a default set of times if no settings file exists
        return [(8, 0), (12, 0), (16, 0), (20, 0)]

    times = []
    with open(SETTINGS_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            if len(row) == 2:
                try:
                    hour = int(row[0])
                    minute = int(row[1])
                    if 0 <= hour < 24 and 0 <= minute < 60:
                        times.append((hour, minute))
                except ValueError:
                    pass
    # Sort times chronologically
    times.sort()
    return times

def save_settings(times):
    """
    Save the given list of (hour, minute) tuples to SETTINGS_FILE (settings.csv).
    """
    with open(SETTINGS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for (hour, minute) in times:
            writer.writerow([hour, minute])

class ReminderPopup(Popup):
    """Popup for adding a new entry with a predefined mood (1..6) and an optional note."""
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.title = "Reminder"
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = False

        layout = FloatLayout()

        label = Label(
            text="How are you feeling?",
            pos_hint={'center_x': 0.5, 'top': 0.95},
            size_hint=(None, None)
        )
        layout.add_widget(label)

        # Spinner (drop-down) for mood values 1..6
        self.mood_spinner = Spinner(
            text="Select Mood",
            values=["1", "2", "3", "4", "5", "6"],
            size_hint=(0.8, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 0.85}
        )
        layout.add_widget(self.mood_spinner)

        note_label = Label(
            text="Additional Note (optional)",
            pos_hint={'center_x': 0.5, 'top': 0.65},
            size_hint=(None, None)
        )
        layout.add_widget(note_label)

        self.note_input = TextInput(
            hint_text="Note",
            multiline=False,
            size_hint=(0.8, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 0.55}
        )
        layout.add_widget(self.note_input)

        save_btn = Button(
            text="Save",
            size_hint=(0.3, None),
            height=40,
            pos_hint={'center_x': 0.3, 'top': 0.3}
        )
        save_btn.bind(on_press=self.save_data)
        layout.add_widget(save_btn)

        cancel_btn = Button(
            text="Cancel",
            size_hint=(0.3, None),
            height=40,
            pos_hint={'center_x': 0.7, 'top': 0.3}
        )
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
    A "floating" settings window with two labeled boxes:
    - "Reminder" (top box): a text field to add/delete times in HH:MM format,
      plus "Add Time" and "Delete Time" buttons below it.
    - "Values" (bottom box): a scrollable grid that lists all times in 4 columns.
    """
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.title = ""  # We'll handle labels ourselves
        self.size_hint = (0.9, 0.8)  # Slightly smaller than full screen to appear "floating"
        self.auto_dismiss = False

        layout = FloatLayout()

        # Top box label: "Reminder"
        reminder_label = Label(
            text="Reminder",
            size_hint=(None, None),
            size=(300, 40),
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        layout.add_widget(reminder_label)

        # Bottom box label: "Values"
        values_label = Label(
            text="Values",
            size_hint=(None, None),
            size=(300, 40),
            pos_hint={'center_x': 0.5, 'top': 0.55}
        )
        layout.add_widget(values_label)

        # Text field for entering times (HH:MM)
        self.time_input = TextInput(
            hint_text="HH:MM",
            multiline=False,
            size_hint=(0.5, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 0.8}
        )
        layout.add_widget(self.time_input)

        # "Add Time" button below the input
        add_btn = Button(
            text="Add Time",
            size_hint=(0.3, None),
            height=40,
            pos_hint={'right': 0.48, 'top': 0.68}
        )
        add_btn.bind(on_press=self.add_time)
        layout.add_widget(add_btn)

        # "Delete Time" button next to "Add Time"
        delete_btn = Button(
            text="Delete Time",
            size_hint=(0.3, None),
            height=40,
            pos_hint={'x': 0.52, 'top': 0.68}
        )
        delete_btn.bind(on_press=self.delete_time)
        layout.add_widget(delete_btn)

        # Scrollable area for the times
        self.scroll_view = ScrollView(
            size_hint=(0.9, 0.35),
            pos_hint={'center_x': 0.5, 'top': 0.5},
            do_scroll_x=False,  # Only vertical scrolling
            do_scroll_y=True
        )
        layout.add_widget(self.scroll_view)

        # Grid to display the times (4 columns)
        self.times_grid = GridLayout(
            cols=4,
            size_hint_y=None
        )
        # Bind the grid's height to its minimum_height so it expands with more items
        self.times_grid.bind(minimum_height=self.times_grid.setter('height'))

        self.scroll_view.add_widget(self.times_grid)

        # "Close" button at the bottom
        close_btn = Button(
            text="Close",
            size_hint=(0.2, None),
            height=40,
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)

        self.content = layout

        # Populate the grid with existing times
        self.update_times_grid()

    def update_times_grid(self):
        """Rebuild the 4-column grid based on the times in main_screen."""
        self.times_grid.clear_widgets()
        for (hour, minute) in self.main_screen.reminder_times:
            time_str = f"{hour:02d}:{minute:02d}"
            label = Label(text=time_str, size_hint=(None, None))
            self.times_grid.add_widget(label)

        # Force the layout to recalculate so scrolling works correctly
        self.times_grid.height = self.times_grid.minimum_height

    def add_time(self, instance):
        """Add a new time (if valid and not already in the list)."""
        time_str = self.time_input.text.strip()
        if time_str:
            try:
                hour, minute = time_str.split(":")
                hour = int(hour)
                minute = int(minute)
                if 0 <= hour < 24 and 0 <= minute < 60:
                    # Only add if not already in the list
                    if (hour, minute) not in self.main_screen.reminder_times:
                        self.main_screen.reminder_times.append((hour, minute))
                        # Sort times so they're in chronological order
                        self.main_screen.reminder_times.sort()
                        # Save and reschedule
                        save_settings(self.main_screen.reminder_times)
                        self.main_screen.schedule_daily_reminders()
                        self.update_times_grid()
            except ValueError:
                pass
        self.time_input.text = ""

    def delete_time(self, instance):
        """Delete a time if it exists in the list."""
        time_str = self.time_input.text.strip()
        if time_str:
            try:
                hour, minute = time_str.split(":")
                hour = int(hour)
                minute = int(minute)
                if (hour, minute) in self.main_screen.reminder_times:
                    self.main_screen.reminder_times.remove((hour, minute))
                    # Save and reschedule
                    save_settings(self.main_screen.reminder_times)
                    self.main_screen.schedule_daily_reminders()
                    self.update_times_grid()
            except ValueError:
                pass
        self.time_input.text = ""

class MainScreen(FloatLayout):
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path

        # Load times from settings
        self.reminder_times = load_settings()

        # Button 1: "Add Entry Manually"
        manual_btn = Button(
            text="Add Entry Manually",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        manual_btn.bind(on_press=self.show_reminder)
        self.add_widget(manual_btn)

        # Button 2: "Settings"
        settings_btn = Button(
            text="Settings",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'center_x': 0.5, 'top': 0.75}
        )
        settings_btn.bind(on_press=self.show_settings)
        self.add_widget(settings_btn)

    def show_reminder(self, instance=None):
        """Open the ReminderPopup to add a new mood entry."""
        popup = ReminderPopup(self.file_path)
        popup.open()

    def show_settings(self, instance=None):
        """Open the new SettingsPopup."""
        popup = SettingsPopup(self)
        popup.open()

    def schedule_daily_reminders(self):
        """
        Stub function for demonstration:
        Here you could implement your daily scheduling logic
        (e.g., using Clock.schedule_once for each time).
        We'll just print them for now.
        """
        print("Rescheduling daily reminders for:")
        for (hour, minute) in self.reminder_times:
            print(f"  - {hour:02d}:{minute:02d}")

class MornfeelsApp(App):
    def build(self):
        init_csv(CSV_FILE)
        return MainScreen(CSV_FILE)

    def on_start(self):
        """
        Optionally schedule the initial daily reminders here
        using the times in MainScreen.
        """
        self.root.schedule_daily_reminders()

if __name__ == '__main__':
    MornfeelsApp().run()

