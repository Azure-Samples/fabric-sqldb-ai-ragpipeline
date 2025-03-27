# RAG Pipeline using SQL Database in Fabric

This project provides step-by-step guidance for building a **Retrieval Augmented Generation (RAG) pipeline** to make your data AI-ready using Microsoft . The RAG pipeline is triggered every time a file is uploaded to Azure Blob Storage. The pipeline processes the file by extracting the textual content, chunking the text, redacting any PII data, generating embeddings, and finally storing the embeddings in a SQL Database in Fabric as a vector store. The stored content can later be utilized to build AI applications such as recommendation engines, chatbots, smart search, etc

![Data Pipeline Activity Workflow](/content/RAG.png)

## Prerequisite
This project requires users to bring their own key (**BYOK**) for AI services, which also means creating these services outside of the Microsoft Fabric platform. 

- [Download Git](https://git-scm.com/downloads) and clone the [rag-pipeline repository](https://github.com/Azure-Samples/fabric-sqldb-ai-ragpipeline).

- Azure Subscription: [Create a free account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account?icid=ai-services&azure-portal=true).

- Microsoft Fabric Subscription: [Create a free trial account](https://www.microsoft.com/en-us/microsoft-fabric/getting-started).

- Azure OpenAI Access: [Apply for access](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/limited-access) in the desired Azure subscription as needed.

- Azure OpenAI Resource: [Deploy an embedding model](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/deploy-models-openai) (e.g. text-emebdding-3-small).

- [Azure AI multi-service resource](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/how-to/create-multi-service-resource), specifically, we will be using Document Intelligence and Azure Language Services from this resource.

- Azure Portal : [Create a Storage Account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) and [assign Storage Blob Data Contributor role](https://learn.microsoft.com/en-us/azure/storage/blobs/assign-azure-role-data-access?tabs=portal).

- Optionally, [download Azure Storage Explorer](https://azure.microsoft.com/en-us/products/storage/storage-explorer/#Download-4) to manage the storage account from your desktop.

- Optionally, [download Visual Studio Code](https://code.visualstudio.com/download) for free and  install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-csharp) if you plan to edit [User Data Functions](https://blog.fabric.microsoft.com/en-us/blog/10474/) using Visual Studio Code.

## Dataset

Considering the  [file formats supported by the Document Intelligence Service](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/general-document?view=doc-intel-3.1.0#input-requirements), we will utilize the PDF files from [Resume Dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset) from Kaggle.


## Steps

1.  [Create a workspace](https://learn.microsoft.com/en-us/fabric/data-warehouse/tutorial-create-workspace) named 
<span style="color:lightblue;font-weight:700;font-size:15px">**IntellegentApp**<span>.

2.	[Create a Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/tutorial-build-lakehouse) named 
<span style="color:lightblue;font-weight:700
font-size:15px">**blob_filestorage**<span>.

3.	[Create SQL Database in Fabric](https://learn.microsoft.com/en-us/fabric/database/sql/create) named  <span style="color:lightblue;font-weight:700
font-size:15px">**datamart**<span>.

4. Navigate to the workspace _IntelligentApp_, click Import - Notebook - From this computer and then import the notebook _cp_azblob_lakehouse.ipynb_ from the cloned repository’s notebook folder.
   ![Import Notebook](/content/image-2.png)


5. Attach the Lakehouse blob_filestorage to cp_azblob_lakehouse notebook
   - Open the notebook, on the Explorer click **Add sources**.
   - Select _Existing data sources_.
   - Select _blob_filestorage_ from OneLake catalog and then click _Connect_.
   
   ![Attach Lakehouse](/content/Lakehouse02.png)

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
   - In the function editor, replace existing content with the contents of   _function\function_app.py_ from the cloned repository.
   - Click "Publsh"_(on the top right)_ to deploy the function. Once the functions are deployed, click "Refresh".

7. Create a Data Pipeline by navigating to the workspace and then clicking on "+ New  Item"
   - Search and select "Data Pipeline".
   - Provide the name _blob_ingest_pipeline_.

8. Create a Data Pipeline storage trigger by clicking "Add trigger (preview)" button and provide the following configuration : 

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
   - Import the file _template/ AI-Develop RAG pipeline using SQL database in Fabric.zip_ from the cloned repository.
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

        Return to the main canvas by clicking the pipeline name _blob_ingest_pipeline_ and use the **On Success** connector of the **If Condition activity** to link to the subsequent Function _(Generate Chunks)_ activity.


    5. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _chunk_text_ associated with this activity uses [tiktoken tokenizer](https://github.com/openai/tiktoken) to "generate chunks" for the text extracted by the previous activity.Configure this activity as outlined below : 

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

        Use **On Success** connector of the activity to link to the subsequent Function _(Redact PII Data)_ activity.

    6. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _redact_text_ associated with this activity uses [Azure AI Language service](https://learn.microsoft.com/en-us/azure/ai-services/language-service/overview) to "Redact PII Data" for the chunks generated by the preceding activity. The chunking of text is done prior to redaction to comply with the [service limits requirements](https://learn.microsoft.com/en-us/azure/ai-services/language-service/concepts/data-limits) for the PII detection feature.Configure this activity as outlined below : 

        - General Tab,
            - Name: _Redact PII Data_
        - Settings Tab,
            - Type: _Fabric user data functions_
            - Connection: : Sign-in (if not already) using your workspace credentials.
            - Workspace: _IntelligentApp_ (default selecteed)
            - User data functions: _file_processor_
            - Function: _redact_text_

            **Parameters:**
            - Name: _text_ 
                - Type: _list_
                - Value: _@activity('Generate Chunks').output.output_
            - Name: _cognitiveServicesEndpoint_ 
                - Type: _str_
                - Value: _@variables('cognitiveServiceEndpoint')_
            - Name: _apiKey_ 
                - Type: _str_
                - Value: _@variables('apiKey')_

        ![Redact PII Data](/content/image-7.png)
        
        Use **On Completion** connector of the activity to link to the subsequent If Condition _(PII Redaction Results)_ activity.
       
      7. Add an **If Conditions activity** to verify the success of the PII redaction in the previous step. If the redaction was unsuccessful, an email would be sent to the configured recipient, and the pipeline would be terminated.Configure this activity as outlined below:

         - General Tab,
           - Name: _PII Reaction Results_
         - Activities Tab,
           - Expression: _@empty(activity('Redact PII Data').error)_
           - Case: **False**. Edit the _false_ condition using the **edit (pencil) icon**, and add the following activities,

             **Office 365 Outlook activity**: To send alert emails.
             - General Tab,
               - Name: _Redaction Failure Email Alert_
             - Settings Tab,
               - Signed in as: Sign-in (if not already) using your workspace credentials.
               - To:_@variables('recepientEmailAddress')_
               - Subject:_Text Extraction Error_
               - Body:_&lt;pre&gt;@{replace(string(activity('Redact PII Data').error.message), '\\','')}&lt;/pre&gt;_

               **Advanced**,
               - From: _@variables('senderEmailAddress')_
               - Importance: _High_

               Use On **Success connector** of the activity to link to the subsequent Fail     activity.

             **Fail activity**: To terminate the pipeline
              - General Tab,
                - Name: _Text Extraction Process Failure_
              - Settings Tab,
                - Fail message: _@{replace(string(activity('Redact PII Data').error), '\\','')}_
                - Error code: _@{activity('Redact PII Data').statuscode}_

         Return to the main canvas by clicking the pipeline name _blob_ingest_pipeline_ and use the **On Success** connector of the **If Condition activity** to link to the subsequent Function _(Generate Embeddings)_ activity.

    8. Add a [**Functions activity**](https://learn.microsoft.com/en-us/fabric/data-factory/functions-activity). The function _generate_embeddings_ associated with this activity uses [Azure Open AI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service?msockid=2c16c7c6d6bd62c139b9d347d7c86394) embedding model to convert the redacted chunks into embeddings.Configure this activity as outlined below : 
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
                - Value: _@activity('Redact PII Data').output.output_
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
          - Case: **False**. Edit the _false_ condition using the **edit (pencil) icon**, and add the following activities,

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
## Troubleshooting

- When adding a Python library from PyPI to User Data Functions, you might notice an error, such as a wiggly line under the library name (e.g., _azure-ai-textanalytics_), like a spelling mistake. Users should ensure the library name is spelled correctly and then ignore the error by tabbing out to the Version dropdown and selecting the correct version. This transient error should resolve itself.

- The imported pipeline reportedly doesn't seem to preload with the parameter values. For each activity in the pipeline, ensure that the parameter values are provided and correct. Refer to the [**Blank Canvas**](#blank-canvas)  section for the required parameters and their values. 

## Execute Pipeline (Pipeline in Action)
  Let's put everything we have done so far into perspective and see the pipeline in action.

- Upload a PDF file,
  - Use the Azure Storage Explorer or alternatively Azure Portal and create a Blob container named _resume_.
  - Upload a PDF file from the Kaggle dataset.

  ![Create a Container and Upload a PDF File](/content/explorer.png)

- Pipeline execution review,
  - From the pipeline’s “Run” menu, select **View run history** and select the recent pipeline run.
  - In the details view, check to see if the status is **Succeeded** 
  - In case of a Failure, try to **Rerun** the pipeline using the rerun option.

  ![Pipeline Review](/content/pipelinerun.png)

- Review Lakehouse,
  - A folder with the same name as that of the container _(resume)_ is created.
  - The PDF file is copied from Azure Blob Storage to the Lakehouse files.
  
  ![Lakehouse Review](/content/lakehouse.png)

- Review Database
  - The document table should be automatically created by the pipeline.
  - Redacted chunk data and the embeddings stored in the documents table.

  ![Database Review](/content/data.png)