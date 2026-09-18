# --- Função para Gerar o PDF Oficial corrigida para fpdf2 ---
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
    
    # Correção compatível com fpdf2 para retornar os bytes
    return pdf.output()
