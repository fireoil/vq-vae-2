"""
Train a PixelCNN on MNIST using a pre-trained VQ-VAE.
"""

import os

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.datasets
import torchvision.transforms

from vq_vae_2.examples.mnist.model import Encoder, Generator

BATCH_SIZE = 32
LR = 1e-3


def main():
    encoder = Encoder()
    encoder.load_state_dict(torch.load('enc.pt'))
    encoder.eval()

    generator = Generator()
    if os.path.exists('gen.pt'):
        generator.load_state_dict(torch.load('gen.pt'))

    optimizer = optim.Adam(generator.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss()

    test_images = load_images(train=False)
    for batch_idx, images in enumerate(load_images()):
        losses = []
        for img_set in [images, next(test_images)]:
            _, (_, _, encoded) = encoder(img_set)
            logits = generator(encoded)
            logits = logits.permute(0, 2, 3, 1).contiguous()
            logits = logits.view(-1, logits.shape[-1])
            losses.append(loss_fn(logits, encoded.view(-1)))
        optimizer.zero_grad()
        losses[0].backward()
        optimizer.step()
        print('train=%f test=%f' % (losses[0].item(), losses[1].item()))
        if not batch_idx % 100:
            torch.save(generator.state_dict(), 'gen.pt')


def load_images(train=True):
    while True:
        for data, _ in create_data_loader(train):
            yield data


def create_data_loader(train):
    mnist = torchvision.datasets.MNIST('./data', train=train, download=True,
                                       transform=torchvision.transforms.ToTensor())
    return torch.utils.data.DataLoader(mnist, batch_size=BATCH_SIZE, shuffle=True)


if __name__ == '__main__':
    main()
