import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np

# 하이퍼파라미터 설정
EPOCHS = 200
BATCH_SIZE = 32
LR = 0.0002
BETA1 = 0.5
LATENT_DIM = 100
IMG_SIZE = 128
CHANNELS = 1

# Mac 최적화(MPS) 또는 CPU 사용 설정
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

# 데이터 로드 (흑백 1채널, 128x128 리사이즈 후 [-1, 1] 정규화)
transform = transforms.Compose([
    transforms.Grayscale(CHANNELS),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

dataset = torchvision.datasets.ImageFolder(root='data/gan_train', transform=transform)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

print(f"Total batches per epoch: {len(dataloader)}")

# DCGAN 모델 아키텍처
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.main = nn.Sequential(
            # Input: 100 x 1 x 1
            nn.ConvTranspose2d(LATENT_DIM, 512, 4, 1, 0, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            # State: 512 x 4 x 4
            nn.ConvTranspose2d(512, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            # State: 256 x 8 x 8
            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            # State: 128 x 16 x 16
            nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            # State: 64 x 32 x 32
            nn.ConvTranspose2d(64, 32, 4, 2, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            # State: 32 x 64 x 64
            nn.ConvTranspose2d(32, CHANNELS, 4, 2, 1, bias=False),
            nn.Tanh()
            # Final: 1 x 128 x 128
        )

    def forward(self, input):
        return self.main(input)

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.main = nn.Sequential(
            # Input: 1 x 128 x 128
            nn.Conv2d(CHANNELS, 32, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            # State: 32 x 64 x 64
            nn.Conv2d(32, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),
            # State: 64 x 32 x 32
            nn.Conv2d(64, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            # State: 128 x 16 x 16
            nn.Conv2d(128, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            # State: 256 x 8 x 8
            nn.Conv2d(256, 512, 4, 2, 1, bias=False),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),
            # State: 512 x 4 x 4
            nn.Conv2d(512, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )

    def forward(self, input):
        return self.main(input).view(-1, 1).squeeze(1)

# 네트워크 초기화
netG = Generator().to(device)
netD = Discriminator().to(device)

criterion = nn.BCELoss()
optimizerD = optim.Adam(netD.parameters(), lr=LR, betas=(BETA1, 0.999))
optimizerG = optim.Adam(netG.parameters(), lr=LR, betas=(BETA1, 0.999))

os.makedirs('results/gan_samples', exist_ok=True)
os.makedirs('models/generator', exist_ok=True)

# 시각화 검증용 고정 노이즈
fixed_noise = torch.randn(16, LATENT_DIM, 1, 1, device=device)

print("\n=== GAN 학습 시작 (Total Epochs: 200) ===")
for epoch in range(EPOCHS):
    for i, data in enumerate(dataloader, 0):
        # --- 1. Discriminator 학습 ---
        netD.zero_grad()
        real_cpu = data[0].to(device)
        b_size = real_cpu.size(0)
        label = torch.full((b_size,), 1.0, dtype=torch.float, device=device)
        output = netD(real_cpu)
        errD_real = criterion(output, label)
        errD_real.backward()
        
        noise = torch.randn(b_size, LATENT_DIM, 1, 1, device=device)
        fake = netG(noise)
        label.fill_(0.0)
        output = netD(fake.detach())
        errD_fake = criterion(output, label)
        errD_fake.backward()
        optimizerD.step()

        # --- 2. Generator 학습 ---
        netG.zero_grad()
        label.fill_(1.0)
        output = netD(fake)
        errG = criterion(output, label)
        errG.backward()
        optimizerG.step()
        
    if (epoch+1) % 10 == 0 or epoch == 0:
        print(f'[Epoch {epoch+1:03d}/{EPOCHS}] Loss_D: {errD_real.item() + errD_fake.item():.4f} Loss_G: {errG.item():.4f}')
        # 샘플 이미지 저장
        with torch.no_grad():
            fake = netG(fixed_noise).detach().cpu()
        grid = torchvision.utils.make_grid(fake, padding=2, normalize=True)
        plt.figure(figsize=(6,6))
        plt.axis("off")
        plt.title(f"Fake Void Images (Epoch {epoch+1})")
        # 1채널 흑백이므로 컬러맵 처리
        plt.imshow(np.transpose(grid, (1,2,0)))
        plt.savefig(f"results/gan_samples/fake_epoch_{epoch+1:03d}.png")
        plt.close()

# 모델 저장
torch.save(netG.state_dict(), 'models/generator/dcgan_g.pt')
torch.save(netD.state_dict(), 'models/generator/dcgan_d.pt')
print("\n=== 학습 완료! ===")
print("Generator 가중치: models/generator/dcgan_g.pt")
print("Discriminator 가중치: models/generator/dcgan_d.pt")
print("생성 샘플 이미지 확인: results/gan_samples/")
