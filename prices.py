from mtg import Card
from mtg import Deck
from mtg import connectDB
from mtg import homeDir
import sys
import csv
from os.path import exists
import json
import sqlite3

tcgPrice = open(homeDir+"/data/tcg.json","r")
tcgPrices = json.loads(tcgPrice.read())
tcgPrice.close()

ckPrice = open(homeDir+"/data/ck.json","r")
ckPrices = json.loads(ckPrice.read())
ckPrice.close()

def getCheapestPrinting(card,db):
    query = f"""SELECT name, setCode, uuid FROM cards WHERE name="{card['name']}" AND availability LIKE '%paper%';"""

    if not card.Verified():
        card.verifyCard(db)

    if not card.Verified():
        return 0
    
    db.execute(query)
    printings = db.fetchall()

    if len(printings) == 0:
        return 0.0
    
    cPrice = 100000000.00
    cSet = ""

    for x in printings:
        if x[2] in tcgPrices["data"].keys():
            price = tcgPrices["data"][x[2]]
            c = float(price[max(price.keys())])
            if c < cPrice:
                cPrice = c
                cSet = x[1]
        elif x[2] in ckPrices["data"].keys():
            price = ckPrices["data"][x[2]]
            c = float(price[max(price.keys())])
            if c < cPrice:
                cPrice = c
                cSet = x[1]

    if cSet == "":
        return 0
    if cSet != card['setCode']:
        card.cardInfo['setCode'] = cSet
        card.cardInfo['isFoil'] = ""
        card.verifyCard(db)
    return float(cPrice)

def getPrice(card):
    if card['uuid'] in tcgPrices["data"].keys():
        price = tcgPrices["data"][card["uuid"]]
        return float(price[max(price.keys())])
    elif card['uuid'] in ckPrices["data"].keys():
        price = ckPrices["data"][card["uuid"]]
        return float(price[max(price.keys())])
    return 0


def main(args,db):
    if args is None:
        return
    
    file = args
    d = Deck(file.split('.')[0],file,db=db)
    if ".json" not in file:
        d.exportJSON(file.split('.')[0]+".json")
        d1 = Deck("",file.split('.')[0]+".json")
    else:
        d1 = Deck("",file)
    
    with open(homeDir+"/decks/"+file.split('.')[0]+"-price-comparison.csv",'w+',newline='') as f:
        fieldNames = ["Name","Old Set","Old Price","New Set","New Price", "Variance"]
        csvWriter = csv.DictWriter(f,fieldnames=fieldNames)

        for card in d.cards.keys():
            getCheapestPrinting(card,db)

        rows = [{}]
        for x in fieldNames:
            rows[0][x]=x

        for card in d.cards.keys():
            p = getPrice(card)
            if p == 0:
                print(f"No price found for {str(card)}")
            rows.append({"Name":card['name'],
                         "Old Set":"",
                         "Old Price":0,
                         "New Set":card['setCode'],
                         "New Price":p,
                         "Variance":""})

        r=1
        for card in d1.cards.keys():
            p = getPrice(card)
            if p == 0:
                print(f"No price found for {str(card)}")
            rows[r]["Old Set"]=card['setCode']
            rows[r]["Old Price"]=p
            rows[r]["Variance"]=rows[r]['New Price']-p
            if r+1 < len(rows):
                r+=1
    
        rows.append({})
        for x in fieldNames:
            rows[-1][x] = ""
            
        rows[-1]['Old Price'] = sum(float(rows[x]['Old Price']) for x in range(1,len(rows)-1))
        rows[-1]['New Price'] = sum(float(rows[x]['New Price']) for x in range(1,len(rows)-1))
        rows[-1]['Variance'] = rows[-1]['New Price']-rows[-1]['Old Price']

        for x in rows:
            csvWriter.writerow(x)

        d.exportJSON(file.split('.')[0]+"-cheapest.json")
        d.exportText(file.split('.')[0]+"-cheapest.txt")
                
                    


if __name__ == "__main__":
    args  = str(sys.argv[1]) if len(sys.argv)>1 else str(input("Enter filename: "))
    db = connectDB().cursor()
    main(args,db)
    
