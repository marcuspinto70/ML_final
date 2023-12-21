import streamlit as st 
import pandas as pd
import numpy as np
from pycaret.regression import load_model, predict_model


# Caminho para o arquivo
path = "aluguel_unique.xlsx"


# Ler xlsx
dados = pd.read_excel(path)


regioes_ordenadas = ['Selecione uma região'] + sorted(dados['regiao_nome'].unique())


modelo = load_model('recursos/modelo-previsao-aluguel-sp')


st.header('Previsão de Valor do Aluguel na cidade de São Paulo  🏠')
st.write('Entre com as caracteristicas do imóvel')



#Widgets para fazer os inputs do modelo

col0, col1, col15, col2, col3 = st.columns([0.2,3,1,0.2,3])

with col0:
	c = st.checkbox(label = 'Assinale a caixa ao lado', 
		value = True,
		kwargs=None,
	 	disabled=False, 
	 	label_visibility="collapsed") #hidden #collapsed


with col1:
    valor_imovel = st.slider(label = 'Valor de Venda (100k)', 
        min_value=120., 
        max_value=4500., 
        value= 120., 
        step=1., 
        help='Entre com o valor de venda do imóvel',
        disabled = not c)


    area = st.slider(label = 'Área (m2)', 
        min_value=10, 
        max_value=1200, 
        value= 90, 
        step=1)


    regiao_nome = st.selectbox(label = 'Região', 
        options = regioes_ordenadas, 
        index = 0,
        format_func=lambda x: 'Selecione uma região' if x == 'Selecione uma região' else x)



    vagas = st.number_input(
        label='Nro de Vagas de Garagem',
        min_value=0,
        max_value=20,
        value=1,
        step=1)
    
    

with col2:
	d = st.checkbox(label = 'Assinale', 
		value = True,
		kwargs=None,
	 	disabled=False, 
	 	label_visibility="collapsed") #hidden #collapsed


with col3:
    condo_iptu = st.slider(
        label='Valor do Condomío e IPTU',
        min_value=500.,
        max_value=25000.,
        value=1500.,
        step=1.,
        help='Entre com o valor do condomínio e IPTU somados',
        disabled=not d
    )

    tipo = st.radio(
        'Tipo do Imóvel',
        ['Apartamento', 'casa', 'CasaCondominio', 'StudioOuKitchenette'],
        key='tipo'
    )

    # Define o valor padrão de quartos
    valor_quartos_padrao = 0 if tipo == 'StudioOuKitchenette' else 2

    quartos = st.number_input(
        'Nro de Dormitórios',
        min_value=0,
        max_value=14,
        value=valor_quartos_padrao,
        step=1,
        key='quartos',
        disabled=tipo == 'StudioOuKitchenette'
    )



#Criar um DataFrame com os inputs exatamente iguais aos do dataframe em que foi treinado o modelo
aux =  {'quartos': [quartos],
		'tipo': [tipo,],
		'area': [area], 
		'valor_imovel (100k)': [valor_imovel if c else np.NaN],
		'condo_iptu': [condo_iptu if d else np.NaN],
		'vagas': [vagas],
		'regiao_nome': [regiao_nome]}

prever = pd.DataFrame(aux)

#st.write(prever)

#Usar o modelo salvo para fazer previsao nesse Dataframe

_, c1, _ = st.columns([2,3,1])

with c1:
	botao = st.button('Calcular Valor do Aluguel',
		type = 'primary',
		use_container_width = True)

if botao:
    if regiao_nome == 'Selecione uma região':
        st.error('Por favor, selecione uma região para continuar.')
    else:	
        previsao = predict_model(modelo, data = prever)
        valor = round(previsao.loc[0,'prediction_label'], 2)
        st.write(f'### O valor previsto de aluguel é de ${valor}')