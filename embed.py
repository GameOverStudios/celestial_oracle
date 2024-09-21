import json
print('Loading...')
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from pypdf import PdfReader
import os
#import chromadb
#from chromadb.utils import embedding_functions

directory = 'Test'
chunk_size = 2000  # Adjust this value based on your memory and processing capabilities
overlap_size = 200  # Adjust overlap size as needed
model = SentenceTransformer('flax-sentence-embeddings/all_datasets_v4_MiniLM-L6')

def embed_with_overlap(text, chunk_size, overlap_size):
    """Embeds text with overlapping chunks."""
    embeddings = []
    for i in tqdm(range(0, len(text), chunk_size - overlap_size)):
        chunk = text[i:i + chunk_size]
        embeddings.append(model.encode(chunk))
    return embeddings

def save_embeddings_to_txt(text_embeddings, metadatas, ids, filename):
    """Saves embeddings to a text file."""
    with open(filename, "w") as f:
        print('Saving: '+ filename, end='')
        for i, embedding in enumerate(text_embeddings):
            print('.', end='.')
            metadata_str = json.dumps(metadatas[i])  # Convert metadata to JSON string
            # Convert embedding to a single-line string with spaces
            embedding_str = " ".join(str(x) for x in embedding)
            f.write(f"{ids[i]}[+]{metadata_str}[+]{embedding_str}\n")


# Create ChromaDB collection and add data
def create_chroma_collection(documents, metadatas, ids, embedding_function):
    """Creates a ChromaDB collection and adds data."""
    chroma_client = chromadb.PersistentClient(path="my_vectordb")
    collection = chroma_client.get_or_create_collection(
        name="my_collection", embedding_function=embedding_function
    )
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return collection

# Function to load embeddings from a text file
def load_embeddings_from_txt(filename):
    """Loads embeddings and metadata from a text file."""
    documents = []
    metadatas = []
    embeddings = []
    ids = []

    with open(filename, "r") as f:
        lines = f.readlines()
        i = 0
        while i < len(lines) - 1:  # Check if i is within bounds before accessing lines[i + 1]
            # Extract ID, Metadata, and Embedding
            embd = lines[i].split("[+]")
            id = embd[0]
            metadata_str = embd[1]
            embedding_str = embd[2]
            embedding = [float(x) for x in embedding_str.split()]

            # Extract document from the next line
            document = lines[i + 1].strip()

            # Append data to lists
            ids.append(id)
            metadatas.append(json.loads(metadata_str))  # Evaluate the metadata string
            embeddings.append(embedding)
            documents.append(document)

            i += 2

    return documents, metadatas, ids, embeddings

for file in os.listdir(directory):
    if not file.endswith(".pdf"):
        continue
    with open(os.path.join(directory,file), 'rb') as pdfFileObj:
        print(pdfFileObj)
        reader = PdfReader(pdfFileObj)
        number_of_pages = len(reader.pages)
        text = ""
        for page in tqdm(reader.pages):
            text += page.extract_text()

        text_embeddings = embed_with_overlap(text, chunk_size, overlap_size)
        
        txtFile = pdfFileObj.name.replace('.pdf','.txt')

        # Generate metadata
        metadatas = [{"pdf_file": os.path.basename(file), "chunk_id": i} for i in range(len(text_embeddings))]
        ids = [str(i+1) for i in range(len(text_embeddings))]

        save_embeddings_to_txt(text_embeddings, metadatas, ids, txtFile)
        print('\r\n')

        # Load embeddings and metadata from the text file
        documents, metadatas, ids, embeddings = load_embeddings_from_txt(txtFile)

        # # Create ChromaDB collection with SentenceTransformer embedding
        # sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        #     model_name="all-mpnet-base-v2"
        # )
        # collection = create_chroma_collection(documents, metadatas, ids, sentence_transformer_ef)

        # # Query the vector database
        # # Example queries
        # results = collection.query(
        #     query_texts=["vermiceli"],
        #     n_results=5,
        #     include=["documents", "distances", "metadatas"]
        # )
        # print(results["documents"])

        # results = collection.query(
        #     query_texts=["donut"],
        #     n_results=5,
        #     include=["documents", "distances", "metadatas"]
        # )
        # print(results["documents"])

        # results = collection.query(
        #     query_texts=["shrimp"],
        #     n_results=5,
        #     include=["documents", "distances", "metadatas"]
        # )
        # print(results["documents"])