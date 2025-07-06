import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout
import database
from employee_management import EmployeeManagementWidget
from attendance_tracking import AttendanceTrackingWidget
from absence_management import AbsenceManagementWidget

# Kelas utama aplikasi untuk jendela utama
class MainWindow(QMainWindow):
    """
    Jendela utama aplikasi Sistem Manajemen Kehadiran Karyawan.
    Mengatur layout dengan tab untuk berbagai fitur.
    """
    def __init__(self) -> None:
        super().__init__()

        # Pengaturan jendela utama
        self.setWindowTitle("Sistem Manajemen Kehadiran Karyawan")
        self.setGeometry(100, 100, 800, 600)

        # Setup database - membuat tabel jika belum ada
        database.setup_database()

        # Membuat interface dengan tab
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Menambahkan Tab Manajemen Karyawan
        self.employee_management_tab = EmployeeManagementWidget()
        self.tabs.addTab(self.employee_management_tab, "Manajemen Karyawan")

        # Menambahkan Tab Pelacakan Kehadiran
        self.attendance_tracking_tab = AttendanceTrackingWidget()
        self.tabs.addTab(self.attendance_tracking_tab, "Pelacakan Kehadiran")

        # Menambahkan Tab Manajemen Ketidakhadiran
        self.absence_management_tab = AbsenceManagementWidget()
        self.tabs.addTab(self.absence_management_tab, "Manajemen Ketidakhadiran")

        # Menghubungkan signal antar tab
        self.employee_management_tab.employees_changed.connect(self.attendance_tracking_tab.load_employees_into_combobox)
        self.employee_management_tab.employees_changed.connect(self.absence_management_tab.load_employees_into_combobox)

def main() -> None:
    """
    Fungsi utama untuk menjalankan aplikasi.
    Membuat instance QApplication dan menampilkan jendela utama.
    """
    # Membuat instance aplikasi PyQt6
    app = QApplication(sys.argv)
    
    # Membuat dan menampilkan jendela utama
    window = MainWindow()
    window.show()
    
    # Menjalankan loop aplikasi dan keluar dengan kode exit yang sesuai
    sys.exit(app.exec())

# Blok untuk menjalankan aplikasi jika file ini dijalankan langsung
if __name__ == "__main__":
    main()
