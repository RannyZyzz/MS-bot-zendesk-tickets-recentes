from urllib.parse import urlencode
from datetime import date, datetime
from pytz import timezone
import requests
import os   
from dotenv import load_dotenv
load_dotenv()

data_e_hora_atuais = datetime.now()
fuso_horario = timezone('America/Sao_Paulo')
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
dataPrint = data_e_hora_sao_paulo.strftime('%d/%m/%Y - %H:%M:%S')
dataAtual = data_e_hora_sao_paulo.strftime('%d/%m/%Y')


##Configuracoes Discord
header = {
    'authorization': os.getenv("AUTHORIZATION") ##authorization de acesso ao discord
}
idChannel = os.getenv("ID_CHANNEL")##informar id do canal do discord

##Credenciais Zendesk
credentials = os.getenv("LOGIN"), os.getenv("SENHA") ##informar login e senha de acesso ao zendesk
session = requests.Session()
session.auth = credentials

params = {
    'query': 'type:ticket status:open updated_at:{0}'.format(dataAtual),
    'sort_by': 'updated_at',
    'sort_order': 'desc'
}

## Buscando Tickets Recentes
url_ticket = '{0}/api/v2/search.json?'.format(os.getenv("URL_ZENDESK")) + urlencode(params)
response = session.get(url_ticket)
if response.status_code != 200:
    print('Status:', response.status_code, 'Problem with the request. Exiting.')
    exit()

##Print cabecalho
payload = { 
        'content': "Atualização de tickets recentes - {0}".format(dataPrint)
    } 
requests.post('https://discord.com/api/v9/channels/{0}/messages'.format(idChannel), data=payload, headers=header)

##Buscando os comentarios
objcomments = response.json()
for result in objcomments['results']:
    comment = result['id']
    urlTicket = '{0}/agent/tickets/{1}'.format(os.getenv("URL_ZENDESK"),comment)
    organizationId = result['organization_id']
    
    ##Buscando organizacao
    url_organization= '{0}/api/v2/organizations/{1}'.format(os.getenv("URL_ZENDESK"),organizationId)
    responseOrganization = session.get(url_organization)
    dataOrganization = responseOrganization.json()
    nameOrganization = dataOrganization['organization']['name']

    ##Buscando ultimo comentário
    url_comment = '{0}/api/v2/tickets/{1}/comments.json?sort_order=desc'.format(os.getenv("URL_ZENDESK"),comment)
    response = session.get(url_comment)
    data = response.json()
    for index, result in enumerate(data['comments']):
        if index == 0:
            resultado = str(result['author_id']) ##resultado em inteiro convertido para string
            break
    if(resultado != os.getenv("AUTHOR1") and resultado != os.getenv("AUTHOR2") and resultado != os.getenv("AUTHOR3") ):
        print('Ticket:',comment,'| Cliente:',nameOrganization, '| URL',urlTicket)
        
        payload = { 
            'content': "Ticket: {0} | Cliente: {1} | URL: {2}".format(comment,nameOrganization,urlTicket)
        }   
        requests.post('https://discord.com/api/v9/channels/{0}/messages'.format(idChannel), data=payload, headers=header)

