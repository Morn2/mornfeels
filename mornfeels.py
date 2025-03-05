import os
import csv
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

CSV_FILE = "mornfeels_data.csv"

def init_csv(file_path):
    """Create the CSV file with headers if it does not exist."""
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Mood', 'Note'])

def save_entry(file_path, mood, note):
    """Save a new entry in the CSV file with the current timestamp."""
    timestamp = datetime.now().isoformat()
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, mood, note])

class ReminderPopup(Popup):
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.title = "Reminder"
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(Label(text="How are you feeling?"))

        # TextInput for mood
        self.mood_input = TextInput(hint_text="Mood", multiline=False)
        layout.add_widget(self.mood_input)

        layout.add_widget(Label(text="Additional Note (optional)"))
        self.note_input = TextInput(hint_text="Note", multiline=False)
        layout.add_widget(self.note_input)

        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        save_btn = Button(text="Save")
        save_btn.bind(on_press=self.save_data)
        btn_layout.add_widget(save_btn)

        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_press=self.dismiss)
        btn_layout.add_widget(cancel_btn)

        layout.add_widget(btn_layout)
        self.content = layout

    def save_data(self, instance):
        mood = self.mood_input.text.strip()
        note = self.note_input.text.strip()
        if mood:
            save_entry(self.file_path, mood, note)
        self.dismiss()

class MainScreen(BoxLayout):
    def __init__(self, file_path, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)
        self.file_path = file_path

        self.add_widget(Label(text="Welcome to Mornfeels MVP"))

        manual_btn = Button(text="Add Entry Manually", size_hint=(1, 0.2))
        manual_btn.bind(on_press=self.show_reminder)
        self.add_widget(manual_btn)

    def show_reminder(self, instance=None):
        popup = ReminderPopup(self.file_path)
        popup.open()

class MornfeelsApp(App):
    def build(self):
        init_csv(CSV_FILE)
        self.main_screen = MainScreen(CSV_FILE)
        return self.main_screen

    def on_start(self):
        # Schedule the reminder popup to display every 60 seconds (adjustable interval)
        Clock.schedule_interval(self.main_screen.show_reminder, 60)

if __name__ == '__main__':
    MornfeelsApp().run()

