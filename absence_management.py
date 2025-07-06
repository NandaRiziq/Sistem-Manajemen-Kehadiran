from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QComboBox, QPushButton, QDateEdit, QLineEdit, QTableView, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QDate
from typing import Optional
import database

# widget untuk mengelola ketidakhadiran karyawan
class AbsenceManagementWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Layout utama vertikal
        main_layout = QVBoxLayout(self)

        # --- Bagian Pencatatan Ketidakhadiran ---
        selection_group = QGroupBox("Pencatatan Ketidakhadiran")
        main_layout.addWidget(selection_group)
        form_layout = QFormLayout(selection_group)

        # Dropdown untuk memilih karyawan
        self.employee_combo = QComboBox()
        
        # Dropdown untuk memilih jenis ketidakhadiran (Sakit, Izin, Cuti)
        self.absence_type_combo = QComboBox()
        self.absence_type_combo.addItems(['Sakit', 'Izin', 'Cuti'])
        
        # Widget untuk memilih tanggal dengan kalender popup
        self.date_entry = QDateEdit(QDate.currentDate())
        self.date_entry.setCalendarPopup(True)
        
        # Input teks untuk alasan ketidakhadiran
        self.reason_entry = QLineEdit()
        
        # Tombol untuk mencatat ketidakhadiran
        self.record_absence_button = QPushButton("Catat Ketidakhadiran")
        self.record_absence_button.clicked.connect(self.record_absence)

        # Memuat daftar karyawan ke dalam dropdown
        self.load_employees_into_combobox()

        # Menambahkan semua widget ke dalam form layout
        form_layout.addRow(QLabel("Karyawan:"), self.employee_combo)
        form_layout.addRow(QLabel("Jenis Ketidakhadiran:"), self.absence_type_combo)
        form_layout.addRow(QLabel("Tanggal:"), self.date_entry)
        form_layout.addRow(QLabel("Alasan:"), self.reason_entry)
        form_layout.addRow(self.record_absence_button)

        # --- Bagian Tabel Catatan Ketidakhadiran ---
        # Group box untuk menampilkan catatan ketidakhadiran
        records_group = QGroupBox("Catatan Ketidakhadiran")
        main_layout.addWidget(records_group)
        records_layout = QVBoxLayout(records_group)

        # Tabel untuk menampilkan daftar catatan ketidakhadiran
        self.records_table = QTableView()
        records_layout.addWidget(self.records_table)
        
        # Model data untuk tabel catatan ketidakhadiran
        self.absence_model = QStandardItemModel()
        self.records_table.setModel(self.absence_model)
        
        # Memuat catatan ketidakhadiran yang sudah ada
        self.load_absence_records()

        # Menambahkan ruang kosong di bagian bawah
        main_layout.addStretch()

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
            self.absence_type_combo.setEnabled(True)
            self.date_entry.setEnabled(True)
            self.reason_entry.setEnabled(True)
            self.record_absence_button.setEnabled(True)
            
            # Menambahkan setiap karyawan ke dropdown dengan ID sebagai data
            for employee in employees:
                self.employee_combo.addItem(employee[1], userData=employee[0])
        else:
            # Jika tidak ada karyawan, nonaktifkan semua widget
            self.employee_combo.addItem("Silakan tambahkan karyawan terlebih dahulu")
            self.employee_combo.setEnabled(False)
            self.absence_type_combo.setEnabled(False)
            self.date_entry.setEnabled(False)
            self.reason_entry.setEnabled(False)
            self.record_absence_button.setEnabled(False)

    def record_absence(self) -> None:
        """
        Mencatat ketidakhadiran karyawan ke dalam database.
        Validasi input dilakukan sebelum menyimpan data.
        """
        # Mengambil ID karyawan yang dipilih
        employee_id = self.employee_combo.currentData()
        if employee_id is None:
            QMessageBox.warning(self, "Kesalahan Pemilihan", "Silakan pilih karyawan.")
            return

        # Mengambil data dari form
        absence_type = self.absence_type_combo.currentText()
        date = self.date_entry.date().toString("yyyy-MM-dd")
        reason = self.reason_entry.text()
        status = absence_type

        # Menyimpan catatan ketidakhadiran ke database
        conn = database.create_connection()
        if conn:
            record = (employee_id, None, None, status, date, reason) 
            database.add_absence_record(conn, record)
            conn.close()
            
            # Menampilkan pesan sukses dan memuat ulang data
            QMessageBox.information(self, "Berhasil", f"Ketidakhadiran tercatat untuk {self.employee_combo.currentText()}.")
            self.load_absence_records()

    def load_absence_records(self) -> None:
        """
        Memuat dan menampilkan semua catatan ketidakhadiran dari database ke dalam tabel.
        """
        # Menghapus data lama dari model tabel
        self.absence_model.removeRows(0, self.absence_model.rowCount())
        
        # Mengatur header kolom tabel
        self.absence_model.setHorizontalHeaderLabels(['Karyawan', 'Tanggal', 'Jenis', 'Alasan'])
        
        # Mengambil data ketidakhadiran dari database
        conn = database.create_connection()
        if conn:
            records = database.get_all_absences(conn)
            conn.close()
            
            # Menambahkan setiap baris data ke model tabel
            for row_data in records:
                items = [QStandardItem(str(field)) for field in row_data]
                self.absence_model.appendRow(items)
        
        # Menyesuaikan ukuran kolom dengan konten
        self.records_table.resizeColumnsToContents()
