import sys

import json
import struct
import sys

# from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QTextEdit,
    QDesktopWidget,
)
from PyQt5.QtCore import QTimer
from gmail_client import get_gmail_service, get_sent_emails


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.displayed_subjects = []
        self.initUI()

    def center(self):
        # Get the geometry of the main window
        qr = self.frameGeometry()

        # Get the screen's center point
        cp = QDesktopWidget().availableGeometry().center()

        # Move the rectangle's center point to the screen's center point
        qr.moveCenter(cp)

        # Top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def check_new_sent_messages(self):

        service = get_gmail_service()
        subjects = get_sent_emails(service)
        new_subjects = [s for s in subjects if s not in self.displayed_subjects]
        if new_subjects:
            self.display_subjects(new_subjects)
            self.displayed_subjects.extend(new_subjects)

    def initUI(self):
        layout = QVBoxLayout()

        self.text_box = QTextEdit(self)
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        btn_login = QPushButton("Login and Fetch Data", self)
        btn_login.clicked.connect(self.login_and_fetch_data)
        layout.addWidget(btn_login)

        self.setLayout(layout)
        self.setWindowTitle("Panza Email")

        # Set the window size
        self.setGeometry(100, 100, 600, 200)  # (x, y, width, height)
        # Center the window on the screen
        self.center()

        self.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_new_sent_messages)
        # self.timer.start(2000)  # Check every 2 seconds (2000 milliseconds)

    def login_and_fetch_data(self):
        service = get_gmail_service()
        subjects = get_sent_emails(service, num_emails=200)
        self.display_subjects(subjects)

    def display_subjects(self, subjects):
        # self.text_box.clear()
        for subject in subjects:
            self.text_box.append(subject)
        self.text_box.append(f"\nSuccessfully downloaded {len(subjects)} sent emails.")


def handle_message(message):
    print(f"Received message from extension: {message}")
    if message is not None:
        subject = message.get("subject", "")
        print(f"Received subject from extension: {subject}")
        response = {"status": "success", "message": "Subject received"}
        send_message(response)


def send_message(message):
    encoded_message = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("I", len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()


import select


def read_message():
    print("Reading message...")
    rlist, _, _ = select.select([sys.stdin], [], [], 0)
    if rlist:
        message_length = sys.stdin.buffer.read(4)
        if len(message_length) == 0:
            return None
        message_length = struct.unpack("i", message_length)[0]
        message = sys.stdin.buffer.read(message_length).decode("utf-8")
        return json.loads(message)
    else:
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    def handle_messages():
        message = read_message()
        handle_message(message)

    timer = QTimer()
    timer.timeout.connect(handle_messages)
    timer.start(1000)  # Check for messages every 1 second (1000 milliseconds)

    sys.exit(app.exec_())
