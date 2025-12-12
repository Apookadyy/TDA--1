✨ Productivity Suite - A python Project 

A desktop-based productivity application built using Python (Tkinter).
This all-in-one tool brings together essential daily utilities including:

🧮 Calculator

📝 Notes Manager

📁 File Organizer

⏱️ Countdown Timer & Stopwatch

The project is simple, colorful, beginner-friendly, and easy to run on any system with Python installed.

🚀 Features

1. Calculator

Supports standard arithmetic operations

Safe expression evaluation using Python ast

Real-time result display

Keyboard support (Enter = evaluate, Backspace = delete)


2. Notes Manager

Create, edit, save, and delete text notes

Notes saved automatically within a /notes folder

“Save As” option to export notes to any location

Clean two-panel layout (notes list + editor)


3. File Organizer

Automatically organizes files in a selected folder

Groups files by extension (e.g., .jpg_files, .pdf_files)

Log window showing all moved files

Useful for cleaning Downloads or Project folders


4. Timer Module

Contains two tools:

⏳ Countdown Timer

Set minutes & seconds

Start, Stop, Reset controls

Auto-alert when finished


⏱️ Stopwatch

Start/Stop/Reset

Precise real-time tracking

Clean digital display


📂 Project Structure

ProductivitySuite/
│── productivity_suite.py
│── notes/
│     └── (auto-generated .txt notes)
│── README.md

🛠️ Requirements

Python 3.8+

Tkinter (usually pre-installed with Python)

No additional external libraries required

▶️ How to Run the Application
Step 1: Clone the Repository
git clone https://github.com/your-username/ProductivitySuite.git
cd ProductivitySuite

Step 2: Run the App
python productivity_suite.py


The app will launch with a full GUI window.

📸 Screenshots

(Add your own images here when uploaded)

/screenshots
   calculator.png
   notes.png
   organizer.png
   timer.png

🧩 How It Works
Technologies Used:

Tkinter for GUI

AST module for secure calculator logic

OS + shutil for file operations

Time module for stopwatch/timer

Zipfile reserved for future enhancements

🌟 Future Enhancements

Potential upgrades:

Dark mode UI

Rich-text editor for notes

Drag-and-drop file organizer

Built-in reminder/alarms

Export notes as PDF

Add search function inside notes




