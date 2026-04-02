import os
import zipfile
import gzip
import tarfile
import re
import json


# ================= CONFIG =================
DIRECTORY = 'C:\\Users\\cuong.huynh\\Downloads\\FOS'
DIRSAVE   = 'C:\\Users\\cuong.huynh\\Downloads'
SAVE = True
OUTPUT_JSON = True
MAX_FILE_SIZE_MB = 5000  # skip file quá lớn

file_save = os.path.join(DIRSAVE, 'NEWLOG.txt')
file_json = os.path.join(DIRSAVE, 'NEWLOG.json')


# ================= RULE ENGINE =================
RULES = [
    {
        "name": "EKYC",
        "level": "INFO",
        "type": "any", # any / all / regex / exclude / priority
        "keywords": ["0392250340", "079169004409"],
        "priority": 3
    },
    # {
    #     "name": "ERROR",
    #     "level": "ERROR",
    #     "type": "any",
    #     "keywords": ["error", "fail", "exception", "fatal"],
    #     "priority": 1
    # },
    # {
    #     "name": "PHONE",
    #     "level": "INFO",
    #     "type": "regex",
    #     "pattern": r'\b0\d{9}\b',
    #     "priority": 4
    # }
]


# ================= WRITE =================
def writetxt(path, data):
    try:
        with open(path, "a", encoding="utf8") as f:
            if isinstance(data, list):
                f.write("\n".join(data) + "\n")
            else:
                f.write(data + "\n")
    except:
        pass

def writejson(path, obj):
    try:
        with open(path, "a", encoding="utf8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except:
        pass

# ================= TEXT DETECT =================
def is_text_file(file_path, blocksize=1024):
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(blocksize)
            if b'\x00' in chunk:
                return False
        return True
    except:
        return False


# ================= RULE MATCH =================
def match_rules(text):
    text_lower = text.lower()
    for rule in RULES:
        if rule["type"] == "exclude":
            if any(k in text_lower for k in rule["keywords"]):
                return []

    matched = []
    for rule in RULES:
        t = rule["type"]
        if t == "any":
            if any(k in text_lower for k in rule["keywords"]):
                matched.append(rule)
        elif t == "all":
            if all(k in text_lower for k in rule["keywords"]):
                matched.append(rule)
        elif t == "regex":
            if re.search(rule["pattern"], text):
                matched.append(rule)
    if matched:
        matched.sort(key=lambda x: x.get("priority", 999))
        return [matched[0]]
    return []

# ================= PROCESS =================
def process_line(line, line_no, source, content):
    text = line.strip()
    matches = match_rules(text)
    for rule in matches:
        msg = f"[{rule['level']}] [{rule['name']}] [{line_no}] {text}"
        print(msg)
        content.append(msg)
        if OUTPUT_JSON:
            writejson(file_json, {
                "file": source,
                "line": line_no,
                "rule": rule["name"],
                "level": rule["level"],
                "message": text
            })

# ================= READERS =================
def read_normal(file_path):
    content = []
    try:
        with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                process_line(line, i, file_path, content)
    except:
        pass
    return content

def read_zip(file_path):
    content = []
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            for name in z.namelist():
                with z.open(name) as f:
                    for i, line in enumerate(f, 1):
                        text = line.decode('utf8', errors='ignore')
                        process_line(text, i, name, content)
    except:
        pass
    return content

def read_gz(file_path):
    content = []
    try:
        with gzip.open(file_path, 'rt', encoding='utf8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                process_line(line, i, file_path, content)
    except:
        pass
    return content

def read_tar(file_path):
    content = []
    try:
        with tarfile.open(file_path, 'r:*') as tar:
            for member in tar.getmembers():
                if member.isfile():
                    f = tar.extractfile(member)
                    if f:
                        for i, line in enumerate(f, 1):
                            text = line.decode('utf8', errors='ignore')
                            process_line(text, i, member.name, content)
    except:
        pass
    return content

# ================= MAIN =================
for root, dirs, files in os.walk(DIRECTORY):
    if 'node_modules' in root.lower():
        continue
    for file in files:
        file_path = os.path.join(root, file)
        file_lower = file.lower()
        try:
            file_size = os.stat(file_path).st_size
            file_size_mb = file_size / (1024 * 1024)
        except:
            continue
        if file_size_mb > MAX_FILE_SIZE_MB:
            continue
        header = f"[+] File: {file} | Size: {int(file_size_mb)} MB"
        print(header)
        if SAVE:
            writetxt(file_save, header)
        content = []
        if file_lower.endswith('.zip'):
            content = read_zip(file_path)
        elif file_lower.endswith('.gz'):
            content = read_gz(file_path)
        elif file_lower.endswith(('.tar.gz', '.tgz')):
            content = read_tar(file_path)
        else:
            if is_text_file(file_path):
                content = read_normal(file_path)
        if SAVE and content:
            writetxt(file_save, content)
