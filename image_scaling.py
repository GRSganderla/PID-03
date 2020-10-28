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

def padding( imagem, height, width, channel):
    imagem_preenchida                                                        = np.zeros(( height + 4, width + 4, channel))
    imagem_preenchida[2:height + 2, 2:width + 2, : channel]                  = imagem
    
    imagem_preenchida[2:height + 2, 0 : 2, :channel]                         = imagem[: , 0 : 1, :channel]
    imagem_preenchida[height + 2:height + 4, 2:width + 2, :]                 = imagem[height - 1 :height, : , : ]
    imagem_preenchida[2:height + 2, width + 2:width + 4, :]                  = imagem[: , width - 1:width , : ]
    imagem_preenchida[0:2, 2 :width + 2, :channel]                           = imagem[ 0:1, : , :channel]
    
    imagem_preenchida[0:2 , 0:2 , :channel]                                  = imagem[0 , 0, :channel]
    imagem_preenchida[height + 2:height + 4, 0:2 , :channel]                 = imagem[height - 1, 0, :channel]
    imagem_preenchida[height + 2:height + 4, width + 2:width + 4, :channel]  = imagem[height - 1, width - 1, :channel]
    imagem_preenchida[ 0:2, width + 2:width + 4, :channel]                   = imagem[0, width - 1, :channel]
    
    return imagem_preenchida

def bicubic(imagem, novo_width:int, novo_height:int, a):
    height, width, channel = imagem.shape

    imagem = padding(imagem, height, width, channel)

    hW = 1/ (novo_width/width)
    hH = 1/ (novo_height/height)

    dst = np.zeros((novo_height, novo_width, 3))
    bar = progressbar.ProgressBar(max_value=(channel * novo_width * novo_height))

    for canal in range(Channel):
        for j in range(novo_height):
            for i in range(novo_width):
                
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
                mat_m = np.matrix([[imagem[int(y-y1),int(x-x1),c],imagem[int(y-y2),int(x-x1),c],imagem[int(y+y3),int(x-x1),c],imagem[int(y+y4),int(x-x1),c]],
                                    [imagem[int(y-y1),int(x-x2),c],imagem[int(y-y2),int(x-x2),c],imagem[int(y+y3),int(x-x2),c],imagem[int(y+y4),int(x-x2),c]],
                                    [imagem[int(y-y1),int(x+x3),c],imagem[int(y-y2),int(x+x3),c],imagem[int(y+y3),int(x+x3),c],imagem[int(y+y4),int(x+x3),c]],
                                    [imagem[int(y-y1),int(x+x4),c],imagem[int(y-y2),int(x+x4),c],imagem[int(y+y3),int(x+x4),c],imagem[int(y+y4),int(x+x4),c]]])
                
                mat_r = np.matrix([[u(y1,a)],[u(y2,a)],[u(y3,a)],[u(y4,a)]])
                dst[j, i, c] = np.dot(np.dot(mat_l, mat_m),mat_r)


                bar.update(c*(novo_width * novo_height) + j*novo_width + i)

    return dst

def bilinear(imagem, novo_width:int, novo_height:int):

    H, W, C = imagem.shape
    imagem = padding(imagem, H, W, C)

    ty = H/novo_height
    tx = W/novo_width

    dst = np.zeros((novo_height, novo_width, 3))
   
    bar = progressbar.ProgressBar(max_value=C*novo_width*novo_height)

    for c in range(C):
      for j in range(novo_height):
        for i in range(novo_width):
          
            x = int (tx * i)
            y = int (ty * j)

            x_diff = (tx * i) - x
            y_diff = (ty * j) - y

            dst[j, i, c] = imagem[y, x, c] * (1 - x_diff) * (1 - y_diff) + imagem[y, x+1, c] * (1-y_diff) * (x_diff) + imagem[y+1, x, c] * (y_diff) * (1-x_diff) + imagem[y+1, x+1, c] * (y_diff) * (x_diff)

            bar.update(c*(novo_width*novo_height) + j*novo_width + i)

    return dst

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Use 'image_scaling.py [-h | --help]' para informações de uso")
        sys.exit()

    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print('Exemplo de execução:')
        print('                     image_scaling.py <nome_arquivo> <tipo_de_interpolação> [<nome_arquivo_imagem_destino>]')
        print('')
        print('tipo_de_interpolação: informe o tipo de interpolação, -b para interpolação bilinear e -B para interpolação bicúbica. Seguido do novo width e height da imagem')
        print('                      Ex: -b=1920_1080; -B=520_480; -b=720_1080')
        sys.exit()

    if not sys.argv[1].endswith(('.png', '.jpg', '.jpeg')):
        print('Extensão de arquivo não é aceitável')
        sys.exit()

    if not re.match('-b=(\d+)_(\d+)', sys.argv[2]) and not re.match('-B=(\d+)_(\d+)', sys.argv[2]):
        print('Não informado o tipo de escalamento [Bilinear, Bicúbica] e tamanho novo da imagem')
        print('Exemplo: -b=1080_720 para usar interpolação bilinear com resolução de 1080x720')
        print('Exemplo: -B=1920_1080 para usar interpolação bicúbica com resolução de 1920x1080')
        sys.exit()

    imagem_fonte = sys.argv[1]
    mode = sys.argv[2]

    novo_width, novo_height = (re.findall('\d+', mode))
    novo_width, novo_height = int(novo_width), int(novo_height)

    imagem = cv2.imread(imagem_fonte)

    if len(sys.argv) == 4 and not sys.argv[3].endswith(('.png', '.jpg', '.jpeg')):
        print(f"Formato do Arquivo não aceitavel, utilizando {imagem_fonte[:-4] + mode[:2] + imagem_fonte[len(imagem_fonte)-4:]}")

        imagem_destino = imagem_fonte[:-4] + ('-bilinear' if mode[:2] == '-b' else '-bicúbica') + imagem_fonte[len(imagem_fonte)-4:]
        temp = imagem_destino
        i = 1 
        while glob(temp):
            print(f"Arquivo existente no diretório, utilizando {i} para identificar novo arquivo")
            temp = imagem_destino[:-4] + 'f({i})' + imagem_destino[len(imagem_fonte)-4:]
            i += 1
        imagem_destino = temp

    elif len(sys.argv) == 3:
        print(f"Arquivo de imagem_destino não informado, utilizando {imagem_fonte[:-4] + ('-bilinear' if mode[:2] == '-b' else '-bicúbica') + imagem_fonte[len(imagem_fonte)-4:]}")
        imagem_destino = imagem_fonte[:-4] + ('-bilinear' if mode[:2] == '-b' else '-bicubica') + imagem_fonte[len(imagem_fonte)-4:]
        temp = imagem_destino
        i = 1
        
        while glob(temp):
            print(f"Arquivo existente no diretório, utilizando {i} para identificar novo arquivo")
            temp = imagem_destino[:-4] + f'({i})' + imagem_destino[len(imagem_destino)-4:]
            i += 1
        imagem_destino = temp
    else: 
        imagem_destino = sys.argv[3]

        temp = imagem_destino
        i = 1
        while glob(temp):
            print(f"Arquivo existente no diretório, utilizando {i} para identificar novo arquivo")
            temp = imagem_destino[:-4] + f'({i})' + imagem_destino[len(imagem_destino)-4:]
            i += 1
        imagem_destino = temp

    if(mode[:2] == '-b'):
        dst = bilinear(imagem, novo_width, novo_height)
        cv2.imwrite(imagem_destino, dst)

    elif(mode[:2] == '-B'):
        a = -1/2
        dst = bicubic(imagem, novo_width, novo_height, a)
        cv2.imwrite(imagem_destino, dst)