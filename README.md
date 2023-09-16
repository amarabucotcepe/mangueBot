# mangueBot

É um projeto conceitual para apresentar capacidades e habilidades que podem ser desenvolvidas com o uso de inteligência artificial baseada em Large Language Models (LLM). 

* 🔗 Link: https://manguebot.streamlit.app

O aplicativo consiste em três robôs:

- **🦀 MangueBot :** um robô relacionado ao universo cultural da mangue beat. Compõe-se de uma chain conectada a vectorstore com algumas letras de músicas das bandas Nação Zumbi e Mundo Livre S/A. Possibilita obter informações sobre o movimento, artistas, letrar, inclusive criar novas composições a partir dessa base de conhecimento.

- **📑 DocBot:** um robô relacionado ao análise de documentos. Compõe-se de uma chain conectada a vectorstore com o Parecer Prévio do TCU sobre as contas da Presidência da República de 2022. Possibilita fazer perguntas e obter resumos, dentre outras tarefas, sobre a documentação que apresenta ~500 páginas.

- **🎲 DataBot:** um robô relacionado a análise de dados. Compõe-se de uma chain conectada a um banco de dados sql que permite gerar consultas sql a partir dos perguntas enviadas, e usa outra chain para transformar os dados em tabelas markdown.

Algumas das tecnologias utilizadas: 
* Streamlit - FrontEnd
* LangChain - Backend
* Pandas - Manipulação de dados
* Chroma - Vectorstore
* Sqlite - Banco de dados
* VertexAI - Plataforma de IA da Google 
* OpenAI - API

Fonte dos dados:
* Portal letras (https://www.letras.mus.br)
* TCU (https://portal.tcu.gov.br/contas-e-fiscalizacao/contas-do-presidente-da-republica/)
* Portal da Transparência Federal (https://portaldatransparencia.gov.br/download-de-dados)