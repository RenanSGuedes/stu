import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

def formatar_data_hora(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%d/%m/%Y %H:%M:%S')

def escrever_dados_firebase_em_dataframe(api_key, database_url):
    url = f'{database_url}/.json?auth={api_key}'
    response = requests.get(url)
    dados = response.json()

    dados_para_dataframe = []
    for sensor, registros in dados.items():
        for data_hora, registro in registros.items():
            temp = registro.get('Temp: ', '')
            umid = registro.get('Umid: ', '')
            data_formatada = formatar_data_hora(int(data_hora))
            dados_para_dataframe.append([sensor, data_formatada, temp, umid])

    df = pd.DataFrame(dados_para_dataframe, columns=['Sensor', 'Data/Horário', 'Temperatura (°C)', 'Umidade (%)'])
    return df

def plotar_grafico(df, sensor_selecionado):
    df_filtrado = df[df['Sensor'] == sensor_selecionado]
    fig = px.line(df_filtrado, x='Data/Horário', y=['Temperatura (°C)', 'Umidade (%)'], title=f'Dados do Sensor {sensor_selecionado}')
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title('Firebase Data to DataFrame com Filtragem e Gráfico')

    api_key = "AAIzaSyAEH4zVSmhB11xF0KiWzbqDs7F6b130fto"
    database_url = "https://tarvos-electronic-default-rtdb.firebaseio.com"

    
    if api_key and database_url:
        df = escrever_dados_firebase_em_dataframe(api_key, database_url)

        sensores = df['Sensor'].unique()
        sensor_selecionado = st.selectbox('Escolha um Sensor', sensores)

        if sensor_selecionado:
            plotar_grafico(df, sensor_selecionado)
    else:
        st.error('Por favor, insira a API Key e a URL do Banco de Dados Firebase.')

if __name__ == '__main__':
    main()
