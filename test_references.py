import chromadb
client = chromadb.PersistentClient(path='./knowledge_base')
policy = client.get_collection('policy')
metas = policy.get(include=['metadatas'])['metadatas']
print(sorted(set(m.get('policy_document', '') for m in metas)))
