

def clear_log():
    with open("log.txt", "w") as f:
        f.write("")

def log(s):
    with open("log.txt", "a") as f:
        f.write(s + "\n")