import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from fpdf import FPDF

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

# --- Carregar a Relação de Frota a partir do CSV ---
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
st.write("💡 **Dica no telemóvel:** Toque no campo e use o microfone do teclado para ditar o diagnóstico/avaria.")

# Componente e Descrição
componente = st.text_input("Componente Afetado:", placeholder="Ex: Embreagem, Sistema Hidráulico, Motor...")
descricao_problema = st.text_area("Diagnóstico / Observações:", placeholder="Ex: TROCAR KIT EMBREAGEM E VOLANTE DO MOTOR")

# Solicitante
solicitante = st.text_input("Solicitante da OS:", placeholder="Nome do encarregado ou motorista")

# Odómetro / Quilometragem atual
odometro = st.text_input("Odómetro / Horímetro Atual (km):", placeholder="Ex: 445.253 km")

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

# --- Função para Gerar o PDF Oficial compatível com fpdf2 ---
def gerar_pdf_os(num_os, data_atual, v_data, comp, desc, sol, odo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 8, "ORDEM DE SERVIÇO", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "Controle de Frota e Manutenção - Transresíduos", ln=True)
    pdf.set_xy(150, 10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(50, 6, f"Nº #{num_os}", align="R", ln=True)
    pdf.set_xy(150, 16)
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, f"Data: {data_atual}", align="R", ln=True)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    # Dados do Veículo
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 5, "DADOS DO VEÍCULO", ln=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(95, 6, f"Frota: {v_data['code']}", ln=0)
    pdf.cell(95, 6, f"Placa/Chassis: {v_data['chassis']}", ln=1)
    pdf.cell(95, 6, f"Modelo: {v_data['model']} ({v_data['year']})", ln=0)
    pdf.cell(95, 6, f"Odómetro: {odo}", ln=1)
    pdf.cell(0, 6, f"Solicitante da OS: {sol.upper()}", ln=1)
    
    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    # Detalhes do Serviço
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 5, "DETALHES DO SERVIÇO", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Componente: {comp}", ln=1)
    
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 5, "Observações / Diagnóstico:", ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 8, desc, border=1)
    
    pdf.ln(5)
    pdf.cell(95, 8, "Hora Inicial do Serviço: ____________________", ln=0)
    pdf.cell(95, 8, "Hora Final do Serviço: ____________________", ln=1)
    
    pdf.ln(3)
    pdf.cell(0, 6, "Descrição do Serviço Executado (Mecânico, Eletricista, etc.):", ln=1)
    pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
    pdf.ln(8)
    pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
    pdf.ln(8)
    
    pdf.ln(10)
    pdf.cell(95, 6, "________________________________________", align="C", ln=0)
    pdf.cell(95, 6, "________________________________________", align="C", ln=1)
    pdf.cell(95, 5, "Assinatura do Responsável", align="C", ln=0)
    pdf.cell(95, 5, "Assinatura do Mecânico/Guincho", align="C", ln=1)
    
    return pdf.output()

# Botão de Gerar OS
if st.button("Gerar OS Oficial e Descarregar 🚀", type="primary"):
    if not descricao_problema.strip() or not solicitante.strip():
        st.warning("Por favor, preencha a descrição da avaria e o nome do solicitante antes de gerar a OS.")
    else:
        num_os = datetime.now().strftime('%d%H%M')
        data_atual = datetime.now().strftime('%d/%m/%Y')

        st.success(f"Ordem de Serviço gerada com sucesso para a Frota **{dados_veiculo['code']}**!")

        # Gerar o ficheiro PDF em memória
        pdf_bytes = gerar_pdf_os(
            num_os=num_os,
            data_atual=data_atual,
            v_data=dados_veiculo,
            comp=componente if componente else "Geral",
            desc=descricao_problema,
            sol=solicitante,
            odo=odometro if odometro else "Não informado"
        )

        # Botão de Download direto do PDF
        st.download_button(
            label="📥 Descarregar Ficha de OS em PDF (Oficial)",
            data=pdf_bytes,
            file_name=f"OS_{dados_veiculo['code']}_{num_os}.pdf",
            mime="application/pdf"
        )

        st.markdown("---")
        st.markdown("### 📄 Pré-visualização da Ficha")
        st.markdown(f"""
        - **Frota:** `{dados_veiculo['code']}`
        - **Modelo:** `{dados_veiculo['model']} ({dados_veiculo['year']})`
        - **Chassis/Placa:** `{dados_veiculo['chassis']}`
        - **Solicitante:** `{solicitante}`
        - **Componente:** `{componente}`
        - **Diagnóstico:** `{descricao_problema}`
        - **Destinatário do Envio:** `{email_destino}`
        """)

        if fotos_enviadas:
            st.markdown("**Fotografias Anexadas:**")
            for foto in fotos_enviadas:
                st.image(foto, caption=foto.name, use_container_width=True)

        st.toast("OS gerada com sucesso!", icon="🟢")
