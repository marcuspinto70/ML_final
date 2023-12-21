import streamlit as st 
import pandas as pd
import pinecone
import requests
from bs4 import BeautifulSoup
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import os
from openai import OpenAI



# Função para extrair e limpar o conteúdo
def extract_and_clean(url):
    response = requests.get(url, verify=False) # Desativa a verificação de SSL
    soup = BeautifulSoup(response.content, 'html.parser')

    elements = soup.find_all('h2', class_='page-section-heading')
    contents = []

    for element in elements:
        content = [element.get_text(separator='\n').strip()]

        # Percorrer os elementos subsequentes até encontrar outro 'page-section-heading'
        for sibling in element.next_siblings:
            if sibling.name == 'h2' and 'page-section-heading' in sibling.get('class', []):
                break
            if sibling.name:
                text = sibling.get_text(separator='\n').strip()
                text = text.replace('R$', 'R$ ')  # Adiciona um espaço após 'R$'
                content.append(text)


        contents.append('\n'.join(content).strip())

    return contents


# Classe Customizada para Carregar Textos
class CustomTextLoader:
    def __init__(self, texts):
        self.texts = texts

    def load(self):
        documents = [{'content': text} for text in self.texts]
        return documents


class Document:
    def __init__(self, content):
        self.page_content = content
        self.metadata = {}  # Adicionar mais campos conforme necessário


# URL para extrair os dados quando necessário
url = 'https://festafacilsalgados.com.br/'



st.header('Configuração do Assitente de Atendimento Festa Fácil')
st.write('Entre com as caracteristicas do assistente')

chave_valida = False


if not chave_valida:
   # obter chave openai
   chave = st.sidebar.text_input('Chave da API OpenAI', type='password')

    # Verificar se a chave da API OpenAI foi fornecida
   if chave:
        try:
            # chamada de uma função openai para testar se a chave informada é válida
            os.environ["OPENAI_API_KEY"] = chave
            embeddings = OpenAIEmbeddings()
            client = OpenAI()
            client.models.list()
        except Exception as e:
            #st.error("Chave da API OpenAI inválida ou ocorreu um erro: " + str(e))
            chave_valida = False 
        else:
            chave_valida = True
        
    
    
if chave_valida:

#Widgets para fazer os inputs do modelo

    col1, col2, col3 = st.columns([3,2,3])

    with col1:
    
        criatividade = st.slider(label = 'Criatividade da Resposta', 
            min_value=0.1, 
            max_value=1.0, 
            value=0.3,
            help='Valores baixos são mais conservadores, valores altos são mais criativos', 
            step=0.1)
        
        tamanho = st.slider(label = 'Tamanho da Resposta', 
            min_value=10, 
            max_value=100, 
            value= 50,
            help='Controla o tamanho das respostas do assistente em tokens',          
            step=5)
       
        especialidades = st.multiselect(
            'Especialidades do assistente',
            ['Salgados', 'Doces e Bolos', 'Tortas e Sanduíches de Metro'],
            default=['Salgados', 'Doces e Bolos', 'Tortas e Sanduíches de Metro'])
    
    
    with col3:
        estilo = st.radio(
            'Estilo da Escrita',
            ['Profissional e Informativo', 'Amigável e Acolhedor', 'Como um poeta'])
        
        
        moderacao = st.number_input(
            label='Controle de Moderação do Usuário',
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1
        )
        
        
    _, _, c1 = st.columns([2,1,2])
    
    with c1:
    	botao = st.button('Configurar o Assistente',
    		type = 'primary',
    		use_container_width = True)
    
    if botao:
        if not especialidades:
            st.error('Por favor, selecione ao menos uma especialidade.')
        else:
        
            # Configurando a conexão com o Pinecone
            pinecone_api_key = st.secrets["pinecone_api_key"]
            pinecone_environment = "gcp-starter"
            pinecone_index_name = "ffacil-index"
        
            # Inicializa o cliente Pinecone
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
        
            # Conecta ao índice
            index = pinecone.Index(pinecone_index_name)
        
            # Verifica se existem registros
            info = index.describe_index_stats()
            if info['total_vector_count'] == 0:
        
                # Executando a função de extração
                texts = extract_and_clean(url)
        
                # Instanciando e utilizando o CustomTextLoader
                text_loader = CustomTextLoader(texts)
                documentos = text_loader.load()        
            
                # Convertendo a lista de textos extraídos da url para objetos Document
                documentos_objetos = [Document(content=texto) for texto in texts]
        
                # Carregando os documentos no Pinecone
                pine = Pinecone.from_documents(documentos_objetos, embeddings, index_name=pinecone_index_name)
        
        
            #Criar um DataFrame com as respostas para validação
            aux =  {'criatividade': [criatividade],
            		'tamanho': [tamanho],
            		'estilo': [estilo],
                    'moderacao': [moderacao],
                    'especialidades': [especialidades],
                    'chave': [chave]}
            
            config = pd.DataFrame(aux)
            
            st.session_state['config'] = config
        
            st.session_state['assistente_configurado'] = True
            st.write('Assistente configurado com sucesso!!')
                    
else:
    st.warning('Por favor, insira uma chave válida da API OpenAI para continuar.')