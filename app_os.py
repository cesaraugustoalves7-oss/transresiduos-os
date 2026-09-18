import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Transresíduos - Ordens de Serviço", page_icon="🚚", layout="centered")

# --- Carregar e Exibir o Logo da Transresíduos ---
def carregar_logo():
    for nome_possivel in ["logo (3).png", "logo.png", "logo (3).jpg"]:
        if os.path.exists(nome_possivel):
            return Image.open(nome_possivel)
    return None

logo = carregar_logo()
if logo:
    st.image(logo, width=180)

st.title("🚚 Transresíduos - Gestão de Frota")
st.subheader("Abertura de Ordem de Serviço (OS)")

# Base de dados dos veículos
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

dados_veiculo = veiculo_selecionado

st.markdown("---")
st.markdown("### 2. Registo da Avaria / Manutenção")
st.write("💡 **Dica no telemóvel:** Toque no campo abaixo e use o microfone do seu teclado (Gboard/Apple) para ditar. O texto aparecerá escrito e poderá editá-lo livremente.")

# Campo de texto para a descrição (permite ditar por voz e editar diretamente)
descricao_problema = st.text_area("Descrição da Avaria (Dite ou Escreva):", placeholder="Ex: Vazamento de óleo na mangueira principal...")

# Campo para o Solicitante
solicitante = st.text_input("Solicitante da Manutenção:", placeholder="Nome de quem reportou o problema")

# Novo campo para anexar Fotografias
st.markdown("### 3. Registo Fotográfico")
fotos_enviadas = st.file_uploader(
    "Adicionar fotos da avaria (Pode tirar foto direta ou carregar da galeria):", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# 4. E-mail de destino
st.markdown("### 4. Envio da OS")
email_destino = st.text_input("E-mail da Oficina / Responsável:", value="manutencao@transresiduos.com.br")

# 5. Botão de Gerar OS
if st.button("Gerar OS e Enviar 🚀", type="primary"):
    if not descricao_problema.strip():
        st.warning("Por favor, descreva o problema antes de gerar a OS.")
    else:
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

        # Exibir as fotografias anexadas na ficha, se houver
        if fotos_enviadas:
            st.markdown("**Fotografias Anexadas:**")
            for foto in fotos_enviadas:
                st.image(foto, caption=foto.name, use_container_width=True)

        st.toast("OS registrada com sucesso!", icon="🟢")
