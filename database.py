import sqlite3
from sqlite3 import Error, Connection
from typing import Optional

def create_connection(db_file: str = "attendance.db") -> Optional[Connection]:
    """ 
    Membuat koneksi ke database SQLite.
    
    Returns:
        Objek Connection jika berhasil, None jika gagal
    """
    conn: Optional[Connection] = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}, SQLite version: {sqlite3.version}")
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn: Connection, create_table_sql: str) -> None:
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def setup_database() -> None:
    """ 
    Membuat database dan tabel-tabel yang diperlukan jika belum ada. dipanggil saat aplikasi pertama kali dijalankan.
    """
    database_file: str = "attendance.db"

    # SQL untuk membuat tabel karyawan
    sql_create_employees_table: str = """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        position TEXT,
        department TEXT
    );
    """

    # SQL untuk membuat tabel catatan kehadiran
    sql_create_attendance_records_table: str = """
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        check_in_time TEXT,
        check_out_time TEXT,
        status TEXT NOT NULL,
        date TEXT NOT NULL,
        reason TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    );
    """

    # Membuat koneksi dan tabel-tabel
    conn: Optional[Connection] = create_connection(database_file)

    if conn is not None:
        create_table(conn, sql_create_employees_table)
        create_table(conn, sql_create_attendance_records_table)
        conn.close()
        print("Database and tables are set up.")
    else:
        print("Error! cannot create the database connection.")

def add_employee(conn: Connection, employee: tuple[str, str, str]) -> int:
    """
    Menambahkan karyawan baru ke dalam tabel employees.
    
    Args:
        conn: Koneksi database
        employee: Tuple berisi (nama_lengkap, posisi, departemen)
    
    Returns:
        ID karyawan yang baru ditambahkan
    """
    sql = ''' INSERT INTO employees(full_name,position,department)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, employee)
    conn.commit()
    return cur.lastrowid

def get_all_employees(conn: Connection) -> list[tuple]:
    """
    Mengambil semua data karyawan dari tabel employees.
    
    Args:
        conn: Koneksi database
    
    Returns:
        List tuple berisi semua data karyawan
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees")
    rows = cur.fetchall()
    return rows

def update_employee(conn: Connection, employee: tuple[str, str, str, int]) -> None:
    """
    Memperbarui data karyawan berdasarkan ID.
    
    Args:
        conn: Koneksi database
        employee: Tuple berisi (nama_lengkap, posisi, departemen, id)
    """
    sql = ''' UPDATE employees
              SET full_name = ? ,
                  position = ? ,
                  department = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, employee)
    conn.commit()

def delete_employee(conn: Connection, id: int) -> None:
    """
    Menghapus karyawan berdasarkan ID.
    
    Args:
        conn: Koneksi database
        id: ID karyawan yang akan dihapus
    """
    sql = 'DELETE FROM employees WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def add_attendance_record(conn: Connection, record: tuple) -> int:
    """
    Menambahkan catatan kehadiran baru (check-in).
    
    Args:
        conn: Koneksi database
        record: Tuple berisi (employee_id, check_in_time, status, date)
    
    Returns:
        ID catatan yang baru ditambahkan
    """
    sql = ''' INSERT INTO attendance_records(employee_id,check_in_time,status,date)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, record)
    conn.commit()
    return cur.lastrowid

def get_todays_records(conn: Connection, date: str) -> list[tuple]:
    """
    Mengambil semua catatan kehadiran untuk tanggal tertentu.
    
    Args:
        conn: Koneksi database
        date: Tanggal dalam format 'YYYY-MM-DD'
    
    Returns:
        List tuple berisi catatan kehadiran untuk tanggal tersebut
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT e.full_name, ar.check_in_time, ar.check_out_time, ar.status
        FROM attendance_records ar
        JOIN employees e ON ar.employee_id = e.id
        WHERE ar.date = ?
    """, (date,))
    rows = cur.fetchall()
    return rows

def get_last_check_in_for_employee(conn: Connection, employee_id: int, date: str) -> Optional[tuple]:
    """
    Mencari catatan check-in terakhir untuk karyawan pada tanggal tertentu yang belum di-check-out.
    
    Args:
        conn: Koneksi database
        employee_id: ID karyawan
        date: Tanggal dalam format 'YYYY-MM-DD'
    
    Returns:
        Tuple berisi ID catatan jika ditemukan, None jika tidak ada
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM attendance_records
        WHERE employee_id = ? AND date = ? AND check_out_time IS NULL
        ORDER BY check_in_time DESC
        LIMIT 1
    """, (employee_id, date))
    row = cur.fetchone()
    return row

def check_out(conn: Connection, record_id: int, check_out_time: str) -> None:
    """
    Memperbarui waktu check-out untuk catatan kehadiran tertentu.
    
    Args:
        conn: Koneksi database
        record_id: ID catatan kehadiran
        check_out_time: Waktu check-out dalam format ISO
    """
    sql = ''' UPDATE attendance_records
              SET check_out_time = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (check_out_time, record_id))
    conn.commit()

def add_absence_record(conn: Connection, record: tuple) -> int:
    """
    Menambahkan catatan ketidakhadiran (sakit, izin, cuti).
    
    Args:
        conn: Koneksi database
        record: Tuple berisi (employee_id, check_in_time, check_out_time, status, date, reason)
    
    Returns:
        ID catatan yang baru ditambahkan
    """
    sql = ''' INSERT INTO attendance_records(employee_id, check_in_time, check_out_time, status, date, reason)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, record)
    conn.commit()
    return cur.lastrowid

def get_all_absences(conn: Connection) -> list[tuple]:
    """
    Mengambil semua catatan ketidakhadiran (status: Sakit, Izin, Cuti).
    
    Args:
        conn: Koneksi database
    
    Returns:
        List tuple berisi semua catatan ketidakhadiran diurutkan berdasarkan tanggal terbaru
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT e.full_name, ar.date, ar.status, ar.reason
        FROM attendance_records ar
        JOIN employees e ON ar.employee_id = e.id
        WHERE ar.status IN ('Sakit', 'Izin', 'Cuti')
        ORDER BY ar.date DESC
    """)
    rows = cur.fetchall()
    return rows

def search_employees(conn: Connection, term: str) -> list[tuple]:
    """
    Mencari karyawan berdasarkan nama atau ID.
    
    Args:
        conn: Koneksi database
        term: Kata kunci pencarian (nama atau ID)
    
    Returns:
        List tuple berisi data karyawan yang sesuai dengan pencarian
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE full_name LIKE ? OR id = ?", ('%' + term + '%', term))
    rows = cur.fetchall()
    return rows

# Blok untuk menjalankan setup database jika file ini dijalankan langsung
if __name__ == '__main__':
    setup_database()
