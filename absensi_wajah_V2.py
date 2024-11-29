import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import os
import face_recognition
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk
import time

# Koneksi ke MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="absensi_wajah"
)
cursor = db.cursor()

# Fungsi untuk merekam wajah
def record_face():
    def capture_face():
        name = name_entry.get()
        if not name:
            messagebox.showwarning("Peringatan", "Nama tidak boleh kosong!")
            return

        os.makedirs("faces", exist_ok=True)
        count = 0

        def process_frame():
            nonlocal count
            ret, frame = cap.read()
            if not ret:
                print("Gagal membaca frame dari kamera.")
                return

            faces = face_recognition.face_locations(frame)
            for (top, right, bottom, left) in faces:
                count += 1
                face_img = frame[top:bottom, left:right]
                file_path = os.path.join("faces", f"{name}_{count}.jpg")
                cv2.imwrite(file_path, face_img)

                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
                if count >= 10:
                    break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            frame_widget.imgtk = imgtk
            frame_widget.configure(image=imgtk)

            if count < 10:
                frame_widget.after(10, process_frame)
            else:
                cap.release()
                frame_widget.destroy()
                cursor.execute("INSERT INTO users (name, image_path) VALUES (%s, %s)", (name, file_path))
                db.commit()
                messagebox.showinfo("Sukses", "Wajah berhasil direkam!")
                record_window.destroy()

        process_frame()

    record_window = tk.Toplevel(root)
    record_window.title("Rekam Wajah")

    tk.Label(record_window, text="Nama").pack(pady=10)
    name_entry = tk.Entry(record_window)
    name_entry.pack(pady=10)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        messagebox.showerror("Error", "Kamera tidak dapat diakses. Pastikan kamera terhubung dan tidak digunakan oleh aplikasi lain.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_widget = tk.Label(record_window)
    frame_widget.pack()

    tk.Button(record_window, text="Rekam Wajah", command=capture_face).pack(pady=10)

# Fungsi untuk absensi
def mark_attendance():
    start_time = time.time()  # Catat waktu mulai
    recognized = False

    def process_frame():
        nonlocal recognized
        elapsed_time = time.time() - start_time

        ret, frame = cap.read()
        if not ret:
            print("Gagal membaca frame dari kamera.")
            return

        faces = face_recognition.face_locations(frame)
        encodings = face_recognition.face_encodings(frame, faces)

        for face_encoding, (top, right, bottom, left) in zip(encodings, faces):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            if True in matches:
                matched_index = matches.index(True)
                user_id = known_user_ids[matched_index]
                name = known_names[matched_index]

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Tampilkan jendela konfirmasi
                def confirm():
                    now = datetime.now()
                    date = now.date()
                    time = now.time()
                    cursor.execute("INSERT INTO attendance (user_id, date, time) VALUES (%s, %s, %s)", (user_id, date, time))
                    db.commit()
                    messagebox.showinfo("Sukses", f"Wajah dikenali: {name}. Absensi berhasil dicatat.")
                    cap.release()
                    mark_window.destroy()

                # Konfirmasi hanya sekali
                recognized = True
                tk.Button(mark_window, text=f"Wajah dikenali: {name}. Klik untuk konfirmasi.", command=confirm).pack(pady=10)
                break

        # Jika 10 detik berlalu dan wajah belum dikenali
        if not recognized and elapsed_time > 10:
            def no_face():
                messagebox.showwarning("Gagal", "Wajah tidak dikenali. Proses absensi dihentikan.")
                cap.release()
                mark_window.destroy()

            tk.Button(mark_window, text="Wajah tidak dikenali. Klik untuk mengakhiri.", command=no_face).pack(pady=10)
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        frame_widget.imgtk = imgtk
        frame_widget.configure(image=imgtk)

        if not recognized:
            frame_widget.after(10, process_frame)

    # Muat data wajah dari database
    cursor.execute("SELECT id, name, image_path FROM users")
    known_encodings = []
    known_names = []
    known_user_ids = []
    for user_id, name, image_path in cursor.fetchall():
        img = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(name)
            known_user_ids.append(user_id)

    mark_window = tk.Toplevel(root)
    mark_window.title("Absensi Wajah")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        messagebox.showerror("Error", "Kamera tidak dapat diakses. Pastikan kamera terhubung dan tidak digunakan oleh aplikasi lain.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_widget = tk.Label(mark_window)
    frame_widget.pack()

    frame_widget.after(10, process_frame)

# Fungsi untuk melihat laporan
def view_report():
    report_window = tk.Toplevel(root)
    report_window.title("Laporan Kehadiran")

    tree = ttk.Treeview(report_window, columns=("ID", "Nama", "Tanggal", "Waktu"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nama", text="Nama")
    tree.heading("Tanggal", text="Tanggal")
    tree.heading("Waktu", text="Waktu")
    tree.pack(fill=tk.BOTH, expand=True)

    cursor.execute("""
        SELECT a.id, u.name, a.date, a.time 
        FROM attendance a 
        JOIN users u ON a.user_id = u.id
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

# Menu utama
def create_main_menu():
    global root
    root = tk.Tk()
    root.title("Aplikasi Absensi Wajah")
    root.geometry("800x600")
    root.configure(bg="#f8f9fa")

    # Heading
    tk.Label(root, text="Aplikasi Absensi Wajah", font=("Arial", 24, "bold"), bg="#f8f9fa", fg="#343a40").pack(pady=20)

    # Menu vertikal
    menu_frame = tk.Frame(root, bg="#f8f9fa")
    menu_frame.pack(expand=True)

    # Load icons
    record_icon = Image.open("icons/record.png").resize((30, 30))
    record_icon = ImageTk.PhotoImage(record_icon)

    attendance_icon = Image.open("icons/attendance.png").resize((30, 30))
    attendance_icon = ImageTk.PhotoImage(attendance_icon)

    report_icon = Image.open("icons/report.png").resize((30, 30))
    report_icon = ImageTk.PhotoImage(report_icon)

    exit_icon = Image.open("icons/exit.png").resize((30, 30))
    exit_icon = ImageTk.PhotoImage(exit_icon)

    def add_menu_button(text, command, icon, bg_color, fg_color):
        btn = tk.Button(
            menu_frame,
            text=text,
            image=icon,
            compound="left",  # Menempatkan ikon di kiri teks
            command=command,
            font=("Arial", 16),
            bg=bg_color,
            fg=fg_color,
            activebackground=fg_color,
            activeforeground=bg_color,
            relief="flat",
            padx=20,
            pady=10
        )
        btn.pack(fill="x", pady=10)
        return btn

    # Tambahkan tombol menu dengan ikon
    add_menu_button("Rekam Wajah", record_face, record_icon, "#007bff", "white")
    add_menu_button("Absensi", mark_attendance, attendance_icon, "#28a745", "white")
    add_menu_button("Laporan", view_report, report_icon, "#ffc107", "black")
    add_menu_button("Keluar", root.destroy, exit_icon, "#dc3545", "white")

    # Simpan referensi ikon agar tidak dihapus oleh garbage collector
    root.record_icon = record_icon
    root.attendance_icon = attendance_icon
    root.report_icon = report_icon
    root.exit_icon = exit_icon

    root.mainloop()

# Jalankan aplikasi
create_main_menu()
