from sqlite3 import connect

db = connect("data/AllPrintings.sqlite").cursor()
query = "SELECT sql FROM sqlite_master;"

db.execute(query)
i = db.fetchall()
o = {}
with open("data/full_structure.txt",'w') as f:
    name = ""
    for x in i:
        if x != None:
            for y in x:
                if y != None:
                    for z in y.split("\n"):
                        if z != None:
                            f.write(z+"\n")
                            if z.lstrip('/t').startswith("CREATE"):
                                name = z.split(" ")[2].strip("`")
                            else:
                                if z.startswith(" "):
                                    if name in o.keys():
                                        o[name].append(z.lstrip(" ").split(" ")[0])
                                    else:
                                        o[name] = [z.lstrip(" ").split(" ")[0]]
        
with open("data/every_table_dictionary.py",'a') as f:
    for x in o.keys():
        f.write(x)
        f.write(" = {")
        for y in o[x]:
            f.write(f"\n'{y}':'',")
        f.write("}\n\n")

with open("data/every_table_list.py",'a') as f:
    for x in o.keys():
        f.write(x)
        f.write(" = [")
        for y in o[x]:
            f.write(f"'{y}', ")
        f.write("]\n\n")
