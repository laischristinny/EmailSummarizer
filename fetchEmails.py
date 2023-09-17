import os
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from requests import Request
import pandas as pd

# Configurações
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
creds = None

CURR_DIR = os.path.dirname(os.path.abspath(__file__))

# Carregando as credenciais
if os.path.exists(os.path.join(CURR_DIR, 'token.json')):
    creds = Credentials.from_authorized_user_file(
        os.path.join(CURR_DIR, 'token.json'), SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            os.path.join(CURR_DIR, 'credentials.json'), SCOPES)
        creds = flow.run_local_server(port=0)

    with open(os.path.join(CURR_DIR, 'token.json'), 'w') as token:
        token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)

def fetch_emails():
    df = pd.DataFrame(columns=['id', 'from', 'name', 'subject', 'body'])
    try:
        results = service.users().messages().list(
            userId='me', labelIds=['INBOX'], maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print('Nenhum email encontrado.')
        else:
            print('Verificando os emails....:')
            for message in messages:
                msg = service.users().messages().get(
                    userId='me', id=message['id']).execute()
                message_data = msg['payload']['headers']
                for values in message_data:
                    name = values['name']
                    if name == 'From':
                        from_name = values['value']
                    if name == 'Subject':
                        subject = str(values['value'])
                        if not subject:
                            subject = 'Sem Assunto'
                # Obtendo o corpo da mensagem
                if 'parts' in msg['payload']:
                    msg_parts = msg['payload']['parts']
                    for part in msg_parts:
                        if part['mimeType'] == 'text/plain':
                            part_data = part['body']

                            data = part_data['data']
                            byte_code = base64.urlsafe_b64decode(data)
                            text = str(byte_code.decode('utf-8'))
                            if not text:
                                text = 'Sem Mensagem'
                df1 = pd.DataFrame(
                    [{'id': message['id'], 'from': from_name, 'name': name, 'subject': str(subject), 'body': str(text)}])

                df = pd.concat([df, df1], axis=0, ignore_index=True)
        return df
    
    except HttpError as error:
        print(f'Ocorreu um erro: {error}')


def fetch_and_save_emails_to_csv():
    try:
        df = fetch_emails()

        if not df.empty:
            csv_filename = 'emails_details.csv'
            df.to_csv(csv_filename, index=False)
            print(f'Detalhes dos emails salvos em "{csv_filename}"')
        else:
            print('Nenhum email encontrado.')

    except HttpError as error:
        print(f'Ocorreu um erro: {error}')

