import chromadb
from chromadb.utils import embedding_functions

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="nomic-embed-text"
)

client = chromadb.PersistentClient(path="./knowledge_base")
policy_collection = client.get_or_create_collection(
    name="policy",
    embedding_function=ollama_ef
)

results = policy_collection.query(
    query_texts=["design quality and place-making"],
    n_results=3
)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(meta, "\n", doc[:200], "\n---")