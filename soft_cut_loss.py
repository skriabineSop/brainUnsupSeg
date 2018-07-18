import os
import torch
from torch import nn
from torch.autograd import Variable
from torch.utils.data import DataLoader  # , Dataset
from dataset import Dataset
from visualize import plot3d, show
import numpy as np
from tensorboardX import SummaryWriter
import torch.nn.functional as F

class Soft_cut_loss(torch.nn.Module):

    def __init__(self):
        super(Soft_cut_loss, self).__init__()

    def forward(self, x, kernel):
        print('compute soft loss')
        # if torch.cuda.is_available():
        #     res = Variable(torch.tensor(0).float().cuda(), requires_grad=True)
        # else:
        #     res = Variable(torch.tensor(0).float(), requires_grad=True)

        # kernel = Variable(kernel, requires_grad=True)
        # x = Variable(x, requires_grad=True)
        # print( res.type())
        # print( kernel.type())
        # print(x.type())
        for i in range(x.shape[1]):
            gauss = Variable(F.conv3d(x[:, i:i + 1, :, :, :],
                             kernel[np.newaxis, :], bias=None, stride=1, padding=(5, 5, 5)))
            print(gauss.type())
            #gauss = Variable(gauss, requires_grad=True)
            mul = torch.mul(x[:, i:i + 1, :, :, :], gauss)
            # print(type(mul))
            numerator = torch.sum(mul)
            sum_gauss = torch.sum(gauss)
            sub_denom = torch.mul(x[:, i:i + 1, :, :, :], sum_gauss)
            denom = torch.sum(sub_denom)
            res = numerator / denom
            # print(type(res))

        result = x.shape[1] - res
        print('result :',  result.type())
        return result



