import re
from mtg import Card,Deck,nonland
def categorize(deck,quickFilters=[]):
  if type(deck) is Deck:
    data = deck.data
  else:
    data = deck

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
      for x,c in nonland(data).iterrows():
        card = Card.fromData(c)
        if not (card.NS() in checked):
            if p.search(card['text']):
              data.loc[x,'category'] =  cat
              checked.append(card.NS())

  return data

def catCard(card,quickFilters=[]):
  categories = {}
  for x in patterns.keys():
      categories[x] = []

  if type (card) is Card:
    data = card.data
  else:
    data = card

  for x in quickFilters:
    if type(x) is list:
      patterns[x[0]] = re.compile(x[1], re.IGNORECASE)
    else:
      patterns[x] = re.compile(x, re.IGNORECASE)

  for cat in categories.keys():
    p = patterns[cat]
    if p.search(card['text']):
      data['category'] =  cat
      return data
  data['category'] = ""
  return data
  



        
patterns = {'Draw':re.compile(r"draw",re.IGNORECASE),
            'Ramp':re.compile(r'([Ss]earch your library for\s\D+\sland\scard[s]*)|((\{T\}:)*\s[aA]dd\s(((\{[\d+CWUBRG]\})+)|(.*mana\sof\s(any one|each|any|one)\scolor)))',re.IGNORECASE),
            'Tutors':re.compile(r'(?!\sland)search your library for ((.*)[,]*)+\.',re.IGNORECASE),
            'Sacrifice Outlets':re.compile(r"Sacrifice\s(?:any number of|\d|a|X|another)\s(?:.+):\s(?:.+)\.+"),
            'Removal':re.compile(r"((Destroy|Exile)\s(target|any number of target|X target|all|each|a)(?!\scard)([\w\s,']+)\.)|((return\s(target|each|X)\s\D+\sto\s(it's owner's|their)\shand[s]*))|((each|target|any number of target)\s(player[s]*|opponent[s]*)\ssacrifice[s]*)",re.IGNORECASE),
            '+1/+1 Counters':re.compile(r"\+1/\+1\scounter[s]*"),
            'Tribal':re.compile(r"((each|all|creatures)*[\s\D]*\syou\scontrol\s(get[s]*|gain[s]*|has|have|become[s]*|lose[s]*)|(choose a ((creature type)|color)))+",re.IGNORECASE),
            'Counterspell':re.compile(r"Counter\starget.*spell.*\.",re.IGNORECASE),
            'Life':re.compile(r"(gain[s]*|lose[s]*)\s(\d+\s)+life|lifelink",re.IGNORECASE),
            'Landfall':re.compile(r"whenever.*land[s]+\senter[s]+\sthe\sbattlefield",re.IGNORECASE),
            'Graveyard':re.compile(r'graveyard', re.IGNORECASE),
            'Tokens':re.compile(r'token[s]*',re.IGNORECASE)
            }