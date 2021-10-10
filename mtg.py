import sqlite3
from sqlite3 import Error
import json
import re
import os
import requests

homeDir = str(os.path.expanduser("~/documents/magic"))

def connectDB(path=homeDir+"/data/AllPrintings.sqlite"):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print(f"The error '{e}' occurred.")

    return connection

class Card:
    def __init__(self, name, setCode="", category=""):
        self.cardInfo={
        'id':'',
        'artist':'',
        'asciiName':'',
        'availability':'',
        'borderColor':'',
        'colorIdentity':'',
        'colorIndicator':'',
        'colors':'',
        'convertedManaCost':'',
        'duelDeck':'',
        'edhrecRank':'',
        'faceConvertedManaCost':'',
        'faceManaValue':'',
        'faceName':'',
        'finishes':'',
        'flavorName':'',
        'flavorText':'',
        'frameEffects':'',
        'frameVersion':'',
        'hand':'',
        'hasAlternativeDeckLimit':'',
        'hasContentWarning':'',
        'hasFoil':'',
        'hasNonFoil':'',
        'isAlternative':'',
        'isFullArt':'',
        'isOnlineOnly':'',
        'isOversized':'',
        'isPromo':'',
        'isReprint':'',
        'isReserved':'',
        'isStarter':'',
        'isStorySpotlight':'',
        'isTextless':'',
        'isTimeshifted':'',
        'keywords':'',
        'layout':'',
        'leadershipSkills':'',
        'life':'',
        'loyalty':'',
        'manaCost':'',
        'manaValue':'',
        'mcmId':'',
        'mcmMetaId':'',
        'mtgArenaId':'',
        'mtgjsonV4Id':'',
        'mtgoFoilId':'',
        'mtgoId':'',
        'multiverseId':'',
        'name':name,
        'number':'',
        'originalReleaseDate':'',
        'originalText':'',
        'originalType':'',
        'otherFaceIds':'',
        'power':'',
        'printings':'',
        'promoTypes':'',
        'purchaseUrls':'',
        'rarity':'',
        'scryfallId':'',
        'scryfallIllustrationId':'',
        'scryfallOracleId':'',
        'setCode':setCode,
        'side':'',
        'subtypes':'',
        'supertypes':'',
        'tcgplayerEtchedProductId':'',
        'tcgplayerProductId':'',
        'text':'',
        'toughness':'',
        'type':'',
        'types':'',
        'uuid':'',
        'variations':'',
        'watermark':'',
        'isFoil':'',
        'category':'',}

        self.verified = False

    def Verified(self):
        return self.verified

    def isLegal(self, _format, cur):
        if self.Verified():
            query = f"SELECT status FROM legalities WHERE format='{_format}' AND uuid='{self.cardInfo['uuid']}';"
            cur.execute(query)
            res = cur.fetchone()
            print (res)
            if res[0] == "Legal":
                return True
            else:
                return False

    def verifyCard(self, cur):
        self.verified=False
        find_card_set = f"""
        SELECT {','.join([x for x in self.cardInfo.keys() if x not in ['isFoil','category']])}
        FROM cards WHERE name LIKE "{self.cardInfo["name"]}%" 
        AND setCode='{self.cardInfo["setCode"]}';"""

        find_card = f"""
        SELECT {','.join([x for x in self.cardInfo.keys() if x not in ['isFoil','category']])}
        FROM cards WHERE name LIKE "{self.cardInfo["name"]}%" 
        AND availability LIKE '%paper%';"""

        find_card_exact = f"""
        SELECT {','.join([x for x in self.cardInfo.keys() if x not in ['isFoil','category']])}
        FROM cards WHERE name="{self.cardInfo["name"]}" 
        AND availability LIKE '%paper%';"""

        find_card_set_exact = f"""
        SELECT {','.join([x for x in self.cardInfo.keys() if x not in ['isFoil','category']])}
        FROM cards WHERE name="{self.cardInfo["name"]}" 
        AND setCode='{self.cardInfo["setCode"]}';"""

        res = []

        if self.cardInfo["setCode"] == "":
            cur.execute(find_card_exact)
            res = cur.fetchone()
            if res == None:
                cur.execute(find_card)
                res = cur.fetchone()
                if res == None:
                    return
        else:
            cur.execute(find_card_set_exact)
            res = cur.fetchone()
            if res == None:
                cur.execute(find_card_set)
                res=cur.fetchone()
                if res == None:
                    cur.execute(find_card)
                    res = cur.fetchone()
                    if res == None:
                        return

        
        y = 0
        for x in self.cardInfo.keys():
            if y < len(res):
                if res[y] == None:
                    self.cardInfo[x] = "None"
                else:
                    self.cardInfo[x] = res[y]
            y += 1
            
        self.verified = True

    def verifyByUUID(self,uuid,db):
        self.verified = False
        query = "SELECT {','.join([x for x in self.cardInfo.keys() if x not in ['isFoil','category']])} FROM cards WHERE uuid={uuid};";
        db.execute(query)
        res = db.fetchone()
        if res is None:
            return
        y = 0
        for x in self.cardInfo.keys():
            if y < len(res):
                if res[y] == None:
                    self.cardInfo[x] = ""
                else:
                    self.cardInfo[x] = res[y]
            y += 1
            
        self.verified = True
        

    def artURL(self):
        return f"https://api.scryfall.com/cards/{self.cardInfo['scryfallId']}?format=image" if self.Verified() else ""

    def downloadArt(self):
        if not self.verified:
            return
        artdir = homeDir + '/art'
        path = f"{artdir}\\{self.cardInfo['setCode']}" + ("_" if self.cardInfo['setCode'] == "CON" else "")
        name = f"{path}\\{self.cardInfo['name'].replace('/','-')}.jpg"
        if not os.path.exists(artdir):
            os.mkdir(artdir)
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(name):
            image = requests.get(self.artURL()).content
            with open(name,'wb') as f:
                f.write(image)
        if self.cardInfo['otherFaceIds'] != "None":
            if not os.path.exists(f"{path}\\{self.cardInfo['name'].replace('/','-')}-back.jpg"):
                image = requests.get(self.artURL()+"&face=back").content
                with open(f"{path}\\{self.cardInfo['name'].replace('/','-')}-back.jpg", 'wb') as f:
                    f.write(image)

    def __str__(self):
        s = f"{self.cardInfo['name']} ({self.cardInfo['setCode']})"
        if self.cardInfo['isFoil'] != "":
            s+="*F*"
        if self.cardInfo['category'] != "":
            s+=f"[{self.cardInfo['category']}]"
        s+="\n"
        return s

    def __getitem__(self, key):
        return self.cardInfo[key]

class SimpleCard(Card):
    def __init__(self, name, setCode=""):
        Card.__init__(self, name, setCode)
        self.cardInfo={
            'id':'',
            'colorIdentity':'',
            'colors':'',
            'convertedManaCost':'',
            'loyalty':'',
            'manaCost':'',
            'manaValue':'',
            'multiverseId':'',
            'name':name,
            'otherFaceIds':'',
            'power':'',
            'printings':'',
            'promoTypes':'',
            'rarity':'',
            'scryfallId':'',
            'setCode':setCode,
            'side':'',
            'subtypes':'',
            'supertypes':'',
            'text':'',
            'toughness':'',
            'type':'',
            'types':'',
            'uuid':'',
            'isFoil':'',
            'category':'',}
        

class Deck:
    def __init__(self,name,file="",db=None,cType=SimpleCard):
        self.name = name
        self.description = ""
        self.cards = {}
        self.cType = cType

        if db is None:
            db = connectDB().cursor()

        if ".txt" in file:
            self.importText(file,db)
        elif ".json" in file:
            self.importJSON(file)

    def allCards(self):
        return [card for card in self.cards.keys()]
    
    def nonlands(self):
        non = []
        for card in self.allCards():
            if not (card['types'] == "Land" and card['supertypes'] == "Basic"):
                non.append(card)
        return non
    
    def lands(self):
        land = []
        for card in self.allCards():
            if card['types'] == "Land" or card['supertypes'] == "Basic":
                land.append(card)
        return land

    def filterBy(self, key, values):
        res = []
        for card in self.allCards():
            val = card[key].split(',')
            valid = True
            for t in val:
                if t not in values:
                    valid=False
                    break
            if valid:
                res.append(card)
        return res
        
    def importText(self,file,db):
        with open(homeDir+"/decks/"+file,'r') as f:
            i = f.read().split("\n")
            pattern = re.compile(r"(?P<quantity>\d+[x]*)\s(?P<name>(\s*[\w,'-]+)+)\s*([\[\(](?P<setCode>\w+)[\)\]])*\s{0,1}(?P<foil>\*F\*)*(\[(?P<category>\w+)\])*")
            
            for card in i:
                res = pattern.search(card)

                if res != None:
                    res = res.groupdict()
                    quantity = res['quantity']
                    name = res['name']
                    code = res['setCode']
                    if code != None:
                        c = self.cType(name,code)
                    else:
                        c = self.cType(name,"")
                    c.verifyCard(db)
                    if res['category'] != None:
                        c.cardInfo['category'] = res['category']
                    if res['foil'] != None:
                        c.cardInfo['isFoil']=True
                    c.verifyCard(db)
                    self.cards[c] = int(quantity)
                    
    def importJSON(self,file):
        with open(homeDir+"/decks/"+file, 'r') as f:
            i = json.loads(f.read())
            for x in i["Cards"].keys():
                c = self.cType("")
                c.cardInfo = i['Cards'][x][0]
                c.verified = True
                quantity = i['Cards'][x][1]
                self.cards[c] = quantity
            self.name = i["Meta"]["name"]
            self.description = i["Meta"]["description"]
            self.cType = SimpleCard if i["Meta"]["cType"] is "Simple" else Card
                
            
    def exportText(self, file):
        with open(homeDir+"/decks/"+file, 'a+') as f:
            for x in self.cards.keys():
                f.write(f"{self.cards[x]} {str(x)}")

    def exportJSON(self, file):
        out = {"Cards":{},"Meta":{"name":self.name, 
        "description":self.description,
        "cType":"Simple" if self.cType is SimpleCard else "Precise"}}

        for x in self.cards.keys():
            out["Cards"][x['id']] = [x.cardInfo,self.cards[x]]
        with open(homeDir+"/decks/"+file, 'w') as f:
            f.write(json.dumps(out))

    def findCard(self, name):       
        for x in self.cards.keys():
            if name == x['name']:
                return x
        return None

    def downloadArt(self):
        for card in self.cards:
            card.downloadArt()

    def copyArt(self, directory=""):
        if directory is "":
            directory = homeDir+"/"+(self.name if self.name is not "" else "temp")

        if not os.path.exists(directory):
                os.mkdir(directory)
        
        for card in self.cards:
            fix = ""
            if card['setCode'] == "CON":
                fix = "_"
            artFilename = homeDir+f"\\art\\{card['setCode']+fix}\\{card['name'].replace('/','-')}.jpg"
            artFilename1 = homeDir+f"\\art\\{card['setCode']+fix}\\{card['name'].replace('/','-')}-back.jpg"
            newFilename = f"{directory}\\{card['name'].replace('/','-')}_({card['setCode']}).jpg"
            newFilename1 = f"{directory}\\{card['name'].replace('/','-')}_({card['setCode']})-back.jpg"
            if not os.path.exists(artFilename):
                card.downloadArt()

            with open(artFilename, 'rb') as _if:
                image = _if.read()
                with open(newFilename, 'wb') as of:
                    of.write(image)
            if card['otherFaceIds'] != "None":
                with open(artFilename1, 'rb') as _if:
                    image = _if.read()
                with open(newFilename1, 'wb') as of:
                    of.write(image)

    def __getitem__(self, name):
        return self.findCard(name)