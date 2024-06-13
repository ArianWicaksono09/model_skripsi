import numpy as np
import nltk
#nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

stemmer_en = PorterStemmer()
factory_id = StemmerFactory()
stemmer_id = factory_id.create_stemmer()

def tokenize(sentence):
    return nltk.word_tokenize(sentence)

def stem(word, lang):
    if lang == 'id':
        return stemmer_id.stem(word.lower())
    elif lang == 'en':
        return stemmer_en.stem(word.lower())
    else:
        raise ValueError("Unsupported language")

def bag_of_words(tokenized_sentence, words, lang):
    if lang == 'id':
        sentence_words = [stem(word, 'id') for word in tokenized_sentence]
    elif lang == 'en':
        sentence_words = [stem(word, 'en') for word in tokenized_sentence]
    else:
        raise ValueError("Unsupported language")

    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words: 
            bag[idx] = 1

    return bag

