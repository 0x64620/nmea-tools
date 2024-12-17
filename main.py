from message_factory import message_factory
from gga_message import GGAMessage
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QTextEdit, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
import sys

class NMEAParserApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.input_box = QTextEdit(self)
        self.input_box.setPlaceholderText("Введите данные NMEA")
        self.parse_button = QPushButton("Парсить", self)
        self.parse_button.clicked.connect(self.parse_nmea_data)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Time", "Latitude", "Longitude", "Fix Quality", "Number of Satellites", "Altitude"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.parse_button)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.setWindowTitle("NMEA Parser")
        self.resize(800, 600)

    def parse_nmea_data(self):
        raw_messages = self.input_box.toPlainText().splitlines()
        self.table.setRowCount(0)
        for raw in raw_messages:
            message = message_factory(raw)
            if isinstance(message, GGAMessage) and message.valid:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(message.time))
                self.table.setItem(row_position, 1, QTableWidgetItem(str(message.latitude)))
                self.table.setItem(row_position, 2, QTableWidgetItem(str(message.longitude)))
                self.table.setItem(row_position, 3, QTableWidgetItem(message.fix_quality))
                self.table.setItem(row_position, 4, QTableWidgetItem(str(message.num_satellites)))
                self.table.setItem(row_position, 5, QTableWidgetItem(str(message.altitude)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NMEAParserApp()
    window.show()
    sys.exit(app.exec())
