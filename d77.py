import logging
import sys
import os
import shlex
import base64

# ============================================================
#  D77 Cipher Tool v2.4
# ============================================================
#  إصلاحات v2.3:
#  12. أسماء الملفات التي تحتوي مسافات على Windows
#  13. cat يزيل الأقواس المحيطة باسم الملف تلقائياً
#  إصلاحات v2.4:
#  14. دعم arrow keys وhistory في الـ shell
#      Linux/Mac → readline (مدمج في Python، يعمل تلقائياً)
#      Windows   → pyreadline3  (pip install pyreadline3)
#                  إذا غير مثبّت → يعمل البرنامج بشكل عادي
# ============================================================

logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")
logger    = logging.getLogger("D77")
KEY       = 77
MAX_LOOPS = 15
IS_WINDOWS = os.name == 'nt'

# ─────────────────────────────────────────────────────────────
# FIX #14: readline — يجب أن يكون بعد IS_WINDOWS
# ─────────────────────────────────────────────────────────────
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".d77_history")
_readline_available = False

def _setup_readline():
    """
    يفعّل readline للـ arrow keys والـ history.
    Linux/Mac : readline مدمج في Python — يعمل دائماً.
    Windows   : يحتاج pyreadline3  →  pip install pyreadline3
                إذا غير مثبّت: البرنامج يعمل بشكل عادي بدون history.

    ملاحظة: pyreadline3 واجهته مختلفة عن readline الأصلي:
      - لا يدعم parse_and_bind()
      - الـ history يعمل تلقائياً بمجرد الـ import
    """
    global _readline_available
    try:
        if IS_WINDOWS:
            # pyreadline3 يفعّل arrow keys والـ history تلقائياً بالـ import
            # لا تستدعِ parse_and_bind — غير موجودة فيه
            import pyreadline3  # noqa: F401
        else:
            import readline
            # على Linux/Mac فقط نستدعي parse_and_bind
            readline.parse_and_bind('tab: complete')
        _readline_available = True
        # نُعيد الـ module الصحيح للـ history save/load
        if IS_WINDOWS:
            import pyreadline3
            return pyreadline3
        else:
            import readline
            return readline
    except ImportError:
        if IS_WINDOWS:
            print("⚠ Tip: install pyreadline3 for arrow-key history support:")
            print("       pip install pyreadline3\n")
        return None


def _load_history(readline_mod):
    """
    يحمّل الـ history من الملف.
    pyreadline3 لا يدعم read_history_file → نتجاهل الخطأ بهدوء.
    """
    if not readline_mod or not os.path.exists(HISTORY_FILE):
        return
    try:
        readline_mod.read_history_file(HISTORY_FILE)
        readline_mod.set_history_length(500)
    except AttributeError:
        pass  # pyreadline3 لا يدعم هذه الدوال
    except Exception:
        pass


def _save_history(readline_mod):
    """
    يحفظ الـ history عند الخروج.
    pyreadline3 لا يدعم write_history_file → نتجاهل الخطأ بهدوء.
    """
    if not readline_mod:
        return
    try:
        readline_mod.write_history_file(HISTORY_FILE)
    except AttributeError:
        pass  # pyreadline3
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# FIX #12: تحليل الأوامر مع دعم المسافات في أسماء الملفات
# ─────────────────────────────────────────────────────────────
def _parse_command(user_input: str) -> list[str]:
    """
    يحلل الأمر بشكل صحيح على Windows وLinux.
    يدعم:
      cat file.txt
      cat 'file name.txt'
      cat "file name.txt"
      -e "my file.txt"
      -e 3 "my file.txt"
    """
    try:
        if IS_WINDOWS:
            lex = shlex.shlex(user_input, posix=False)
            lex.whitespace_split = False
            lex.whitespace = ' \t'
            tokens = list(lex)
            cleaned = []
            for t in tokens:
                if (t.startswith('"') and t.endswith('"')) or \
                   (t.startswith("'") and t.endswith("'")):
                    cleaned.append(t[1:-1])
                else:
                    cleaned.append(t)
            return [t for t in cleaned if t]
        else:
            return shlex.split(user_input)
    except ValueError:
        return user_input.split()


def _strip_quotes(s: str) -> str:
    """FIX #13: يزيل الأقواس المحيطة بالنص إن وُجدت."""
    s = s.strip()
    if len(s) >= 2 and \
       ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


# ─────────────────────────────────────────────────────────────
# خوارزمية التشفير
# ─────────────────────────────────────────────────────────────
def _build_decrypt_lookup(key: int, loop: int) -> dict[int, list[int]]:
    lookup: dict[int, list[int]] = {}
    for orig_b in range(256):
        transformed = (orig_b * key + loop) % 256
        lookup.setdefault(transformed, []).append(orig_b)
    return lookup


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

    else:
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

            current_text = base64.urlsafe_b64decode(original_b64_bytes).decode('utf-8')

        return current_text


# ─────────────────────────────────────────────────────────────
# ملف I/O
# ─────────────────────────────────────────────────────────────
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
    path = _strip_quotes(path)
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


def _validate_loops(loops: int) -> bool:
    if loops < 1:
        print("Error: loops must be >= 1.")
        return False
    if loops > MAX_LOOPS:
        print(f"Error: loops={loops} exceeds max ({MAX_LOOPS}). High values cause freezing.")
        return False
    return True


# ─────────────────────────────────────────────────────────────
# معالجة أوامر الملفات
# ─────────────────────────────────────────────────────────────
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

    input_file  = _strip_quotes(args[0])
    output_file = _strip_quotes(args[1]) if len(args) > 1 else None

    # Fallback: إذا الملف غير موجود جرب دمج كل args كاسم ملف واحد
    if not os.path.exists(input_file) and len(args) > 1:
        merged = " ".join(args)
        if os.path.exists(merged):
            input_file  = merged
            output_file = None
        else:
            print(f"Error: '{input_file}' does not exist!")
            print(f"Tip: wrap filenames with spaces in quotes → -e \"not secret.xml\"")
            return
    elif not os.path.exists(input_file):
        print(f"Error: '{input_file}' does not exist!")
        print(f"Tip: wrap filenames with spaces in quotes → -e \"not secret.xml\"")
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
║         D77 Cipher Tool v2.4 - Stable Edition           ║
╚══════════════════════════════════════════════════════════╝
Usage:
  -e  [loops] <file>          Encrypt file in-place
  -E  [loops] <file> <out>    Encrypt to another file
  -Ec [loops] <file> <out>    Encrypt + change extension to .d77
  -d  [loops] <file>          Decrypt file in-place
  -D  [loops] <file> <out>    Decrypt to another file
  -Dc [loops] <file> <out>    Decrypt + restore original extension

  Max loops : {MAX_LOOPS}
  Spaces    : wrap in quotes → -e "my file.txt"

💡 Direct text:
  (your text)        → Instant encrypt
  [encrypted text]   → Instant decrypt

Shell: ls/dir, cd, cat, pwd, clear, exit
  ↑↓ Arrow keys & history supported (Linux always / Windows: pip install pyreadline3)
""")


_WINDOWS_COMMANDS = {'dir', 'cls', 'type', 'copy', 'move', 'del', 'ren', 'md', 'rd'}
_UNIX_COMMANDS    = {'ls', 'clear', 'cat', 'cp', 'mv', 'rm', 'mkdir', 'rmdir',
                     'touch', 'head', 'tail', 'grep', 'find', 'chmod'}


def _safe_system(command: str):
    parts    = _parse_command(command)
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


# ─────────────────────────────────────────────────────────────
# الـ Interactive Shell الرئيسي
# ─────────────────────────────────────────────────────────────
def start_interactive_shell():
    if IS_WINDOWS:
        os.system("chcp 65001 > nul 2>&1")
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

    # FIX #14: تفعيل readline وتحميل الـ history
    rl = _setup_readline()
    _load_history(rl)

    print_usage()
    print("[+] D77 Interactive Shell. Type 'exit' to quit.\n")
    home_dir = os.path.expanduser("~")

    try:
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

            # ── تشفير/فك تشفير نص مباشر ─────────────────────
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

            # ── تحليل الأمر ──────────────────────────────────
            try:
                parts = _parse_command(user_input)
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
                target = _strip_quotes(" ".join(args) if args else "~").replace("~", home_dir)
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
                    c = _read_file(_strip_quotes(" ".join(args)))
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

    finally:
        # FIX #14: حفظ الـ history دائماً عند الخروج حتى لو crash
        _save_history(rl)


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