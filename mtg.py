import pandas as pd
import numpy as np
import json
import re
import os
import requests
import sqlalchemy as sql
from sqlalchemy.sql.expression import select
from mtg import *

homeDir = str(os.path.expanduser("~/documents/magic"))
All = slice(None)

engine = sql.create_engine(f"sqlite:///{homeDir}/data/AllPrintings.sqlite")
conn = engine.connect()
meta = sql.MetaData()

cards = sql.Table("cards",meta,autoload=True,autoload_with=engine)
sets = sql.Table('sets',meta,autoload=True,autoload_with=engine)
legalities = sql.Table("legalities",meta,autoload=True,autoload_with=engine)

def set_from_code(code):
    query = sql.select(
        [sets]
    ).where(
        sets.code == code
    )
    results = conn.execute(query).fetchone()
    return results


def formatLegal(format):
    """
    SELECT * 
    FROM cards 
    LEFT JOIN legalities 
    ON legalities.uuid == cards.uuid 
    WHERE legalities.format='{format}' 
    AND legalities.status='Legal'
    ORDER BY name
    """
    query = sql.select([cards,legalities])
    query = query.select_from(
        cards.join(
            legalities, 
            cards.c.uuid == legalities.c.uuid
        )
        ).where(
            sql.and_(
                legalities.c.format == format,
                legalities.c.status == "Legal"
            )
    ).order_by(cards.c.name)

    df = pd.read_sql(query,conn)
    #Drop duplicate cards by name, then drop cards with no rules text
    df = df.drop_duplicates('name')
    df = df.dropna(axis=0,subset=['text'])
    #The join inserts matching columns, in this case just UUID and ID, this probably isn't the optimal
    #way of querying for legality, but it works and this isn't terribly expensive to do after the fact.
    df.drop(['uuid_1','id_1'],axis=1,inplace=True)
    return df

def compareColors(c1,c2):
    if c1 is None:
        return True
    if c2 is None:
        if c1 is None:
            return True
        return False
    for color in c1.split(','):
        if color not in c2:
            return False
    return True

def nonland(l):
    return l.loc[l.types.str.contains("Land") == False,:]

def land(l):
    return l.loc[l.types == 'Land',:]

def byType(l,t):
    return l.loc[l.types.str.contains(t),:]

def bySubType(l,t):
    return l.loc[l.subtypes.str.contains(t),:]
    
def byColor(l,c):
    return l.loc[l.colors.str.contains(c),:]

def find_card(name,setCode="%"):
        quote = "\"" if "\'" in name else "\'"
        """
        SELECT * FROM cards 
        WHERE name LIKE {quote}{name}%{quote} 
        AND setCode LIKE '{setCode}' 
        AND availability LIKE '%paper%'
        AND borderColor IN ('black','white');
        """
        query = sql.select(
            [cards]
        ).where(
            sql.and_(
                cards.c.name.like(f"{name}%"),
                cards.c.setCode.like(setCode),
                cards.c.availability.contains("paper"),
                cards.c.borderColor.in_(['black','white'])
            )
        )
        possibilities = pd.read_sql(query,conn)
        if not possibilities.empty:
            return possibilities
        else:
            return None

    
class Card:
    def __init__(self, name=None, setCode="%"):
        self.data=None
        self.verified = False
        if name:
            self.verifyCard(name,setCode)

    def Verified(self):
        return self.verified

    def verifyCard(self,name,setCode="%"):
        self.verified=False
        possibilities = find_card(name,setCode)
        if possibilities is not None:
            self.data = possibilities.iloc[0].copy()
            self.data.loc['isFoil']=False
            self.data.loc['category']=None
            self.verified = True
        else:
            possibilities = find_card(name)
            if possibilities is not None:
                self.data = possibilities.iloc[0].copy()
                self.data.loc['isFoil']=False
                self.data.loc['category']=None
                self.verified = True
            else:
                raise KeyError(f"{name} not found.")
        
    


    def artURL(self):
        return f"https://api.scryfall.com/cards/{self.data['scryfallId']}?format=image" if self.Verified() else ""

    def downloadArt(self):
        if not self.verified:
            return
        artdir = homeDir + '/art'
        path = f"{artdir}\\{self.data['setCode']}" + ("_" if self.data['setCode'] == "CON" else "")
        name = f"{path}\\{self.data['name'].replace('/','-')}.jpg"
        if not os.path.exists(artdir):
            os.mkdir(artdir)
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(name):
            image = requests.get(self.artURL()).content
            with open(name,'wb') as f:
                f.write(image)
        if self.data['otherFaceIds'] != None:
            if not os.path.exists(f"{path}\\{self.data['name'].replace('/','-')}-back.jpg"):
                image = requests.get(self.artURL()+"&face=back").content
                with open(f"{path}\\{self.data['name'].replace('/','-')}-back.jpg", 'wb') as f:
                    f.write(image)

    def __str__(self):
        s = f"{self.data['name']} ({self.data['setCode']})"
        if self.data['isFoil']:
            s+="*F*"
        if self.data['category'] != "" and self.data['category'] != None:
            s+=f"[{self.data['category']}]"
        return s

    def NS(self):
        return f"{self.data['name']} ({self.data['setCode']})"

    def fromData(data):
        card = Card()
        card.data = data
        if not 'isFoil' in card.data.keys() or 'category' not in card.data.keys():
            card['isFoil'] = False
            card['category'] = ''
        card.verified = True
        return card

    def __getitem__(self, column):
        return self.data[column]
    
    def __setitem__(self, key, value):
        self.data.loc[key] = value
class Deck:
    def __init__(self, file=None):
        self.name = ""
        self.data = find_card("Muldrotha, the Gravetide", "DOM")
        self.data['qty'] = None
        self.data['category'] = None
        self.data = self.data.dropna(axis=0,how="any")

        if file:
            self._import(file)
        
    def downloadArt(self):
        for x,card in self.data.iterrows():
            c = Card.fromData(card)
            c.downloadArt()

    def _import(self, filename):
        if os.path.exists(filename):
            name, ext = filename.split("/")[-1].split('.')
            self.name = name
            if ext == "json":
                self._importJson(filename)
            else:
                self._importText(filename)
    
    def _importJson(self,filename):
        with open(filename,'r') as f:
            self.data = pd.DataFrame(json.loads(f.read()))
    
    def _importText(self,filename):
        pattern = re.compile(r"(?P<qty>\d+)[x]*\s(?P<name>(\s*[\w,'-]+)+)\s*([\[\(](?P<setCode>\w+)[\)\]])*\s*(?P<isFoil>\*F\*)*(\[(?P<category>\w+)\])*")
        cards = open(filename,'r').read().split('\n')
        data = []
        for card in cards:
            m = pattern.match(card)
            if m:
                data.append(m.groupdict())
        
        cardData = [Card(x['name'],x['setCode']).data for x in data]
        #inject quantity, foil,and category
        for x in range(len(cardData)):
            cardData[x]['qty'] = int(data[x]['qty'])
            cardData[x]['isFoil'] = True if data[x]['isFoil'] else False
            cardData[x]['category'] = data[x]['category'] if data[x]['category'] else None
        


        self.data = pd.DataFrame(cardData,(np.arange(0,len(cardData))))

    def _exportJson(self,filename):
        with open(filename,'w') as f:
            f.write(self.data.to_json())

    def _exportText(self,filename):
        with open(filename,'a+') as f:
            for index,data in self.data[['qty','name','setCode','isFoil','category']].iterrows():
                qty = str(data['qty'])+" "
                name = data['name']
                code = f" ({data['setCode']})"
                foil = "*F*" if data['isFoil'] else ""
                category = f"[{data['category']}]\n" if data['category'] else "\n"
                f.write(qty+name+code+foil+category)

    def index(self,name,setCode):
        n = self.data.copy()
        return n.loc[(n.name == name) & (n.setCode == setCode),:].index

    def addCard(self,card):
        n = self.data.copy()
        possible = n.loc[n.name == card['name']]
        if not possible.empty and card['setCode'] in possible['setCode'].values:
            i = self.index(card['name'],card['setCode'])
            n.loc[i,'qty']+=card['qty']
        else:
            n = n.append(card.data,ignore_index=True)
        self.data = n.copy()

    def addCardNS(self,name,setCode="%",qty=1):
        card = Card(name,setCode)
        card['qty'] = qty
        self.addCard(card)

    def setQty(self,name,setCode,qty):
        self.data.loc[self.index(name,setCode),'qty'] += qty