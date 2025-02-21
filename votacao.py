import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Configuração do Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sYEi_6zcVfiv7rwUQi5ZwNqdzHH9qXTh8dpKSEabi7o/edit?gid=0#gid=0"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

credenciais = st.secrets["gcp_service_account"]
credenciais_dict = dict(credenciais)

CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_dict(credenciais_dict, SCOPES)
client = gspread.authorize(CREDENTIALS)
sheet = client.open_by_url(SHEET_URL).sheet1

# Inicializa a votação
CANTORES = ["Xico Gaiato - 'Ai Senhor'", "Rita Sampaio - 'Voltas'", "Du Nothin - 'Sobre Nós'", "Marco Rodrigues - 'A Minha Casa'", "Margarida Campelo - 'Eu sei que o amor'", "Josh - 'Tristeza'", "Capital da Bulgária - 'Lisboa'", "Bluay - 'Ninguém'", "Jéssica Pina - 'Calafrio'", "Peculiar - 'Adamastor'"]

st.title("Votação Festival da Canção - 1ª Semi-Final")
st.write("""
Bem-vindos à votação da primeira Semi-Final do  Festival da Canção! Apenas 6 cantores passam para a Final, então só podem votar "Passa" 6 vezes, e "Não passa" para os restantes. 
""")

# Carregar votos do Google Sheets
def carregar_votos():
    data = sheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["Cantor", "Passa", "Não passa"])

# Salvar votos no Google Sheets
def salvar_votos(votos):
    for cantor, escolha in votos.items():
        sheet.append_row([cantor, 1 if escolha == "Passa" else 0, 1 if escolha == "Não passa" else 0])

# Criar um dicionário para armazenar as escolhas do usuário
votos_usuario = {}

# Exibir votações
for cantor in CANTORES:
    escolha = st.radio(f"{cantor}", ["Passa", "Não passa"], key=cantor)
    votos_usuario[cantor] = escolha

# Botão único para concluir a votação
if st.button("Concluir"):
    num_passa = sum(1 for escolha in votos_usuario.values() if escolha == "Passa")
    num_nao_passa = sum(1 for escolha in votos_usuario.values() if escolha == "Não passa")
    
    if num_passa == 6 and num_nao_passa == 4:
        salvar_votos(votos_usuario)
        st.success("Votos guardados com sucesso!")
    else:
        st.error("Erro: Você deve selecionar exatamente 6 cantores como 'Passa' e 4 como 'Não passa'.")

# Exibir resultados
st.subheader("Resultados")
votos_df = carregar_votos()
if not votos_df.empty:
    resultado = votos_df.groupby("Cantor").sum()
    resultado["Total"] = resultado["Passa"] + resultado["Não passa"]
    resultado["% Passa"] = (resultado["Passa"] / resultado["Total"]) * 100
    resultado["% Não passa"] = (resultado["Não passa"] / resultado["Total"]) * 100
    st.dataframe(resultado[["% Passa", "% Não passa"]].round(2))
else:
    st.write("Nenhum voto registado ainda.")

# Seção de reset de votação (somente para administrador)
st.subheader("Reset")

senha = st.text_input("Digite a senha para resetar a votação:", type="password")
if senha == "carolgostosa":  # Substitua por uma senha segura
    if st.button("Resetar votação"):
        sheet.clear()  # Limpa toda a planilha
        sheet.append_row(["Cantor", "Passa", "Não passa"])  # Recria os cabeçalhos
        st.warning("As votações foram zeradas!")
else:
    st.info("Digite a senha correta para acessar o reset.")

