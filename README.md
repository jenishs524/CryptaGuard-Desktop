# Symmetric Cryptography & Authenticated Encryption Tool

A modern, high-security desktop application for symmetric key encryption and decryption built with Python, PyCryptodome, and Tkinter.

The application utilizes **AES-GCM** (Galois/Counter Mode) to ensure both **data confidentiality** and **data integrity/authenticity** for text messages and files. It features user authentication, flexible key generation (hex keys or PBKDF2 passphrase derivation), a dark-mode GUI, real-time activity logging, and an interactive cryptographic workflow diagram.

---

## 📌 Key Features

- **Authenticated Encryption (AES-GCM)**:
  - Supports **128-bit**, **192-bit**, and **256-bit** symmetric encryption.
  - Uses 12-byte random nonces and 16-byte authentication tags to prevent data tampering.
- **Flexible Key Management**:
  - **Hex Key Mode**: Enter custom hex keys or generate cryptographically secure random keys with a single click.
  - **Password Derivation Mode (PBKDF2)**: Derive cryptographic keys from passphrases using PBKDF2-HMAC-SHA256, custom/random salts, and configurable iterations (default: 100,000).
- **Message & File Security**:
  - **Text Mode**: Encrypt text into Base64-encoded strings or decrypt Base64 ciphertexts back to plaintext with one-click clipboard copying.
  - **File Mode**: Securely encrypt and decrypt any file format (documents, images, videos, archives) directly on disk.
- **User Authentication System**:
  - Built-in registration and login interface backed by an SQLite database (`users.db`) using SHA-256 password hashing.
- **Interactive Cryptographic Flow Diagram**:
  - Dynamic GUI Canvas diagram illustrating the symmetric encryption and decryption workflow in real time.
- **Real-Time Activity Logging**:
  - Embedded execution log displaying timestamped status updates and system events.
- **Modern Dark Mode UI**:
  - Sleek visual theme crafted using Tkinter and custom `ttk` styling.

---

## 🧠 How It Works

### Cryptographic Architecture
Symmetric encryption uses the **same secret key** for both encryption and decryption.

```
+-----------------+      Encrypt      +-----------------+      Decrypt      +-----------------+
|  Original Text  | ----------------> |   Cipher Text   | ----------------> |  Original Text  |
+-----------------+                   +-----------------+                   +-----------------+
         ^                                     ^                                     ^
         |                                     |                                     |
         +--------------- [ Symmetric Key ] ---+-------------------------------------+
```

### Encryption Process
1. **Key Acquisition**:
   - **Hex Key**: Validates key length according to selected size (16, 24, or 32 bytes).
   - **PBKDF2 Derivation**: Passphrase + 16-byte salt derived through `PBKDF2` using `HMAC-SHA256` and user-defined iteration count.
2. **AES-GCM Initialization**:
   - Generates a cryptographically secure 12-byte initialization vector (`nonce`).
3. **Data Protection & Tag Generation**:
   - Encrypts payload and generates a 16-byte authentication `tag`.
   - Data structure: `nonce (12B) + ciphertext + tag (16B)`.
   - Text output is Base64-encoded; files are stored in binary format.

### Decryption & Verification Process
1. Payload is split into `nonce` (first 12 bytes), `tag` (last 16 bytes), and intermediate `ciphertext`.
2. AES-GCM verifies the authentication tag against the secret key.
3. If verified, the original data is returned; if tampered with or incorrect key is provided, authentication fails and errors are raised.

---

## 🛠️ Prerequisites & Installation

### Prerequisites
- **Python 3.8+**
- **PyCryptodome** (`pip install pycryptodome`)
- **Tkinter** (included with standard Python installations; on Ubuntu/Debian: `sudo apt install python3-tk`)

### Installation Steps

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/your-username/Symmetric-Cryptography-Tool.git
   cd Symmetric-Cryptography-Tool
   ```

2. **Install Required Packages**:
   ```bash
   pip install pycryptodome
   ```

3. **Run the Application**:
   ```bash
   python semmitic.py
   ```

---

## 🚀 Step-by-Step Usage Guide

### 1. User Registration & Login
- Launch the application to open the **Login / Register** screen.
- Click **Register**, enter a username and password (min. 4 characters), and submit.
- Switch to **Login**, enter your credentials, and access the application main interface.

### 2. Key Setup
- Select key length: **128 bits**, **192 bits**, or **256 bits** (default: 256 bits).
- Select Key Source:
  - **Hex Key**: Click **Generate** to produce a random hex key or input your own.
  - **Password (PBKDF2)**: Enter a password, click **Gen Salt** to generate a 16-byte salt, and set iterations (default: 100,000).

### 3. Text Message Encryption & Decryption
1. Go to the **Message** tab.
2. Enter plain text into **Input Text**.
3. Click **🔒 Encrypt**. The Base64 ciphertext appears in **Output Text**.
4. To decrypt: paste the Base64 ciphertext into **Input Text**, ensure the correct key parameters are selected, and click **🔓 Decrypt**.
5. Click **Copy Output** to quickly copy results to clipboard.

### 4. File Encryption & Decryption
1. Go to the **File** tab.
2. Click **Browse** to select the target **Input File**.
3. Click **Save As** to specify the destination **Output File** path.
4. Click **🔒 Encrypt File** to create an encrypted binary file, or **🔓 Decrypt File** to restore original contents.

---

## 📂 File & Directory Structure

```
.
├── semmitic.py         # Main GUI application script (Tkinter + PyCryptodome + SQLite)
├── users.db            # SQLite database storing user authentication records
├── crypto_log.txt      # Log file output for system events
├── README.md           # Technical documentation and usage instructions
└── LICENSE             # Software license details
```

---

## ⚠️ Security Guidelines

- **Protect Your Keys**: AES security relies entirely on keeping keys secret.
- **Store Your Salt & Iterations**: When using PBKDF2, you must use the same salt and iteration count to reconstruct the key during decryption.
- **Integrity Guarantee**: AES-GCM guarantees data integrity; any modification to encrypted data will prevent decryption and throw an error.
