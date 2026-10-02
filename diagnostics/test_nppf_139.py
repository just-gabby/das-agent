import chromadb
from chromadb.utils import embedding_functions

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="nomic-embed-text"
)

client = chromadb.PersistentClient(path="./knowledge_base")

policy = client.get_or_create_collection(
    name="policy",
    embedding_function=ollama_ef
)

results = policy.get(
    where={
        "$and": [
            {"policy_document": "NPPF"},
            {"paragraph_number": "139"}
        ]
    },
    include=["documents", "metadatas"]
)

print("\n========================================")
print("NPPF PARAGRAPH 139 TEST")
print("========================================")

print(f"\nRecords found: {len(results['ids'])}")

for document, metadata in zip(
    results["documents"],
    results["metadatas"]
):
    print("\nMetadata:")
    print(metadata)

    print("\nText:")
    print(document)

print("\n========================================")
