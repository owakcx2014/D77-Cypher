import logging
import sys
import os
import shlex
import base64

# ============================================================
#  D77 Cipher Tool v2.2 - Stable Edition
# ============================================================
#  إصلاحات v2.2:
#  8. d77_logic ترفع Exception بدل ما تُعيد string خطأ
#     → الملف لا يُكتب أبداً عند فشل العملية
#  9. handle_direct_commands يلتقط الخطأ ويوقف الكتابة
#  10. _write_file تكتب في ملف مؤقت أولاً ثم تستبدل الأصلي
#      (atomic write) لحماية الملف من التلف عند انقطاع مفاجئ
#  11. حد أقصى للـ loops لمنع التجميد
# ============================================================

logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("D77")

KEY       = 77
MAX_LOOPS = 15   # فوق هذا يصبح بطيئاً جداً


def _build_decrypt_lookup(key: int, loop: int) -> dict[int, list[int]]:
    lookup: dict[int, list[int]] = {}
    for orig_b in range(256):
        transformed = (orig_b * key + loop) % 256
        lookup.setdefault(transformed, []).append(orig_b)
    return lookup


# FIX #8: ترفع Exception عند الخطأ — لا تُعيد string خطأ أبداً
def d77_logic(text: str, key: int = KEY, mode: str = 'encrypt', loops: int = 1) -> str:
    if mode == 'encrypt':
        current_text = text
        for loop in range(loops):
            b64_bytes    = base64.urlsafe_b64encode(current_text.encode('utf-8'))
            cipher_bytes = bytearray()
            for b in b64_bytes:
                cipher_bytes.append((b * key + loop) % 256)
            current_text = cipher_bytes.decode('latin-1')
        return base64.urlsafe_b64encode(current_text.encode('latin-1')).decode('utf-8')

    else:  # decrypt — لا try/except هنا، الخطأ يصعد للمستدعي
        decoded_bytes = base64.urlsafe_b64decode(text.encode('utf-8'))
        current_text  = decoded_bytes.decode('latin-1')

        for loop in reversed(range(loops)):
            cipher_bytes       = current_text.encode('latin-1')
            original_b64_bytes = bytearray()
            decrypt_lookup     = _build_decrypt_lookup(key, loop)

            for b in cipher_bytes:
                candidates = decrypt_lookup.get(b)
                if not candidates:
                    raise ValueError(
                        f"No reverse candidate for byte {b} at loop={loop}. "
                        "Wrong loops count or corrupted data."
                    )
                original_b64_bytes.append(candidates[0])

            # يرفع UnicodeDecodeError إذا كان عدد loops خاطئاً
            current_text = base64.urlsafe_b64decode(original_b64_bytes).decode('utf-8')

        return current_text


# FIX #10: Atomic write — يكتب مؤقت ثم يستبدل الأصلي
def _write_file(path: str, content: str) -> bool:
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp_path, path)
        return True
    except OSError as e:
        print(f"Error writing '{path}': {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return False


def _read_file(path: str) -> str | None:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        logger.warning("'%s' not UTF-8, falling back to latin-1.", path)
        with open(path, 'r', encoding='latin-1') as f:
            return f.read()
    except OSError as e:
        print(f"File read error: {e}")
        return None


def _apply_extension_change(output_file: str, mode: str) -> str:
    base, ext = os.path.splitext(output_file)
    if mode == 'encrypt':
        return base + '.d77'
    return base if ext.lower() == '.d77' else output_file + '.dec'


def ask_overwrite(file_name: str) -> bool:
    if os.path.exists(file_name):
        try:
            ans = input(f"Warning: '{file_name}' exists! Overwrite? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return False
        if ans != 'y':
            print("Operation cancelled.")
            return False
    return True


# FIX #9: يلتقط Exception من d77_logic → لا يكتب الملف عند الخطأ
def _run_cipher(content: str, mode: str, loops: int) -> str | None:
    try:
        return d77_logic(content, KEY, mode, loops)
    except (ValueError, UnicodeDecodeError) as e:
        print(f"\n✖ Operation failed: {e}")
        print("  → The file was NOT modified.")
        return None
    except Exception as e:
        print(f"\n✖ Unexpected error: {e}")
        print("  → The file was NOT modified.")
        return None


# FIX #11: حد أقصى للـ loops
def _validate_loops(loops: int) -> bool:
    if loops < 1:
        print("Error: loops must be >= 1.")
        return False
    if loops > MAX_LOOPS:
        print(f"Error: loops={loops} exceeds max ({MAX_LOOPS}). High values cause freezing.")
        return False
    return True


def handle_direct_commands(flag: str, args: list[str]):
    loops = 1

    if not args:
        print("Error: file name is required.")
        return

    if args[0].isdigit():
        loops = int(args[0])
        args  = args[1:]

    if not _validate_loops(loops):
        return

    if not args:
        print("Error: file name required after loops count.")
        return

    input_file  = args[0]
    output_file = args[1] if len(args) > 1 else None

    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' does not exist!")
        return

    content = _read_file(input_file)
    if content is None:
        return

    if flag == '-e':
        result = _run_cipher(content, 'encrypt', loops)
        if result and _write_file(input_file, result):
            print(f"✔ Encrypted in-place ({loops} loop(s)).")

    elif flag == '-E':
        if not output_file:
            print("Error: output file required with -E.")
            return
        if not ask_overwrite(output_file):
            return
        result = _run_cipher(content, 'encrypt', loops)
        if result and _write_file(output_file, result):
            print(f"✔ Encrypted ({loops} loop(s)) → {output_file}")

    elif flag == '-Ec':
        if not output_file:
            print("Error: output file required with -Ec.")
            return
        final_output = _apply_extension_change(output_file, 'encrypt')
        if not ask_overwrite(final_output):
            return
        result = _run_cipher(content, 'encrypt', loops)
        if result and _write_file(final_output, result):
            print(f"✔ Encrypted ({loops} loop(s)) → {final_output}")

    elif flag == '-d':
        result = _run_cipher(content, 'decrypt', loops)
        if result and _write_file(input_file, result):
            print(f"✔ Decrypted in-place ({loops} loop(s)).")

    elif flag == '-D':
        if not output_file:
            print("Error: output file required with -D.")
            return
        if not ask_overwrite(output_file):
            return
        result = _run_cipher(content, 'decrypt', loops)
        if result and _write_file(output_file, result):
            print(f"✔ Decrypted ({loops} loop(s)) → {output_file}")

    elif flag == '-Dc':
        if not output_file:
            print("Error: output file required with -Dc.")
            return
        final_output = _apply_extension_change(output_file, 'decrypt')
        if not ask_overwrite(final_output):
            return
        result = _run_cipher(content, 'decrypt', loops)
        if result and _write_file(final_output, result):
            print(f"✔ Decrypted ({loops} loop(s)) → {final_output}")

    else:
        print(f"Error: unknown flag '{flag}'. Use --help.")


def print_usage():
    print(f"""
╔══════════════════════════════════════════════════════════╗
║         D77 Cipher Tool v2.2 - Stable Edition           ║
╚══════════════════════════════════════════════════════════╝
Usage:
  -e  [loops] <file>          Encrypt file in-place
  -E  [loops] <file> <out>    Encrypt to another file
  -Ec [loops] <file> <out>    Encrypt + change extension to .d77
  -d  [loops] <file>          Decrypt file in-place
  -D  [loops] <file> <out>    Decrypt to another file
  -Dc [loops] <file> <out>    Decrypt + restore original extension

  Max loops: {MAX_LOOPS}

💡 Direct text:
  (your text)        → Instant encrypt
  [encrypted text]   → Instant decrypt

Shell: ls/dir, cd, cat, pwd, clear, exit
""")


_WINDOWS_COMMANDS = {'dir', 'cls', 'type', 'copy', 'move', 'del', 'ren', 'md', 'rd'}
_UNIX_COMMANDS    = {'ls', 'clear', 'cat', 'cp', 'mv', 'rm', 'mkdir', 'rmdir',
                     'touch', 'head', 'tail', 'grep', 'find', 'chmod'}
IS_WINDOWS = os.name == 'nt'


def _safe_system(command: str):
    parts    = command.split() if IS_WINDOWS else shlex.split(command)
    if not parts:
        return
    cmd_name = parts[0].lower().lstrip('-')
    allowed  = _WINDOWS_COMMANDS if IS_WINDOWS else _UNIX_COMMANDS
    if cmd_name not in allowed:
        print(f"⚠ '{parts[0]}' not allowed. Allowed: {', '.join(sorted(allowed))}")
        return
    if IS_WINDOWS:
        os.system(f"cmd /c chcp 65001 >nul 2>&1 && cmd /c {command}")
    else:
        os.system(command)


def start_interactive_shell():
    if IS_WINDOWS:
        os.system("chcp 65001 > nul 2>&1")
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

    print_usage()
    print("[+] D77 Interactive Shell. Type 'exit' to quit.\n")
    home_dir = os.path.expanduser("~")

    while True:
        cwd          = os.getcwd()
        display_path = cwd.replace(home_dir, "~").replace("\\", "/")

        try:
            user_input = input(f"D77/{display_path}> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.startswith('(') and user_input.endswith(')'):
            text = user_input[1:-1].strip("'\"")
            if text:
                result = _run_cipher(text, 'encrypt', 1)
                if result:
                    print(f"\n[+] Encrypted:\n{result}\n")
            continue

        if user_input.startswith('[') and user_input.endswith(']'):
            text = user_input[1:-1].strip("'\"")
            if text:
                result = _run_cipher(text, 'decrypt', 1)
                if result:
                    print(f"\n[+] Decrypted:\n{result}\n")
            continue

        try:
            parts = user_input.split() if IS_WINDOWS else shlex.split(user_input)
        except Exception as e:
            print(f"Parse error: {e}")
            continue

        if not parts:
            continue

        cmd  = parts[0]
        args = parts[1:]

        if cmd.lower() == 'exit':
            print("Goodbye!")
            break
        elif cmd.lower() in ('--help', '-h', 'help'):
            print_usage()
        elif cmd.lower() == 'pwd':
            print(os.getcwd())
        elif cmd.lower() == 'cd':
            target = (" ".join(args) if args else "~").replace("~", home_dir)
            try:
                os.chdir(target)
            except FileNotFoundError:
                print(f"Error: '{target}' not found.")
            except PermissionError:
                print(f"Error: access denied to '{target}'.")
            except Exception as e:
                print(f"Error: {e}")
        elif cmd.lower() in ('ls', 'dir'):
            try:
                for item in sorted(os.listdir('.')):
                    print(("[D] " if os.path.isdir(item) else "    ") + item)
            except Exception as e:
                print(f"Error: {e}")
        elif cmd.lower() == 'cat':
            if not args:
                print("Usage: cat <file>")
            else:
                c = _read_file(" ".join(args))
                if c is not None:
                    print(c)
        elif cmd.lower() in ('clear', 'cls'):
            os.system('cls' if IS_WINDOWS else 'clear')
        elif cmd in ('-e', '-E', '-Ec', '-d', '-D', '-Dc'):
            handle_direct_commands(cmd, args)
        elif user_input.lower() == 'say wallahi bro':
            print("wallahi bro! 😄")
        else:
            _safe_system(user_input)


def main():
    if len(sys.argv) == 1:
        start_interactive_shell()
    elif sys.argv[1] in ('--help', '-h'):
        print_usage()
    elif sys.argv[1] in ('-e', '-E', '-Ec', '-d', '-D', '-Dc'):
        handle_direct_commands(sys.argv[1], sys.argv[2:])
    else:
        print(f"Error: unknown flag '{sys.argv[1]}'. Use --help.")
        sys.exit(1)


if __name__ == "__main__":
    main()