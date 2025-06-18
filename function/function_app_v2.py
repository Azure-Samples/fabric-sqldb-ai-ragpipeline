import fabric.functions as fn
import tiktoken
import requests
import json

#import Client for AI Services
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

udf = fn.UserDataFunctions()

# using managed connection to SQL Database to create database objects
@udf.connection(argName="sqlDB",alias="datamart")
@udf.function()
def create_table(sqlDB: fn.FabricSqlConnection) -> str:
    connection = sqlDB.connect()
    cursor = connection.cursor()
  
    # Create the table if it doesn't exist
    create_table_query = """
      IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'documents' AND TABLE_SCHEMA = 'dbo')
      BEGIN
        CREATE TABLE dbo.documents (
          [ChunkId] INT IDENTITY(1,1) NOT NULL,
          [DocumentLocation] VARCHAR(1000) NULL, 
          [CandidateName] VARCHAR(255) NULL,
          [PhoneNumber] VARCHAR(50) NULL,
          [Email] VARCHAR(255) NULL,
          [CandidateLocation] VARCHAR(1000) NULL,
          [Embedding] VECTOR(1536) NOT NULL,
          [ChunkText] VARCHAR(MAX) NOT NULL,
          CONSTRAINT PK_ChunkId PRIMARY KEY ([ChunkId]) 
        );
      END
    """ 
    cursor.execute(create_table_query)    
    connection.commit()
    # Close the connection
    cursor.close()
    connection.close()               
    return f"Database objects created successfully"


#Using managed connection to SQL Database to insert records
@udf.connection(argName="sqlDB",alias="datamart")
@udf.function()
def insert_data(sqlDB: fn.FabricSqlConnection, data: list, documentLocation: str, candidateName: str, phoneNumber : str, email : str, candidateLocation : str) -> str:
    connection = sqlDB.connect()
    cursor = connection.cursor()    

    insert_query = "INSERT INTO dbo.documents (DocumentLocation, CandidateName, PhoneNumber, Email, CandidateLocation, Embedding, ChunkText) VALUES (?, ?, ?, ?, ?, ?, ?);"     
     
    rows = []
    for d in data:
        row = (documentLocation,candidateName,phoneNumber,email,candidateLocation, json.dumps(d["embedding"]), d["chunk"])
        rows.append(row) 
      
    #bulk insert records
    cursor.executemany(insert_query, rows) 
    connection.commit()

    cursor.close()
    connection.close()               
    return f"{len(data)} rows were added to the documents table"

#Use managed lakehouse connection to connect to lakehouse file system and extract text.

@udf.connection(argName="myLakehouse", alias="blobfilestorage")
@udf.function()
def extract_text(myLakehouse: fn.FabricLakehouseClient, filePath: str, cognitiveServicesEndpoint: str, apiKey: str ) -> str:
  text = "" 
  try:
    document_analysis_client = DocumentAnalysisClient(
    endpoint=cognitiveServicesEndpoint,
    credential=AzureKeyCredential(apiKey)
   )

    connection = myLakehouse.connectToFiles()   

    fileHandle = connection.get_file_client(filePath)
    downloadFile=fileHandle.download_file()
    doc = downloadFile.readall()  
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document=doc)
    result = poller.result()
  
    for page in result.pages:
     for line in page.lines:
         text += line.content + " "
  except Exception as ex:
    raise ex
  return text

@udf.function()
def extract_entities(text: str, cognitiveServicesEndpoint: str, apiKey: str ) -> str:
  client = TextAnalyticsClient(endpoint=cognitiveServicesEndpoint, credential=AzureKeyCredential(apiKey))
  response = client.recognize_entities(documents=[text])
  entity_dict = {
        "PhoneNumber": "",
        "Location": "",
        "Name": "",
        "Email": "",
        "Skills": ""
    }
  for doc in response:
        for entity in doc.entities:
            category = entity.category
            if category == "PhoneNumber":
                mapped_key = "PhoneNumber"
            elif category == "Location":
                mapped_key = "Location"
            elif category == "Person":
                mapped_key = "Name"
            elif category == "Email":
                mapped_key = "Email"
            elif category == "Skill":
                mapped_key = "Skills"
            else:
                continue  # Skip other categories
            # Only set the value if not already set
            if entity_dict[mapped_key] == "":
                entity_dict[mapped_key] = entity.text
    # Return a list containing the dictionary
  return entity_dict
#Chunk text using fixed size chunking strategy,  tiktoken tokenizer
@udf.function()
def chunk_text(text: str, maxToken: int, encoding: str) -> list:
    results = []
    try:
        if not encoding:
          encoding = "cl100k_base"
        tokenizer = tiktoken.get_encoding(encoding)
        tokens = tokenizer.encode(text)
        
        for i in range(0, len(tokens), maxToken):
            chunk_tokens = tokens[i:i + maxToken]
            chunk_text = tokenizer.decode(chunk_tokens)
            results.append(chunk_text)
    except Exception as ex:
        raise ex
    return results

#Using language service to redact sensitive PII data
@udf.function()
def redact_text(text: list, cognitiveServicesEndpoint: str, apiKey: str) -> list:
  
  client = TextAnalyticsClient(
            endpoint=cognitiveServicesEndpoint, 
            credential=AzureKeyCredential(apiKey))
  result = []
  for item in text :
    record =[item]
    response = client.recognize_pii_entities(record, language="en")
    result.append(response[0]["redacted_text"])
  return result

#Generate embeddings using Azure Open AI Service 
@udf.function()
def generate_embeddings(text: list, openAIServiceEndpoint: str, 
    embeddingModel: str, openAIKey: str) -> list: 
 results = []
 try:
  openai_url = f"{openAIServiceEndpoint}/openai/deployments/{embeddingModel}/embeddings?api-version=2023-05-15"
  for chunk in text:
    embedding = get_embedding(chunk, openai_url, openAIKey)
    data={     
      "embedding" : embedding,      
      "chunk": chunk
    }
    results.append(data)
 except Exception as ex:
  raise ex
 return results


# Private / internal function - emebedd individual text
def get_embedding(text: str, openaiurl: str, openaikey: str) -> list:
  embedding = []
  try:
   response = requests.post(openaiurl,
    headers={"api-key": openaikey, "Content-Type": "application/json"},
     json={"input": [text]}  # Embed the extracted chunk
    )    
   if response.status_code == 200:
     response_json = response.json()
     embedding = json.loads(str(response_json['data'][0]['embedding']))     
  except Exception as ex:
    raise ex
  return embedding
