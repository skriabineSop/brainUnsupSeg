import os
import torch
from torch import nn
from torch.autograd import Variable
from torch.utils.data import DataLoader # , Dataset
from dataset import Dataset
from visualize import plot3d, show
import numpy as np
from tensorboardX import SummaryWriter

num_epochs = 100
batch_size = 128
learning_rate = 1e-3

workdir = '/mnt/raid/UnsupSegment/patches/10-43-24_IgG_UltraII[02 x 05]_C00'
logdir = 'logs'
savedmodeldir = 'savedModels'

writer = SummaryWriter(logdir)

# autoencoder test
class autoencoder(nn.Module):

    def __init__(self):
        super(autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv3d(1, 32, 3, stride=1, padding=(1, 1, 1)),
            nn.ReLU(True),
            nn.Conv3d(32, 16, 3, stride=1, padding=(1, 1, 1)),
            nn.ReLU(True),
            nn.Conv3d(16, 2, 3, stride=1, padding=(1, 1, 1)),
            nn.Softmax(dim=1))

        self.decoder = nn.Sequential(
            nn.Conv3d(2, 16, 3, stride=1, padding=(1, 1, 1)),
            nn.ReLU(True),
            nn.Conv3d(16, 32, 3, stride=1, padding=(1, 1, 1)),
            nn.ReLU(True),
            nn.Conv3d(32, 1, 3, stride=1, padding=(1, 1, 1)))

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


def preprocess(x):
    x = torch.clamp(x, max=20000.)
    x = torch.clamp(x, min=500.)
    x -= 500.
    x /= 19500
    return x


def main():

    print("load dataset")
    dataset = Dataset(workdir)
    dataloader = DataLoader(dataset, shuffle=True,  batch_size=16)

    print("Initialize model")
    if torch.cuda.is_available():
        model = autoencoder().cuda()
    else:
        model = autoencoder()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)

    print("begin training")
    num_iteration = 0

    for epoch in range(num_epochs):
        for data in dataloader:
            if torch.cuda.is_available():
                img = data.float().cuda()
            else:
                img = data.float()
            # ===================preprocess=====================
            img = preprocess(img)
            img = Variable(img)
            # ===================forward=====================
            output = model(img)
            loss = criterion(output, img)
            writer.add_scalar('Train/Loss', loss, num_iteration)
            if num_iteration % 500 == 0:
                writer.add_image('Train/Input', img.data[0, :, 20], num_iteration)
                writer.add_image('Train/Output', output.data[0, :, 20], num_iteration)
                np.save(os.path.join(logdir, 'output_' + str(num_iteration)), output.data[0, 0])
                np.save(os.path.join(logdir, 'input_' + str(num_iteration)), img.data[0, 0])
            # ===================backward====================
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            num_iteration += 1
        # ===================log========================
        print('epoch [{}/{}], loss:{:.4f}'
              .format(epoch + 1, num_epochs, loss.data[0]))
        if epoch % 10 == 0:
            # check the output
            print('save picture')
        torch.save(model.state_dict(), os.path.join(savedmodeldir, 'sim_autoencoder.pth'))


def test():
    dataset = Dataset(workdir)
    dataloader = DataLoader(dataset)
    if torch.cuda.is_available():
        model = autoencoder().cuda()
    else:
        model = autoencoder()

    for data in dataloader:
        if torch.cuda.is_available():
            img = data.float().cuda()
        else:
            img = data.float()
        plot3d(np.array(img).reshape((40, 40, 40)))
        show()

        output = model(Variable(img))
        plot3d(np.array(output.data).reshape((40, 40, 40)))
        show()


if __name__ == "__main__":
    main()
