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

## Installation Guide

### On Windows:

1. Download the Windows `.Zip` file from [Releases](https://github.com/owakcx2014/D77-Cypher/releases)
2. Unzip it, then install D77 from the `D77_Setup.exe` File
3. Start D77 Cypher and Enjoy Cyphering!

### On Linux

1. Download the Linux `.Zip` File from [Releases](https://github.com/owakcx2014/D77-Cypher/releases)
2. Unzip it, then install it from the `install.sh` File
3. open Terminal then Run `cd {file directory}` then run `./install.sh`
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

## Uninstallation:

### on Windows:

1. From the Control Panel or settings
2. You can also Uninstall From start menu folder `Uninstall D77 Cipher`

### On Linux:

1. Use the `uninstall.sh` file by running `cd /path/to/your/file` then run `./uninstall.sh`
2. You can also run `sudo rm /usr/local/bin/d77`

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

## 😂 Joke for Fun!

try to type "say wallahi bro"

---

## 😔 Facts About Developer:

I'm 11 years old. My PC is cooked (2008 Model), I really need a new PC, but I don't have money. I'm from Egypt but living in Saudi Arabia, I'm using Linux, and I use Arch BTW

---

## 📄 License

MIT License

---

## Support Developer:

Please put a star on this project and see my other projects in my Account on GitHub

Contact me: owaxck2014@gmail.com

> [!NOTE]
> ✍️ Note: I used Grammarly to help me polish the English side of this documentation, but unfortunately, it doesn't support Arabic due to its rich complexity (which makes me feel both proud and a bit frustrated at the same time! 👑❤️).

Developed with 💻, 🧠, and pure open-source passion by Abdullah Nagy.
