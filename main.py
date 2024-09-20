import os


def writetxt(path, data):
    try:
        with open(path, "a+", encoding = "utf8") as f:
            f.seek(0)
            fdata = f.read(100)
            if len(fdata) > 0: f.write("\n")
            if type(data) == list: f.write("\n".join(data))
            elif type(data) == str: f.write(data)
        return True
    except OSError as e: return False

DIRECTORY = 'C:\\Users\\<username>\\Downloads'
EXTENSION = ('.log', '.txt')
SEARCH    = '35=A'
SAVE      = True

file_save = os.path.join(DIRECTORY, 'NEWLOG')

for root, dirs, files in os.walk(DIRECTORY):
    for file in files:
        file_path = os.path.join(root, file)
        file_size = int(int(os.stat(file_path).st_size) / 1024) # KB
        print(f"[+] File: {file} | Size: {'{:,} KB'.format(file_size)}")
        writetxt(file_save, f"[+] File: {file} | Size: {'{:,} KB'.format(file_size)}")
        if file.lower().endswith(EXTENSION):
            content = []
            with open(file_path, 'r', encoding='utf8') as f:
                result = f.readlines()
                f.close()
                for i in range(len(result)):
                    if result[i].find(SEARCH) != -1:
                        text = result[i].replace('\n','')
                        print(f"[-] [{i + 1}] {text}")
                        content.append(f"[-] [{i + 1}] {text}")
            writetxt(file_save, content)