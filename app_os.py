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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuração da página
st.set_page_config(page_title="Transresíduos - Sistema Integrado", page_icon="🚚", layout="centered")

# --- E-MAIL FIXO DE DESTINO ---
EMAIL_FIXO_DESTINO = "compras@transresiduos.com.br"

# --- Carregar e Exibir o Logo da Transresíduos ---
def carregar_logo():
    for nome_possivel in ["logo (3).png", "logo.png", "logo (3).jpg"]:
        if os.path.exists(nome_possivel):
            return Image.open(nome_possivel)
    return None

logo = carregar_logo()
if logo:
    st.image(logo, width=180)

st.title("🚚 Transresíduos - Sistema de Gestão")

# --- CRIAÇÃO DE ABAS ---
aba_os, aba_checklist = st.tabs([
    "🔧 Ordem de Serviço (Frota)", 
    "☑️ Check-List de Manutenção"
])

# ==========================================
# ABA 1: ORDENS DE SERVIÇO (FROTA)
# ==========================================
with aba_os:
    st.subheader("Abertura e Emissão de Ordem de Serviço (OS)")

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
        format_func=lambda x: f"C: {x['code']} - {x['model']} ({x['year']})",
        key="sel_veiculo_os"
    )

    st.markdown("---")
    st.markdown("### 2. Detalhes da Manutenção e Foto")
    
    componente = st.text_input("Componente Afetado:", placeholder="Ex: Embreagem, Pneu...", key="comp_os")
    observacoes = st.text_area("Observações / Diagnóstico:", placeholder="Ex: TROCAR KIT EMBREAGEM", key="obs_os")
    solicitante = st.text_input("Solicitante da OS:", placeholder="Nome do encarregado", key="sol_os")
    
    # --- CÂMARA DIRETA PARA MOBILE ---
    st.markdown("#### 📷 Tirar Foto da Avaria")
    foto_os = st.camera_input("Clique para tirar a foto", key="cam_os_mob")

    email_destino_os = st.text_input("E-mail de Destino (Oficina / Responsável):", value=EMAIL_FIXO_DESTINO, key="email_os")

    def gerar_pdf_os(num_os, data_atual, veiculo, componente, observacoes, solicitante, img_file=None):
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
        t_obs.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke), ('BOX', (0,0), (-1,-1), 1, colors.gray), ('PADDING', (0,0), (-1,-1), 6)]))
        elements.append(t_obs)
        elements.append(Spacer(1, 10))

        # --- TRATAMENTO ROBUSTO DA FOTO NA OS ---
        if img_file is not None:
            elements.append(Paragraph("<b>REGISTO FOTOGRÁFICO:</b>", secao_estilo))
            elements.append(Spacer(1, 5))
            img_path_temp = "temp_foto_os.jpg"
            try:
                img_bytes = img_file.read()
                img_pil = Image.open(io.BytesIO(img_bytes))
                
                if img_pil.mode in ("RGBA", "P"):
                    img_pil = img_pil.convert("RGB")
                
                img_pil.save(img_path_temp, "JPEG", quality=90)
                
                if os.path.exists(img_path_temp):
                    elements.append(RLImage(img_path_temp, width=250, height=187))
                else:
                    elements.append(Paragraph("<i>[Erro: Ficheiro de imagem não gravado]</i>", texto_estilo))
            except Exception as e:
                elements.append(Paragraph(f"<i>[Erro ao processar imagem: {str(e)}]</i>", texto_estilo))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def enviar_email_brevo(destinatario, assunto, pdf_bytes, nome_pdf):
        api_key = st.secrets.get("BREVO_API_KEY", "")
        if not api_key:
            return False, "Chave API do Brevo não configurada."
        
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {"accept": "application/json", "api-key": api_key, "content-type": "application/json"}
        payload = {
            "sender": {"name": "Transresíduos - Frota", "email": "cesaraugustoalves7@gmail.com"},
            "to": [{"email": destinatario}],
            "subject": assunto,
            "htmlContent": "<p>Segue em anexo o documento gerado pelo sistema com o respetivo registo fotográfico.</p>",
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

    if st.button("Gerar e Enviar Ordem de Serviço por E-mail ✉️", type="primary", key="btn_os"):
        if not componente.strip() or not solicitante.strip() or not observacoes.strip():
            st.warning("Preencha todos os campos obrigatórios da OS.")
        else:
            num_os = f"#{datetime.now().strftime('%d%H%M')}"
            data_atual = datetime.now().strftime('%d/%m/%Y')
            nome_arquivo_pdf = f"OS_{veiculo_selecionado['code']}_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"

            pdf_file = gerar_pdf_os(num_os, data_atual, veiculo_selecionado, componente, observacoes, solicitante, foto_os)
            pdf_bytes = pdf_file.getvalue()

            assunto = f"Ordem de Serviço {num_os} - C: {veiculo_selecionado['code']}"
            sucesso, msg_retorno = enviar_email_brevo(email_destino_os, assunto, pdf_bytes, nome_arquivo_pdf)

            if sucesso:
                st.success(f"OS enviada com sucesso para **{email_destino_os}**! ✅")
            else:
                st.warning(f"Aviso no envio: {msg_retorno}")

            st.download_button("📥 Descarregar PDF da OS", data=pdf_bytes, file_name=nome_arquivo_pdf, mime="application/pdf", key="dl_os")


# ==========================================
# ABA 2: CHECK-LIST DE MANUTENÇÃO (FOR LOG 06.001/c)
# ==========================================
with aba_checklist:
    st.subheader("Formulário de Check-List para Manutenção")
    st.markdown("<b>FOR LOG 06.001/c</b> (Revisão: 03)", unsafe_allow_html=True)

    if "num_checklist" not in st.session_state:
        st.session_state["num_checklist"] = 100  

    st.markdown(f"**Número Sequencial do Check-List:** #{st.session_state['num_checklist']}")

    veiculo_chk = st.selectbox(
        "Veículo / Equipamento:",
        options=veiculos_data,
        format_func=lambda x: f"C: {x['code']} - {x['model']} ({x['year']})",
        key="sel_veiculo_chk"
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        colaborador = st.text_input("Colaborador / Motorista:", placeholder="Nome do motorista", key="chk_colab")
    with col_b:
        supervisor = st.text_input("Supervisor de Manutenção:", placeholder="Nome do supervisor", key="chk_sup")

    # --- CÂMARA DIRETA PARA MOBILE ---
    st.markdown("#### 📷 Tirar Foto da Inspeção")
    foto_chk = st.camera_input("Clique para tirar a foto", key="cam_chk_mob")

    email_destino_chk = st.text_input("E-mail de Destino do Check-List:", value=EMAIL_FIXO_DESTINO, key="email_chk")

    st.markdown("---")
    st.markdown("### Itens de Inspeção")
    st.write("Indique a situação de cada item (Conforme: SIM, NÃO ou N/A):")

    itens_checklist = [
        "Óleo do motor (Nível)",
        "Óleo Hidráulico equip. (Nível)",
        "Fluido do Radiador (Nível)",
        "Ar Comprimido (Despressurizando rápido)",
        "Rodoar (Quebras/Vazamento de Ar)",
        "Buzina (Funcionamento)",
        "Luz de freio (Funcionamento)",
        "Piscas (Funcionamento)",
        "Meia luz e Luz de placa (Funcionamento)",
        "Farol (Ver se liga junto com a chave)",
        "Giroflex (Funcionamento)",
        "Marcador de combustível (Funcionamento)",
        "Freio estacionário (Funcionamento)",
        "Freio de serviço (Frenagem regular)",
        "Embreagem (Suavidade no pedal e engates)",
        "Cinto de segurança (Funcionamento)",
        "Limpador de para brisa (Funcionamento)",
        "Retrovisores (Fixação)",
        "Vidros de porta (Funcionamento)",
        "Cabine (Bascular)",
        "Pneus (Desgastes)",
        "Molas e grampos de molas (Quebras)",
        "Motor/Caixa/Diferencial (Vazamento de óleo / Barulho)",
        "Pistões hidráulicos (Vazamento)",
        "Comando hidráulico (Vazamento)",
        "Lataria / Para-choques (Batidos)",
        "Sapatas do elevador / prensa (Gastos ou soltos)",
        "Caixa compactadora (Vazamento de Chorume / Fixação)",
        "Travas de Arrocho (Perfeição das roscas / Alavancas)",
        "Cocho de coleta (Vazamento / Trincas)",
        "Placas Detran (Estado de conservação / pintura)",
        "Volante de direção (Acabamento de Superfície)",
        "Baterias (Sem carga toda manhã)",
        "Extintor de cabine (1 Extintor de 2 kg)",
        "Triângulo (Existência do mesmo)",
        "Placa/Pintura Peso Bruto/Tara/Líquido (Legível)",
        "Pasta de Documentação (Cronotacógrafo/ANTT/CIV/CRLV)",
        "Ordem de serviço manual / Tacógrafo (Min. 5 ordens)"
    ]

    respostas_chk = {}
    for i, item_nome in enumerate(itens_checklist):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(f"• {item_nome}")
        with c2:
            respostas_chk[item_nome] = st.radio(
                f"sit_{i}", 
                options=["SIM", "NÃO", "N/A"], 
                index=0, 
                key=f"radio_chk_{i}", 
                label_visibility="collapsed",
                horizontal=True
            )

    observacoes_chk = st.text_area("Observações Gerais do Check-List:", placeholder="Relate avarias ou detalhes importantes...", key="obs_geral_chk")

    def gerar_pdf_checklist(num_chk, data_atual, veiculo, colab, sup, respostas, obs, img_file=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []
        styles = getSampleStyleSheet()
        
        titulo_estilo = ParagraphStyle('TituloChk', parent=styles['Heading1'], fontSize=12, fontName='Helvetica-Bold', textColor=colors.black)
        texto_estilo = ParagraphStyle('TextoChk', parent=styles['Normal'], fontSize=8, fontName='Helvetica', textColor=colors.black)
        
        elements.append(Paragraph("TRANSRESÍDUOS - CHECK-LIST PARA MANUTENÇÃO (FOR LOG 06.001/c)", titulo_estilo))
        elements.append(Paragraph(f"<b>Check-List Nº:</b> #{num_chk} | <b>Data:</b> {data_atual} | <b>Revisão:</b> 03", texto_estilo))
        elements.append(Spacer(1, 5))
        
        elements.append(Paragraph(f"<b>Veículo:</b> C: {veiculo['code']} - {veiculo['model']} ({veiculo['year']}) | <b>Chassis:</b> {veiculo['chassis']}", texto_estilo))
        elements.append(Paragraph(f"<b>Colaborador:</b> {colab.upper()} | <b>Supervisor:</b> {sup.upper()}", texto_estilo))
        elements.append(Spacer(1, 10))
        
        tabela_dados = [["Item a Examinar", "Situação"]]
        for item, sit in respostas.items():
            tabela_dados.append([item, sit])
            
        t_chk = Table(tabela_dados, colWidths=[440, 100])
        t_chk.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(t_chk)
        elements.append(Spacer(1, 10))
        
        if obs.strip():
            elements.append(Paragraph(f"<b>Observações:</b> {obs.upper()}", texto_estilo))
            elements.append(Spacer(1, 10))

        # --- TRATAMENTO ROBUSTO DA FOTO NO CHECK-LIST ---
        if img_file is not None:
            elements.append(Paragraph("<b>REGISTO FOTOGRÁFICO DA INSPEÇÃO:</b>", texto_estilo))
            elements.append(Spacer(1, 5))
            img_path_temp = "temp_foto_chk.jpg"
            try:
                img_bytes = img_file.read()
                img_pil = Image.open(io.BytesIO(img_bytes))
                
                if img_pil.mode in ("RGBA", "P"):
                    img_pil = img_pil.convert("RGB")
                
                img_pil.save(img_path_temp, "JPEG", quality=90)
                
                if os.path.exists(img_path_temp):
                    elements.append(RLImage(img_path_temp, width=220, height=165))
                else:
                    elements.append(Paragraph("<i>[Erro: Ficheiro de imagem não gravado]</i>", texto_estilo))
            except Exception as e:
                elements.append(Paragraph(f"<i>[Erro ao processar imagem: {str(e)}]</i>", texto_estilo))
            
        doc.build(elements)
        buffer.seek(0)
        return buffer

    if st.button("Gerar e Enviar Check-List por E-mail ☑️✉️", type="primary", key="btn_chk"):
        if not colaborador.strip() or not supervisor.strip():
            st.warning("Preencha o nome do Colaborador e do Supervisor.")
        else:
            data_atual = datetime.now().strftime('%d/%m/%Y')
            num_atual = st.session_state["num_checklist"]
            nome_arquivo_chk = f"Checklist_{veiculo_chk['code']}_{num_atual}.pdf"

            pdf_file = gerar_pdf_checklist(num_atual, data_atual, veiculo_chk, colaborador, supervisor, respostas_chk, observacoes_chk, foto_chk)
            pdf_bytes = pdf_file.getvalue()

            assunto = f"Check-List de Manutenção #{num_atual} - C: {veiculo_chk['code']}"
            sucesso, msg_retorno = enviar_email_brevo(email_destino_chk, assunto, pdf_bytes, nome_arquivo_chk)

            if sucesso:
                st.success(f"Check-List Nº {num_atual} enviado com sucesso para **{email_destino_chk}**! ✅")
                st.session_state["num_checklist"] += 1
            else:
                st.warning(f"Aviso no envio: {msg_retorno}")

            st.download_button("📥 Descarregar PDF do Check-List", data=pdf_bytes, file_name=nome_arquivo_chk, mime="application/pdf", key="dl_chk")
