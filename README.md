# PID-03
Repositorio para implementação de uma escalador de imagem para o trabalho de tema 3 da matéria de Processamento de Imagens Digitais

## Uso

> $ py image_scaling.py [-h | --help | <nome_da_imagem>] [-b=Width_Height | -B=Width_Height] [<nome_da_imagem_destino>]

## Exemplos

Se usado o comando:
> py image_scaling.py -h 
> py image_scaling.py --help
É apresentado todas as opções de uso para o script.

Para alterar a resolução espacial de uma imagem(exemplo.png) para uma resolução de 1080x920 utilizando a interpolação bilinear, se usa a linha de comando:
> py image_scaling.py exemplo.png -b=1080_920 

Nota o fato que o arquivo de destino não foi citado, então é gerado o arquivo "exemplo-bilinear.png"

Para se alterar a resolução utilizando a interpolação bicúbica, da mesma imagem de exemplo, se utiliza o comando:
> py image_scaling.py exemplo.png -B=720_480 exemplo_hd.png

Nesse caso, se gera uma imagem de destino chamada de "exemplo_hd.png" de resolução 720x480. 