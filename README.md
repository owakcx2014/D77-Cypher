![D77 Banner](https://github.com/owakcx2014/D77-Cypher/blob/main/d77.png?raw=true)
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

## Installation Guid

### On windows:

1. Download The Windows `.Zip` file From [Releases](https://github.com/owakcx2014/D77-Cypher/releases)
2. Unzip it then install D77 From `D77_Setup.exe` File
3. Start D77 Cypher and Enjoy Cyphering!

### On Linux

1. Download The Linux `.Zip` File From [Releases](https://github.com/owakcx2014/D77-Cypher/releases)
2. Unzip it then install it from `install.sh` File
3. open Terminal then Run `cd {file dirictory}` then run `./install.sh`
4. Start D77 Cypher and Enjoy Cyphering!

---

## 🚀 Quick Start & Usage

Run the compiled executable or script to enter the **D77 Interactive Shell**:

```cmd/bash
D77
```
Or run the app from the Start Menu

> [!TIP]
> It's much better to use the app if you are on Windows!
---

## 1. File Cipher Options

```text
d77 -e [loops] <A.txt>         (Encrypt file in-place)
d77 -E [loops] <A.txt> <B.txt>   (Encrypt to a new file)
d77 -d [loops] <B.txt>         (Decrypt file in-place)
d77 -D [loops] <B.txt> <A.txt>   (Decrypt to a new file)
d77 -Ec [loops] <A.txt> <B.d77>  (Encrypt & change file extension and name)
d77 -Dc [loops] <B.d77> <A.dec>  (Decrypt & change file extension and name)
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
[+] Encrypted Result: 91vel3pb2PveCiVleltdSA==

D77/~/desktop> [91vel3pb2PveCiVleltdSA==]
[+] Decrypted Result: Hello World!
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
