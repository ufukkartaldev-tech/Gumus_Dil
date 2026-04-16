import os
import re

replacements = {
    "değilse": "yoksa",
    "döngü": "için",
    "deneme": "dene",
    "KW_DEGILSE": "KW_YOKSA",
    "KW_DENEME": "KW_DENE",
    "degilse": "yoksa",
    "dongu": "için"
}

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return # Skip binary or weirdly encoded files

    new_content = content
    for old, new in replacements.items():
        if old.startswith("KW_"):
            new_content = new_content.replace(old, new)
        else:
            # simple replacement for the keywords.
            # to be safe, only replace if surrounded by non-alphanumeric (like boundary)
            # but regex \b doesn't always work perfectly with Turkish chars without regex module flags.
            # simple replace is usually fine for keywords like 'değilse ', 'döngü(', etc.
            new_content = re.sub(r'(?<![a-zA-Z0-9çğıöşüÇĞIÖŞÜ])' + old + r'(?![a-zA-Z0-9çğıöşüÇĞIÖŞÜ])', new, new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk('.'):
    # Skip environments and git
    if any(ignore in root for ignore in ['.venv', '.git', 'build', 'node_modules', 'lexer', 'parser']):
        continue
    for file in files:
        if file.endswith(('.tr', '.py', '.cpp', '.h', '.md', '.txt')):
            path = os.path.join(root, file)
            process_file(path)

print("Replacement complete.")
