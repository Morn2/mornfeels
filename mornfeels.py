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
from kivy.uix.spinner import Spinner  # <-- Import Spinner for the dropdown

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
        # Retrieve the selected mood value from the spinner
        mood = self.mood_spinner.text.strip()
        note = self.note_input.text.strip()

        # Only save if a valid mood has been selected (i.e., not the default text)
        if mood != "Select Mood":
            save_entry(self.file_path, mood, note)
        self.dismiss()

class MainScreen(FloatLayout):
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path

        # Button in the top area
        manual_btn = Button(
            text="Add Entry Manually",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        manual_btn.bind(on_press=self.show_reminder)
        self.add_widget(manual_btn)

    def show_reminder(self, instance=None):
        popup = ReminderPopup(self.file_path)
        popup.open()

class MornfeelsApp(App):
    def build(self):
        init_csv(CSV_FILE)
        return MainScreen(CSV_FILE)

    def on_start(self):
        # Schedule the reminder popup to display every 60 seconds (adjustable interval)
        Clock.schedule_interval(self.root.show_reminder, 60)

if __name__ == '__main__':
    MornfeelsApp().run()

