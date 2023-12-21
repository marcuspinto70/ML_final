import datetime
import streamlit as st
import pandas as pd
import pinecone
import openai
from fpdf import FPDF
import tiktoken  

from openai import OpenAI

# Capturar o timestamp do início da conversa
st.session_state.inicio_conversa = datetime.datetime.now()


if 'assistente_configurado' not in st.session_state or not st.session_state['assistente_configurado']:
    st.error("Por favor, configure o assistente primeiro.")
    st.stop()

# Acessando o DataFrame
if 'config' in st.session_state:
    config = st.session_state['config']
    estilo = config['estilo'][0]  # Acessando o primeiro elemento do DataFrame para o estilo
    criatividade = config['criatividade'][0]  # Acessando o valor da criatividade
    tamanho = int(config['tamanho'][0])  # Acessando o valor do tamanho
    moderacao = config['moderacao'][0]  # Acessando grau de moderação
    especialidades = config['especialidades'][0]  # Acessando as especialidades
    chave =  config['chave'][0] # chave openai
else:
    st.error("Dados de configuração não encontrados.")


ffacil = 'recursos/coxinhas.gif'

st.title("🍗 Festa Fácil Salgados e Doces 🍰")

# Cria três colunas
col1, col2, col3 = st.columns([1,1,1])

# Usando a coluna do meio para centralizar o GIF
with col2:
    st.image(ffacil,width=250)


client = OpenAI(api_key=chave)



# Configurando a conexão com o Pinecone
pinecone_api_key = st.secrets["pinecone_api_key"]
pinecone_environment = "gcp-starter"
pinecone_index_name = "ffacil-index"

# Inicializa o cliente Pinecone
pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)

# Conectando ao índice Pinecone
index = pinecone.Index(pinecone_index_name)

cardapio = ""

for especialidade in especialidades:
    
    especialidade_embedding = openai.embeddings.create(
    input= especialidade,
    model="text-embedding-ada-002")
    vetor = especialidade_embedding.data[0].embedding

    # Realizar a busca de similaridade

    try:
        busca = index.query(vector=vetor, top_k=1, include_metadata=True)

        busca_dict = busca.to_dict() 
        
        # Verificando se há resultados
        if busca_dict['matches']:
            # Iterando pelos resultados
            for match in busca_dict['matches']:
                # Acessando os metadados
                metadata = match.get('metadata', {})
                # Acessando o texto dentro dos metadados
                texto = metadata.get('text', '')

                # Concatena a especialidade e o texto ao cardápio
                if cardapio:  # Se cardapio já tem conteúdo, adiciona uma linha separadora
                    cardapio += "\n***\n"
                cardapio += especialidade + ' ' + texto

        else:
            # Se não houver matches
            st.error("Nenhum resultado encontrado.")
    except Exception as e:
        st.error(f"Erro ao realizar a busca de similaridade: {e}")        


prompt = ('Você será o atendente da Rotisseria Festa Fácil, uma pequena loja familiar que confecciona e vende salgados, doces, bolos, tortas e sanduiches. Tudo caseiro. '
          'Sua função será atender os clientes que contactarem a loja pelo whatsapp. '
          'Use a primeira pessoa do plural, sempre! '
          f'Suas respostas devem ser no estilo: {estilo}. '
          f'Suas respostas serão curtas, de no máximo {tamanho} tokens. '
          f'Você só fornecerá respostas relacionadas aos seguintes produtos:{especialidades}. Se o cliente perguntar sobre quaisquer outros produtos, responda educadamente que irá encaminhar o atendimento para outro atendente. '
          f'O cardápio que servirá de base para suas respostas é este:  {cardapio}. '
          'Suas respostas serão exclusivamente sobre o cardápio fornecido, não é permitido inventar outros produtos ou respostas. '
          'Se a resposta não estiver no cardápio, responda educadamente que irá encaminhar o atendimento para outro atendente. '
          'Atenção aos valores, quando estiverem em "centos", divida por 100 e calcule o custo dos pedidos dos clientes com base em unidades. '
          )



# Iniciar Historico Chat

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [{"role": 'system', "content": prompt}]



# Aparecer o Historico do Chat na tela
for mensagens in st.session_state.mensagens[1:]:
    with st.chat_message(mensagens["role"]):
        st.markdown(mensagens["content"])


# React to user input
prompt_usuario = st.chat_input("Digite algo")

if prompt_usuario:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt_usuario)
    
    # Verifica a entrada do usuário com o sistema de moderação
    mod_response = client.moderations.create(input=prompt_usuario)
    df = pd.DataFrame(dict(mod_response.results[0].category_scores).items(), columns=['Category', 'Value'])

    # Checa se alguma categoria excede o limite 
    if (df['Value'] > moderacao).any():
        violacao = df[df['Value'] > moderacao]
        st.error(f"Violação detectada: {violacao['Category'].values[0]} com valor {violacao['Value'].values[0]:.2f}")
    else:
        # Add user message to chat history
        st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})

        # Fazendo a chamada para a API da OpenAI
        chamada = client.chat.completions.create(
             model='gpt-3.5-turbo',
             messages=st.session_state.mensagens,
             max_tokens=tamanho,
             temperature=criatividade
        )

        resposta = chamada.choices[0].message.content

        # Display assistant response in chat message container
        with st.chat_message("system", avatar="🍰"):
            st.markdown(resposta)
        # Add assistant response to chat history
        st.session_state.mensagens.append({"role": "system", "content": resposta})


_, _, c1 = st.columns([2,1,2])
 
with c1:
	botao = st.button('Finalizar Conversa',
		type = 'primary',
		use_container_width = True)

if botao:

    todas_mensagens = ' '.join(mensagem['content'] for mensagem in st.session_state.mensagens)
    
    # Calcula o número total de tokens
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(todas_mensagens))
    custo_estimado=(num_tokens/1000)*0.0015

    # Cria um DataFrame com as informações da conversa
    df_conversa = pd.DataFrame({
        "Data e Hora": [st.session_state.inicio_conversa],
        "Tokens Utilizados": [num_tokens],
        "Custo Estimado": [custo_estimado],
        "Histórico do Diálogo": ["\n".join(mensagem["content"] for mensagem in st.session_state.mensagens)]
    })
    
    # Gera um PDF com o histórico da conversa
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Adiciona os dados do DataFrame ao PDF
    for index, row in df_conversa.iterrows():
        pdf.cell(200, 10, txt="Data e Hora: " + str(row["Data e Hora"]), ln=True, align="L")
        pdf.cell(200, 10, txt="Tokens Utilizados: " + str(row["Tokens Utilizados"]), ln=True, align="L")
        pdf.cell(200, 10, txt="Custo Estimado: " + str(row["Custo Estimado"]), ln=True, align="L")
        pdf.cell(200, 10, txt="Histórico do Diálogo:", ln=True, align="L")
        dialogos = row["Histórico do Diálogo"].split('\n')
        for dialogo in dialogos:
            pdf.multi_cell(0, 10, txt=dialogo, align="L")
    
    pdf.output("historico_conversa.pdf")
    
    # Permite ao usuário baixar o PDF
    with open("historico_conversa.pdf", "rb") as file:
        btn = st.download_button(
            label="Baixar Histórico da Conversa em PDF",
            data=file,
            file_name="historico_conversa.pdf",
            mime="application/octet-stream"
        )
    
    
    
