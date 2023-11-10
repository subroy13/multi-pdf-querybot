import streamsync as ss
import pandas as pd
import datetime as dt
from dependencies import TEMP_PDF_FILE_NAME
from datastore import insert_pdf_to_store, get_llm_response

# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://streamsync.cloud

# Shows in the log when the app starts

def get_chatbot_response(state):
    query = state['chatbot']['query']
    state['chatbot']['response'] = get_llm_response(query)
    state['chatbot']['response_visible'] = True

def add_file_to_db(state):
    input_file = state['database']['input_file']
    if input_file is not None and len(input_file) > 0:
        input_file = input_file[0]
        fdata = input_file[0]

        with open(TEMP_PDF_FILE_NAME, 'wb') as f:
            f.write(fdata)
            f.close()

        # input the file into vector store 
        insert_pdf_to_store(fdata)

def file_change_name(state, payload):
    if payload is not None or len(payload) > 0:
        name = payload[0].get('name')
        state['database']['input_file_name'] = name


def db_selection_delete(state, context):
    del state['database']['files'][context['itemid']]  # remove the item from DB

    # remove embeddings and save into DB
    pass



# Initialise the state

# "_my_private_element" won't be serialised or sent to the frontend,
# because it starts with an underscore
initial_state = ss.init_state({
    "my_app": {
        "title": "Multi PDF QueryBot",
        "primary": "#6699ff",
        "danger": "#ff0000",
        "primary_text": "#ffffff"
    },
    "database":  {
        "files": {
        },
        "input_file": None,
        'input_file_name': ""
    },
    "chatbot": {
        "query": "",
        "response": "",
        "response_visible": False
    }
})
