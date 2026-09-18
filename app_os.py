import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Transresíduos - Ordens de Serviço", page_icon="🚚", layout="centered")

# --- Carregar e Exibir o Logo da Transresíduos ---
def carregar_logo():
    # Verifica possíveis nomes para o arquivo de logo que você enviou
    for nome_possivel in ["logo (3).png", "logo.png", "logo (3).jpg"]:
        if os.path.exists(nome_possivel):
            return Image.open(nome_possivel)
    return None

logo = carregar_logo()
if logo:
    st.image(logo, width=180)

st.title("🚚 Transresíduos - Gestão de Frota")
st.subheader("Abertura de Ordem de Serviço (OS) por Voz")

# Carregar a base de dados dos veículos (simulada ou a partir de CSV se houver)
# Lista de veículos da frota com base na atividade recente
veiculos_data = [
    {"code": "HD-80", "model": "Hyundai HD 80 Diesel", "year": "2020", "chassis": "9BW...HD802020"},
    {"code": "ONIX-01", "model": "Chevrolet Onix", "year": "2022", "chassis": "9BG...ONIX2022"}
]

st.markdown("### 1. Seleção do Veículo")
veiculo_selecionado = st.selectbox(
    "Selecione o Veículo / Caminhão:",
    options=veiculos_data,
    format_func=lambda x: f"{x['code']} - {x['model']} ({x['year']})"
)

# Guardar dados do veículo selecionado
dados_veiculo = veiculo_selecionado

st.markdown("---")
st.markdown("### 2. Registo da Avaria / Manutenção")
st.write("💡 Dica no celular: Toque no microfone do seu teclado (Gboard/Apple) para ditar o texto.")

descricao_problema = st.text_area("Descrição da Avaria:", placeholder="Ex: Vazamento de óleo na mangueira principal...")

# Novo campo para o Solicitante
solicitante = st.text_input("Solicitante da Manutenção:", placeholder="Nome de quem reportou o problema")

# 3. E-mail de destino
st.markdown("### 3. Envio da OS")
email_destino = st.text_input("E-mail da Oficina / Responsável:", value="manutencao@transresiduos.com.br")

# 4. Botão de Gerar OS
if st.button("Gerar OS e Enviar 🚀", type="primary"):
    if not descricao_problema.strip():
        st.warning("Por favor, descreva o problema antes de gerar a OS.")
    else:
        # Geração do número sequencial único
        num_os = f"TR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        st.success(f"Ordem de Serviço gerada com sucesso! Número: **{num_os}**")

        st.markdown("---")
        st.markdown("### 📄 Ficha de OS Oficial")
        st.markdown(f"""
        - **Número da OS:** `{num_os}`
        - **Data/Hora:** `{data_atual}`
        - **Veículo:** `{dados_veiculo['code']} - {dados_veiculo['model']} ({dados_veiculo['year']})`
        - **Chassis:** `{dados_veiculo['chassis']}`
        - **Solicitante:** `{solicitante}`
        - **Descrição:** _{descricao_problema}_
        - **Destinatário:** `{email_destino}`
        """)
        st.toast("OS registrada com sucesso!", icon="🟢")
