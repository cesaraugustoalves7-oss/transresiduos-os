import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Transresíduos - Ordens de Serviço", page_icon="🚛", layout="centered")

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

st.title("🚛 Transresíduos - Gestão de Frota")
st.subheader("Abertura de Ordem de Serviço (OS) por Voz")

# Carregar a base de dados dos 355 veículos
@st.cache_data
def carregar_frota():
    if os.path.exists("veiculos_import.csv"):
        df = pd.read_csv("veiculos_import.csv")
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df
    else:
        return pd.DataFrame(columns=["code", "model", "chassis", "year"])

df_frota = carregar_frota()

if df_frota.empty:
    st.error("⚠️ Aviso: O arquivo 'veiculos_import.csv' precisa estar na mesma pasta!")
else:
    # 1. Seleção do veículo
    st.markdown("### 1. Identificação do Veículo")
    lista_codigos = df_frota["code"].tolist()
    veiculo_selecionado = st.selectbox("Selecione o Código do Veículo:", lista_codigos)
    
    # Puxa os dados do veículo escolhido automaticamente
    dados_veiculo = df_frota[df_frota["code"] == veiculo_selecionado].iloc[0]
    
    st.info(f"""
    **Modelo:** {dados_veiculo['model']}  
    **Ano:** {dados_veiculo['year']}  
    **Chassis:** {dados_veiculo['chassis']}
    """)

    # 2. Relato do problema (Comando de voz pelo teclado do celular ou PC)
    st.markdown("### 2. Relato do Problema")
    st.write("💡 Dica no celular: Toque no microfone do seu teclado (Gboard/Apple) para ditar o texto.")
    
    descricao_problema = st.text_area("Descrição da Avaria:", placeholder="Ex: Vazamento de óleo na mangueira principal...")

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
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            st.success(f"Ordem de Serviço gerada com sucesso! Número: **{num_os}**")
            
            st.markdown("---")
            st.markdown("### 📄 Ficha de OS Oficial")
            st.markdown(f"""
            - **Número da OS:** `{num_os}`
            - **Data/Hora:** `{data_atual}`
            - **Veículo:** `{dados_veiculo['code']} - {dados_veiculo['model']} ({dados_veiculo['year']})`
            - **Chassis:** `{dados_veiculo['chassis']}`
            - **Descrição:** _{descricao_problema}_
            - **Destinatário:** `{email_destino}`
            """)
            st.toast("OS registrada com sucesso!", icon="🟢")