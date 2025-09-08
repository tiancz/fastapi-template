from langchain_community.embeddings import ZhipuAIEmbeddings

embeddings = ZhipuAIEmbeddings()

print(embeddings.embed_query("hello world"))