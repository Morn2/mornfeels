import os
import csv
from datetime import datetime

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.spinner import Spinner  # for the drop-down in the ReminderPopup

# Force a "phone-like" window size (portrait).
Window.size = (360, 640)

CSV_FILE = "mornfeels_data.csv"

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

class ReminderPopup(Popup):
    """Popup for adding a new entry with a predefined mood (1..6) and an optional note."""
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.title = "Reminder"
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = False

        layout = FloatLayout()

        # Label at the top (centered horizontally).
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

        # Label for optional note
        note_label = Label(
            text="Additional Note (optional)",
            pos_hint={'center_x': 0.5, 'top': 0.65},
            size_hint=(None, None)
        )
        layout.add_widget(note_label)

        # TextInput for note
        self.note_input = TextInput(
            hint_text="Note",
            multiline=False,
            size_hint=(0.8, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 0.55}
        )
        layout.add_widget(self.note_input)

        # "Save" button
        save_btn = Button(
            text="Save",
            size_hint=(0.3, None),
            height=40,
            pos_hint={'center_x': 0.3, 'top': 0.3}
        )
        save_btn.bind(on_press=self.save_data)
        layout.add_widget(save_btn)

        # "Cancel" button
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
        """Save the selected mood and optional note to the CSV file."""
        mood = self.mood_spinner.text.strip()
        note = self.note_input.text.strip()

        # Only save if a valid mood has been selected (i.e., not the default text)
        if mood != "Select Mood":
            save_entry(self.file_path, mood, note)
        self.dismiss()

class SettingsPopup(Popup):
    """Popup for changing the reminder interval (in seconds)."""
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.title = "Settings"
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = False

        layout = FloatLayout()

        # Label for the interval setting
        interval_label = Label(
            text="Set reminder interval (seconds):",
            pos_hint={'center_x': 0.5, 'top': 0.9},
            size_hint=(None, None)
        )
        layout.add_widget(interval_label)

        # TextInput showing the current interval
        self.interval_input = TextInput(
            text=str(self.main_screen.reminder_interval),
            multiline=False,
            size_hint=(0.8, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 0.75}
        )
        layout.add_widget(self.interval_input)

        # "Save Interval" button
        save_btn = Button(
            text="Save Interval",
            size_hint=(0.3, None),
            height=40,
            pos_hint={'center_x': 0.3, 'top': 0.4}
        )
        save_btn.bind(on_press=self.save_interval)
        layout.add_widget(save_btn)

        # "Close" button
        close_btn = Button(
            text="Close",
            size_hint=(0.3, None),
            height=40,
            pos_hint={'center_x': 0.7, 'top': 0.4}
        )
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)

        self.content = layout

    def save_interval(self, instance):
        """Update the main screen's reminder interval and reschedule the reminder."""
        new_interval_str = self.interval_input.text.strip()
        try:
            new_interval = float(new_interval_str)

            # Unschedule the old reminder
            Clock.unschedule(self.main_screen.show_reminder)

            # Update the interval in MainScreen
            self.main_screen.reminder_interval = new_interval

            # Reschedule the reminder with the new interval
            Clock.schedule_interval(self.main_screen.show_reminder, new_interval)
        except ValueError:
            # If the user enters something invalid, just ignore or handle as needed
            pass

        self.dismiss()

class MainScreen(FloatLayout):
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path

        # Default reminder interval (in seconds)
        self.reminder_interval = 60.0

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
            pos_hint={'center_x': 0.5, 'top': 0.7}
        )
        settings_btn.bind(on_press=self.show_settings)
        self.add_widget(settings_btn)

    def show_reminder(self, instance=None):
        """Open the ReminderPopup to add a new mood entry."""
        popup = ReminderPopup(self.file_path)
        popup.open()

    def show_settings(self, instance=None):
        """Open the SettingsPopup to configure the reminder interval."""
        popup = SettingsPopup(self)
        popup.open()

class MornfeelsApp(App):
    def build(self):
        init_csv(CSV_FILE)
        return MainScreen(CSV_FILE)

    def on_start(self):
        """Schedule the first reminder using the default (or last set) interval."""
        Clock.schedule_interval(self.root.show_reminder, self.root.reminder_interval)

if __name__ == '__main__':
    MornfeelsApp().run()

