from mtg import connectDB
from mtg import Card
import sqlite3
from sqlite3 import Error

con = connectDB()
con.isolation_level = None
cur = con.cursor()

buffer = ""

print("Enter your SQL commands to execute in sqlite3.")
print("Enter a blank line to exit.")

while True:
    line = input()
    out = ""
    if line == "":
        break
    buffer += line
    if sqlite3.complete_statement(buffer):
        try:
            buffer = buffer.strip()
            cur.execute(buffer)

            if buffer.lstrip().upper().startswith("SELECT"):
                out = cur.fetchall()
                if len(out) < 69:
                    print(out)
                elif len(out) == 69:
                    print("nice")
                elif len(out) > 69:
                    print("Wow that's a lot of text.")
        except Error as e:
            print("An error occurred:", e.args[0])
        buffer = ""
        line = input("Save to file? ")
        if line != "":
            line = input("filename: ")
            with open(f"lists/{line}", 'a+') as f:
                line = input("Just the names? ")
                if line != "":
                    for x in out:
                        f.write(f"1 {x[0]}\n")
                else:
                    for x in out:
                        for y in x:
                            if type(y) == None:
                                f.write("None")
                            else:
                                f.write(str(y)+" | ")
                        f.write("\n")
                            

con.close()
