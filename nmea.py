import sys
import json
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QTextEdit, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog

class NMEAData:
    def __init__(self):
        self.date = "N/A"
        self.time = "N/A"
        self.latitude = "N/A"
        self.longitude = "N/A"
        self.altitude = "N/A"
        self.fix = "No"
        self.fix_quality = "N/A"
        self.pdop = "N/A"
        self.hdop = "N/A"
        self.vdop = "N/A"
        self.inview_sats = 0
        self.active_sats = 0
        self.active_gps = 0
        self.active_glo = 0
        self.active_gal = 0
        self.active_bei = 0
        self.total_inview_sats = set()

def parse_nmea_sentence(sentence, data):
    if sentence.startswith("$GNRMC") or sentence.startswith("$GPRMC"):
        parts = sentence.split(',')
        if len(parts) > 6 and parts[2] == 'A':
            data.time = format_time(parts[1])
            data.date = format_date(parts[9])
            data.latitude = convert_to_degrees(parts[3], parts[4])
            data.longitude = convert_to_degrees(parts[5], parts[6])
            data.fix = "Yes"
    elif sentence.startswith("$GNGGA") or sentence.startswith("$GPGGA"):
        parts = sentence.split(',')
        if len(parts) > 6:
            data.time = format_time(parts[1])
            data.latitude = convert_to_degrees(parts[2], parts[3])
            data.longitude = convert_to_degrees(parts[4], parts[5])
            data.fix_quality = "GPS" if parts[6] == "1" else "N/A"
            data.altitude = parts[9]
    elif sentence.startswith("$GPGSV") or sentence.startswith("$GBGSV") or sentence.startswith("$GAGSV"):
        parts = sentence.split(',')
        num_sats_in_view = int(parts[3]) if parts[3].isdigit() else 0
        
        for i in range(4, len(parts) - 1, 4):
            if parts[i].isdigit():
                sat_id = int(parts[i])
                if sat_id not in data.total_inview_sats:
                    data.total_inview_sats.add(sat_id)
                    if 1 <= sat_id <= 32:  # GPS
                        data.active_gps += 1
                    elif 201 <= sat_id <= 237:  # Beidou
                        data.active_bei += 1
                    elif 65 <= sat_id <= 96:  # ГЛОНАСС
                        data.active_glo += 1
                    elif 301 <= sat_id <= 336:  # Galileo
                        data.active_gal += 1
        
        data.inview_sats = len(data.total_inview_sats)
        data.active_sats = data.active_gps + data.active_glo + data.active_bei + data.active_gal
    elif sentence.startswith("$GNGSA"):
        parts = sentence.split(',')
        data.pdop = parts[15] if len(parts) > 15 else "N/A"
        data.hdop = parts[16] if len(parts) > 16 else "N/A"
        data.vdop = parts[17].split('*')[0] if len(parts) > 17 else "N/A"
    return data

def format_time(nmea_time):
    if len(nmea_time) >= 6:
        return f"{nmea_time[:2]}:{nmea_time[2:4]}:{nmea_time[4:6]}"
    return nmea_time

def format_date(nmea_date):
    if len(nmea_date) == 6:
        return f"20{nmea_date[4:6]}-{nmea_date[2:4]}-{nmea_date[0:2]}"
    return nmea_date

def convert_to_degrees(value, direction):
    if not value:
        return ""
    degrees = float(value[:2])
    minutes = float(value[2:])
    result = degrees + minutes / 60
    if direction == 'S' or direction == 'W':
        result = -result
    return f"{result:.8f}"

class NMEAParserApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.input_box = QTextEdit(self)
        self.input_box.setPlaceholderText("NMEA")
        self.parse_button = QPushButton("go", self)
        self.parse_button.clicked.connect(self.parse_nmea_data)

        self.save_button = QPushButton("JSON", self)
        self.save_button.clicked.connect(self.export_to_json)

        self.table = QTableWidget()
        self.table.setColumnCount(15)
        self.table.setHorizontalHeaderLabels([
            "Date", "Time", "Latitude", "Longitude", "Altitude", "Fix", "Fix Quality", "PDOP", "HDOP", "VDOP", 
            "Inview Sats", "Active Sats", "Active GPS", "Active GLO", "Active BEI"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.parse_button)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.setWindowTitle("NMEA Parser")
        self.resize(800, 600)

    def parse_nmea_data(self):
        raw_text = self.input_box.toPlainText()
        sentences = raw_text.strip().split('\n')
        self.table.setRowCount(0)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                data = NMEAData()
                data = parse_nmea_sentence(sentence, data)
                self.add_row(data)




    def add_row(self, data):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(data.date))
        self.table.setItem(row_position, 1, QTableWidgetItem(data.time))
        self.table.setItem(row_position, 2, QTableWidgetItem(data.latitude))
        self.table.setItem(row_position, 3, QTableWidgetItem(data.longitude))
        self.table.setItem(row_position, 4, QTableWidgetItem(data.altitude))
        self.table.setItem(row_position, 5, QTableWidgetItem(data.fix))
        self.table.setItem(row_position, 6, QTableWidgetItem(data.fix_quality))
        self.table.setItem(row_position, 7, QTableWidgetItem(data.pdop))
        self.table.setItem(row_position, 8, QTableWidgetItem(data.hdop))
        self.table.setItem(row_position, 9, QTableWidgetItem(data.vdop))
        self.table.setItem(row_position, 10, QTableWidgetItem(str(data.inview_sats)))
        self.table.setItem(row_position, 11, QTableWidgetItem(str(data.active_sats)))
        self.table.setItem(row_position, 12, QTableWidgetItem(str(data.active_gps)))
        self.table.setItem(row_position, 13, QTableWidgetItem(str(data.active_glo)))
        self.table.setItem(row_position, 14, QTableWidgetItem(str(data.active_bei)))

    def export_to_json(self):
        data_list = []
        for row in range(self.table.rowCount()):
            row_data = {
                "Date": self.table.item(row, 0).text(),
                "Time": self.table.item(row, 1).text(),
                "Latitude": self.table.item(row, 2).text(),
                "Longitude": self.table.item(row, 3).text(),
                "Altitude": self.table.item(row, 4).text(),
                "Fix": self.table.item(row, 5).text(),
                "Fix Quality": self.table.item(row, 6).text(),
                "PDOP": self.table.item(row, 7).text(),
                "HDOP": self.table.item(row, 8).text(),
                "VDOP": self.table.item(row, 9).text(),
                "Inview Sats": self.table.item(row, 10).text(),
                "Active Sats": self.table.item(row, 11).text(),
                "Active GPS": self.table.item(row, 12).text(),
                "Active GLO": self.table.item(row, 13).text(),
                "Active BEI": self.table.item(row, 14).text(),
            }
            data_list.append(row_data)

        json_data = json.dumps(data_list, indent=4)
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("JSON Files (*.json)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, 'w') as json_file:
                json_file.write(json_data)

def main():
    app = QApplication(sys.argv)
    window = NMEAParserApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()