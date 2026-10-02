from pathlib import Path
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions
import re

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="nomic-embed-text"
)

client = chromadb.PersistentClient(path="./knowledge_base")
policy_collection = client.get_or_create_collection(
    name="policy",
    embedding_function=ollama_ef
)

def split_page_into_policies(page_text):
    pattern = r"\n(?=[A-Z]{1,6}\d+:\s)"
    pieces = re.split(pattern, page_text)
    return [p.strip() for p in pieces if p.strip()]

def split_into_lettered_clauses(text):
    """Split any block of text into its lettered sub-clauses (a., b., c., ...),
    tagging each with its letter, plus any intro text before the list. Used
    for both named policies (PM15) and plain paragraphs with sub-clauses
    (NPPF 135(a)-(f))."""
    pieces = re.split(r"\n(?=\(?[a-z]\)?\.?\s?[A-Za-z])", text)
    chunks = []
    intro = pieces[0].strip()
    if intro:
        chunks.append({"clause": "", "text": intro})
    for piece in pieces[1:]:
        piece = piece.strip()
        letter_match = re.match(r"^\(?([a-z])\)?\.?\s?", piece)
        chunks.append({"clause": letter_match.group(1) if letter_match else "", "text": piece})
    return chunks

def split_into_paragraphs(text):
    pieces = re.split(r"\n(?=\d{1,3}\.\s)", text)
    return [p.strip() for p in pieces if p.strip()]

policy_folder = Path("/Users/netadmin/Documents/AI/Datasets/PolicyLibrary")

for pdf_path in policy_folder.rglob("*.pdf"):
    policy_document = pdf_path.parent.name
    version_label = pdf_path.stem
    reader = PdfReader(pdf_path)

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text or not text.strip():
            continue

        for block in split_page_into_policies(text):
            header_match = re.match(r"^([A-Z]{1,6}\d+):\s*(.+)", block)

            if header_match:
                policy_code = header_match.group(1)
                for i, clause in enumerate(split_into_lettered_clauses(block)):
                    policy_collection.upsert(
                        documents=[clause["text"]],
                        metadatas=[{
                            "policy_document": policy_document,
                            "version": version_label,
                            "page": page_number,
                            "policy_code": policy_code,
                            "paragraph_number": "",
                            "clause": clause["clause"]
                        }],
                        ids=[f"{policy_document}_{version_label}_p{page_number}_{policy_code}_{i}"]
                    )
            else:
                for para_text in split_into_paragraphs(block):
                    para_match = re.match(r"^(\d{1,3})\.\s*(.+)", para_text, re.DOTALL)
                    if not para_match:
                        continue
                    paragraph_number = para_match.group(1)
                    for i, clause in enumerate(split_into_lettered_clauses(para_text)):
                        policy_collection.upsert(
                            documents=[clause["text"]],
                            metadatas=[{
                                "policy_document": policy_document,
                                "version": version_label,
                                "page": page_number,
                                "policy_code": "",
                                "paragraph_number": paragraph_number,
                                "clause": clause["clause"]
                            }],
                            ids=[f"{policy_document}_{version_label}_p{page_number}_{paragraph_number}_{i}"]
                        )

print(f"Loaded {policy_collection.count()} policy chunks into the library.")