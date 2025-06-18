import os
from typing import Optional
from dotenv import load_dotenv
import requests
import json
from azure.identity import InteractiveBrowserCredential
from mcp.server.fastmcp import FastMCP

# Extracting environment variables
load_dotenv()
FABRIC_GRAPHQL_ENDPOINT = os.getenv("FABRIC_GRAPHQL_ENDPOINT")

# Initialising MCP server
mcp = FastMCP("Microsoft Fabric GraphQL MCP Server")

# Getting Entra ID access token
app = InteractiveBrowserCredential()
scp = "https://analysis.windows.net/powerbi/api/user_impersonation"
result = app.get_token(scp)
if not result.token:
    raise Exception("Could not get access token")
token = result.token

# Function to execute GraphQL query
def execute_graphql_query(endpoint, query, variables):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(endpoint, json={'query': query, 'variables': variables}, headers=headers)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data, indent=4)
    except Exception as error:
        return f"Query failed with error: {error}"

@mcp.tool()
def get_resumes(search_query: str, top: int, candidateLocation: Optional[str] = None) -> str:
    """Retrieve the matching contextual resumes from the database based on the search query."""
    query = """
    query executesimilarity_search($top: Int!, $search_query: String!, $candidateLocation: String!) {
            executesimilarity_search(top: $top, search_query: $search_query, candidateLocation: $candidateLocation) {
                DocumentLocation
                CandidateName
                PhoneNumber
                CandidateLocation
                Email
                ChunkText       
                Score  
        }
    }
    """
    variables = {"top": top, "search_query": search_query, "candidateLocation": candidateLocation} 
    result = execute_graphql_query(FABRIC_GRAPHQL_ENDPOINT, query, variables)
    return result


# Start the server
if __name__ == "__main__":
    mcp.run()