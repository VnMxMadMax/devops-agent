import chromadb
from typing import List, Dict, Any

# Persistent local database
client = chromadb.PersistentClient(path="./chroma_db")

# Create or load collection

collection = client.get_or_create_collection(
    name="incident_history"
)


def save_incident(
    incident_id: str,
    symptoms: str,
    root_cause: str,
    resolution: str
) -> None:
    """
    Save a resolved incident into long-term memory.

    The data is stored as a vectorized document so future
    incidents can be matched semantically.
    """

    # Create a single searchable document
    document = f"""
    Symptoms:
    {symptoms}

    Root Cause:
    {root_cause}

    Resolution:
    {resolution}
    """

    collection.upsert(
        ids=[incident_id],
        documents=[document],
        metadatas=[{
            "root_cause": root_cause,
            "resolution": resolution
        }]
    )

def search_past_incidents(
    symptoms: str,
    n_results: int = 2
) -> Dict[str, Any]:
    """
    Search memory for similar historical incidents.

    Returns the closest semantic matches based on symptoms.
    """

    results = collection.query(
        query_texts=[symptoms],
        n_results=n_results
    )

    return results