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
