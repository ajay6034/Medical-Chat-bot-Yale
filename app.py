from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import HuggingFaceDatasetLoader
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
import os
import gradio as gr

from dotenv import load_dotenv
load_dotenv()


dataset_name = "Pijush2023/Yale_Psychilogy"
page_content_column = 'Biography'
loader = HuggingFaceDatasetLoader(dataset_name, page_content_column)
data = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
documents = text_splitter.split_documents(data)


embeddings=OpenAIEmbeddings(api_key=os.environ['OPENAI_API_KEY'])
# Instantiate chat model
chat_model= ChatOpenAI(api_key=os.environ['OPENAI_API_KEY'], temperature=0.5, model='gpt-3.5-turbo-0125')

# pip install pinecone-client
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

index_name = "medical"

if index_name not in pc.list_indexes().names():
  pc.create_index(
      name=index_name,
      dimension=1536,
      metric='cosine',
      spec=ServerlessSpec(
          cloud='aws',
          region='us-east-1'
      )
  )

vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
vectorstore.add_documents(documents)

query = "who is the best doctor for depression?"
vectorstore.similarity_search(query,k=1)

retriever = vectorstore.as_retriever(search_kwargs={'k':1})
docs = retriever.invoke("who is the best doctors for depression ?")

prompt=hub.pull("rlm/rag-prompt")

rag_chain=(
    {"context":retriever , "question" : RunnablePassthrough()}
    | prompt
    | chat_model
    | StrOutputParser()
)

query="depression"
rag_chain.invoke(query)

def generate_answer(message, history):
    return rag_chain.invoke(message)

# Set up chat bot interface
answer_bot = gr.ChatInterface(
                            generate_answer,
                            chatbot=gr.Chatbot(height=300),
                            textbox=gr.Textbox(placeholder="Ask me a question about Doctor on Psychiatry", container=False, scale=7),
                            title="Psychiatry Doctor Chat-Bot",
                            description="This is a chat bot related to top School in United States about Psychiatry",
                            theme="soft",
                            examples=["depression", "Mental-Stress", "Bipolar Disorder", "Eating Disorders" , "etc....."],
                            cache_examples=False,
                            retry_btn=None,
                            undo_btn=None,
                            clear_btn=None,
                            submit_btn="Ask"
                        )

answer_bot.launch()

