import streamlit as st

# Função para mostrar a descrição de cada módulo
def mostrar_descricoes():
    st.header("Descrição dos Módulos do Aplicativo")

    # Módulo 1: Calcula Valor Aluguel SP
    st.subheader("1) Módulo Calcula Valor Aluguel SP")
    st.write("""
    Este módulo permite ao usuário estimar o valor de aluguel de um imóvel na cidade de São Paulo. 
    Os usuários inserem informações como valor de venda, área, região, número de vagas de garagem, 
    valor do condomínio e IPTU, tipo de imóvel e número de dormitórios. 
    Após isso, podem calcular uma estimativa do valor de aluguel com base em um modelo de previsão obtido a partir de informações do site "Quinto Andar".
    """)

    # Módulo 2: Configuração do Assistente Festa Fácil
    st.subheader("2) Configuração do Assistente Festa Fácil")
    st.write("""
    Este módulo permite configurar um assistente virtual para um negócio de festas e eventos. 
    Os usuários podem ajustar a criatividade e o tamanho das respostas, selecionar especialidades, 
    definir o estilo de escrita e o controle de moderação das entradas do cliente. 
    É necessária a utilização de uma chave API da OpenAI para configuração e utilização do assistente.
    """)

    # Módulo 3: ChatBot Assistente Festa Fácil
    st.subheader("3) ChatBot Assistente Festa Fácil")
    st.write("""
    Este módulo é um chatbot que funciona como assistente para a loja de festas e eventos. 
    Baseando-se nas configurações definidas, o chatbot interage com os usuários, 
    responde com base em um cardápio específico, e controla o estilo e tamanho das respostas. 
    É possível, ao finalizar a conversa, gerar um histórico em PDF para download.
    """)

# Chamada da função para mostrar as descrições
mostrar_descricoes()

