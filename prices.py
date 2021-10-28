from mtg import *
import pandas as pd
import os
import json

def paths(uuid):
    return {"TCG":[f"{homeDir}/Data/Prices/TCG/normal/{uuid}.json",f"{homeDir}/Data/Prices/TCG/foil/{uuid}.json"],"CK":[f"{homeDir}/Data/Prices/CK/normal/{uuid}.json",f"{homeDir}/Data/Prices/CK/foil/{uuid}.json"]}

def insertCheapest(p):
    cheapestMarkets = pd.eval("p.TCG - p.CK < 0")
    cheaper = lambda x: "TCG" if x else "CK"
    cheapestMarkets.normal = cheapestMarkets.normal.apply(cheaper)
    cheapestMarkets.foil = cheapestMarkets.foil.apply(cheaper)
    p[("Cheapest","normal")] = cheapestMarkets.normal
    p[("Cheapest",'foil')] = cheapestMarkets.foil
    return p

def getPrices(card):
    structure = [(x,y) for x in ['TCG','CK'] for y in ['normal','foil']]
    structure = pd.MultiIndex.from_tuples(structure)
    path = paths(card['uuid'])
    prices = [[]]
    for market in path:
        for p in path[market]:
            if os.path.exists(p):
                with open(p,'r') as f:
                    history = json.loads(f.read())
                    price = history[max(history.keys())]*card['qty'] if card['qty'] else 1
                    prices[0].append(price)
            else:
                prices[0].append(None)
    return pd.DataFrame(prices,[(card['name'],card['setCode'])],structure)

def deckPrices(deck,file=None):
    prices = []
    data = deck.data if type(deck) is Deck else deck
    for x,card in data.iterrows():
        p = getPrices(Card.fromData(card))
        prices.append(p)
    prices = pd.concat(prices,axis=0)

    if file:
        with open(file,'w') as f:
            f.write(prices.to_csv())
    return prices

def cheapestPrinting(card):
    printings = find_card(card['name'])
    printings['qty'] = 1
    p = deckPrices(printings)
    m = p.min()
    pairs = [(x,y) for x in ['TCG','CK'] for y in ['normal','foil']]
    indeces = pd.MultiIndex.from_tuples(pairs)
    cheap = [[]]
    for pair in pairs:
        cheap[0].append(p.loc[p[pair] == m[pair]].index[0][1])

    return pd.DataFrame(cheap,[card['name']],indeces)

def deckPrintings(deck):
    printings = []
    for x,card in deck.data.iterrows():
        printings.append(cheapestPrinting(card))
    printings = pd.concat(printings)
    return printings

def insertPrices(deck):
    if type(deck) is Deck:
        c = deck.data.copy()
    else:
        c = deck.copy()
    p = deckPrices(c)
    p = p.set_index(c.index)
    return pd.concat([c,p],axis=1)