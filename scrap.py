import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import datetime
import os
import time
import utils.helpers as helpers
from dotenv import load_dotenv

load_dotenv()

R_EMAIL_ADDRESS = os.environ['R_EMAIL_ADDRESS'] #'felipe.gutierreze@hotmail.com'#
S_EMAIL_PWSD = os.environ['S_EMAIL_PWSD'] #'tfhaxuyryjmpvcec'#

S_EMAIL_ADDRESS = os.environ['S_EMAIL_ADDRESS'] #'Datatroopermailservice@gmail.com'#


personal_email_info = {'email': S_EMAIL_ADDRESS, 'password': S_EMAIL_PWSD}

while 1:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
            'Accept-Language': 'en-US, en;q=0.5'
        }
        df_in = pd.read_excel('input.xlsx')

        query_product = df_in["Producto"].values[0]
        #print('query: ',query_product)
        base_url = f'https://www.amazon.com/s?k={query_product}'
        response = requests.get(base_url, headers=headers)
        print('respuesta: ',response)
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('a', {'class': 'a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        print(results)
        df = pd.DataFrame(columns=['Fecha', 'Busqueda', 'Producto', 'Precio', 'Descuento', 'Link'])

        for res in results:
            try:
                res_disc = res.find('span', {'class': 'a-size-extra-large s-color-discount puis-light-weight-text'}).text
                link = f'https://www.amazon.com/-/es{res["href"]}'
                price = res.find('span', {'class': 'a-offscreen'}).text
                name = res.parent.parent.parent.find('span', {'class': 'a-size-base-plus a-color-base a-text-normal'}).text

                df = df.append({'Fecha': datetime.datetime.now(), 'Busqueda': query_product, 'Producto': name, 'Precio': price, 'Descuento': res_disc, 'Link': link}, ignore_index=True)
            except Exception as e:
                #print(e)
                pass

        df['Descuento'] = df['Descuento'].str.replace('%', '').str.replace('-', '').astype(float)
        df.sort_values(by=['Descuento'], inplace=True, ascending=False)

        umbral = df_in['Umbral'].values[0]

        df = df[df['Descuento'] > umbral]
        print(df)
        df.reset_index(drop=True, inplace=True)
        print(df)
        if not df.empty:
            helpers.send_email(email_address=R_EMAIL_ADDRESS, df=df, personal_email_info=personal_email_info)
            print('email sent')

        if os.path.isfile('Precios amazon.xlsx'):
            helpers.append_df_to_excel('Precios amazon.xlsx', df, header=False, index=False)
        else:
            helpers.append_df_to_excel('Precios amazon.xlsx', df, index=False)
        
        print('Resultados guardados en Precios amazon.xlsx')

        print('Esperando para volver a buscar...')
        time.sleep(60*60)
    except Exception as e:
        
        print('Error: ', e)
        time.sleep(60*10)

