import cv2
import numpy as np
import math
import sys
import re
from glob import glob
import time
import progressbar

def u(s,a):
    if (abs(s) >=0) & (abs(s) <=1):
        return (a+2)*(abs(s)**3)-(a+3)*(abs(s)**2)+1
    elif (abs(s) > 1) & (abs(s) <= 2):
        return a*(abs(s)**3)-(5*a)*(abs(s)**2)+(8*a)*abs(s)-4*a
    return 0

def padding(img,H,W,C):
    zimg = np.zeros((H+4,W+4,C))
    zimg[2:H+2,2:W+2,:C] = img
    
    zimg[2:H+2,0:2,:C]=img[:,0:1,:C]
    zimg[H+2:H+4,2:W+2,:]=img[H-1:H,:,:]
    zimg[2:H+2,W+2:W+4,:]=img[:,W-1:W,:]
    zimg[0:2,2:W+2,:C]=img[0:1,:,:C]
    
    zimg[0:2,0:2,:C]=img[0,0,:C]
    zimg[H+2:H+4,0:2,:C]=img[H-1,0,:C]
    zimg[H+2:H+4,W+2:W+4,:C]=img[H-1,W-1,:C]
    zimg[0:2,W+2:W+4,:C]=img[0,W-1,:C]
    
    return zimg

def bicubic(img, dW:int, dH:int, a):
    H,W,C = img.shape

    img = padding(img, H, W, C)

    hW = 1/ (dW/W)
    hH = 1/ (dH/H)

    dst = np.zeros((dH, dW, 3))
    bar = progressbar.ProgressBar(max_value=C*dW*dH)

    for c in range(C):
        for j in range(dH):
            for i in range(dW):
                x, y = i * hW + 2 , j * hH + 2

                x1 = 1 + x - math.floor(x)
                x2 = x - math.floor(x)
                x3 = math.floor(x) + 1 - x
                x4 = math.floor(x) + 2 - x

                y1 = 1 + y - math.floor(y)
                y2 = y - math.floor(y)
                y3 = math.floor(y) + 1 - y
                y4 = math.floor(y) + 2 - y

                mat_l = np.matrix([[u(x1,a),u(x2,a),u(x3,a),u(x4,a)]])
                mat_m = np.matrix([[img[int(y-y1),int(x-x1),c],img[int(y-y2),int(x-x1),c],img[int(y+y3),int(x-x1),c],img[int(y+y4),int(x-x1),c]],
                                    [img[int(y-y1),int(x-x2),c],img[int(y-y2),int(x-x2),c],img[int(y+y3),int(x-x2),c],img[int(y+y4),int(x-x2),c]],
                                    [img[int(y-y1),int(x+x3),c],img[int(y-y2),int(x+x3),c],img[int(y+y3),int(x+x3),c],img[int(y+y4),int(x+x3),c]],
                                    [img[int(y-y1),int(x+x4),c],img[int(y-y2),int(x+x4),c],img[int(y+y3),int(x+x4),c],img[int(y+y4),int(x+x4),c]]])
                mat_r = np.matrix([[u(y1,a)],[u(y2,a)],[u(y3,a)],[u(y4,a)]])
                dst[j, i, c] = np.dot(np.dot(mat_l, mat_m),mat_r)
                bar.update(c*(dW*dH) + j*dW + i)

    return dst

def bilinear(img, dW:int, dH:int):

    H, W, C = img.shape
    img = padding(img, H, W, C)

    ty = H/dH
    tx = W/dW

    dst = np.zeros((dH, dW, 3))
   
    bar = progressbar.ProgressBar(max_value=C*dW*dH)

    for c in range(C):
      for j in range(dH):
        for i in range(dW):
          
            x = int (tx * i)
            y = int (ty * j)

            x_diff = (tx * i) - x
            y_diff = (ty * j) - y

            dst[j, i, c] = img[y, x, c] * (1 - x_diff) * (1 - y_diff) + img[y, x+1, c] * (1-y_diff) * (x_diff) + img[y+1, x, c] * (y_diff) * (1-x_diff) + img[y+1, x+1, c] * (y_diff) * (x_diff)

            bar.update(c*(dW*dH) + j*dW + i)

    return dst

if sys.argv[1] == ['-h', '--help']:
    print('image_scaling.py <nome_arquivo> <tipo_de_interpolação> [<nome_arquivo_destino>]')
    print('tipo_de_interpolação: informe o tipo de interpolação, -b para interpolação bilinear e -B para interpolação bicúbica. Seguido do novo width e height da imagem')
    print('Ex: -b=1920_1080; -B=520_480; -b=720_1080')
    sys.exit()

if not sys.argv[1].endswith(('.png', '.jpg', '.jpeg')):
    print('Extensão de arquivo não é aceitável')
    sys.exit()

if not re.match('-b=(\d+)_(\d+)', sys.argv[2]) and not re.match('-B=(\d+)_(\d+)', sys.argv[2]):
    print('Não informado o tipo de escalamento [Bilinear, Bicúbica]')
    sys.exit()

if __name__ == "__main__":
    source_img = sys.argv[1]
    mode = sys.argv[2]

    dW, dH = (re.findall('\d+', mode))
    dW, dH = int(dW), int(dH)

    img = cv2.imread(source_img)

    a = -1/2

    if len(sys.argv) == 4 and not sys.argv[3].endswith(('.png', '.jpg', '.jpeg')):
        print(f"Formato do Arquivo não aceitavel, utilizando {source_img[:-4] + mode[:2] + source_img[len(source_img)-4:]}")

        destino = source_img[:-4] + ('-bilinear' if mode[:2] == '-b' else '-bicúbica') + source_img[len(source_img)-4:]
        temp = destino
        i = 1 
        while glob(temp):
            print(f"Arquivo existente no diretório, utilizando {i} para identificar novo arquivo")
            temp = destino[:-4] + 'f({i})' + destino[len(source_img)-4:]
            i += 1
        destino = temp

    elif len(sys.argv) == 3:
        print(f"Arquivo de destino não informado, utilizando {source_img[:-4] + ('-bilinear' if mode[:2] == '-b' else '-bicúbica') + source_img[len(source_img)-4:]}")
        destino = source_img[:-4] + ('-bilinear' if mode[:2] == '-b' else '-bicubica') + source_img[len(source_img)-4:]
        temp = destino
        i = 1
        
        while glob(temp):
            print(f"Arquivo existente no diretório, utilizando {i} para identificar novo arquivo")
            temp = destino[:-4] + f'({i})' + destino[len(destino)-4:]
            i += 1
        destino = temp
    else: 
        destino = sys.argv[3]

        temp = destino
        i = 1
        while glob(temp):
            print(f"Arquivo existente no diretório, utilizando {i} para identificar novo arquivo")
            temp = destino[:-4] + f'({i})' + destino[len(destino)-4:]
            i += 1
        destino = temp

    if(mode[:2] == '-b'):
        dst = bilinear(img, dW, dH)
        cv2.imwrite(destino, dst)
    elif(mode[:2] == '-B'):
        dst = bicubic(img, dW, dH, a)
        cv2.imwrite(destino, dst)