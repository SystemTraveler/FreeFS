import os
import sys
from PyQt5 import QtWidgets, uic

class FreeFSFormattingTool(QtWidgets.QMainWindow):
    def __init__(self):
        super(FreeFSFormattingTool, self).__init__()
        uic.loadUi('main.ui', self)

        # Подключаем кнопки и виджеты к функциям
        self.format.clicked.connect(self.start_format)
        self.fs.currentIndexChanged.connect(self.toggle_password_field)
        self.selImage.clicked.connect(self.select_image)
        self.device.currentIndexChanged.connect(self.update_disk_size_and_sector_size)

    def toggle_password_field(self):
        if self.fs.currentIndex() == 1:  # Если выбран Encrypted
            self.password.setReadOnly(False)
        else:
            self.password.setReadOnly(True)

    def select_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Disk Image", "", "Disk Image Files (*.fimg);;All Files (*)", options=options)
        if file_name:
            self.device.addItem(file_name)
            self.device.setCurrentText(file_name)
            self.size.setReadOnly(False)
            self.fs_2.setEnabled(True)
        self.statusBar.showMessage("Image file selected: " + file_name, 5000)

    def update_disk_size_and_sector_size(self):
        current_device = self.device.currentText()
        if current_device != "No device found.":
            self.size.setReadOnly(True)
            self.fs_2.setEnabled(False)
            disk_size = self.get_disk_size(current_device)
            self.size.setText(str(disk_size))
        else:
            self.size.clear()
            self.fs_2.setEnabled(True)
        self.statusBar.showMessage("Device selected: " + current_device, 5000)

    def get_disk_size(self, disk_path):
        # Имитация получения размера диска
        return 1024  # Замените на реальное получение размера диска, если требуется

    def start_format(self):
        disk_path = self.device.currentText()
        if disk_path == "No device found.":
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select an image file.")
            return

        try:
            total_size = self.convert_size(self.size.text(), self.SizeType.currentText())
            disk_name = self.diskLabel.text()
            sector_size = int(self.fs_2.currentText())

            if not disk_name:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a disk name.")
                return

            self.format_disk(disk_path, total_size, disk_name, sector_size)

        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Warning", "Invalid size input.")
            self.statusBar.showMessage("Invalid size input.", 5000)

    def convert_size(self, size_text, size_unit):
        size = int(size_text)
        unit_multiplier = {
            'Kb': 1024,
            'Mb': 1024 * 1024,
            'Gb': 1024 * 1024 * 1024,
            'Tb': 1024 * 1024 * 1024 * 1024
        }
        return size * unit_multiplier.get(size_unit, 1)

    def format_disk(self, disk_path, total_size, disk_name, sector_size):
        try:
            with open(disk_path, 'wb') as disk:
                total_sectors = total_size // sector_size
                signature_format = f"FreeFS;{disk_name};{total_sectors};{sector_size};"
                signature = signature_format.encode()

                disk.write(signature)
                disk.write(bytearray(sector_size - len(signature)))

                remaining_size = total_size - sector_size
                sectors = remaining_size // sector_size
                progress_step = sectors // 100 if sectors >= 100 else 1

                for i in range(sectors):
                    disk.write(bytearray(sector_size))
                    if i % progress_step == 0:
                        percent_complete = (i * 100) // sectors
                        self.progressBar.setValue(percent_complete)
                        QtWidgets.QApplication.processEvents()

                disk.seek(total_size - sector_size)
                end_marker = 'END'.encode()
                disk.write(end_marker)
                disk.write(bytearray(sector_size - len(end_marker)))

            QtWidgets.QMessageBox.information(self, "Success", "Disk formatted successfully.")
            self.statusBar.showMessage("Disk formatted successfully", 5000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.statusBar.showMessage("An error occurred: " + str(e), 5000)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = FreeFSFormattingTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
