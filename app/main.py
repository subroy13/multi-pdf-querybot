import streamsync as ss
import pandas as pd
import datetime as dt
from dependencies import TEMP_PDF_FILE_NAME
from datastore import insert_pdf_to_store, get_llm_response, load_metadata_database, delete_pdf_from_store

# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://streamsync.cloud

# Shows in the log when the app starts

def get_chatbot_response(state):
    state['chatbot']['response_visible'] = False
    state['chatbot']['thinking_message'] = "% Thinking..."
    query = state['chatbot']['query']
    try:
        state['chatbot']['response'] = get_llm_response(query)
        state['chatbot']['thinking_message'] = '+ Here you go, please find the answer below.'
        state['chatbot']['response_visible'] = True
    except Exception as e:
        state['chatbot']['thinking_message'] = f"- {str(e)}\nPlease try again"  

def add_file_to_db(state):
    fdata = state['database']['input_file']
    print(fdata)
    if fdata is not None:
        with open(TEMP_PDF_FILE_NAME, 'wb') as f:
            f.write(fdata)
            f.close()

        # input the file into vector store 
        insert_pdf_to_store(state['database']['input_file_name'], state)
        state['database']['files'] = load_metadata_database()


def file_change_name(state, payload):
    if payload is not None or len(payload) > 0:
        name = payload[0].get('name')
        state['database']['input_file_name'] = name
        state['database']['input_file'] = payload[0].get('data')


def db_selection_delete(state, context):
    delete_pdf_from_store(context['itemId'], state)
    state['database']['files'] = load_metadata_database()


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
        "files": load_metadata_database(),
        "input_file": None,
        'input_file_name': "",
        "parse_message": ""
    },
    "chatbot": {
        "query": "",
        "response": "",
        "thinking_message": "", 
        "response_visible": False
    }
})
