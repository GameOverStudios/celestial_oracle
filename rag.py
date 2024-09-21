import json
import sqlite3
from tqdm import tqdm
from pypdf import PdfReader
import os
#import chromadb
#from chromadb.utils import embedding_functions

def embed_with_overlap(file, text, chunk_size, overlap_size):
    """Embeds text with overlapping chunks."""
    embeddings = []
    for i in tqdm(range(0, len(text), chunk_size - overlap_size), desc="Processing Chunks"):
        chunk = text[i:i + chunk_size]
        embeddings.append(model.encode(chunk))
        
        # Save embedding to SQLite immediately
        save_embedding_to_sqlite(embeddings[-1], {"pdf_file": os.path.basename(file), "chunk_id": i}, chunk, db_file)
        
    return embeddings

def save_embedding_to_sqlite(embedding, metadata, text, db_file):
    """Saves an embedding and metadata to an SQLite database."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            metadata TEXT,
            embedding TEXT,
            text TEXT
        )
    ''')

    metadata_str = json.dumps(metadata)
    embedding_str = " ".join(str(x) for x in embedding)
    
    # Insert the data
    cursor.execute(
        "INSERT INTO embeddings VALUES (NULL, ?, ?, ?, ?)",
        (metadata['pdf_file'], metadata_str, embedding_str, text)
    )

    conn.commit()
    conn.close()

def create_chroma_collection(documents, metadatas, ids, embedding_function):
    """Creates a ChromaDB collection and adds data."""
    chroma_client = chromadb.PersistentClient(path="my_vectordb")
    collection = chroma_client.get_or_create_collection(
        name="my_collection", embedding_function=embedding_function
    )
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return collection

def load_embeddings_from_sqlite(db_file):
    """Loads embeddings and metadata from a SQLite database."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    documents = []
    metadatas = []
    embeddings = []
    ids = []

    for row in cursor.execute("SELECT id, filename, metadata, embedding, text FROM embeddings"):
        ids.append(row[0])
        metadatas.append(json.loads(row[2]))  # Adjust to load metadata from correct column
        embeddings.append([float(x) for x in row[3].split()])  # Convert embedding string to list of floats
        documents.append(row[4])

    conn.close()
    return documents, metadatas, ids, embeddings

def process_pdf_embeddings():
    for file in os.listdir(directory):
        #try:
        if not file.endswith(".pdf"):
            continue
        with open(os.path.join(directory,file), 'rb') as pdfFileObj:          
            print('[+] ' + pdfFileObj.name)
            reader = PdfReader(pdfFileObj)
            number_of_pages = len(reader.pages)
            text = ""
            for page in tqdm(reader.pages, desc="Processing Pages"):
                text += page.extract_text()

            embed_with_overlap(file, text, chunk_size, overlap_size)
        #except:
            #print('***ERROR*** [-] >>> ' + file)

def get_chunks(db_file, filename=None, chunk_id=None):
    """Retrieves chunks from the SQLite database.

    Args:
        db_file (str): The path to the SQLite database file.
        filename (str, optional): The name of the PDF file to retrieve chunks from. Defaults to None.
        chunk_id (int, optional): The ID of the chunk to retrieve. Defaults to None.

    Returns:
        list: A list of tuples containing (id, filename, metadata, embedding, text) for the retrieved chunks.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    query = "SELECT id, filename, metadata, embedding, text FROM embeddings"
    params = []

    if filename:
        query += " WHERE filename = ?"
        params.append(filename)
    if chunk_id:
        if filename:
            query += " AND id = ?"
        else:
            query += " WHERE id = ?"
        params.append(chunk_id)

    chunks = cursor.execute(query, params).fetchall()

    conn.close()
    return chunks

def load_embeddings_chromadb():
    # Load embeddings and metadata from the SQLite database
    documents, metadatas, ids, embeddings = load_embeddings_from_sqlite(db_file)

    # # Create ChromaDB collection with SentenceTransformer embedding
    # sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    #     model_name="all-mpnet-base-v2"
    # )
    # collection = create_chroma_collection(documents, metadatas, ids, sentence_transformer_ef)

    # # Query the vector database
    # # Example queries
    # # results = collection.query(
    # #     query_texts=["vermiceli"],
    # #     n_results=5,
    # #     include=["documents", "distances", "metadatas"]
    # # )
    # # print(results["documents"])

    # # results = collection.query(
    # #     query_texts=["donut"],
    # #     n_results=5,
    #     include=["documents", "distances", "metadatas"]
    # # )
    # # print(results["documents"])

    # # results = collection.query(
    # #     query_texts=["shrimp"],
    # #     n_results=5,
    #     include=["documents", "distances", "metadatas"]
    # # )
    # # print(results["documents"])

def print_pdf_chunks(db_file, filename, num_chunks=None):
    """Prints PDF chunks from the SQLite database.

    Args:
        db_file (str): Path to the SQLite database.
        filename (str): Name of the PDF file.
        num_chunks (int, optional): Number of chunks to print. Defaults to None (print all).
    """
    try:
        chunks = get_chunks(db_file, filename=filename)
        if num_chunks is not None:
            chunks = chunks[:num_chunks]  # Limit to specified number of chunks

        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1}:")
            print(chunk[4])  # Print the text of the chunk
            print("-" * 20)  # Separator
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("The 'embeddings' table does not exist. Please run the script to create it.")

generate = False
db_file = 'Ebooks.db'
directory = 'Test'
chunk_size = 8000
overlap_size = 200

if generate == True:
    print('Loading...')
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('flax-sentence-embeddings/all_datasets_v4_MiniLM-L6')
    process_pdf_embeddings()
else: model = ''

print_pdf_chunks(db_file, 'A Dictionary of Angels, including the fallen angels - PDF Room.pdf', num_chunks=3)