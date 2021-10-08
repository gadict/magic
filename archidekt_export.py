#For some reason Archidekt's exports don't insert newlines
#between cards. No idea why. This results in double spacing, but the rest
#of the programs here will ignore whitespace in files so I didn't feel
#like fixing it lmao.

importFile = input("Enter input filename: ")
exportFile = input("Enter export filename: ")

_import = ""

if exportFile=="":
    exportFile = importFile
_export = ""
n = ""

with open(importFile, 'r') as f:
    _import = f.read()
    offset=0
    for x in range(len(_import)):
        if _import[min(x+offset, len(_import)-1)].isnumeric():
            _export += "\n"
            _export += _import[min(x+offset, len(_import)-1)]
            offset+=1
            if _import[min(x+offset, len(_import)-1)].isnumeric():
                _export += _import[min(x+offset, len(_import)-1)]
                offset+=1
        
    
        _export += _import[min(x+offset, len(_import)-1)]
    f.close()

with open(exportFile, 'w') as f:
    f.write(_export)
