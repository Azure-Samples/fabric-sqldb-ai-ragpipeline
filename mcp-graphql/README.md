> 📘 **Note:** If you're looking for a step-by-step guide for building a **Retrieval Augmented Generation (RAG) pipeline** alone, visit [RAG Pipeline](/README.md)

# Chat with your data using SQL Database in Fabric, GraphQL and MCP Server.

This project builds upon the step-by-step guidance for creating a Retrieval-Augmented Generation (RAG) pipeline to make your data AI-ready. It extends the previous implementation by demonstrating how to expose the processed data—stored in a SQL Database in Microsoft Fabric through a GraphQL endpoint. Furthermore, it shows how to **Integrate GraphQL with a Model Context Protocol (MCP) server**, enabling agentic interactions with your data.

The RAG pipeline is automatically triggered whenever a file is uploaded to Azure Blob Storage. It processes the file by extracting textual content, identifying candidate information, chunking the text, generating embeddings, and storing those embeddings in SQL Database in Fabric. This enriched data is then made accessible via GraphQL and can be consumed by MCP agents through the MCP server, allowing for natural language interactions with your enterprise data.

![RAG to Chat](/content/RAG_v2.png)

## Prerequisite
This project requires users to bring their own key (**BYOK**) for AI services, which also means creating these services outside of the Microsoft Fabric platform. 

- [Download Git](https://git-scm.com/downloads) and clone the [rag-pipeline repository](https://github.com/Azure-Samples/fabric-sqldb-ai-ragpipeline).

- Azure Subscription: [Create a free account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account?icid=ai-services&azure-portal=true).

- Microsoft Fabric Subscription: [Create a free trial account](https://www.microsoft.com/en-us/microsoft-fabric/getting-started).

- Azure OpenAI Access: [Apply for access](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/limited-access) in the desired Azure subscription as needed.

- Azure OpenAI Resource: [Deploy an embedding model](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/deploy-models-openai) (e.g. text-emebdding-3-small).

- [Azure AI multi-service resource](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/how-to/create-multi-service-resource), specifically, we will be using Document Intelligence and Azure Language Services from this resource.

- Azure Portal : [Create a Storage Account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal), [assign Storage Blob Data Contributor role](https://learn.microsoft.com/en-us/azure/storage/blobs/assign-azure-role-data-access?tabs=portal) and [configure anonymous read access for blobs](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-configure?tabs=portal).

- Optionally, [download Azure Storage Explorer](https://azure.microsoft.com/en-us/products/storage/storage-explorer/#Download-4) to manage the storage account from your desktop.

- Optionally, [download Visual Studio Code](https://code.visualstudio.com/download) for free and  install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-csharp) if you plan to edit [User Data Functions](https://blog.fabric.microsoft.com/en-us/blog/10474/) using Visual Studio Code.

- [Download](https://www.python.org/downloads/) and install the latest version of Python.

- Download and install MCP Client of your choice [Claude](https://claude.ai/download) or [GithHub Copilot in Visual Studio](https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-install-and-states?view=vs-2022).

## Dataset

Considering the  [file formats supported by the Document Intelligence Service](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/general-document?view=doc-intel-3.1.0#input-requirements), we will utilize the PDF files from [Resume Dataset](/dataset/resume).


> ⚠️ All resumes in this dataset are AI-generated and contain only fictional information for demonstration purposes.

> 🔄 **Note:** In a previous blog, we recommended using a Kaggle resume dataset. However, due to inconsistent formatting in that dataset, which often leads to errors or difficulties when extracting key entities such as candidate name, location, phone number, and email. We now recommend using the curated dataset provided here. It is optimized for better compatibility with entity extraction service and ensures a smoother experience.



## Steps

1.  [Create a workspace](https://learn.microsoft.com/en-us/fabric/data-warehouse/tutorial-create-workspace) named 
<span style="color:lightblue;font-weight:700;font-size:15px">**IntellegentApp**<span>.

2.	[Create a Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/tutorial-build-lakehouse) named 
<span style="color:lightblue;font-weight:700
font-size:15px">**blob_filestorage**<span>.

3.	[Create SQL Database in Fabric](https://learn.microsoft.com/en-us/fabric/database/sql/create) named  <span style="color:lightblue;font-weight:700
font-size:15px">**datamart**<span>.
> 🧹 **Important:** If you followed the previous blog and already created the `dbo.documents` table, please drop it before proceeding. The schema has been updated in this blog to include candidate-specific fields such as name, location, phone, and email. You can run the following SQL command to drop the table:
```sql
   DROP TABLE IF EXISTS dbo.documents;
```
 This ensures a clean start with the updated structure.


4. Navigate to the workspace _IntelligentApp_, click Import - Notebook - From this computer and then import the notebook _cp_azblob_lakehouse.ipynb_ from the cloned repository’s notebook folder.
   ![Import Notebook](/content/image-2.png)


5. Attach the Lakehouse blob_filestorage to cp_azblob_lakehouse notebook
   - Open the notebook, on the Explorer click **Add sources**.
   - Select _Existing data sources_.
   - Select _blob_filestorage_ from OneLake catalog and then click _Connect_.
   
   ![Attach Lakehouse](/content/lakehouse02.png)

6. Create a User Data Function 
   - Navigate to the _IntelligentApp_ workspace and click **+New item**
   - Search for Function and Select "User data function(s)".
   - Provide the name _file_processor_.
   - Click "New Function".
   - Add Lakehouse and SQL Database as managed connection(s).
     - In the Home menu, click **Manage Connections** and then click "+ Add data connection".
     - From the **OneLake catalog** select _datamart_ (SQL Database) and then click "Connect".
     - Repeat the previous step to add _blob_filestorage_ (Lakehouse) as a managed connection.
   - Click  **Library management**, and add the following dependencies _(Click "+ Add from PyPI to add the dependencies")_.The dependencies are also listed in _/functions/requirements.txt_ file of the cloned repository.Ensure you are using  _fabric-user-data-functions_ version **0.2.28rc0** or higher.
   ![Add Managed Connection & Dependencies](/content/image-3.png)
   - In the function editor, replace existing content with the contents of   **_function\function_app_v2.py_** from the cloned repository.
   - Click "Publsh"_(on the top right)_ to deploy the function. Once the functions are deployed, click "Refresh".

7. Create a Data Pipeline by navigating to the workspace and then clicking on "+ New  Item"
   - Search and select "Data Pipeline".
   - Provide the name _blob_ingest_pipeline_.

8. Create a Data Pipeline storage trigger by clicking "Add trigger" button and provide the following configuration : 

   - Source: Select _Azure Blob Storage events_.
   - Storage account: Connect to existing Azure Blob Storage account.
   - Subscription: Select your Azure subscription.
   - Azure Blob Storage account: Select the blob storage account under your subscription.
   - Eventstream name: _blob_ingest_stream_.

     ![Create Trigger](/content/image-5.png)

   Click "Next", to configure the event type and source

   - Event Type(s): Select only the **Microsoft.Storage.BlobCreated** event. This will ensure that an event is generated each time a new blob object is uploaded.

   Click "Next" to review the configuration. Then, click "Connect" to connect to the blob storage. A successful connection will be indicated by the status "Successful". Finally, click "Save".

   On the Set alert screen, under Save location, configure the following settings,
  
   - Select, **Create a new item**.
   - New item name: _blob_activator_ 

   Click "Create" to create and save the alert. 
    
   ![Save alert](/content/image-6.png)

    Now that we have setup the stream, it's time to define the _blob_ingest_pipeline_.
    
   ## Pipeline Definition
   Pipeline can be defined in two distinct ways as outlined below,
   ### Import Template
   Templates offer a quick way to begin building data pipelines. Importing a template brings in all required activities for orchestrating a pipeline.

   To import a template,
   - Navigate to the **Home menu** of the data pipeline.
   - Click, **Use a template**
   - From the **Pipeline templates** page click **Import template**.
   - Import the template [AI-Develop RAG pipeline using SQL database in Fabric_v2.zip](/template/AI-Develop%20RAG%20pipeline%20using%20SQL%20database%20in%20Fabric_v2.zip) from the cloned repository.
    ![Save alert](/content/template02.png)

   The imported data pipeline is preloaded with all necessary activities, variables, and connectors required for end-to-end orchestration. Consequently, there is **no need to manually add a variable or an activity**. Instead, you can proceed directly to configuring values for the variables and each activity parameter in the pipeline, as detailed in the  [Blank Canvas](#blank-canvas) section.
   
   ### Blank Canvas
   1. Establish pipeline variables. Click on the pipeline canvas, select the **Variables** menu, and then click "+ New" to add and configure values for the following variables:

      ![Configure Pipeline Parameters](/content/image-4.png)

      | Name                    | Type    | Value                                                      | Comments                                                   |
      |-------------------------|---------|------------------------------------------------------------|------------------------------------------------------------|
      | _fileName_              | String  | _@pipeline()?.TriggerEvent?.FileName_                      |                                                            |
      |   _container_             | String  | _@pipeline()?.TriggerEvent?.FolderPath_                    |                                                            |
      | _source_                | String  | _@pipeline()?.TriggerEvent?.Source_                        |                                                            |
      | _cognitiveServiceEndpoint_ | String  | _https://YOUR-MULTI-SERVICE-ACCOUNT-NAME.cognitiveservices.azure.com/_ | _Replace YOUR-MULTI-SERVICE-ACCOUNT-NAME with the name of your multi-service account_ |
      | _apiKey_                | String  | _YOUR-MULTI-SERVICE-ACCOUNT-APIKEY_                        | _Replace YOUR-MULTI-SERVICE-ACCOUNT-APIKEY with the apikey of your multi-service account_ |
      | _openAIEndpoint_        | String  | _https://YOUR-OPENAI-ACCOUNT-NAME.openai.azure.com/_       | _Replace YOUR-OPENAI-ACCOUNT-NAME with the name of your Azure OpenAI Account_ |
      | _openAIKey_             | String  | _YOUR-OPENAI-APIKEY_                                       | _Replace YOUR-OPENAI-APIKEY with the apikey of your Azure OpenAI Account_ |
      | _embeddingModel_        | String  | _text-embedding-3-small_                                   |                                                            |
      | _recepientEmailAddress_ | String  | _to-email-address_                                         |receipeint email address                                                            |
      | _senderEmailAddress_    | String  | _from-email-address_                                       | sender's email address                                                            |

      ![Configure Pipeline Parameters](/content/cognitiveservice.png)
   2. Add a **Notebook activity**. The notebook associated with this activity utilizes [NotebookUtils](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-utilities) to manage file system. During the execution of the notebook, a folder corresponding to the container name will be created if it does not exist. Subsequently, the file will be copied from Azure Blob Storage to the Lakehouse folder. Configure this activity as outlined below:

      - General Tab,
        - Name: _azureblob_to_lakehouse_
      - Settings Tab,
        - Notebook: _cp_azblob_lakehouse_

        **Base parameters**

          Click "+New" to add the following _parameters_,
        - Name: _fileName_ 
          - Type: _String_
          - Value: _@variables('fileName')_
        - Name: _container_ 
          - Type: _String_
          - Value: _@variables('container')_
        - Name: _source_ 
          - Type: _String_
          - Value: _@variables('source')_

       Use **On Success** connector of the activity to link to the subsequent function _(Extract Text)_ activity.

    3. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _extract_text_ associated with this activity uses [Azure AI Document Intelligence service](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence) to extract the "text" content from the file copied into the Lakehouse by the previous activity.Configure this activity as outlined below : 

        - General Tab,
            - Name: _Extract Text_
        - Settings Tab,
            - Type: _Fabric user data functions_
            - Connection: : Sign-in (if not already) using your workspace credentials.
            - Workspace: _IntelligentApp_ (default selecteed)
            - User data functions: _file_processor_
            - Function: _extract_text_

            **Parameters:**
            - Name: _filePath_ 
                - Type: _str_
                - Value: _@activity('azureblob_to_lakehouse').output.result.exitValue_
            - Name: _cognitiveServicesEndpoint_ 
                - Type: _str_
                - Value: _@variables('cognitiveServiceEndpoint')_
            - Name: _apiKey_ 
                - Type: _str_
                - Value: _@variables('apiKey')_

        Use **On Completion** connector of the activity to link to the subsequent If Condition _(Text Extraction Results)_ activity.

    4. Add an **If Conditions activity** to verify the success of the text extraction in the previous step.If the extraction was unsuccessful, an email would be sent to the configured recepient and the pipeline would be terminated.Configure this activity as outlined below:

        - General Tab,
          - Name: _Text Extraction Results_
        - Activities Tab,
          - Expression: _@empty(activity('Extract Text').error)_
          - Case: **False**. Edit the _false_ condition using the **edit (pencil) icon**, and add the following activities,

            **Office 365 Outlook activity**: To send alert emails.
            - General Tab,
              - Name: _Text Extraction Failure Email Alert_
            - Settings Tab,
              - Signed in as: Sign-in (if not already) using your workspace credentials.
              - To:_@variables('recepientEmailAddress')_
              - Subject:_Text Extraction Error_
              - Body:_&lt;pre&gt;@{replace(string(activity('Extract Text').error.message), '\\','')}&lt;/pre&gt;_

              **Advanced**,
              - From: _@variables('senderEmailAddress')_
              - Importance: _High_

              Use On **Success connector** of the activity to link to the subsequent Fail     activity.

            **Fail activity**: To terminate the pipeline
            - General Tab,
              - Name: _Text Extraction Process Failure_
            - Settings Tab,
              - Fail message: _@{replace(string(activity('Extract Text').error), '\\','')}_
              - Error code: _@{activity('Extract Text').statuscode}_

        Return to the main canvas by clicking the pipeline name _blob_ingest_pipeline_ and use the **On Success** connector of the **If Condition activity** to link to the subsequent Function _(Extract Entities)_ activity.

    5. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _extract_entities_ associated with this activity uses [Azure AI Language service](https://learn.microsoft.com/en-us/azure/ai-services/language-service/overview) to extract entities such as name, email, phone, location etc for the text extracted by the previous activity.Configure this activity as outlined below : 

        - General Tab,
            - Name: _Extract Entities_
        - Settings Tab,
            - Type: _Fabric user data functions_
            - Connection: : Sign-in (if not already) using your workspace credentials.
            - Workspace: _IntelligentApp_ (default selecteed)
            - User data functions: _file_processor_
            - Function: _extract_entities_

            **Parameters:**
            - Name: _text_ 
                - Type: _str_
                - Value: _@activity('Extract Text').output.output_

            - Name: _cognitiveServicesEndpoint_ 
                - Type: _str_
                - Value: _@variables('cognitiveServiceEndpoint')_
            - Name: _apiKey_ 
                - Type: _str_
                - Value: _@variables('apiKey')_

        Use **On Success** connector of the activity to link to the subsequent Function _(Generate Chunks)_ activity.

    6. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _chunk_text_ associated with this activity uses [tiktoken tokenizer](https://github.com/openai/tiktoken) to "generate chunks" for the text extracted by the previous activity.Configure this activity as outlined below : 

        - General Tab,
            - Name: _Generate Chunks_
        - Settings Tab,
            - Type: _Fabric user data functions_
            - Connection: : Sign-in (if not already) using your workspace credentials.
            - Workspace: _IntelligentApp_ (default selecteed)
            - User data functions: _file_processor_
            - Function: _chunk_text_

            **Parameters:**
            - Name: text_ 
                - Type: _str_
                - Value: _@activity('Extract Text').output.output_
            - Name: _maxToken_ 
                - Type: _int_
                - Value: _500_
            - Name: _encoding_ 
                - Type: _str_
                - Value: _cl100k_base_

        Use **On Success** connector of the activity to link to the subsequent Function _(Generate Embeddings)_ activity.

    8. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _generate_embeddings_ associated with this activity uses [Azure Open AI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service?msockid=2c16c7c6d6bd62c139b9d347d7c86394) embedding model to convert the  chunks into embeddings. Configure this activity as outlined below : 
        - General Tab,
            - Name: _Generate Embeddings_
        - Settings Tab,
            - Type: _Fabric user data functions_
            - Connection: : Sign-in (if not already) using your workspace credentials.
            - Workspace: _IntelligentApp_ (default selecteed)
            - User data functions: _file_processor_
            - Function: _generate_embeddings_

            **Parameters:**
            - Name: _text_ 
                - Type: _list_
                - Value: _@activity('Generate Chunks').output.output_
            - Name: _openAIServiceEndpoint_ 
                - Type: _str_
                - Value: _@variables('openAIEndpoint')_
            - Name: _embeddingModel_ 
                - Type: _str_
                - Value: _@variables('embeddingModel')_
            - Name: _openAIKey_ 
                - Type: _str_
                - Value: _@variables('openAIKey')_
            - Name: _fileName_ 
                - Type: _str_
                - Value: _@variables('fileName')_
        
        Use **On Completion** connector of the activity to link to the subsequent If Condition _(Generate Embeddings Results)_ activity.

    9. Add an **If Conditions activity** activity to verify the success of the Generate Embeddings in the previous step. If the embeddings generation were unsuccessful, an email would be sent to the configured recipient, and the pipeline would be terminated.Configure this activity as outlined below:

        - General Tab,
          - Name: _Generate Embeddings Results_
        - Activities Tab,
          - Expression: _@empty(activity('Generate Embeddings').error)_
          - Case: **False**. Edit the _false_ condition using the ✏️ **edit (pencil) icon**, and add the following activities,

            **Office 365 Outlook activity**: To send alert emails.
             - General Tab,
               - Name: _Generate Embeddings Failure Email Alert_
             - Settings Tab,
               - Signed in as: Sign-in (if not already) using your workspace credentials.
               - To:_@variables('recepientEmailAddress')_
               - Subject:_Generate Embeddings Error_
               - Body:_&lt;pre&gt;@{replace(string(activity('Generate Embeddings').error.message), '\\','')}&lt;/pre&gt;_

               **Advanced**,
               - From: _@variables('senderEmailAddress')_
               - Importance: _High_

               Use On **Success connector** of the activity to link to the subsequent Fail     activity.

             **Fail activity**: To terminate the pipeline
              - General Tab,
                - Name: _Text Extraction Process Failure_
              - Settings Tab,
                - Fail message: _@{replace(string(activity('Generate Embeddings').error), '\\','')}_
                - Error code: _@{activity('Generate Embeddings').statuscode}_

        Return to the main canvas by clicking the pipeline name _blob_ingest_pipeline_ and use the **On Success** connector of the **If Condition activity** to link to the subsequent Function _(Create Database Objects)_ activity.

    10. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _create_table_ associated with this activity executes a SQL command to create a documents table within the previously created _datamart_, SQL Database.Configure this activity as outlined below : 
        - General Tab,
            - Name: _Create Database Objects_
        - Settings Tab,
            - Type: _Fabric user data functions_
            - Connection: : Sign-in (if not already) using your workspace credentials.
            - Workspace: _IntelligentApp_ (default selecteed)
            - User data functions: _file_processor_
            - Function: _create_table_
        
        Use **On Success** connector of the activity to link to the subsequent If Condition _(Generate Embeddings Results)_ activity.

    11. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function “insert_data” associated with this activity executes a SQL command to bulk insert rows in the documents table created in the previous activity.Configure this activity as outlined below : 
        - General Tab,
            - Name: _Save Data_
        - Settings Tab,
            - Type: _Fabric user data functions_
            - Connection: : Sign-in (if not already) using your workspace credentials.
            - Workspace: _IntelligentApp_ (default selecteed)
            - User data functions: _file_processor_
            - Function: _insert_data_

            **Parameters:**
            - Name: _data_ 
                - Type: _list_
                - Value: _@activity('Generate Embeddings').output.output_
            - Name: _documentLocation_ 
                - Type: _str_
                - Value: _@concat(
                        concat(
                            concat(
                                concat(
                                    concat('https://' ,
                                    last(split(variables('source'),'/'))
                                ), 
                                '.blob.core.windows.net/'),
                            variables('container')),
                        '/'), 
                        variables('fileName'))_
            - Name: _candidateName_ 
                - Type: _str_
                - Value: _@activity('Extract Entities').output.output.Name_
            - Name: _phoneNumber_ 
                - Type: _str_
                - Value: _@activity('Extract Entities').output.output.PhoneNumber_
            - Name: _email_ 
                - Type: _str_
                - Value: _@activity('Extract Entities').output.output.Email_
            - Name: _candidateLocation_ 
                - Type: _str_
                - Value: _@activity('Extract Entities').output.output.Location_
## Execute Pipeline (Pipeline in Action)
  Let's put everything we have done so far into perspective and see the pipeline in action.

- Upload a PDF file,
  - Use the Azure Storage Explorer or alternatively Azure Portal and create a Blob container named _resume_.
  - Upload a PDF file from [Resume Dataset](/dataset/resume).

  ![Create a Container and Upload a PDF File](/content/explorer.png)

- Pipeline execution review,
  - From the pipeline’s “Run” menu, select **View run history** and select the recent pipeline run.
  - In the details view, check to see if the status is **Succeeded** 
  - In case of a Failure, try to **Rerun** the pipeline using the rerun option.

- Review Lakehouse,
  - A folder with the same name as that of the container _(resume)_ is created.
  - The PDF file is copied from Azure Blob Storage to the Lakehouse files.
  
  ![Lakehouse Review](/content/lakehouse.png)

- Review Database
  - The document table should be automatically created by the pipeline.
  - Chunk data, embeddings, and other entity (candidate in this case) information (such as name, phone, email, and location) are stored in the documents table.

  ![Database Review](/content/data_v2.png)

## GraphQL API 

So far, we've explored how a data pipeline ingests documents—like resumes from our sample dataset, extracts their content, and then stores the results in a SQL Database within Microsoft Fabric. This stored data includes chunked data, vector embeddings, and associated entity metadata.

In this section, we'll shift our focus to making that enriched data accessible by exposing it through a GraphQL API. By the end of this section, you'll have a fully functional GraphQL endpoint that lets you query documents using natural language, enabling flexible and efficient access to your AI-ready data.

Navigate to the SQL Databaes _datamart_ database in Fabric portal

### Setting up Database Objects
Execute the following [SQL Scripts](/graphql/stored%20procedures/) from the cloned repository in the order as listed below: 

1. [Create Scoped Credentials](/graphql/stored%20procedures/01-create_scoped_credentials.sql) sets up database credentials to access Azure OpenAI API key.In the script, replace the following values before executing,
    - _<<YOUR_STRONG_PASSWORD>>_ with a strong password of your choice (for example, _N'V3RYStr0NGP@ssw0rd!'_).

    - _<<AZURE_OPEN_AI_ENDPOINT>>_ with your Azure Open AI service endpoint (for example, _https://resume.openai.azure.com/_).

    - _<<AZURE_OPEN_AI_API_KEY>>_ with  your Azure Open AI key.

2. [Create Embeddings](/graphql/stored%20procedures/02-create_embedding.sql) is a stored procedure that leverages the configured embedding model to convert natural language to its embedding equivalent. In the script, replace the following values before executing,
    - _<<AZURE_OPEN_AI_ENDPOINT>>_ with your Azure Open AI service endpoint (for example, _https://resume.openai.azure.com/_).

        > Ensure **@Credential** parameter matches the credentials used in the _Create Scoped Credential_ stored procedure.

    - _<<EMBEDDING_MODEL>>_ with the name of your embedding model (for example, _**text-embedding-3-small**_).

    - _<<API_VERSION>>_ with the API Version of the embedding model (for example, _**2023-05-15**_).

    You can find all of this information by logging into **Azure AI Foundry** and navigating to your model deployment.

3. [Similarity Search](/graphql/stored%20procedures/03-similarity_search.sql) stored procedure performs a vector search using the stored embeddings to find relevant documents. It also supports predicate-based filtering, such as search by location. This is the primary stored procedure that will be used by the GraphQL endpoint.

    To ensure your stored procedures are set up correctly, run the command below. Don't worry about the actual results; we just need to confirm that it executes without any errors.
    ```sql

    EXECUTE dbo.similarity_search 'candidates with networking experience'
    ```
    > 🔄 **Note:** Within this Similarity Search stored procedure, there is an internal call to the _Create Embeddings_ stored procedure. This internal call **MUST** explicitly use ```**OUTPUT WITH RESULT SETS NONE**```. This is crucial because it suppresses any result sets that the Create Embeddings procedure might otherwise produce. By doing so, it guarantees that only the Similarity Search stored procedure returns a result set. This singular result set is what the GraphQL API uses to infer and generate its schema definition. If the Create Embeddings procedure were to return a result set, the GraphQL API schema generation process would fail due to unexpected multiple result sets.
    
    ![Search](/content/search_sp.png)

T

### Setting up GraphQL API

Once the _SQL scripts_ are successfully executed, its time to stand up your GraphQL API. 
Setting up a GraphQL API in Microsoft Fabric is very straightforward. 
Simply follow the [Steps to Create GraphQL API in SQL Database](https://learn.microsoft.com/en-us/fabric/database/sql/graphql-api). 

When prompted to enter a name, use _smart_search_. On the **Get Data** screen select all objects, (ensure that the _similarity search_ stored procedure is checked), and then click on the **Load** button.
![Get Data](/content/graphql-getdata.png)

Your GraphQL API should be all ready to go! 
Simply copy and save the **GraphQL endpoint link**;we will be using it in the upcoming section to setup a MCP Server.

![GraphQL](/content/graphql.png)

In order to test the endpoint use the 
[Sample GraphQL Query Script](/graphql/query.graphql). To execute the script, click on the _Query_ tab, paste your script in the new query window, and click the **Run** button as shown below : 


![GraphQL in Action](/content/execute_graphql.png)

## Integrating GraphQL with an MCP Server
If you've followed along thus far, we've successfully created an ingestion pipeline to process documents (like resumes from our dataset) and built a powerful GraphQL API to retrieve that data. While this provides efficient data access, a simple search often isn't enough for truly intelligent applications. To move beyond basic retrieval and enable dynamic, multi-turn interactions, we need to introduce agentic conversation. This section focuses on setting up an MCP (Model Context Protocol) Server, which will expose our GraphQL endpoint as a specialized tool, transforming static searches into fluid, conversational experiences. 

Simply follow the steps given below to stand up a MCP Server:

1. Navigate to the _mcp_graphql_ folder.
2. Rename the file `settings.env` to `.env`.
3. Replace _<<your_fabric_graphql_endpoint>>_ with the **GraphQL endpoint link** obtained in the previous section.
4. Configure Your MCP Client:

    For Claude, 
    - Navigate to File -> Settings -> Developer -> Edit Config
    - Use the template [claude_desktop_config.json](/mcp-graphql/claude_desktop_config.json) as reference.
    - Replace _<<path_to_mcp_graphql_server.py>>_ with the absolute path to your mcp_graphql.py file (for example, _"C:\\\fabric-sqldb-ai-ragpipeline\\\mcp-graphql\\\mcp_graphql.py"_).

    For more information on configuring Claude desktop, refer to the [documentation](https://modelcontextprotocol.info/docs/quickstart/user/).

    For VS Code GitHub,

    - Follow the [steps](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) to configure MCP Server.
    - Use the template [settings.json](/mcp-graphql/settings.json) as reference.
    - Replace _<<path_to_mcp_graphql_server.py>>_ with the absolute path to your mcp_graphql.py file (for example, _"C:\\\fabric-sqldb-ai-ragpipeline\\\mcp-graphql\\\mcp_graphql.py"_).

5. Restart MCP Clients.
6. A new window will prompt you for **Entra Authentication**; please watch for it. Once logged in, you will be able to see the tools listed in the MCP Server.

    > Note make sure your database has sufficient read and write access to the EntraId
7. Select **Claude Sonnet 4** as your model (recommended for its strong reasoning capabilities). 
8. For VS Code, select **Agent** mode. Then, click on the tool icon and select the _get_resumes_ tool.

    ![VS Code](/content/GHC.png)

9. For Claude, tool will be automatically selected.

### Agent in Action

You are all set, start interacting with your MCP Client (Agent Host) using (but not limited to) the following example prompts

_"Looking for chef's resume. The chef must have foundational cooking skills but be exceptional in kitchen hygiene and organizational skills.
Share the candidates profile (link) with a short description, why they are a good fit !"_

![Agent in Action](/content/chef.gif)


_"Looking for a fullstack developer from Alabama"_

![Agent in Action](/content/fullstack.gif)

## Troubleshooting

- When adding a Python library from PyPI to User Data Functions, you might notice an error, such as a wiggly line under the library name (e.g., _azure-ai-textanalytics_), like a spelling mistake. Users should ensure the library name is spelled correctly and then ignore the error by tabbing out to the Version dropdown and selecting the correct version. This transient error should resolve itself.

- The imported pipeline reportedly doesn't seem to preload with the parameter values. For each activity in the pipeline, ensure that the parameter values are provided and correct. Refer to the [**Blank Canvas**](#blank-canvas)  section for the required parameters and their values. 

- While testing the GraphQL API , if you see an error like "Only those stored procedures whose metadata for the first result set described by sys.dm_exec_describe_first_result_set are supported.", it may be due to missing or incorrect configuration in your stored procedures for instance the credentials in Create_Embeddings. Double-check that all required values like endpoint, API key, and model name are correctly filled in and ensure the _dbo.similarity_searh_ stored procedure includes the statement **OUTPUT WITH RESULT SETS NONE**.
