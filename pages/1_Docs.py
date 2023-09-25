import streamlit as st

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import ConversationChain, ConversationalRetrievalChain, RetrievalQA
from langchain.callbacks import StreamlitCallbackHandler, get_openai_callback, FileCallbackHandler
from langchain.memory.chat_message_histories import SQLChatMessageHistory

from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationTokenBufferMemory, ConversationBufferMemory
import uuid
import os
from mangue import get_credentials, get_eastereggs


st.set_page_config(page_title='MangueBot | Docs', page_icon=':crab:', layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Análise de documentos 📑")

origem = 'https://sites.tcu.gov.br/contas-do-presidente/'
origem

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = session_id = 'doc-'+str(uuid.uuid4())
    
    
chat_message_history = SQLChatMessageHistory(
    session_id=st.session_state['session_id'],
    connection_string='sqlite:///sqlite.db'
)

####
from langchain.chat_models import ChatVertexAI 

import google.auth

KEYS = get_credentials()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEYS
credentials, project_id = google.auth.load_credentials_from_file(KEYS)

###
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    
with st.sidebar:
    st.subheader('Modelo: Google - chat-bison')
    temperatura = st.slider('Criatividade', min_value=0, max_value=10, value=0, step=1, disabled=True)
    k = st.slider('Documentos', min_value=1, max_value=5, value=2, step=1)
    max_tokens = st.slider('Tamanho da resposta', min_value=128, max_value=2048, value=512, step=1)
    if st.button("Limpar", type='primary'):
        del st.session_state['session_id']
        del st.session_state['messages']
        st.experimental_rerun()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, eu sou o DocBot, o seu assistente virtual para documentos. Respondo perguntas sobre o parecer prévio do TCU sobre as contas da Presidência da República do exercício 2022."}]
    chat_message_history.add_ai_message(st.session_state["messages"][0]["content"])

for msg in st.session_state.messages:
    # short_llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=temperatura/10)
    # memory = ConversationTokenBufferMemory(llm=short_llm, max_token_limit=10000, memory_key="chat_history", return_messages=True)
    # memory = ConversationBufferMemory()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    if msg["role"] == "assistant":
        st.chat_message(msg["role"], avatar='🤖').write(msg["content"])
        memory.chat_memory.add_ai_message(msg["content"])
    elif msg["role"] == "user":    
       st.chat_message(msg["role"], avatar='🕵️‍♂️').write(msg["content"], avatar=':user:')
       memory.chat_memory.add_user_message(msg["content"])
    else:    
       memory.chat_memory.add_message('system', msg["content"])


if prompt := st.chat_input('Mensagem'):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar='🕵️‍♂️').write(prompt)
    chat_message_history.add_user_message(prompt)
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(collection_name='tcu', persist_directory="./chroma_db", embedding_function=embeddings)

    with st.spinner('Pensando...'):
        stream_handler = StreamlitCallbackHandler(st.empty())
        # long_llm = ChatOpenAI(model_name='gpt-3.5-turbo-16k', streaming=True, temperature=temperatura/10, callbacks=[stream_handler])
        llm = ChatVertexAI(credentials=credentials, project_id=project_id, max_output_tokens=max_tokens, temperature=temperatura/10)
        qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(k=k), memory=memory)
        response = qa(prompt)
        msg = response['answer']
        chat_message_history.add_ai_message(msg)
        source = vectorstore.similarity_search(prompt)
        get_eastereggs(prompt)
        st.chat_message("assistant", avatar='🤖').write(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.expander("Ver contexto"):
            for page in source:
                st.write(page.page_content)
