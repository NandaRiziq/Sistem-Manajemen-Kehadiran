from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit, QPushButton, QTableView, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional
import database

# widget untuk mengelola data karyawan
class EmployeeManagementWidget(QWidget):
    """
    Widget untuk mengelola data karyawan.
    Memungkinkan penambahan, pengeditan, penghapusan, dan pencarian data karyawan.
    """
    # Signal yang dipancarkan ketika data karyawan berubah
    employees_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # --- Layout Utama ---
        main_layout = QVBoxLayout(self)

        # --- Widget-widget Interface ---
        form_groupbox = QGroupBox("Informasi Karyawan")
        main_layout.addWidget(form_groupbox)

        form_layout = QFormLayout(form_groupbox)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Input field untuk data karyawan
        self.name_entry = QLineEdit()
        self.position_entry = QLineEdit()
        self.department_entry = QLineEdit()

        # Menambahkan label dan input field ke form
        form_layout.addRow(QLabel("Nama Lengkap:"), self.name_entry)
        form_layout.addRow(QLabel("Posisi:"), self.position_entry)
        form_layout.addRow(QLabel("Departemen:"), self.department_entry)

        # Tombol-tombol aksi untuk pengelolaan karyawan
        button_layout = QVBoxLayout()
        
        # Tombol untuk menambah karyawan baru
        self.add_button = QPushButton("Tambah Karyawan")
        self.add_button.clicked.connect(self.add_employee)
        
        # Tombol untuk memperbarui data karyawan yang dipilih
        self.update_button = QPushButton("Perbarui Terpilih")
        self.update_button.clicked.connect(self.update_employee)
        
        # Tombol untuk menghapus karyawan yang dipilih
        self.delete_button = QPushButton("Hapus Terpilih")
        self.delete_button.clicked.connect(self.delete_employee)
        
        # Menambahkan tombol ke layout
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        form_layout.addRow(button_layout)

        # --- Bagian Pencarian ---
        search_groupbox = QGroupBox("Cari Karyawan")
        main_layout.addWidget(search_groupbox)
        search_layout = QFormLayout(search_groupbox)

        # Input field untuk pencarian karyawan
        self.search_entry = QLineEdit()
        
        # Tombol untuk melakukan pencarian
        self.search_button = QPushButton("Cari")
        self.search_button.clicked.connect(self.search_employees)
        
        # Tombol untuk membersihkan hasil pencarian
        self.clear_search_button = QPushButton("Bersihkan")
        self.clear_search_button.clicked.connect(self.clear_search)
        
        # Menambahkan widget pencarian ke layout
        search_layout.addRow(QLabel("Cari berdasarkan Nama atau ID:"), self.search_entry)
        search_layout.addRow(self.search_button, self.clear_search_button)

        # Tabel untuk menampilkan daftar karyawan
        self.employee_table = QTableView()
        self.employee_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.employee_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        main_layout.addWidget(self.employee_table)
        
        # Model data untuk tabel karyawan
        self.model = QStandardItemModel()
        self.employee_table.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['ID', 'Nama Lengkap', 'Posisi', 'Departemen'])
        
        # Menghubungkan signal ketika baris dipilih
        self.employee_table.selectionModel().selectionChanged.connect(self.on_row_selected)
        
        # Memuat data karyawan ke dalam tabel
        self.load_employees()
        
        # Variabel untuk menyimpan ID karyawan yang dipilih
        self.selected_employee_id: Optional[int] = None

    def load_employees(self) -> None:
        """
        Memuat semua data karyawan dari database ke dalam tabel.
        """
        # Menghapus data lama dari model tabel
        self.model.removeRows(0, self.model.rowCount()) 
        
        # Mengambil data karyawan dari database
        conn = database.create_connection()
        if conn:
            employees = database.get_all_employees(conn)
            conn.close()

            # Menambahkan setiap karyawan ke dalam tabel
            for row_data in employees:
                items = [QStandardItem(str(field)) for field in row_data]
                self.model.appendRow(items)
            
            # Menyesuaikan ukuran kolom dengan konten
            self.employee_table.resizeColumnsToContents()

    def on_row_selected(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            # Jika tidak ada yang dipilih, reset form
            self.selected_employee_id = None
            self.clear_form()
            return

        # Mengambil data dari baris yang dipilih
        row = indexes[0].row()
        model = self.employee_table.model()
        
        # Mengisi form dengan data karyawan yang dipilih
        self.selected_employee_id = int(model.item(row, 0).text())
        self.name_entry.setText(model.item(row, 1).text())
        self.position_entry.setText(model.item(row, 2).text())
        self.department_entry.setText(model.item(row, 3).text())

    def add_employee(self) -> None:
        """
        Menambahkan karyawan baru ke database.
        Validasi input dilakukan sebelum menyimpan.
        """
        # Mengambil data dari form
        name = self.name_entry.text()
        position = self.position_entry.text()
        department = self.department_entry.text()

        # Validasi: nama harus diisi
        if not name:
            QMessageBox.warning(self, "Kesalahan Input", "Nama lengkap tidak boleh kosong.")
            return

        # Menyimpan karyawan baru ke database
        conn = database.create_connection()
        if conn:
            employee_data = (name, position, department)
            database.add_employee(conn, employee_data)
            conn.close()
            
            # Menampilkan pesan sukses dan memuat ulang data
            QMessageBox.information(self, "Berhasil", f"Karyawan '{name}' berhasil ditambahkan.")
            self.clear_form()
            self.load_employees()
            
            # Memicu signal bahwa data karyawan telah berubah
            self.employees_changed.emit()

    def update_employee(self) -> None:
        """
        Memperbarui data karyawan yang dipilih.
        """
        # Validasi: harus ada karyawan yang dipilih
        if self.selected_employee_id is None:
            QMessageBox.warning(self, "Kesalahan Pemilihan", "Silakan pilih karyawan yang akan diperbarui.")
            return

        # Mengambil data dari form
        name = self.name_entry.text()
        position = self.position_entry.text()
        department = self.department_entry.text()

        # Validasi: nama harus diisi
        if not name:
            QMessageBox.warning(self, "Kesalahan Input", "Nama lengkap tidak boleh kosong.")
            return

        # Memperbarui data karyawan di database
        conn = database.create_connection()
        if conn:
            employee_data = (name, position, department, self.selected_employee_id)
            database.update_employee(conn, employee_data)
            conn.close()
            
            # Menampilkan pesan sukses dan memuat ulang data
            QMessageBox.information(self, "Berhasil", f"Karyawan '{name}' berhasil diperbarui.")
            self.clear_form()
            self.load_employees()
            
            # Memicu signal bahwa data karyawan telah berubah
            self.employees_changed.emit()

    def delete_employee(self) -> None:
        """
        Menghapus karyawan yang dipilih dari database.
        Konfirmasi diperlukan sebelum penghapusan.
        """
        # Validasi: harus ada karyawan yang dipilih
        if self.selected_employee_id is None:
            QMessageBox.warning(self, "Kesalahan Pemilihan", "Silakan pilih karyawan yang akan dihapus.")
            return

        # Konfirmasi penghapusan
        reply = QMessageBox.question(self, 'Konfirmasi Hapus', 
                                     f"Apakah Anda yakin ingin menghapus karyawan {self.name_entry.text()}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        # Jika dikonfirmasi, hapus karyawan
        if reply == QMessageBox.StandardButton.Yes:
            conn = database.create_connection()
            if conn:
                database.delete_employee(conn, self.selected_employee_id)
                conn.close()
                
                # Menampilkan pesan sukses dan memuat ulang data
                QMessageBox.information(self, "Berhasil", "Karyawan berhasil dihapus.")
                self.clear_form()
                self.load_employees()
                
                # Memicu signal bahwa data karyawan telah berubah
                self.employees_changed.emit()

    def clear_form(self) -> None:
        """
        Membersihkan semua input field dalam form.
        """
        self.name_entry.clear()
        self.position_entry.clear()
        self.department_entry.clear()
        self.selected_employee_id = None
        self.employee_table.clearSelection()

    def search_employees(self) -> None:
        """
        Mencari karyawan berdasarkan nama atau ID.
        Jika tidak ada kata kunci, tampilkan semua karyawan.
        """
        search_term = self.search_entry.text()
        if not search_term:
            # Jika tidak ada kata kunci, tampilkan semua karyawan
            self.load_employees()
            return

        # Melakukan pencarian di database
        conn = database.create_connection()
        if conn:
            employees = database.search_employees(conn, search_term)
            conn.close()

            # Menampilkan hasil pencarian di tabel
            self.model.removeRows(0, self.model.rowCount())
            for row_data in employees:
                items = [QStandardItem(str(field)) for field in row_data]
                self.model.appendRow(items)

    def clear_search(self) -> None:
        """
        Membersihkan kata kunci pencarian dan menampilkan semua karyawan.
        """
        self.search_entry.clear()
        self.load_employees()
