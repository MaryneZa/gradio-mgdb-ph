import os
import re
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI, connect=False)
db = client['text_phoneme']
collection = db['data']

def insert_data(text, phoneme):
    """
    Insert or update a document in the MongoDB collection.

    Args:
        text (str): The input text.
        phoneme (str): The input phoneme.

    Returns:
        str: A status message indicating the result of the operation.
    """
    try:
        document = {"text": text, "phoneme": phoneme}
        collection.insert_one(document)
        return f'<div style="display: flex; flex-direction: row; align-items: center;"><span style="color: #51D1E1; font-weight: bold;">Data added!</span>&nbsp;<span>text: {text} phoneme: {phoneme}</span></div>'
    except DuplicateKeyError:
        # If the text already exists, update the phoneme
        try:
            collection.update_one({"text": text}, {"$set": {"phoneme": phoneme}})
            return f'<div style="display: flex; flex-direction: row; align-items: center;"><span style="color: #51D1E1; font-weight: bold;">Phoneme updated!</span>&nbsp;<span>text: {text} new phoneme: {phoneme}</span></div>'
        except Exception as e:
            return f'<span style="color: red;">Error updating phoneme: {str(e)}</span>'
    except Exception as e:
        return f'<span style="color: red;">Error adding data: {str(e)}</span>'

def fetch_data(search_query=None):
    """
    Fetch data from the MongoDB collection and filter based on the search query.

    Args:
        search_query (str, optional): The search query to filter data. Defaults to None.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the fetched data.
        str: A status message indicating any error occurred during the operation.
    """
    try:
        documents = list(collection.find({}))
        data = {"text": [], "phoneme": []}
        for doc in documents:
            if 'text' in doc and 'phoneme' in doc:
                data["text"].append(doc['text'])
                data["phoneme"].append(doc['phoneme'])
        df = pd.DataFrame(data)
        if search_query:
            pattern = re.compile(search_query, re.IGNORECASE)  # Compile the pattern with case insensitivity
            df = df[df['text'].apply(lambda x: bool(pattern.search(x)))]
        return df, None
    except Exception as e:
        return pd.DataFrame(), f'<span style="color: red;">Error fetching data: {str(e)}</span>'
