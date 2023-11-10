#############
# This module handles all data store related operations
############
import json
import datetime as dt
from dependencies import (
    TEMP_PDF_FILE_NAME, METADATA_DB_PATH,
    CHUNK_SIZE, chroma_client, claude_completion
)
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter



def load_metadata_database():
    with open(METADATA_DB_PATH, 'r') as f:
        data = json.load(f)
        f.close()
    return data

def save_metadata_database(data):
    with open(METADATA_DB_PATH, 'w') as f:
        json.dump(data, f)
        f.close()
    return True


def insert_pdf_to_store(filename: str):
    loader = PyPDFLoader(TEMP_PDF_FILE_NAME)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=0)
    print('Extracting texts')
    pages = loader.load_and_split(
        text_splitter=text_splitter
    )
    print('Processing embeddings')
    chroma_client.add_documents(pages)
    chroma_client.persist()   # save to the disk

    print('Saving metadata')
    metadata = load_metadata_database()
    metadata[filename.replace('.', '')] = {
        'fname': filename,
        'chunks': len(pages),
        'createdat': dt.datetime.now().strftime('%d-%m-%Y')        
    }
    save_metadata_database(metadata)


def get_llm_response(query: str):
    ret = chroma_client.as_retriever().get_relevant_documents(query)
    prompt = """
    Based on the following context, try to answer the question only using the context. If the answer is not provided in the context, do not try to guess, simply say that you do not know.

    Examples:

    Context: Bruce Wayne is simply a rich young CEO of the company at day, but during night, he is the upholder of justice, as the mighty Batman.
    Question: Who is Batman?
    Answer: Bruce Wayne is the Batman

    Question: Who is Superman?
    Answer: I don't know.
    ---
    Context: {context}
    ---

    Question: {question}
    Answer: """.format(context = "\n\n".join([x.page_content for x in ret]), question = query)
    return claude_completion(prompt)


