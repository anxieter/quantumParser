

def clear_log():
    with open("log.txt", "w") as f:
        f.write("")

def log(s):
    with open("log.txt", "a") as f:
        f.write(s + "\n")

def log_matrix(mat):
    with open("log.txt", "a") as f:
        f.write("[")
        for i in range(len(mat)-1):
            f.write("[")
            f.write(f"{mat[i][0]}")
            for j in range(1, len(mat)):
                f.write(f",{mat[i][j]}")
            f.write("],\n")
        f.write("[")
        f.write(f"{mat[len(mat)-1][0]}")
        for j in range(1, len(mat)):
            f.write(f",{mat[len(mat)-1][j]}")
        f.write("]")
        f.write("]")
        f.write("\n")