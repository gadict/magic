import re
import sys
import os
import argparse
from pathlib import Path
from mtg import Deck
from mtg import Card
from mtg import connectDB
def categorize(deck,quickFilters=[]):
  patterns = {'draw':re.compile(r"draw",re.IGNORECASE),
              'ramp':re.compile(r'([Ss]earch your library for\s\D+\sland\scard[s]*)|((\{T\}:)*\s[aA]dd\s(((\{[\d+CWUBRG]\})+)|(.*mana\sof\s(any one|each|any|one)\scolor)))',re.IGNORECASE),
              'tutor':re.compile(r'(?!\sland)search your library for ((.*)[,]*)+\.',re.IGNORECASE),
              'sacOutlet':re.compile(r"Sacrifice\s(?:any number of|\d|a|X|another)\s(?:.+):\s(?:.+)\.+"),
              'removal':re.compile(r"((Destroy|Exile)\s(target|any number of target|X target|all|each|a)(?!\scard)([\w\s,']+)\.)|((return\s(target|each|X)\s\D+\sto\s(it's owner's|their)\shand[s]*))|((each|target|any number of target)\s(player[s]*|opponent[s]*)\ssacrifice[s]*)",re.IGNORECASE),
              'buffCounters':re.compile(r"\+1/\+1\scounter[s]*"),
              'tribal':re.compile(r"(each|all)*\s\D+\syou\scontrol\s(get[s]*|gain[s]*|has|become[s]*|lose[s]*)+",re.IGNORECASE),
              'counterspell':re.compile(r"Counter\starget.*spell.*\.",re.IGNORECASE),
              'life':re.compile(r"(gain[s]*|lose[s]*)\s(\d+\s)+life|lifelink",re.IGNORECASE),
              'landfall':re.compile(r"whenever.*land[s]+\senter[s]+\sthe\sbattlefield",re.IGNORECASE),
              'graveyard':re.compile('graveyard', re.IGNORECASE),
              'tokens':re.compile('token[s]*',re.IGNORECASE)}

  for x in quickFilters:
    if type(x) is list:
      patterns[x[0]] = re.compile(x[1], re.IGNORECASE)
    else:
      patterns[x] = re.compile(x, re.IGNORECASE)
  
  categories = {}
  for x in patterns.keys():
      categories[x] = []
                                

       
  checked = []
  for cat in categories.keys():
      p = patterns[cat]
        
      for card in deck.cards.keys():
          if card['category'] == "":
              if card not in checked:
                  text = card['text']
                  res = p.search(text)
                  if res != None:
                      if cat == "ramp":
                          if card['types'] != "Land":
                              categories[cat].append(card)
                              card.cardInfo['category'] = cat
                              checked.append(card)
                      else:
                          categories[cat].append(card)
                          card.cardInfo['category'] = cat
                          checked.append(card)
          else:
              checked.append(card)
              categories[cat].append(card)

  misc = [x for x in deck.cards.keys() if x not in checked]
  for x in misc:
    if x['types'] != "Land" and card['supertypes'] != "Basic" and x['category'] == "":
      x.cardInfo['category'] = "misc"
  
  return (categories,checked)

if __name__ == "__main__":
  args = argparse.ArgumentParser()
  args.add_argument('file', type=str)
  info = args.parse_args() if len(sys.argv)>1 else str(input("Enter filename: "))
  name = info.file
  
  if name != "":
    db = connectDB().cursor()
    d = Deck(name.split(".")[0],name,db=db)
    categorize(d)
    d.exportText(name.split(".")[0]+"-categorized.txt")
    d.exportJSON(name.split(".")[0]+"-categorized.json")
    
