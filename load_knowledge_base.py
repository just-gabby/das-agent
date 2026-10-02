from pathlib import Path
from docx import Document
import chromadb
from chromadb.utils import embedding_functions

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="nomic-embed-text"
)

# Open (or create) the local database folder
client = chromadb.PersistentClient(path="./knowledge_base")

collection = client.get_or_create_collection(
    name="precedents",
    embedding_function=ollama_ef
)

source_folder = Path("/Users/netadmin/Documents/AI/Datasets/DAS")
print(f"Looking in: {source_folder.resolve()}")
print(f"Files found: {len(list(source_folder.rglob('*.docx')))}")

for docx_path in source_folder.rglob("*.docx"):
    section = docx_path.parent.name
    project_name = docx_path.stem

    doc = Document(docx_path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if not text:
        print(f"Skipping empty file: {docx_path}")
        continue

    collection.add(
        documents=[text],
        metadatas=[{
            "doc_type": "DAS",
            "section": section,
            "project_name": project_name
        }],
        ids=[str(docx_path.relative_to(source_folder))]
    )

print(f"Loaded {collection.count()} sections into the knowledge base.")