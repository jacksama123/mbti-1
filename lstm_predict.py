import os
import pickle
import sys

import numpy as np
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable

from config import parse_config
from lstm import LSTMClassifier, MbtiDataset
from preprocess import preprocess_text
from utils import FIRST, FOURTH, SECOND, THIRD, codes, get_char_for_binary
from word2vec import load_word2vec, word2vec


def np_sentence_to_list(L_sent):
    newsent = []
    for sentance in L_sent:
        temp = []
        for word in sentance:
            temp.append(word.tolist())
        newsent.append(temp)
    return newsent


def load_model(config, code):
    model_file = 'saves/{}_model'.format(code)
    model = LSTMClassifier(
        config,
        embedding_dim=config.feature_size,
        hidden_dim=128,
        label_size=2)
    model.load_state_dict(torch.load(model_file))
    return model


def predict(config, text, code, model=None):
    if model is None:
        model = load_model(config, code)

    preprocessed = preprocess_text(text)

    word_model = load_word2vec(config.embeddings_model)
    embedding = []
    embedding = []
    for word in preprocessed.split(' '):
        if word in word_model.wv.index2word:
            vec = word_model.wv[word]
            embedding.append(vec)

    input = Variable(torch.Tensor(np_sentence_to_list(embedding)))

    pred = model(input)
    pred_label = pred.data.max(1)[1].numpy()[0]
    pred_char = get_char_for_binary(code, pred_label)
    return pred_char


if __name__ == '__main__':
    config = get_config()

    if sys.stdin.isatty():
        text = raw_input('Enter some text: ')
    else:
        text = sys.stdin.read()

    personality = ''
    codes = [FIRST, SECOND, THIRD, FOURTH]
    for code in codes:
        personality += predict(code, text)

    print('Prediction is {}'.format(personality))
