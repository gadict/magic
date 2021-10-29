from mtg import *
from sentence_transformers import SentenceTransformer as ST
from sentence_transformers.util import pairwise_dot_score
from categorize import *
import pandas as pd
import torch

def dataset():
    data = formatLegal("commander")
    data = data.drop_duplicates('name')
    data = data.dropna(axis=0, subset=['text'])
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
        mask = cardDataset['colors'].apply(lambda colors: compareColors(colors,card['colorIdentity']))
        cardDataset = cardDataset.loc[mask,:]
    if byCategory:
        card = catCard(card)
        cardDataset = categorize(cardDataset)
        mask = cardDataset.loc[cardDataset.category == card.category,:].index
        cardDataset = cardDataset.loc[mask,:]
    return cardDataset    

def defaultModel():
    model = "bert-base-nli-mean-tokens"
    tf = ST(f"{homeDir}/data/text/sentence-transformers_bert-base-nli-mean-tokens",cache_folder=f"{homeDir}/data/text")
    return tf