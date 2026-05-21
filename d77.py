import sys
import os
import shutil
import shlex  # المكتبة السحرية للتعامل مع علامات التنصيص والمسافات

def d77_logic(text, key, mode='encrypt'):
    encrypted_text = ""
    for index, char in enumerate(text):
        char_code = ord(char)
        if mode == 'encrypt':
            if index % 2 == 0: 
                new_code = char_code + (key + index)
            else: 
                new_code = char_code - (key - index)
        else:
            if index % 2 == 0: 
                new_code = char_code - (key + index)
            else: 
                new_code = char_code + (key - index)
        encrypted_text += chr(new_code % 1114111)
    return encrypted_text

def ask_overwrite(file_name):
    if os.path.exists(file_name):
        ans = input(f"Warning: '{file_name}' already exists! Overwrite? (y/n): ").lower()
        if ans != 'y':
            print("Operation cancelled.")
            sys.exit(0)

# --- دليل المستخدم الكامل والمطور تلقائياً ---
def print_usage():
    print("D77 Cipher Tool")
    print("Usage:")
    print("  d77 -e [loops] <file>         (Encrypt file in-place)")
    print("  d77 -E [loops] <file> <out>   (Encrypt to a new file)")
    print("  d77 -d [loops] <file>         (Decrypt file in-place)")
    print("  d77 -D [loops] <file> <out>   (Decrypt to a new file)")
    print("  d77 -Ec [loops] <file> <out>  (Encrypt & change file extension)")
    print("  d77 -Dc [loops] <file> <out>  (Decrypt & change file extension)")
    print("\n Quick Text Cipher:")
    print("  (your text)                   (Encrypt text instantly using normal brackets)")
    print("  [encrypted text]              (Decrypt text instantly using square brackets)")
    print("\n Pro Tips:")
    print("  1. If file name or text contains spaces, ALWAYS wrap it in quotes: \"my file.txt\" or 'my file.txt'")
    print("  2. Inside brackets, if your text has spaces, use quotes inside: (\"hello world\") or [\"hello world\"]")
    print("  3. you can use ls for showing what is there in the folder (like linux!)")
    print("  4. you can use cat for showing what is there in the file (like linux!)")
    print("  5. you can use cp for copy and rm for remove and mv to move or rename (like linux!)")


def handle_direct_commands(flag, args):
    key = 77
    loops = 1
    
    if len(args) == 0:
        print("Error: Missing file arguments.")
        return
        
    if args[0].isdigit():
        loops = int(args[0])
        args = args[1:]
        
    if len(args) == 0:
        print("Error: Missing file name after loops count.")
        return
        
    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None

    if not os.path.exists(input_file):
        print(f"Error: Source file '{input_file}' not found!")
        return

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    flag_lower = flag.lower()
    
    if flag_lower in ['-e', '-ec']:
        result = content
        for _ in range(loops):
            result = d77_logic(result, key, 'encrypt')
            
        if flag_lower == '-e':
            with open(input_file, 'w', encoding='utf-8') as f: f.write(result)
            print(f"File encrypted successfully {loops} times in-place!")
        else:
            if not output_file:
                print("Error: Please specify the output file!")
                return
            ask_overwrite(output_file)
            with open(output_file, 'w', encoding='utf-8') as f: f.write(result)
            print(f"Encrypted {loops} times and saved to: {output_file}")

    elif flag_lower in ['-d', '-dc']:
        result = content
        for _ in range(loops):
            result = d77_logic(result, key, 'decrypt')
            
        if flag_lower == '-d':
            with open(input_file, 'w', encoding='utf-8') as f: f.write(result)
            print(f"File decrypted successfully {loops} times in-place!")
        else:
            if not output_file:
                print("Error: Please specify the output file!")
                return
            ask_overwrite(output_file)
            with open(output_file, 'w', encoding='utf-8') as f: f.write(result)
            print(f"Decrypted {loops} times and saved to: {output_file}")
    else:
        print("Invalid flag! Use -e, -E, -d, or -D.")

def start_interactive_shell():
    os.system("chcp 65001 > nul")  # بقاء نظام الـ UTF-8 الأصلي لعرض الرموز
    print_usage()
    print("\n[+] Entered D77 Custom Interactive Shell. Type 'exit' to logout.")
    
    home_dir = os.path.expanduser("~")
    
    while True:
        current_full_path = os.getcwd()
        
        if current_full_path.lower().startswith(home_dir.lower()):
            display_path = current_full_path.replace(home_dir, "~").replace("\\", "/")
        else:
            display_path = current_full_path.replace("\\", "/")
            
        prompt = f"D77/{display_path}> "
        
        try:
            user_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            break
            
        if not user_input:
            continue
            
        # 1. التشفير الفوري التلقائي عند استخدام الأقواس العادية ( )
        if user_input.startswith('(') and user_input.endswith(')'):
            pure_text = user_input[1:-1].strip()
            if (pure_text.startswith('"') and pure_text.endswith('"')) or (pure_text.startswith("'") and pure_text.endswith("'")):
                pure_text = pure_text[1:-1]
            if not pure_text:
                print("Error: Brackets are empty!")
                continue
            cipher_res = d77_logic(pure_text, 77, 'encrypt')
            print(f"\n[+] Encrypted Result:\n{cipher_res}\n")
            continue

        # 2. فك التشفير الفوري التلقائي عند استخدام الأقواس المعقوفة [ ]
        if user_input.startswith('[') and user_input.endswith(']'):
            pure_text = user_input[1:-1].strip()
            if (pure_text.startswith('"') and pure_text.endswith('"')) or (pure_text.startswith("'") and pure_text.endswith("'")):
                pure_text = pure_text[1:-1]
            if not pure_text:
                print("Error: Brackets are empty!")
                continue
            cipher_res = d77_logic(pure_text, 77, 'decrypt')
            print(f"\n[+] Decrypted Result:\n{cipher_res}\n")
            continue

        try:
            parts = shlex.split(user_input)
        except Exception as e:
            print(f"Error parsing command: {e}")
            continue
            
        if not parts:
            continue
            
        cmd = parts[0]
        args = parts[1:]
        
        if cmd.lower() == 'exit':
            break
            
        elif cmd.lower() == 'cd':
            target = " ".join(args) if args else "~"
            if target == "~":
                target = home_dir
            elif target.startswith("~/"):
                target = target.replace("~", home_dir)
            try:
                os.chdir(target)
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd.lower() == 'ls':
            try:
                files = os.listdir('.')
                if not files: print("[Empty Directory]")
                for item in files: print(item)
            except Exception as e: print(f"Error: {e}")
                
        elif cmd.lower() == 'cat':
            if args:
                try:
                    with open(args[0], 'r', encoding='utf-8', errors='replace') as f:
                        print(f.read())
                except Exception as e: print(f"Error: {e}")
            else:
                print("Error: cat requires a file name.")
                
        elif cmd.lower() == 'rm':
            if args:
                try:
                    os.remove(args[0])
                    print("File removed successfully.")
                except Exception as e: print(f"Error: {e}")
        elif cmd.lower() == 'mv':
            if len(args) >= 2:
                try:
                    shutil.move(args[0], args[1])
                    print("Moved successfully.")
                except Exception as e: print(f"Error: {e}")
                
        elif cmd in ['-e', '-E', '-ec', '-Ec', '-d', '-D', '-dc', '-Dc']:
            handle_direct_commands(cmd, args)
                
        elif user_input.lower() == 'say wallahi bro':
            print("wallahi bro!")
            
        else:
            os.system(user_input)

def main():
    if len(sys.argv) == 1:
        start_interactive_shell()
    else:
        flag = sys.argv[1]
        args = sys.argv[2:]
        handle_direct_commands(flag, args)

if __name__ == "__main__":
    main()