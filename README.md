# 🔒 D77 Cipher Tool

An advanced, military-grade interactive CLI cipher tool and custom shell written in Python. D77 allows users to encrypt and decrypt files or text seamlessly using an enhanced dynamic indexing algorithm, with zero external dependencies

---
## ✨ Features

- 💻 Custom Interactive Shell
- ⛓️ Multi-Layer Encryption
- ⚡ Quick Text Cipher
- 📂 Extension Switcher
- 🛡️ Robust Text Parsing
- 🌍 Full UTF-8 Support

---

## 🚀 Quick Start & Usage

Run the compiled executable or script to enter the **D77 Interactive Shell**:

```cmd
D77
```
Or run the app from the Start Menu

> [!TIP]
> It's much better to use the app if you are on Windows!
---

## 1. File Cipher Options

```text
d77 -e [loops] <file>         (Encrypt file in-place)
d77 -E [loops] <file> <out>   (Encrypt to a new file)
d77 -d [loops] <file>         (Decrypt file in-place)
d77 -D [loops] <file> <out>   (Decrypt to a new file)
d77 -Ec [loops] <file> <out>  (Encrypt & change file extension and name)
d77 -Dc [loops] <file> <out>  (Decrypt & change file extension and name)
```

### Example

```bash
-e 4 "my secret file.txt"
```

### Example without En/Decrypt loop 

```bash
-e "my secret file.txt"
-d errors.log
```
---

## 2. Instant Text Cipher (No Files Required)

### Encrypt
Wrap your text inside normal brackets:

```text
(hello world)
```

### Decrypt
Wrap encrypted text inside square brackets:

```text
[encrypted_text]
```

### Example

```text
D77/~/desktop> (hello world)
[+] Encrypted Result: »#¼...

D77/~/desktop> [»#¼...]
[+] Decrypted Result: hello world
```

---

## 📢 Pro Tips

- Use quotes for paths with spaces:
  ```text
  "my file.txt"
  ```

- Navigate directories using:
  ```bash
  cd ~/desktop
  ```

- Linux-like commands supported:
  ```bash
  ls
  cat
  rm
  mv
  cp
  ```

---

## 🛠️ Compilation

Build a standalone executable using PyInstaller:

```bash
pyinstaller --onefile --icon=d77.ico d77.py
```

---

## 📄 License

MIT License

---

Developed with 💻 and 🧠 by IDK.
