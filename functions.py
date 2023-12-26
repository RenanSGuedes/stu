import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect


# Crie uma conexão com a planilha do Google Sheets.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

@st.cache_resource(ttl=600)
def run_query(query_):
    """
    Função para puxar os dados da planilha e guardá-los em cache
    """
    rows_ = conn.execute(query_, headers=1).fetchall()
    return rows_