import os
import neo4j
import msal  # Microsoft Authentication Library
from dotenv import load_dotenv
from neo4j import bearer_auth

(
    print(".env variables loaded!")
    if load_dotenv() else print("Unable to load .env variables.")
)

# Get information from .env file
TENANT_ID = os.environ.get("TENANT_ID")
NEO4J_CLIENT_ID = os.environ.get("NEO4J_CLIENT_ID")

# Service principal credentials
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = [f"api://{NEO4J_CLIENT_ID}/.default"]

# Neo4j connection uri
NEO4J_URI = os.environ.get("NEO4J_URI")


def get_sso_token():
    app = msal.ConfidentialClientApplication (
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    # Acquire token silently or via a new request
    result = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Failed to get token: {result.get('error_description')}")

token = get_sso_token()

with neo4j.GraphDatabase.driver(
    NEO4J_URI,
    auth=bearer_auth(token)
) as driver:
    driver.verify_connectivity()
    records, summary, keys = driver.execute_query(
        "MATCH (n) RETURN n LIMIT 10", 
        database_= "neo4j")
    print("The query `{query}` returned {records_count} records in {time} ms.".format(
    query=summary.query, records_count=len(records),
    time=summary.result_available_after
))