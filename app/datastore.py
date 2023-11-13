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


def insert_pdf_to_store(filename: str, state):
    fileid = filename.replace('.', '')
    try:
        loader = PyPDFLoader(TEMP_PDF_FILE_NAME)   # uses the pypdf to parse the PDF
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=0)   # create a character text splitters
        state['database']['parse_message'] = '% Extracting texts'
        pages = loader.load_and_split(
            text_splitter=text_splitter
        )   # split the parse PDF text into Chunks
        docs = []
        for page in pages:
            page.metadata['docfilename'] = filename
            page.metadata['docfileid'] = fileid
            docs.append(page)
        state['database']['parse_message'] = '% Extracting embeddings'
        chroma_client.add_documents(docs)       # computes the embeddings and stores the documents into vector DB

        state['database']['parse_message'] = '% Saving to vector store'
        chroma_client.persist()   # save to the disk

        state['database']['parse_message'] = '% Saving metadata information'
        metadata = load_metadata_database()
        metadata[fileid] = {
            'fname': filename,
            'chunks': len(pages),
            'createdat': dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')        
        }
        save_metadata_database(metadata)
        state['database']['parse_message'] = f"+File {filename} parsed successfully"
    except Exception as e:
        state['database']['parse_message'] = f"- {str(e)}\nPlease try again"

def delete_pdf_from_store(fileid: str, state):
    try:
        state['database']['parse_message'] = '% Deleting metadata'

        # delete from metadata
        metadata = load_metadata_database()
        del metadata[fileid]
        save_metadata_database(metadata)

        state['database']['parse_message'] = '% Deleting embeddings'
        # delete corresponding embedding
        doclist = chroma_client.get(where={'docfileid': fileid})
        if len(doclist['ids']) > 0:
            chroma_client.delete(ids = doclist['ids'])
            chroma_client.persist()
        state['database']['parse_message'] = '+ Successfully deleted file from data store'
    except Exception as e:
        state['database']['parse_message'] = f"- {str(e)}\nPlease try again"    

def get_llm_response(query: str):
    ret = chroma_client.as_retriever().get_relevant_documents(query)   # get the closest matched document of this query
    prompt = """
    Based on the following context, try to answer the question only using the context. If the answer is not provided in the context, do not try to guess, simply say that you do not know.
    Also, it is VERY important that you do NOT use the word 'context' in your answer response.

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


