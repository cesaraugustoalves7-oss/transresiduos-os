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
st.subheader("Abertura e Emissão de Ordem de Serviço (OS)")

# --- Carregar a Relação de Frota a partir do CSV (355 veículos) ---
@st.cache_data
def carregar_veiculos():
    if os.path.exists("veiculos_import.csv"):
        df = pd.read_csv("veiculos_import.csv")
        return df.to_dict(orient="records")
    else:
        return [
            {"code": "HD-80", "model": "Hyundai HD 80 Diesel", "year": 2020, "chassis": "9BW...HD802020"},
            {"code": "ONIX-01", "model": "Chevrolet Onix", "year": 2022, "chassis": "9BG...ONIX2022"}
        ]

veiculos_data = carregar_veiculos()

st.markdown("### 1. Seleção do Veículo da Frota")
veiculo_selecionado = st.selectbox(
    "Selecione o Veículo / Frota:",
    options=veiculos_data,
    format_func=lambda x: f"Frota: {x['code']} - {x['model']} ({x['year']})"
)

dados_veiculo = veiculo_selecionado

st.markdown("---")
st.markdown("### 2. Detalhes da Manutenção")
st.write("💡 **Dica no telemóvel:** Toque no campo e use o microfone do teclado para ditar.")

# Apenas o Componente Afetado e o Solicitante
componente = st.text_input("Componente Afetado / Avaria:", placeholder="Ex: Luz de ré queimada, Pneu furado...")
solicitante = st.text_input("Solicitante da OS:", placeholder="Nome do encarregado ou motorista")

# Registo Fotográfico
st.markdown("### 3. Registo Fotográfico (Opcional)")
fotos_enviadas = st.file_uploader(
    "Anexar fotos da avaria:", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# E-mail de destino
st.markdown("### 4. Envio da OS")
email_destino = st.text_input("E-mail da Oficina / Responsável:", value="manutencao@transresiduos.com.br")

# Botão de Gerar OS
if st.button("Gerar Ordem de Serviço 🚀", type="primary"):
    if not componente.strip() or not solicitante.strip():
        st.warning("Por favor, preencha o componente/avaria e o nome do solicitante antes de gerar a OS.")
    else:
        num_os = f"#{datetime.now().strftime('%d%H%M')}"
        data_atual = datetime.now().strftime('%d/%m/%Y')

        st.success(f"Ordem de Serviço gerada com sucesso para a Frota **{dados_veiculo['code']}**!")

        # Exibição Oficial da Ficha de OS no Ecrã
        st.markdown("---")
        st.markdown(f"""
        ### 📄 ORDEM DE SERVIÇO
        **Controle de Frota e Manutenção** \t\t\t\t **{num_os}**  
        *Data: {data_atual}*
        
        ---
        **DADOS DO VEÍCULO**
        - **Frota:** `{dados_veiculo['code']}` | **Placa/Chassis:** `{dados_veiculo['chassis']}`
        - **Modelo:** `{dados_veiculo['model']} ({dados_veiculo['year']})`
        - **Solicitante da OS:** `{solicitante.upper()}`

        **DETALHES DO SERVIÇO**
        - **Componente / Avaria:** `{componente}`

        **Destinatário de Envio:** `{email_destino}`
        """)

        # Exibir as fotografias anexadas
        if fotos_enviadas:
            st.markdown("---")
            st.markdown("**Fotografias Anexadas da Avaria:**")
            for foto in fotos_enviadas:
                st.image(foto, caption=foto.name, use_container_width=True)

        st.toast("OS gerada com sucesso!", icon="🟢")
