from mtg import Deck, connectDB, SimpleCard, homeDir
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
from prices import getPrice

def checkColors(colors1,colors2):
    if colors1 == None:
        return True
    if colors2 == None:
        return True if colors1 == None else False
    for color in colors1.split(','):
        if color not in colors2:
            return False
    return True



def buildTransformer():
    modelname = "bert-base-nli-mean-tokens"
    return SentenceTransformer(modelname)


def buildCardDataset():
    query = """SELECT DISTINCT name, text, colors, setCode FROM cards 
    INNER JOIN legalities 
    ON legalities.uuid=cards.uuid 
    AND legalities.format='commander' AND legalities.status='Legal'
    WHERE isTextless=0 
    ORDER BY name;"""
    db = connectDB().cursor()
    q = db.execute(query)
    r = q.fetchall()

    names = [card[0] for card in r]
    texts = [card[1] for card in r]
    colors = [card[2] for card in r]
    sets = [card[3] for card in r]
    fixedNames, fixedTexts, fixedColors, fixedSets = [],[],[],[]
    for x in range(len(names)):
        if texts[x] != None and names[x] not in fixedNames:
            fixedNames.append(names[x])
            fixedTexts.append(texts[x])
            fixedColors.append(colors[x])
            fixedSets.append(sets[x])
    #Probably entirely unnecessary. But I don't trust a feature with 'garbage' in the name.
    names.clear()
    texts.clear()
    colors.clear()
    sets.clear()
    r.clear()
    return [fixedNames,fixedTexts,fixedColors,fixedSets]


def processDeck(deck, trans, dataset, colors='W,U,B,R,G', simThreshold=0.81):
    fixedNames,fixedTexts,fixedColors,fixedSets = dataset
    with open(f"{homeDir}/data/text/text_vecs.json",'r') as f:
        text_vecs = json.loads(f.read())

    possible_includes = {}
    cached_cards = {}
    for card in deck.allCards():
        if getPrice(card)>15:
            c = cosine_similarity(
                [trans.encode(card['text'])], 
                text_vecs
            )
            possible_includes[card] = []
            for x in range(len(fixedNames)):
                if checkColors(fixedColors[x],colors):
                    if c[0][x] > simThreshold:
                        if not fixedNames[x] in cached_cards.keys():
                            tcard = SimpleCard(fixedNames[x], fixedSets[0])
                            tcard.cardInfo['text'] = fixedTexts[x]
                            tcard.cardInfo['colors'] = fixedColors[x]
                            cached_cards[fixedNames[x]] = tcard
                        possible_includes[card].append(cached_cards[fixedNames[x]])
    return possible_includes

