# Functional Specification (Draft)

**Note:** This document is a working draft and will be continuously updated as the project evolves.

## 1. Introduction

### 1.1 Purpose
Mornfeels is an MVP project designed to help users log and analyze their moods. The primary objective is to provide a simple, intuitive app that allows users to record their mood entries regularly and review their mood history through visualizations and statistics.

### 1.2 Scope
The initial version focuses on:
- Mood logging via a simple interface.
- Data storage using a CSV file for quick analysis.
- A reminder system to prompt mood entries.
- Basic mood analysis and visualization using a Python script.

Future versions may expand to include:
- Enhanced UI with additional customization options.
- Data export in various formats.
- Transition to a full Android application using Kivy.
- Advanced privacy and security features.

### 1.3 Definitions and Abbreviations
- **MVP:** Minimum Viable Product.
- **CSV:** Comma-Separated Values, a simple file format for data storage.
- **UI:** User Interface.
- **Kivy:** A Python framework for developing cross-platform applications.
- **SQLite:** A lightweight, file-based database system (considered for future versions).

## 2. System Overview

Mornfeels is structured around three main components:
- **Mood Logging:** Allows users to record their mood entries.
- **Mood Analysis:** Processes the logged data and provides visual feedback (statistics and graphs).
- **Reminder Functionality:** Notifies users at set intervals to log their mood.

## 3. Functional Requirements

### 3.1 Mood Logging
- **Input:** Users can enter their current mood using predefined options or a numerical scale.
- **Data Storage:** Entries are saved in a CSV file (initial implementation) with fields such as timestamp and mood value.
- **User Feedback:** A confirmation message is shown upon successful logging.

### 3.2 Mood Analysis
- **Data Processing:** A Python script reads the CSV file, analyzes mood trends over time, and generates visualizations.
- **Visualization:** Display statistics and graphs showing mood trends for selected time periods.

### 3.3 Reminder Functionality
- **Notifications:** The app sends reminders at user-defined intervals to prompt mood logging.
- **Customization:** Users can adjust reminder times and intervals.

### 3.4 Settings and Configuration
- **User Setup:** Users can set a username and optionally configure a password for app access.
- **Appearance Settings:** Options for themes, font sizes, and other visual aspects may be included in future updates.
- **Export Options:** Future enhancements might include data export features (e.g., exporting CSV data to other formats).

## 4. Non-Functional Requirements

- **Usability:** The app should be simple to use, with an intuitive interface.
- **Performance:** Quick response times for logging and analyzing mood entries.
- **Scalability:** While the initial CSV-based approach is sufficient for an MVP, future iterations may require a more robust database solution.
- **Maintainability:** The codebase should follow best practices, including clear documentation, modular design, and version control (GitHub).

## 5. Technology Stack

- **Initial Implementation:** Python with CSV file handling.
- **Data Analysis:** Python libraries (e.g., pandas, matplotlib).
- **Future Development:** Android app development using Kivy (or potentially Kotlin) with possible integration of SQLite for data storage.

## 6. Use Cases

### 6.1 Log Mood Entry
- **Actor:** User
- **Preconditions:** The app is installed and opened.
- **Flow:**
  1. The user receives a reminder to log their mood.
  2. The user selects a mood value and confirms the entry.
  3. The entry is saved with a timestamp.
- **Postconditions:** The mood entry is stored and available for analysis.

### 6.2 Analyze Mood Data
- **Actor:** User
- **Preconditions:** At least one mood entry exists.
- **Flow:**
  1. The user selects a time period for analysis.
  2. The system processes the CSV data.
  3. Visualizations (graphs/statistics) are displayed.
- **Postconditions:** The user gains insight into mood trends.

### 6.3 Configure Reminders
- **Actor:** User
- **Preconditions:** The app is installed.
- **Flow:**
  1. The user sets or adjusts reminder intervals.
  2. The system schedules notifications accordingly.
- **Postconditions:** Reminders are updated based on user settings.

## 7. Future Enhancements

- Transition to a full Android app with a dedicated UI.
- Integration with a robust database system (e.g., SQLite).
- Additional data export and import functionalities.
- Enhanced security features (e.g., data encryption, password protection).

## 8. Revision History

- **Draft Version:** This document is a draft and will be updated regularly as new requirements emerge and features are refined.

