import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

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

# Componente e Solicitante
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

# --- Função para Enviar E-mail ---
def enviar_email_os(destinatario, assunto, corpo_html, fotos):
    # Configurações do Servidor de E-mail (Exemplo utilizando Gmail)
    # Dica: Para usar o Gmail, deve gerar uma "Senha de App" nas definições de segurança da Google.
    remetente = st.secrets.get("EMAIL_REMETENTE", "seu_email@gmail.com")
    senha = st.secrets.get("EMAIL_SENHA", "sua_senha_app")
    
    # Se não houver configuração de segredos, avisa mas não trava a aplicação visual
    if remetente == "seu_email@gmail.com":
        return False, "E-mail de remetente não configurado nos segredos do Streamlit."

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto

        # Corpo da mensagem em HTML
        msg.attach(MIMEText(corpo_html, 'html'))

        # Anexar fotografias se existirem
        if fotos:
            for foto in fotos:
                img_data = foto.getvalue()
                img = MIMEImage(img_data, name=foto.name)
                msg.attach(img)

        # Conexão com o servidor SMTP (Gmail como padrão)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        return False, str(e)

# Botão de Gerar OS
if st.button("Gerar e Enviar Ordem de Serviço 🚀", type="primary"):
    if not componente.strip() or not solicitante.strip():
        st.warning("Por favor, preencha o componente/avaria e o nome do solicitante antes de gerar a OS.")
    else:
        num_os = f"#{datetime.now().strftime('%d%H%M')}"
        data_atual = datetime.now().strftime('%d/%m/%Y')

        # Montar o conteúdo HTML para o e-mail e ecrã
        corpo_html = f"""
        <h3>📄 ORDEM DE SERVIÇO - {num_os}</h3>
        <p><b>Controle de Frota e Manutenção - Transresíduos</b><br>
        <i>Data: {data_atual}</i></p>
        <hr>
        <h4>DADOS DO VEÍCULO</h4>
        <ul>
            <li><b>Frota:</b> {dados_veiculo['code']}</li>
            <li><b>Modelo:</b> {dados_veiculo['model']} ({dados_veiculo['year']})</li>
            <li><b>Placa/Chassis:</b> {dados_veiculo['chassis']}</li>
            <li><b>Solicitante:</b> {solicitante.upper()}</li>
        </ul>
        <h4>DETALHES DO SERVIÇO</h4>
        <p><b>Componente / Avaria:</b> {componente}</p>
        <hr>
        <p><i>Mensagem gerada automaticamente pelo aplicativo de Gestão de Frota Transresíduos.</i></p>
        """

        # Tentar enviar o e-mail
        assunto_email = f"Nova OS {num_os} - Frota {dados_veiculo['code']}"
        sucesso_envio, mensagem_retorno = enviar_email_os(email_destino, assunto_email, corpo_html, fotos_enviadas)

        if sucesso_envio:
            st.success(f"Ordem de Serviço gerada e enviada com sucesso para **{email_destino}**! ✉️")
        else:
            st.success(f"Ordem de Serviço gerada com sucesso para a Frota **{dados_veiculo['code']}**!")
            st.info(f"Nota sobre o envio de e-mail: {mensagem_retorno} (A Ficha foi gerada no ecrã abaixo).")

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

        st.toast("OS processada!", icon="🟢")
