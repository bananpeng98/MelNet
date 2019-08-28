import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .rnn import DelayedRNN


class Tier(nn.Module):
    def __init__(self, hp, freq, layers, first=False):
        super(Tier, self).__init__()
        num_hidden = hp.model.hidden
        self.hp = hp
        self.first = first

        self.W_t_0 = nn.Linear(1, num_hidden)
        self.W_f_0 = nn.Linear(1, num_hidden)
        self.W_c_0 = nn.Linear(freq, num_hidden)

        self.layers = nn.ModuleList([
            DelayedRNN(num_hidden) for _ in range(layers)
        ])

        # Gaussian Mixture Model: eq. (2)
        self.K = hp.model.gmm
        self.pi_softmax = nn.Softmax(dim=3)

        # map output to produce GMM parameter eq. (10)
        self.W_theta = nn.Linear(num_hidden, 3*self.K)

    def forward(self, x):
        if self.first:
            h_t = self.W_t_0(F.pad(x, [0, 0, -1, 1, 0, 0]).unsqueeze(-1))
            h_f = self.W_f_0(F.pad(x, [0, 0, 0, 0, -1, 1]).unsqueeze(-1))
            h_c = self.W_c_0(F.pad(x, [0, 0, -1, 1, 0, 0]))
        else:
            h_t = self.W_t_0(x.unsqueeze(-1))
            h_f = self.W_f_0(x.unsqueeze(-1))
            h_c = self.W_c_0(x)


        for layer in self.layers:
            h_t, h_f, h_c = layer(h_t, h_f, h_c)

        theta_hat = self.W_theta(h_f)

        mu = theta_hat[:, :, :, :self.K] # eq. (3)
        std = torch.exp(theta_hat[:, :, :, self.K:2*self.K]) # eq. (4)
        pi = self.pi_softmax(theta_hat[:, :, :, 2*self.K:]) # eq. (5)

        return mu, std, pi