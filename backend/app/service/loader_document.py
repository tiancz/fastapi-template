import bs4
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import WebBaseLoader

page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"

loader = WebBaseLoader(web_paths=[page_url])
docs = []
async for doc in loader.alazy_load():
    docs.append(doc)

assert len(docs) == 1
doc = docs[0]

loader = CSVLoader(file_path='data.csv',encoding='utf-8')
data = loader.load()