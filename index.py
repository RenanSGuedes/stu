import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

@st.cache_data
def escrever_dados_firebase_em_dataframe(api_key, database_url):
    url = f'{database_url}/.json?auth={api_key}'
    response = requests.get(url)
    dados = response.json()

    dados_para_dataframe = []
    for sensor, registros in dados.items():
        for data_hora, registro in registros.items():
            temp = registro.get('Temp: ')
            umid = registro.get('Umid: ')
            data_formatada = datetime.fromtimestamp(int(data_hora))
            # Converte para float, usando None para valores ausentes
            temp = float(temp) if temp is not None else None
            umid = float(umid) if umid is not None else None
            dados_para_dataframe.append([sensor, data_formatada, temp, umid])

    df = pd.DataFrame(dados_para_dataframe, columns=['Sensor', 'Data/Horário', 'Temperatura (°C)', 'Umidade (%)'])
    return df

def plotar_grafico(df, sensor_selecionado, data_inicio, data_fim):
    df_filtrado = df[(df['Sensor'] == sensor_selecionado) & (df['Data/Horário'] >= data_inicio) & (df['Data/Horário'] <= data_fim)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_filtrado['Data/Horário'], y=df_filtrado['Temperatura (°C)'], 
                             mode='lines', name='Temperatura (°C)'))

    fig.add_trace(go.Scatter(x=df_filtrado['Data/Horário'], y=df_filtrado['Umidade (%)'], 
                             mode='lines', name='Umidade (%)', yaxis='y2'))

    fig.update_layout(
        title=f'Dados do Sensor {sensor_selecionado}',
        xaxis_title='Data e Hora',
        yaxis_title='Temperatura (°C)',
        yaxis2=dict(
            title='Umidade (%)',
            overlaying='y',
            side='right',
            showgrid=False
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def main():
    st.title(':thermometer: Dados do Sensor de Temperatura e Umidade :desktop_computer:')

    api_key = st.secrets['api_key']
    database_url = st.secrets['database_url']

    if api_key and database_url:
        df = escrever_dados_firebase_em_dataframe(api_key, database_url)
        df['Data/Horário'] = pd.to_datetime(df['Data/Horário'])

        sensores = df['Sensor'].unique()
        sensor_selecionado = st.selectbox('Escolha um Sensor', sensores)

        # Filtros de data e exibição de métricas
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(
                'Data Inicial', 
                value=df['Data/Horário'].min().date(),
                min_value=df['Data/Horário'].min().date(),
                max_value=df['Data/Horário'].max().date()
            )
        with col2:
            data_fim = st.date_input(
                'Data Final', 
                value=df['Data/Horário'].max().date(),
                min_value=df['Data/Horário'].min().date(),
                max_value=df['Data/Horário'].max().date()
            )

        if sensor_selecionado and data_inicio and data_fim:
            df_filtrado = df[(df['Sensor'] == sensor_selecionado) & (df['Data/Horário'] >= pd.Timestamp(data_inicio)) & (df['Data/Horário'] <= pd.Timestamp(data_fim) + pd.Timedelta(days=1))]

            # Calculando métricas
            umidade_min = df_filtrado['Umidade (%)'].min()
            umidade_max = df_filtrado['Umidade (%)'].max()
            temperatura_min = df_filtrado['Temperatura (°C)'].min()
            temperatura_max = df_filtrado['Temperatura (°C)'].max()
            horario_recente = df_filtrado['Data/Horário'].max()

            # Encontrando os valores atuais de temperatura e umidade
            valores_atuais = df_filtrado[df_filtrado['Data/Horário'] == horario_recente]
            if not valores_atuais.empty:
                temperatura_atual = valores_atuais['Temperatura (°C)'].iloc[0]
                umidade_atual = valores_atuais['Umidade (%)'].iloc[0]
            else:
                temperatura_atual = None
                umidade_atual = None

            col1, col2, col3, col4, col5 = st.columns(5)
            # Exibindo métricas
            with col1:
                st.metric("Umidade Mínima", f"{umidade_min:.2f}%" if umidade_min is not None else "N/A")
            with col2:
                st.metric("Umidade Máxima", f"{umidade_max:.2f}%" if umidade_max is not None else "N/A")
            with col3:
                st.metric("Temperatura Mínima", f"{temperatura_min:.2f}°C" if temperatura_min is not None else "N/A")
            with col4:
                st.metric("Temperatura Máxima", f"{temperatura_max:.2f}°C" if temperatura_max is not None else "N/A")
            with col5:
                st.metric("Última atualização", datetime.now().strftime('%H:%M:%S') if horario_recente is not None else "N/A")

            # Adicionando colunas para temperatura e umidade atuais
            col1, col2 = st.columns(2)
            col1.metric("💧 Umidade Atual", f"{umidade_atual:.2f}%" if umidade_atual is not None else "N/A")
            col2.metric(":thermometer: Temperatura Atual", f"{temperatura_atual:.2f}°C" if temperatura_atual is not None else "N/A")

            plotar_grafico(df, sensor_selecionado, pd.Timestamp(data_inicio), pd.Timestamp(data_fim) + pd.Timedelta(days=1))
    else:
        st.error('Por favor, insira a API Key e a URL do Banco de Dados Firebase.')

if __name__ == '__main__':
    main()
