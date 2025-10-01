"""
This is SunTide: A script to generate spreadsheets of data containing
day-by-day tide predictions and daylight information for a given year.

Copyright (C) 2025  Zach Harwood

This file is part of SunTide

SunTide is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import json
import webbrowser
from pathlib import Path
from datetime import datetime

import pytz
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QRadioButton, QDoubleSpinBox, QLabel,
    QComboBox, QPushButton, QListWidget, QSpinBox,
    QMessageBox, QProgressBar, QGroupBox, QFrame, QDialog
)

import worker

CONFIG_FILE = Path("config.json")


class Worker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        # Run the external script with both user data + callback
        worker.compile_data(self.data, self.report_progress)
        self.finished.emit(self.data)

    def report_progress(self, percent, message):
        self.progress.emit(percent, message)


class InputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SunTide - Daylight and Tide Predictions")
        self.setStyleSheet("""/* Global background */
                               QWidget {
                                   background-color: #eeeeee; 
                                   font-size: 12pt;
                               }

                               /* Buttons */
                               QPushButton {
                                   background-color: #eeeeee;
                                   color: black;
                                   border: 1px dotted #555555;
                                   border-radius: 6px;
                                   padding: 6px 6px;
                                   font-size: 11pt;
                               }
                               QPushButton:hover {
                                   color: black;

                                   border: 1px solid #555555;
                               }

                               /* Entry fields */
                               QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QRadioButton, QListWidget {
                                   background-color: #f0f0f0;
                               }
                               QRadioButton, QListWidget {
                                    border: 1px solid #565656;
                                   border-radius: 6px;
                                   padding: 6px;
                               }

                               /* Group boxes */
                               QGroupBox {
                                   border: 1px solid #000000;
                                   border-radius: 6px;
                                   margin-top: 10px;
                                   padding: 6px;
                                   font-weight: bold;
                               }
                               QGroupBox::title {
                                   font-weight: bold;
                                   subcontrol-origin: margin;
                                   subcontrol-position: top left;
                                   padding: 0 6px;
                               }
                           """)
        self.resize(800, 400)

        # -------- MAIN LAYOUT --------
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("☀️  SunTide  🌊")
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # About Buttons
        button_layout = QHBoxLayout()
        instruction_button = QPushButton("Instructions")
        contribute_button = QPushButton("Contribute")
        report_bug_button = QPushButton("Report Bug")
        about_button = QPushButton("About")
        button_layout.addWidget(instruction_button)
        button_layout.addWidget(contribute_button)
        button_layout.addWidget(report_bug_button)
        button_layout.addWidget(about_button)
        main_layout.addLayout(button_layout)

        instruction_button.clicked.connect(self.open_instructions)
        about_button.clicked.connect(self.open_about)
        contribute_button.clicked.connect(self.open_contribute)
        report_bug_button.clicked.connect(self.open_report)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # ------ PANEl CONTAINER ------
        panel_layout = QHBoxLayout()
        panel_layout.setSpacing(20)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        # ---- LEFT PANEL ----
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        # Radio buttons group
        radio_groupbox = QGroupBox("Choose a year")
        radio_layout = QVBoxLayout()
        self.radio1 = QRadioButton(f"{datetime.now().year + 1}")
        self.radio2 = QRadioButton(f"{datetime.now().year}")
        self.radio1.setChecked(True)
        radio_layout.addWidget(self.radio1)
        radio_layout.addWidget(self.radio2)
        radio_groupbox.setLayout(radio_layout)
        left_panel.addWidget(radio_groupbox)

        # Coordinates group
        coord_groupbox = QGroupBox("Coordinates for sunrise/set predictions")
        coord_layout = QVBoxLayout()
        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90, 90)
        self.lat_input.setDecimals(6)
        self.lat_input.setPrefix("Latitude: ")
        self.long_input = QDoubleSpinBox()
        self.long_input.setRange(-180, 180)
        self.long_input.setDecimals(6)
        self.long_input.setPrefix("Longitude: ")
        coord_layout.addWidget(self.lat_input)
        coord_layout.addWidget(self.long_input)
        coord_groupbox.setLayout(coord_layout)
        left_panel.addWidget(coord_groupbox)

        # Timezone group
        tz_groupbox = QGroupBox("Convert times to timezone:")
        tz_layout = QVBoxLayout()
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems(pytz.all_timezones)
        tz_layout.addWidget(self.timezone_combo)  # add items later
        tz_groupbox.setLayout(tz_layout)
        left_panel.addWidget(tz_groupbox)

        left_panel.addStretch()  # push everything up

        # ---- RIGHT PANEL ----
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        int_groupbox = QGroupBox("List NOAA Station ID's to use for Tide Predictions")
        int_layout = QVBoxLayout()
        self.int_list = QListWidget()
        int_layout.addWidget(self.int_list)

        # Controls for add/remove
        controls_layout = QHBoxLayout()
        self.spin_input = QSpinBox()
        self.spin_input.setRange(1000000, 9999999)
        add_button = QPushButton("Add Station")
        remove_button = QPushButton("Remove Station")
        controls_layout.addWidget(self.spin_input)
        controls_layout.addWidget(add_button)
        controls_layout.addWidget(remove_button)
        int_layout.addLayout(controls_layout)

        int_groupbox.setLayout(int_layout)
        right_panel.addWidget(int_groupbox)
        right_panel.addStretch()

        add_button.clicked.connect(self.add_integer)
        remove_button.clicked.connect(self.remove_selected)

        # -------- COMBINE PANELS --------
        panel_layout.addLayout(left_panel, 1)  # stretch factor 1
        panel_layout.addLayout(right_panel, 1)  # stretch factor 1

        main_layout.addLayout(panel_layout)

        # ---- Confirm button ----
        self.confirm_button = QPushButton("Generate Spreadsheets")
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.confirm_button.setStyleSheet("""
                               QPushButton {
                                   background-color: #ff773e;
                                   color: white;
                                   border: none;
                                   border-radius: 6px;
                                   padding: 6px 12px;
                                   min-width: 0px;
                                   font-size: 18px;
                               }
                               QPushButton:hover {
                                   border: 1px solid #000000;
                                   font-style: bold;
                                   color: black;
                               }""")
        confirm_button_layout = QHBoxLayout()
        confirm_button_layout.addStretch()  # left spacer
        confirm_button_layout.addWidget(self.confirm_button)
        confirm_button_layout.addStretch()  # right spacer

        # ---- Progress bar ----
        self.progress_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()

        # ---- Finish main layout ----
        main_layout.addLayout(confirm_button_layout)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)
        self.load_config()

    # -------- BUTTON FUNCTIONS --------
    def open_about(self):
        text = "SunTide v4.0.0 \n\nA program to compile spreadsheets of data containing " \
               "day-by-day tide predictions and daylight information for a given year." \
               "\n\nCopyright (C) 2025  Zach Harwood.\nhttps://github.com/techno-user314" \
               "\n____________________________________" \
               "\n\nThis program is licensed under the GNU General Public License, " \
               "and is distributed in the hope that it will be useful, " \
               "but WITHOUT ANY WARRANTY; without even the implied warranty of " \
               "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. " \
               "\n\nSee the GNU General Public License for more details." \
               "\n\nYou should have received a copy of the GNU General Public License " \
               "along with this program. If not, see \nhttps://www.gnu.org/licenses/."
        QMessageBox.information(self, "About", text)

    def open_instructions(self):
        popup = QDialog(self)
        popup.setWindowTitle("Usage Guide")
        popup.resize(500, 400)
        popup.show()

    def open_contribute(self):
        webbrowser.open('https://github.com/techno-user314/suntide/')

    def open_report(self):
        webbrowser.open('https://github.com/techno-user314/suntide/issues')

    def add_integer(self):
        value = self.spin_input.value()
        self.int_list.addItem(str(value))

    def remove_selected(self):
        for item in self.int_list.selectedItems():
            self.int_list.takeItem(self.int_list.row(item))

    def confirm_selection(self):
        self.confirm_button.hide()
        data = self.get_form_data()
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

        self.set_form_enabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")

        self.worker = Worker(data)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.task_finished)
        self.worker.start()

    # -------- UTILITY --------
    def get_form_data(self):
        return {
            "radio_selection": int(datetime.now().year + 1) if self.radio1.isChecked() else int(datetime.now().year),
            "latitude": self.lat_input.value(),
            "longitude": self.long_input.value(),
            "timezone": self.timezone_combo.currentText(),
            "integer_list": [int(self.int_list.item(i).text()) for i in range(self.int_list.count())]
        }

    def set_form_enabled(self, enabled):
        for widget in [
            self.radio1, self.radio2, self.lat_input, self.long_input,
            self.timezone_combo, self.int_list, self.spin_input,
            self.confirm_button
        ]:
            widget.setEnabled(enabled)

    def update_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.progress_label.setText(msg)

    def task_finished(self, data):
        self.progress_bar.hide()
        self.progress_label.setText("")
        self.confirm_button.show()
        self.set_form_enabled(True)
        QMessageBox.information(self, "Done", "Data compiled successfully!")

    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            if data.get("radio_selection") == datetime.now().year:
                self.radio2.setChecked(True)
            else:
                self.radio1.setChecked(True)
            self.lat_input.setValue(data.get("latitude", 0.0))
            self.long_input.setValue(data.get("longitude", 0.0))
            tz = data.get("timezone", "UTC")
            if tz in pytz.all_timezones:
                self.timezone_combo.setCurrentText(tz)
            self.int_list.clear()
            for val in data.get("integer_list", []):
                self.int_list.addItem(str(val))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InputApp()
    window.show()
    sys.exit(app.exec())
