import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from functions import run_query

# Configuração da página
st.set_page_config(layout="wide")

# Obtendo dados da planilha
sheet_url = st.secrets["spreadsheet_stu"]
query = f'SELECT * FROM "{sheet_url}"'
rows = run_query(query)

# Criando DataFrame
df = pd.DataFrame(
    rows,
    columns=[
        'sensor',
        'time',
        'temperature',
        'humidity'
    ]
)

# Convertendo a coluna de tempo para datetime
df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S')
df = df.sort_values(by='time', ascending=True)

# Seletor de sensor
sensor_selected = st.selectbox('Escolha o sensor', options=df['sensor'].unique())

# Filtros de data
col1, col2 = st.columns(2)

start_date = col1.date_input(
    "Data Inicial",
    value=df['time'].min(),
    min_value=df['time'].min(),
    max_value=df['time'].max(),
    format="DD/MM/YYYY"
)

end_date = col2.date_input(
    "Data Final",
    value=df['time'].max(),
    min_value=df['time'].min(),
    max_value=df['time'].max(),
    format="DD/MM/YYYY"
)

# Convertendo datas de date para datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filtrando DataFrame por sensor e datas
df_filtered = df[(df['sensor'] == sensor_selected) & (df['time'] >= start_date) & (df['time'] <= end_date + pd.Timedelta(days=1))]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperatura", f"{df_filtered.iloc[-1][2]:.2f}°C")
col2.metric("Umidade", f"{df_filtered.iloc[-1][3]:.2f}%")
col3.metric("Data", df_filtered.iloc[-1][1].strftime("%H:%M:%S"))

# Plotando gráficos combinados de temperatura e umidade
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Adicionando temperatura ao gráfico
fig.add_trace(
    go.Scatter(x=df_filtered['time'], y=df_filtered['temperature'], name='Temperatura', mode='lines'),
    secondary_y=False,
)

# Adicionando umidade ao gráfico
fig.add_trace(
    go.Scatter(x=df_filtered['time'], y=df_filtered['humidity'], name='Umidade', mode='lines'),
    secondary_y=True,
)

# Configurações do layout
fig.update_layout(
    title='Temperatura e Umidade ao Longo do Tempo',
    xaxis=dict(
        title='Tempo',
        tickformat='%d/%m %H:%M',
        tickangle=-45
    )
)

# Configurações do eixo Y para temperatura
fig.update_yaxes(title_text="Temperatura", secondary_y=False)

# Configurações do eixo Y para umidade
fig.update_yaxes(title_text="Umidade", secondary_y=True)

# Mostrando o gráfico combinado
st.plotly_chart(fig, use_container_width=True)

