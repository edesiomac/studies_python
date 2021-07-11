#Este projeto consiste em pegar dados sobre a COVID19 de uma API 
#pública e gerar gráficos com esses dados

from typing import Text
import requests as r
import datetime as dt
import csv
from PIL import Image
from IPython.display import display
from urllib.parse import quote
#criando variáveis como espécie de constantes para me ajudar a referenciar cada posição dentro da lista
CONFIRMADOS = 0
MORTOS = 1
RECUPERADOS = 2
ATIVOS = 3
DATA = 4

url = 'https://api.covid19api.com/dayone/country/brazil'

req = r.get(url)#criei uma variável que recebe os dados requisitados na AP

dados_iniciais = req.json() #essa variável ta recebendo os dados requisitados na API e formatá-los em JSON
#print(req.status_code)
#print(dados_iniciais)#imprimindos os dados

#criei uma varíavel onde vou armazenar somente os dados que eu vou ultilizar com observação
dados_finais = []

for obs in dados_iniciais:
    dados_finais.append([obs['Confirmed'], obs['Deaths'], obs['Recovered'], obs['Active'], obs['Date']])
print(['Confirmados', 'Mortos', 'Recuperados', 'Ativos', 'Data'])

for i in range(1, len(dados_finais)):
    dados_finais[i][DATA] = dados_finais[i][DATA][:10]
    
for i in range(1, len(dados_finais)):
    dados_finais[i][DATA] = dt.datetime.strptime(dados_finais[i][DATA], '%Y-%m-%d')

#gravar os dados finais dentro de um arquivo CSV
with open('brasil_covid19', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(dados_finais)

#criando algumas funções helprs para ajudar na criação do gráfico que vamos gerar

#essa funcão é responsável pelas chaves datasets que está na documentação da API que vai construir os dados de eixo Y
def get_datasets(y, labels):
    #verificando se o tipo do valor em Y é do tipo lista ou um valor comum
    if type(y[0]) == list:
        datasets = [] #variavel contendo os valores de Y e os Labels
        for i in range(len(y)):
            datasets.append({
                'label': labels[i],
                'data': y[i]
            })
            return datasets
    else:
        return [
            {
                'labels': labels[0],
                'data': y
            }
        ]

#criando uma função que vai definir o titulo do gráfico
def set_tilte(title=''):
    if title != '':
        display = 'true' #true minúscula e não maiúscula porque é assim que a API pede que a gente passe
    else:
        display = 'false'
        return {
        'title': title,
        'display': display
    }

#criando uma função que cria o nosso dicionário que representa o nosso gráfico
def create_chart(x, y,labels, kind='bar', title=''):
    datasets = get_datasets(y, labels)
    options = set_tilte(title)

    chart = {
        'type': kind,
        'data':{
            'labels': x,
            'datasets': datasets
        },
        'options': options
    }
    return chart

#criando uma funcção que vai fazer a requisão na API dos dados desse dicionário
def get_api_chart(chart):
    url_base = 'https://quickchart.io/?chart'
    resp = r.get(f'{url_base}?c={str(chart)}')
    return resp.content

#criando uma função responsável por salvar a imagem retornada
def save_image(path, content):
    with open(path, 'wb') as image:
        image.write(content)

#criando uma função para mostrar essa imagem
def display_image(path):
    img_pill = Image.open(path)
    display(img_pill)

y_data_1 = []
for obs in dados_finais[1::10]: #por uma questão de visualização lógica nao vamos conseguir mostrar todos os dados numa unica visualização, vou pular de 10 em 10 dias
    y_data_1.append(obs[CONFIRMADOS])
    
y_data_2 = []
for obs in dados_finais[1::10]: #por uma questão de visualização lógica nao vamos conseguir mostrar todos os dados numa unica visualização, vou pular de 10 em 10 dias
    y_data_2.append(obs[RECUPERADOS])
    
labels = ['Confirmados', 'Recuperados']

#valores de X
x = []
for obs in dados_finais[1::10]:
    x.append(obs[DATA].strftime('%d/%m/%Y')) #strftime uma função que parte de um valor de tempo
    
#criando uma variável chart que recebe o retorno da nossa função
chart = create_chart(x, [y_data_1, y_data_2], labels, title='Grafico confirmados vs recuperados')
chart_content = get_api_chart(chart)
save_image('meu-primeiro-grafico.jpg', chart_content)

#Vamos gerar um QrCode
def get_api_qrcode(link):
    text = quote(link) #parsing do link para url
    url_base = 'https://quickchart.io/?qr'
    resp = r.get(f'{url_base}?text={text}')
    return resp.content

url_base = 'https://quickchart.io/?chart'
link = f'{url_base}?c={str(chart)}'
save_image('qr-code.jpg', get_api_qrcode(link))
display('qr-code.jpg')