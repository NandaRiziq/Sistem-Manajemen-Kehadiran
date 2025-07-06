from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QComboBox, QPushButton, QDateTimeEdit, QTableView, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QDateTime
from typing import Optional
import database

# widget untuk melacak kehadiran karyawan
class AttendanceTrackingWidget(QWidget):
    """
    Widget untuk melacak kehadiran harian karyawan.
    Memungkinkan pencatatan waktu masuk (check-in) dan keluar (check-out) karyawan.
    """
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Layout utama vertikal untuk widget
        main_layout = QVBoxLayout(self)

        # --- Bagian Pemilihan Karyawan ---
        # Group box untuk memilih karyawan
        selection_group = QGroupBox("Pilih Karyawan")
        main_layout.addWidget(selection_group)
        selection_layout = QFormLayout(selection_group)

        # Dropdown untuk memilih karyawan
        self.employee_combo = QComboBox()
        selection_layout.addRow(QLabel("Karyawan:"), self.employee_combo)
        
        # --- Bagian Aksi Kehadiran ---
        # Group box untuk tombol-tombol pencatatan kehadiran
        action_group = QGroupBox("Pencatatan Kehadiran")
        main_layout.addWidget(action_group)
        action_layout = QFormLayout(action_group)

        # Tombol untuk mencatat waktu masuk (check-in)
        self.check_in_button = QPushButton("Masuk")
        self.check_in_button.clicked.connect(self.check_in)
        
        # Tombol untuk mencatat waktu keluar (check-out)
        self.check_out_button = QPushButton("Keluar")
        self.check_out_button.clicked.connect(self.check_out)
        
        # Menambahkan tombol ke layout
        action_layout.addRow(self.check_in_button)
        action_layout.addRow(self.check_out_button)

        # Memuat daftar karyawan ke dalam dropdown
        self.load_employees_into_combobox()

        # --- Bagian Tabel Catatan Harian ---
        # Group box untuk menampilkan catatan kehadiran hari ini
        records_group = QGroupBox("Catatan Hari Ini")
        main_layout.addWidget(records_group)
        records_layout = QVBoxLayout(records_group)

        # Tabel untuk menampilkan catatan kehadiran hari ini
        self.records_table = QTableView()
        records_layout.addWidget(self.records_table)
        
        # Model data untuk tabel catatan harian
        self.daily_model = QStandardItemModel()
        self.records_table.setModel(self.daily_model)

        # Mendorong semua widget ke bagian atas
        main_layout.addStretch() 
        
        # Memuat catatan kehadiran hari ini
        self.load_daily_records()

    def load_employees_into_combobox(self) -> None:
        """
        Memuat daftar karyawan dari database ke dalam dropdown.
        Jika tidak ada karyawan, widget akan dinonaktifkan.
        """
        # Mengosongkan dropdown sebelum memuat ulang
        self.employee_combo.clear()
        
        # Membuat koneksi ke database dan mengambil data karyawan
        conn = database.create_connection()
        employees = []
        if conn:
            employees = database.get_all_employees(conn)
            conn.close()

        # Mengatur status widget berdasarkan ketersediaan data karyawan
        if employees:
            # Jika ada karyawan, aktifkan semua widget
            self.employee_combo.setEnabled(True)
            self.check_in_button.setEnabled(True)
            self.check_out_button.setEnabled(True)
            
            # Menambahkan setiap karyawan ke dropdown dengan ID sebagai data
            for employee in employees:
                self.employee_combo.addItem(employee[1], userData=employee[0])
        else:
            # Jika tidak ada karyawan, nonaktifkan semua widget
            self.employee_combo.addItem("Silakan tambahkan karyawan terlebih dahulu")
            self.employee_combo.setEnabled(False)
            self.check_in_button.setEnabled(False)
            self.check_out_button.setEnabled(False)

    def load_daily_records(self) -> None:
        """
        Memuat dan menampilkan catatan kehadiran hari ini dari database.
        Menghitung jam kerja berdasarkan waktu masuk dan keluar.
        """
        # Menghapus data lama dari model tabel
        self.daily_model.removeRows(0, self.daily_model.rowCount())
        
        # Mengatur header kolom tabel
        self.daily_model.setHorizontalHeaderLabels(['Karyawan', 'Waktu Masuk', 'Waktu Keluar', 'Jam Kerja', 'Status'])
        
        # Mendapatkan tanggal hari ini dalam format string
        today_str = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        
        # Mengambil catatan kehadiran hari ini dari database
        conn = database.create_connection()
        if conn:
            records = database.get_todays_records(conn, today_str)
            conn.close()
            
            # Memproses setiap catatan untuk menghitung jam kerja
            for row_data in records:
                # Mengambil waktu masuk dan keluar
                check_in_str = row_data[1]
                check_out_str = row_data[2]
                work_hours_str = ""
                
                # Menghitung jam kerja jika kedua waktu tersedia
                if check_in_str and check_out_str:
                    check_in_dt = QDateTime.fromString(check_in_str, Qt.DateFormat.ISODate)
                    check_out_dt = QDateTime.fromString(check_out_str, Qt.DateFormat.ISODate)
                    if check_in_dt.isValid() and check_out_dt.isValid():
                        # Menghitung durasi dalam detik dan mengkonversi ke jam
                        duration_secs = check_in_dt.secsTo(check_out_dt)
                        duration_hours = duration_secs / 3600.0
                        work_hours_str = f"{duration_hours:.1f}"

                # Menyisipkan jam kerja ke dalam data baris
                new_row_data = list(row_data)
                new_row_data.insert(3, work_hours_str)
                
                # Membuat item untuk setiap field dan menambahkan ke model
                items = [QStandardItem(str(field) if field is not None else "") for field in new_row_data]
                self.daily_model.appendRow(items)
        
        # Menyesuaikan ukuran kolom dengan konten
        self.records_table.resizeColumnsToContents()

    def check_in(self) -> None:
        """
        Mencatat waktu masuk (check-in) karyawan.
        Menggunakan waktu saat ini sebagai waktu masuk.
        """
        # Mengambil ID karyawan yang dipilih
        employee_id = self.employee_combo.currentData()
        if employee_id is None:
            QMessageBox.warning(self, "Kesalahan Pemilihan", "Silakan pilih karyawan.")
            return

        # Mendapatkan waktu saat ini
        now = QDateTime.currentDateTime()
        check_in_time = now.toString(Qt.DateFormat.ISODate)
        date = now.toString("yyyy-MM-dd")
        status = "Hadir"

        # Menyimpan catatan kehadiran ke database
        conn = database.create_connection()
        if conn:
            record = (employee_id, check_in_time, status, date)
            database.add_attendance_record(conn, record)
            conn.close()
            
            # Menampilkan pesan sukses dan memuat ulang data
            QMessageBox.information(self, "Berhasil", f"{self.employee_combo.currentText()} berhasil check-in.")
            self.load_daily_records()

    def check_out(self) -> None:
        """
        Mencatat waktu keluar (check-out) karyawan.
        Mencari catatan check-in terakhir untuk diupdate dengan waktu keluar.
        """
        # Mengambil ID karyawan yang dipilih
        employee_id = self.employee_combo.currentData()
        if employee_id is None:
            QMessageBox.warning(self, "Kesalahan Pemilihan", "Silakan pilih karyawan.")
            return

        # Mendapatkan waktu saat ini
        now = QDateTime.currentDateTime()
        check_out_time = now.toString(Qt.DateFormat.ISODate)
        date = now.toString("yyyy-MM-dd")

        # Mencari dan mengupdate catatan check-in terakhir
        conn = database.create_connection()
        if conn:
            # Mencari catatan check-in terakhir yang belum di-check-out
            last_check_in = database.get_last_check_in_for_employee(conn, employee_id, date)
            
            if last_check_in:
                # Jika ditemukan, update dengan waktu check-out
                record_id = last_check_in[0]
                database.check_out(conn, record_id, check_out_time)
                QMessageBox.information(self, "Berhasil", f"{self.employee_combo.currentText()} berhasil check-out.")
                self.load_daily_records()
            else:
                # Jika tidak ditemukan catatan check-in, tampilkan peringatan
                QMessageBox.warning(self, "Kesalahan Check-out", "Tidak ditemukan catatan check-in untuk karyawan ini hari ini.")
            
            conn.close()
