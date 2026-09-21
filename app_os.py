import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import io
import requests
import base64

# Importações do ReportLab para gerar o PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuração da página
st.set_page_config(page_title="Transresíduos - Ordens de Serviço", page_icon="🚚", layout="centered")

# --- E-MAIL FIXO DE DESTINO ---
EMAIL_FIXO_DESTINO = "compras@transreisuduos.com.br"

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

st.markdown("### 1. Seleção do Veículo")
veiculo_selecionado = st.selectbox(
    "Selecione o Veículo:",
    options=veiculos_data,
    format_func=lambda x: f"C: {x['code']} - {x['model']} ({x['year']})"
)

dados_veiculo = veiculo_selecionado

st.markdown("---")
st.markdown("### 2. Detalhes da Manutenção")
st.write("💡 **Dica no telemóvel:** Toque no campo e use o microfone do teclado para ditar.")

componente = st.text_input("Componente Afetado:", placeholder="Ex: Embreagem, Pneu, Sistema Elétrico...")
observacoes = st.text_area("Observações / Diagnóstico:", placeholder="Ex: TROCAR KIT EMBREAGEM E VOLANTE DO MOTOR")
solicitante = st.text_input("Solicitante da OS:", placeholder="Nome do encarregado ou motorista (Ex: TEDESCO)")

# Campo para o e-mail de destino
st.markdown("### 3. Opções de Envio")
email_destino_input = st.text_input("E-mail de Destino (Oficina / Responsável):", value=EMAIL_FIXO_DESTINO)

# Registo Fotográfico
st.markdown("### 4. Registo Fotográfico (Opcional)")
fotos_enviadas = st.file_uploader(
    "Anexar fotos da avaria:", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# --- Função para Gerar o PDF ---
def gerar_pdf_os(num_os, data_atual, veiculo, componente, observacoes, solicitante):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    titulo_estilo = ParagraphStyle('TituloOS', parent=styles['Heading1'], fontSize=16, fontName='Helvetica-Bold', textColor=colors.black)
    sub_estilo = ParagraphStyle('SubOS', parent=styles['Normal'], fontSize=9, fontName='Helvetica', textColor=colors.gray)
    secao_estilo = ParagraphStyle('SecaoOS', parent=styles['Heading3'], fontSize=10, fontName='Helvetica-Bold', textColor=colors.black)
    texto_estilo = ParagraphStyle('TextoOS', parent=styles['Normal'], fontSize=9, fontName='Helvetica', textColor=colors.black)
    
    header_data = [
        [Paragraph("<b>ORDEM DE SERVIÇO</b>", titulo_estilo), Paragraph(f"<b>Nº {num_os}</b>", ParagraphStyle('Num', parent=titulo_estilo, alignment=2))],
        [Paragraph("Controle de Frota e Manutenção", sub_estilo), Paragraph(f"Data: {data_atual}", ParagraphStyle('Data', parent=sub_estilo, alignment=2))]
    ]
    t_header = Table(header_data, colWidths=[350, 190])
    t_header.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 2), ('LINEBELOW', (0,1), (-1,1), 1, colors.black)]))
    elements.append(t_header)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("DADOS DO VEÍCULO", secao_estilo))
    veiculo_data = [
        [Paragraph(f"<b>C:</b> {veiculo['code']}", texto_estilo), Paragraph(f"<b>Placa/Chassis:</b> {veiculo['chassis']}", texto_estilo)],
        [Paragraph(f"<b>Modelo:</b> {veiculo['model']} ({veiculo['year']})", texto_estilo), Paragraph("", texto_estilo)],
        [Paragraph(f"<b>Solicitante da OS:</b> {solicitante.upper()}", texto_estilo), Paragraph("", texto_estilo)]
    ]
    t_veiculo = Table(veiculo_data, colWidths=[300, 240])
    t_veiculo.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.lightgrey)]))
    elements.append(t_veiculo)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("DETALHES DO SERVIÇO", secao_estilo))
    elements.append(Paragraph(f"<b>Componente:</b> {componente}", texto_estilo))
    elements.append(Spacer(1, 5))
    
    obs_content = [
        [Paragraph("<b>Observações / Diagnóstico:</b>", ParagraphStyle('ObsTitle', parent=texto_estilo, fontSize=8, textColor=colors.darkgray))],
        [Paragraph(f"<b>{observacoes.upper()}</b>", texto_estilo)]
    ]
    t_obs = Table(obs_content, colWidths=[540])
    t_obs.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke), ('BOX', (0,0), (-1,-1), 1, colors.gray), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('LEFTPADDING', (0,0), (-1,-1), 8)]))
    elements.append(t_obs)
    elements.append(Spacer(1, 15))
    
    tempo_data = [
        [Paragraph("Hora Inicial do Serviço: ___________________________", texto_estilo), 
         Paragraph("Hora Final do Serviço: ___________________________", texto_estilo)]
    ]
    t_tempo = Table(tempo_data, colWidths=[270, 270])
    elements.append(t_tempo)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("<b>Descrição do Serviço Executado (Mecânico, Eletricista, etc.):</b>", texto_estilo))
    elements.append(Spacer(1, 8))
    
    linhas_exec = [
        ["_________________________________________________________________________________________________"],
        ["_________________________________________________________________________________________________"],
        ["_________________________________________________________________________________________________"],
        ["_________________________________________________________________________________________________"]
    ]
    t_exec = Table(linhas_exec, colWidths=[540])
    t_exec.setStyle(TableStyle([('TEXTCOLOR', (0,0), (-1,-1), colors.gray), ('BOTTOMPADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_exec)
    elements.append(Spacer(1, 40))
    
    assinatura_data = [
        ["________________________________________", "________________________________________"],
        ["Assinatura do Responsável", "Assinatura do Mecânico/Guincho"]
    ]
    t_ass = Table(assinatura_data, colWidths=[270, 270])
    t_ass.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,1), (-1,1), 2)]))
    elements.append(t_ass)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- Função para Enviar E-mail via API Brevo ---
def enviar_email_com_pdf(destinatario, assunto, pdf_bytes, nome_pdf):
    api_key = st.secrets.get("BREVO_API_KEY", "")
    if not api_key:
        return False, "Chave API do Brevo não configurada nos Secrets."
    
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"name": "Transresíduos - Frota", "email": "cesaraugustoalves7@gmail.com"},
        "to": [{"email": destinatario}],
        "subject": assunto,
        "htmlContent": f"<p>Segue em anexo a Ordem de Serviço gerada automaticamente pelo sistema de Gestão de Frota.</p>",
        "attachment": [{"content": pdf_base64, "name": nome_pdf}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            return True, "E-mail enviado com sucesso!"
        else:
            return False, f"Erro na API: {response.text}"
    except Exception as e:
        return False, str(e)

# --- BOTÃO DE E-MAIL ---
if st.button("Gerar e Enviar Ordem de Serviço por E-mail ✉️", type="primary"):
    if not componente.strip() or not solicitante.strip() or not observacoes.strip():
        st.warning("Por favor, preencha todos os campos obrigatórios (Componente, Diagnóstico e Solicitante).")
    else:
        num_os = f"#{datetime.now().strftime('%d%H%M')}"
        data_atual = datetime.now().strftime('%d/%m/%Y')
        nome_arquivo_pdf = f"OS_{dados_veiculo['code']}_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"

        pdf_file = gerar_pdf_os(num_os, data_atual, dados_veiculo, componente, observacoes, solicitante)
        pdf_bytes = pdf_file.getvalue()

        assunto = f"Ordem de Serviço {num_os} - C: {dados_veiculo['code']}"
        sucesso, msg_retorno = enviar_email_com_pdf(email_destino_input, assunto, pdf_bytes, nome_arquivo_pdf)

        if sucesso:
            st.success(f"Ordem de Serviço gerada e enviada com sucesso para **{email_destino_input}**! ✉️✅")
        else:
            st.warning(f"OS gerada, mas houve um aviso no envio do e-mail: {msg_retorno}")

        st.download_button(
            label="📥 Descarregar PDF Localmente",
            data=pdf_bytes,
            file_name=nome_arquivo_pdf,
            mime="application/pdf"
        )
