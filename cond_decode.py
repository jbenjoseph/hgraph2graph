import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torch.utils.data import DataLoader

import math, random, sys
import numpy as np
import argparse

from hgraph import *
import rdkit

lg = rdkit.RDLogger.logger() 
lg.setLevel(rdkit.RDLogger.CRITICAL)

parser = argparse.ArgumentParser()
parser.add_argument('--test', required=True)
parser.add_argument('--vocab', required=True)
parser.add_argument('--atom_vocab', default=common_atom_vocab)
parser.add_argument('--model', required=True)

parser.add_argument('--num_decode', type=int, default=20)
parser.add_argument('--enum_root', action='store_true')
parser.add_argument('--cond', type=str, default="1,0,1,0")
parser.add_argument('--seed', type=int, default=1)

parser.add_argument('--rnn_type', type=str, default='LSTM')
parser.add_argument('--hidden_size', type=int, default=300)
parser.add_argument('--embed_size', type=int, default=300)
parser.add_argument('--batch_size', type=int, default=1)
parser.add_argument('--latent_size', type=int, default=4)
parser.add_argument('--depthT', type=int, default=20)
parser.add_argument('--depthG', type=int, default=20)
parser.add_argument('--diterT', type=int, default=1)
parser.add_argument('--diterG', type=int, default=3)
parser.add_argument('--dropout', type=float, default=0.0)

args = parser.parse_args()

args.test = [line.strip("\r\n ") for line in open(args.test)]
vocab = [x.strip("\r\n ").split() for x in open(args.vocab)] 
args.vocab = PairVocab(vocab)

assert args.cond in ['1,0,1,0', '0,1,1,0', '1,0,0,1']
cond = map(float, args.cond.split(','))
args.cond_size = len(cond)
cond = torch.tensor(cond).cuda()

model = HierCondVGNN(args).cuda()
model.load_state_dict(torch.load(args.model))
model.eval()

dataset = MolEnumRootDataset(args.test, args.vocab, args.atom_vocab)
loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0, collate_fn=lambda x:x[0])

torch.manual_seed(args.seed)
with torch.no_grad():
    for i,batch in enumerate(loader):
        new_mols = model.translate(batch[1], cond, args.num_decode, args.enum_root)
        smiles = args.test[i]
        for k in xrange(args.num_decode):
            print smiles, new_mols[k]

