from mtg import *
from sentence_transformers import SentenceTransformer as ST
from sentence_transformers.util import pairwise_dot_score
from categorize import *
import pandas as pd


def dataset():
    data = formatLegal("commander")
    #Drop duplicate cards by name, then drop cards with no rules text
    data = data.drop_duplicates('name')
    data = data.dropna(axis=0,subset=['text'])
    #The join inserts matching columns, in this case just UUID and ID, this probably isn't the optimal
    #way of querying for legality, but it works and this isn't terribly expensive to do after the fact.
    data.drop(['uuid_1','id_1'],axis=1,inplace=True)
    return data

def cachedEmbeds(file=f"{homeDir}/data/text/text_embeds.json"):
    return np.array(json.loads(open(file).read()))

def findSimilarCards(card,transformer,cardDataset,embeds,thresh=0.8,byCategory=False,byColors=True):
    if type(card) is Card:
        card = card.data
    text = transformer.encode(card['text'],normalize_embeddings=True)
    scores = pd.Series(pairwise_dot_score([text],embeds), index=cardDataset.index)
    cardDataset['score'] = scores
    mask = cardDataset.loc[cardDataset.score >= thresh,:].index
    cardDataset = cardDataset.loc[mask,:]
    if byColors:
        mask = cardDataset['colorIdentity'].apply(lambda colors: compareColors(colors,card['colorIdentity']))
        cardDataset = cardDataset.loc[mask,:]
    if byCategory:
        if card['category'] != None:
            card = catCard(card)
        cardDataset = categorize(cardDataset)
        mask = cardDataset.loc[cardDataset.category == card.category,:].index
        cardDataset = cardDataset.loc[mask,:]
    return cardDataset    

def defaultModel():
    model = "bert-base-nli-mean-tokens"
    tf = ST(f"{homeDir}/data/text/sentence-transformers_bert-base-nli-mean-tokens",cache_folder=f"{homeDir}/data/text")
    return tf