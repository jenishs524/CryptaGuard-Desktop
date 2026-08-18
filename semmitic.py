"""
Symmetric Encryption and Decryption Tool
- AES-GCM (authenticated) with 128/192/256 bit keys
- Key from hex OR password (PBKDF2)
- Message & File encryption/decryption
- Login/Register (SQLite, SHA-256)
- Dark theme, activity log, professional workflow diagram
"""
import base64
import hashlib
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

# ===================== DATABASE =====================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

conn = init_db()

# ===================== APPLICATION =====================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Symmetric Encryption and Decryption Tool – SECRET DOUBLE DETECTORS")
        self.root.geometry("720x680")
        self.root.resizable(True, True)

        self.bg = "#1e1e1e"
        self.fg = "#dcdcdc"
        self.entry_bg = "#2d2d2d"
        self.btn_bg = "#3c3c3c"
        self.accent = "#0e639c"
        self.root.configure(bg=self.bg)

        self._setup_styles()
        self.login_frame = tk.Frame(root, bg=self.bg)
        self.main_frame = tk.Frame(root, bg=self.bg)
        self._build_login()
        self._build_main()
        self.show_login()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=self.bg, foreground=self.fg, fieldbackground=self.entry_bg)
        style.configure("TLabel", background=self.bg, foreground=self.fg)
        style.configure("TEntry", fieldbackground=self.entry_bg, insertcolor=self.fg)
        style.configure("TButton", background=self.btn_bg, foreground="white",
                        borderwidth=0, focusthickness=0, padding=(10, 5))
        style.map("TButton", background=[("active", "#505050")])
        style.configure("TLabelframe", background=self.bg, foreground=self.fg)
        style.configure("TLabelframe.Label", background=self.bg, foreground=self.fg)
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure("TNotebook.Tab", background="#2d2d2d", foreground="white",
                        padding=[12, 6], borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", self.accent)],
                  foreground=[("selected", "white")])
        style.configure("TCombobox", foreground=self.fg, fieldbackground=self.entry_bg,
                        background=self.bg, arrowcolor=self.fg)

    # ---------- LOGIN / REGISTER ----------
    def _build_login(self):
        frame = tk.Frame(self.login_frame, bg=self.bg)
        frame.pack(expand=True)

        top = tk.Frame(frame, bg=self.bg)
        top.pack(pady=10)
        self.login_btn = tk.Button(top, text="Login", bg=self.accent, fg="white",
                                   font=("Arial", 10, "bold"), relief="flat",
                                   command=self.show_login_tab)
        self.login_btn.pack(side="left", padx=5)
        self.reg_btn = tk.Button(top, text="Register", bg=self.btn_bg, fg="white",
                                 font=("Arial", 10), relief="flat",
                                 command=self.show_reg_tab)
        self.reg_btn.pack(side="left", padx=5)

        self.login_form = tk.Frame(frame, bg=self.bg)
        ttk.Label(self.login_form, text="Username:").grid(row=0, column=0, sticky="e", pady=5)
        self.login_user = ttk.Entry(self.login_form, width=25)
        self.login_user.grid(row=0, column=1, pady=5, padx=5)
        ttk.Label(self.login_form, text="Password:").grid(row=1, column=0, sticky="e", pady=5)
        self.login_pass = ttk.Entry(self.login_form, width=25, show="*")
        self.login_pass.grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(self.login_form, text="Login", command=self.do_login).grid(row=2, column=0, columnspan=2, pady=15)
        self.login_form.pack()

        self.reg_form = tk.Frame(frame, bg=self.bg)
        ttk.Label(self.reg_form, text="Username:").grid(row=0, column=0, sticky="e", pady=5)
        self.reg_user = ttk.Entry(self.reg_form, width=25)
        self.reg_user.grid(row=0, column=1, pady=5, padx=5)
        ttk.Label(self.reg_form, text="Password:").grid(row=1, column=0, sticky="e", pady=5)
        self.reg_pass = ttk.Entry(self.reg_form, width=25, show="*")
        self.reg_pass.grid(row=1, column=1, pady=5, padx=5)
        ttk.Label(self.reg_form, text="Confirm Password:").grid(row=2, column=0, sticky="e", pady=5)
        self.reg_confirm = ttk.Entry(self.reg_form, width=25, show="*")
        self.reg_confirm.grid(row=2, column=1, pady=5, padx=5)
        ttk.Button(self.reg_form, text="Register", command=self.do_register).grid(row=3, column=0, columnspan=2, pady=15)

        self.login_status = tk.Label(frame, text="", fg="#e06c75", bg=self.bg, font=("Arial", 9))
        self.login_status.pack(pady=10)

    def show_login_tab(self):
        self.reg_form.pack_forget()
        self.login_form.pack()
        self.login_btn.configure(bg=self.accent)
        self.reg_btn.configure(bg=self.btn_bg)

    def show_reg_tab(self):
        self.login_form.pack_forget()
        self.reg_form.pack()
        self.reg_btn.configure(bg=self.accent)
        self.login_btn.configure(bg=self.btn_bg)

    def do_login(self):
        user = self.login_user.get().strip()
        pwd = self.login_pass.get().strip()
        if not user or not pwd:
            self.login_status.config(text="Please enter username and password.")
            return
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username=?", (user,))
        row = cur.fetchone()
        if row is None:
            self.login_status.config(text="Username not registered.")
            return
        if row[0] == hashlib.sha256(pwd.encode()).hexdigest():
            self.current_user = user
            self._log(f"User '{user}' logged in")
            self.show_main()
        else:
            self.login_status.config(text="Invalid password.")

    def do_register(self):
        user = self.reg_user.get().strip()
        pwd = self.reg_pass.get().strip()
        conf = self.reg_confirm.get().strip()
        if not user or not pwd or not conf:
            self.login_status.config(text="Please fill all fields.")
            return
        if pwd != conf:
            self.login_status.config(text="Passwords do not match.")
            return
        if len(pwd) < 4:
            self.login_status.config(text="Password too short (min 4 characters).")
            return
        try:
            cur = conn.cursor()
            h = hashlib.sha256(pwd.encode()).hexdigest()
            cur.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", (user, h))
            conn.commit()
            self._log(f"New user registered: '{user}'")
            self.login_status.config(fg="#98c379", text="Registration successful! You can now login.")
            self.show_login_tab()
            self.reg_user.delete(0, "end")
            self.reg_pass.delete(0, "end")
            self.reg_confirm.delete(0, "end")
        except sqlite3.IntegrityError:
            self.login_status.config(text="Username already exists.")

    # ---------- MAIN (after login) ----------
    def _build_main(self):
        main = self.main_frame

        top = tk.Frame(main, bg=self.bg)
        top.pack(fill="x", padx=10, pady=5)
        tk.Label(top, text="Symmetric Encryption and Decryption Tool", bg=self.bg, fg=self.fg,
                 font=("Arial", 12, "bold")).pack(side="left")
        tk.Button(top, text="Logout", bg="#c0392b", fg="white", relief="flat",
                  command=self.logout).pack(side="right")

        # ---- PROFESSIONAL WORKFLOW DIAGRAM ----
        self.canvas = tk.Canvas(main, bg=self.bg, height=140, bd=0, highlightthickness=0)
        self.canvas.pack(fill="x", padx=10, pady=(5,0))
        self.canvas.bind("<Configure>", self._draw_flow)

        # Key configuration
        key_frame = tk.LabelFrame(main, text="Key Configuration", bg=self.bg, fg=self.fg,
                                  font=("Arial", 10, "bold"), padx=10, pady=10)
        key_frame.pack(fill="x", padx=10, pady=10)

        self.key_mode = tk.StringVar(value="hex")
        tk.Radiobutton(key_frame, text="Hex Key", variable=self.key_mode, value="hex",
                       bg=self.bg, fg=self.fg, selectcolor=self.bg,
                       activebackground=self.bg, activeforeground=self.fg,
                       command=self._toggle_key_mode).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(key_frame, text="Password (PBKDF2)", variable=self.key_mode, value="password",
                       bg=self.bg, fg=self.fg, selectcolor=self.bg,
                       activebackground=self.bg, activeforeground=self.fg,
                       command=self._toggle_key_mode).grid(row=0, column=1, sticky="w", padx=10)

        ttk.Label(key_frame, text="Key Size:").grid(row=0, column=2, sticky="e", padx=(20,5))
        self.key_size_var = tk.StringVar(value="256 bits")
        sizes = ttk.Combobox(key_frame, textvariable=self.key_size_var,
                             values=["128 bits", "192 bits", "256 bits"], state="readonly", width=10)
        sizes.grid(row=0, column=3, sticky="w")

        self.hex_frame = tk.Frame(key_frame, bg=self.bg)
        self.hex_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        ttk.Label(self.hex_frame, text="Hex Key:").pack(side="left")
        self.key_entry = ttk.Entry(self.hex_frame, width=40)
        self.key_entry.pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(self.hex_frame, text="Generate", command=self.generate_key).pack(side="left", padx=5)

        self.pwd_frame = tk.Frame(key_frame, bg=self.bg)
        self.pwd_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=5)
        ttk.Label(self.pwd_frame, text="Password:").grid(row=0, column=0, sticky="e", pady=2)
        self.pwd_entry = ttk.Entry(self.pwd_frame, width=25, show="*")
        self.pwd_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(self.pwd_frame, text="Salt (hex, optional):").grid(row=0, column=2, sticky="e", pady=2)
        self.salt_entry = ttk.Entry(self.pwd_frame, width=30)
        self.salt_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        ttk.Button(self.pwd_frame, text="Gen Salt", command=self._gen_salt).grid(row=0, column=4, padx=5)
        ttk.Label(self.pwd_frame, text="Iterations:").grid(row=1, column=0, sticky="e", pady=2)
        self.iter_spin = tk.Spinbox(self.pwd_frame, from_=10000, to=500000, increment=10000,
                                    width=10, bg=self.entry_bg, fg=self.fg, buttonbackground=self.btn_bg)
        self.iter_spin.delete(0, "end")
        self.iter_spin.insert(0, "100000")
        self.iter_spin.grid(row=1, column=1, sticky="w", pady=2, padx=5)

        self._toggle_key_mode()

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.msg_tab = tk.Frame(self.notebook, bg=self.bg)
        self.file_tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(self.msg_tab, text="Message")
        self.notebook.add(self.file_tab, text="File")

        self._build_message_tab()
        self._build_file_tab()

        log_frame = tk.LabelFrame(main, text="Activity Log", bg=self.bg, fg=self.fg)
        log_frame.pack(fill="x", padx=10, pady=(0,10))
        self.log_text = tk.Text(log_frame, height=4, bg="#1a1a1a", fg=self.fg,
                                wrap="word", relief="flat", borderwidth=0, font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    # ========== PROFESSIONAL FLOW CHART ==========
    def _draw_flow(self, event=None):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 100: return

        # ---- Title & Branding ----
        c.create_text(w/2, 10, text="Symmetric Key Encryption", fill="#ffffff",
                      font=("Arial", 11, "bold"))
        c.create_text(w/2, 26, text="SECRET DOUBLE DETECTORS", fill="#888888",
                      font=("Arial", 8, "italic"))

        # ---- Colors ----
        color_plaintext = "#2e7d32"   # green
        color_encrypt = "#1565c0"     # blue
        color_cipher = "#ef6c00"      # orange
        color_decrypt = "#1565c0"     # blue
        color_key = "#ffca28"         # yellow, text will be black
        arrow_color = "#b0bec5"
        text_fg = "#ffffff"

        # ---- Layout ----
        box_w = 85
        box_h = 30
        gap = 25
        total_width = 5 * box_w + 4 * gap
        start_x = (w - total_width) / 2
        y_top = 40
        y_bottom = y_top + 60   # for key box

        # Box definitions
        boxes = [
            (start_x, y_top, start_x + box_w, y_top + box_h, "Original Text", color_plaintext),
            (start_x + box_w + gap, y_top, start_x + 2*box_w + gap, y_top + box_h, "Encryption", color_encrypt),
            (start_x + 2*box_w + 2*gap, y_top, start_x + 3*box_w + 2*gap, y_top + box_h, "Cipher Text", color_cipher),
            (start_x + 3*box_w + 3*gap, y_top, start_x + 4*box_w + 3*gap, y_top + box_h, "Decryption", color_decrypt),
            (start_x + 4*box_w + 4*gap, y_top, start_x + 5*box_w + 4*gap, y_top + box_h, "Original Text", color_plaintext),
        ]

        # Draw boxes
        for (x1, y1, x2, y2, label, color) in boxes:
            c.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ffffff", width=1, activedash=(2,2))
            c.create_text((x1+x2)/2, (y1+y2)/2, text=label, fill=text_fg,
                          font=("Arial", 9, "bold"))

        # Arrows and labels
        arrow_y = y_top + box_h/2
        for i in range(len(boxes)-1):
            x_from = boxes[i][2]
            x_to = boxes[i+1][0]
            c.create_line(x_from, arrow_y, x_to, arrow_y, fill=arrow_color, width=2,
                          arrow="last", arrowshape=(10,12,6))
            # Label above arrow
            if i == 0 or i == 3:
                lbl = "Encrypt" if i == 0 else "Decrypt"
                c.create_text((x_from+x_to)/2, arrow_y - 12, text=lbl, fill="#aaaaaa",
                              font=("Arial", 7, "italic"))

        # ---- Symmetric Key Box ----
        key_w = 80
        key_h = 28
        key_x = (w - key_w) / 2
        key_y = y_bottom + 10
        c.create_rectangle(key_x, key_y, key_x + key_w, key_y + key_h,
                           fill=color_key, outline="#ffffff", width=1)
        c.create_text(key_x + key_w/2, key_y + key_h/2, text="Symmetric Key",
                      fill="#000000", font=("Arial", 8, "bold"))

        # Connect key to Encryption and Decryption boxes
        enc_center_x = (boxes[1][0] + boxes[1][2]) / 2
        dec_center_x = (boxes[3][0] + boxes[3][2]) / 2
        # from key top to encryption bottom
        c.create_line(key_x + key_w/2, key_y, enc_center_x, y_top + box_h,
                      fill=color_key, width=2, arrow="last", arrowshape=(8,10,4))
        # from key top to decryption bottom
        c.create_line(key_x + key_w/2, key_y, dec_center_x, y_top + box_h,
                      fill=color_key, width=2, arrow="last", arrowshape=(8,10,4))

    # ----- key management (unchanged) -----
    def _toggle_key_mode(self):
        if self.key_mode.get() == "hex":
            self.pwd_frame.grid_remove()
            self.hex_frame.grid()
        else:
            self.hex_frame.grid_remove()
            self.pwd_frame.grid()

    def generate_key(self):
        key_bytes = self._get_key_size_bytes()
        key = get_random_bytes(key_bytes)
        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, key.hex())
        self._log("Random key generated")

    def _gen_salt(self):
        salt = get_random_bytes(16)
        self.salt_entry.delete(0, "end")
        self.salt_entry.insert(0, salt.hex())

    def _get_key_size_bytes(self):
        size_str = self.key_size_var.get()
        if "128" in size_str: return 16
        elif "192" in size_str: return 24
        return 32

    def _get_derived_key(self):
        password = self.pwd_entry.get().strip()
        if not password:
            self._log("Error: no password entered")
            messagebox.showerror("Key Error", "Enter a password for key derivation.")
            return None
        salt_hex = self.salt_entry.get().strip()
        if salt_hex:
            try:
                salt = bytes.fromhex(salt_hex)
            except ValueError:
                self._log("Error: invalid salt hex")
                messagebox.showerror("Key Error", "Invalid salt hex.")
                return None
        else:
            salt = get_random_bytes(16)
            self.salt_entry.delete(0, "end")
            self.salt_entry.insert(0, salt.hex())
        try:
            iterations = int(self.iter_spin.get())
        except ValueError:
            iterations = 100000
        key_bytes = self._get_key_size_bytes()
        return PBKDF2(password, salt, dkLen=key_bytes, count=iterations, hmac_hash_module=SHA256)

    def _get_key(self):
        if self.key_mode.get() == "hex":
            key_hex = self.key_entry.get().strip()
            if not key_hex:
                self._log("Error: no hex key")
                messagebox.showerror("Key Error", "Enter a hex key or generate one.")
                return None
            try:
                key = bytes.fromhex(key_hex)
            except ValueError:
                self._log("Error: invalid hex key")
                messagebox.showerror("Key Error", "Invalid hex string.")
                return None
            expected = self._get_key_size_bytes()
            if len(key) != expected:
                self._log(f"Error: key length mismatch (got {len(key)} bytes, expected {expected})")
                messagebox.showerror("Key Error", f"Key must be exactly {expected*2} hex characters ({expected*8} bits).")
                return None
            return key
        else:
            return self._get_derived_key()

    # ----- AES-GCM -----
    @staticmethod
    def _encrypt_gcm(plaintext: bytes, key: bytes) -> bytes:
        nonce = get_random_bytes(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return nonce + ciphertext + tag

    @staticmethod
    def _decrypt_gcm(data: bytes, key: bytes) -> bytes:
        if len(data) < 28:
            raise ValueError("Ciphertext too short.")
        nonce = data[:12]
        tag = data[-16:]
        ciphertext = data[12:-16]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

    # ----- message tab ------
    def _build_message_tab(self):
        tab = self.msg_tab
        ttk.Label(tab, text="Input Text:").pack(anchor="w", padx=10, pady=(5,0))
        self.msg_input = tk.Text(tab, height=6, bg=self.entry_bg, fg=self.fg, insertbackground="white",
                                 relief="flat", borderwidth=2)
        self.msg_input.pack(fill="x", padx=10, pady=5)

        btn_frame = tk.Frame(tab, bg=self.bg)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="🔒 Encrypt", command=self.encrypt_message).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔓 Decrypt", command=self.decrypt_message).pack(side="left", padx=5)

        ttk.Label(tab, text="Output Text:").pack(anchor="w", padx=10, pady=(5,0))
        self.msg_output = tk.Text(tab, height=6, bg="#1a1a1a", fg="#98c379", insertbackground="white",
                                  relief="flat", borderwidth=2)
        self.msg_output.pack(fill="x", padx=10, pady=5)
        ttk.Button(tab, text="Copy Output", command=self._copy_msg_output).pack(pady=5)

    def encrypt_message(self):
        plain = self.msg_input.get("1.0", "end-1c").strip()
        if not plain:
            self._log("Encrypt: no plaintext entered")
            return
        key = self._get_key()
        if key is None: return
        try:
            encrypted = self._encrypt_gcm(plain.encode("utf-8"), key)
            b64 = base64.b64encode(encrypted).decode()
            self.msg_output.delete("1.0", "end")
            self.msg_output.insert("1.0", b64)
            self._log("Message encrypted successfully")
        except Exception as e:
            self._log(f"Encryption failed: {e}")
            messagebox.showerror("Error", f"Encryption failed: {e}")

    def decrypt_message(self):
        cipher_b64 = self.msg_input.get("1.0", "end-1c").strip()
        if not cipher_b64:
            self._log("Decrypt: no ciphertext entered")
            return
        key = self._get_key()
        if key is None: return
        try:
            raw = base64.b64decode(cipher_b64)
            plain = self._decrypt_gcm(raw, key).decode("utf-8")
            self.msg_output.delete("1.0", "end")
            self.msg_output.insert("1.0", plain)
            self._log("Message decrypted successfully")
        except Exception as e:
            self._log(f"Decryption failed: {e}")
            messagebox.showerror("Error", f"Decryption failed: {e}\nCheck key or ciphertext integrity.")

    def _copy_msg_output(self):
        txt = self.msg_output.get("1.0", "end-1c").strip()
        if txt:
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self._log("Output copied to clipboard")

    # ----- file tab ------
    def _build_file_tab(self):
        tab = self.file_tab
        ttk.Label(tab, text="Input File:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.file_in_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.file_in_var, width=40).grid(row=0, column=1, padx=5, sticky="we")
        ttk.Button(tab, text="Browse", command=self._browse_infile).grid(row=0, column=2, padx=5)

        ttk.Label(tab, text="Output File:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.file_out_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.file_out_var, width=40).grid(row=1, column=1, padx=5, sticky="we")
        ttk.Button(tab, text="Save As", command=self._browse_outfile).grid(row=1, column=2, padx=5)

        btn_frame = tk.Frame(tab, bg=self.bg)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=15)
        ttk.Button(btn_frame, text="🔒 Encrypt File", command=self.encrypt_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔓 Decrypt File", command=self.decrypt_file).pack(side="left", padx=5)
        tab.columnconfigure(1, weight=1)

    def _browse_infile(self):
        path = filedialog.askopenfilename()
        if path: self.file_in_var.set(path)

    def _browse_outfile(self):
        path = filedialog.asksaveasfilename()
        if path: self.file_out_var.set(path)

    def encrypt_file(self):
        in_path = self.file_in_var.get()
        out_path = self.file_out_var.get()
        if not in_path or not out_path:
            self._log("File encrypt: missing paths")
            return
        key = self._get_key()
        if key is None: return
        try:
            with open(in_path, "rb") as f: plain = f.read()
            encrypted = self._encrypt_gcm(plain, key)
            with open(out_path, "wb") as f: f.write(encrypted)
            self._log(f"File encrypted: {in_path} -> {out_path}")
            messagebox.showinfo("Success", "File encrypted successfully.")
        except Exception as e:
            self._log(f"File encryption failed: {e}")
            messagebox.showerror("Error", f"File encryption failed: {e}")

    def decrypt_file(self):
        in_path = self.file_in_var.get()
        out_path = self.file_out_var.get()
        if not in_path or not out_path:
            self._log("File decrypt: missing paths")
            return
        key = self._get_key()
        if key is None: return
        try:
            with open(in_path, "rb") as f: data = f.read()
            plain = self._decrypt_gcm(data, key)
            with open(out_path, "wb") as f: f.write(plain)
            self._log(f"File decrypted: {in_path} -> {out_path}")
            messagebox.showinfo("Success", "File decrypted successfully.")
        except Exception as e:
            self._log(f"File decryption failed: {e}")
            messagebox.showerror("Error", f"File decryption failed: {e}")

    # ----- frame switching -----
    def show_login(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(expand=True, fill="both")

    def show_main(self):
        self.login_frame.pack_forget()
        self.main_frame.pack(expand=True, fill="both")
        self.login_user.delete(0, "end")
        self.login_pass.delete(0, "end")
        self._log("Logged in")
        self.root.after(10, self._draw_flow)

    def logout(self):
        self.current_user = None
        self._log("Logged out")
        self.show_login()

    def _log(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        line = f"[{now}] {msg}\n"
        def write():
            self.log_text.insert("end", line)
            self.log_text.see("end")
        self.root.after(0, write)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()