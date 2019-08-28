import os
import glob
import torch
import random
import numpy as np
from torch.utils.data import Dataset, DataLoader

from utils.utils import read_wav_np


def create_dataloader(hp, args, train):
    if train:
        return DataLoader(dataset=AudioOnlyDataset(hp, args, True),
                          batch_size=hp.train.batch_size,
                          shuffle=True,
                          num_workers=hp.train.num_workers,
                          pin_memory=True,
                          drop_last=True)
    else:
        return DataLoader(dataset=AudioOnlyDataset(hp, args, False),
                          batch_size=1,
                          shuffle=False,
                          num_workers=1,
                          pin_memory=True,
                          drop_last=False)


class AudioOnlyDataset(Dataset):
    def __init__(self, hp, args, train):
        self.hp = hp
        self.args = args
        self.train = train
        self.data = hp.data.train if train else hp.data.test

        self.wav_list = glob.glob(os.path.join(self.data, '**', '*.wav'), recursive=True)

    def __len__(self):
        return len(self.wav_list)

    def __getitem__(self, idx):
        wav = read_wav_np(self.wav_list[idx])
        return wav


class AudioTextDataset(Dataset):
    def __init__(self, hp, args, train):
        self.hp = hp
        self.args = args
        self.train = train

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self):
        raise NotImplementedError