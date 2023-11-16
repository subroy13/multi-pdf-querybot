from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import json

TEMP_PDF_FILE_NAME = 'temp.pdf'
METADATA_DB_PATH = './database/metadata.json'
CHROMADB_PATH = './database/chroma'


# Create a creds.json with the proper API tokens
with open('creds.json', 'r') as f:
    creds = json.load(f)
    HF_API_TOKEN = creds['HF_API_TOKEN']
    CLAUDE_API_KEY = creds['CLAUDE_API_KEY']
    f.close()


CHUNK_SIZE = 1000


embeder = HuggingFaceInferenceAPIEmbeddings(
    api_key=HF_API_TOKEN, model_name="sentence-transformers/all-MiniLM-l6-v2"
)
chroma_client = Chroma(
    embedding_function=embeder,
    persist_directory=CHROMADB_PATH
)
claude = Anthropic(api_key=CLAUDE_API_KEY)

# claude API calling function
def claude_completion(prompt, model_name = "claude-instant-1", max_tokens = 500):
    final_prompt = f"{HUMAN_PROMPT} " + str(prompt) + f" {AI_PROMPT}"
    res = claude.completions.create(
        model = model_name,
        max_tokens_to_sample = max_tokens,
        prompt=final_prompt
    )
    return res.completion
