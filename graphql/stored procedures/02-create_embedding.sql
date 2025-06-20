create or alter procedure dbo.create_embeddings
(
    @input_text nvarchar(max),
    @embedding vector(1536) output
)
AS
BEGIN
declare @url varchar(max) = '<<AZURE_OPEN_AI_ENDPOINT>>/openai/deployments/<<EMBEDDING_MODEL>>/embeddings?api-version=<<API_VERSION>>';
declare @payload nvarchar(max) = json_object('input': @input_text);
declare @response nvarchar(max);
declare @retval int;

-- Call to Azure OpenAI to get the embedding of the search text
begin try
    exec @retval = sp_invoke_external_rest_endpoint
        @url = @url,
        @method = 'POST',
        @credential = [<<AZURE_OPEN_AI_ENDPOINT>>],
        @payload = @payload,
        @response = @response output;
end try
begin catch
    select 
        'SQL' as error_source, 
        error_number() as error_code,
        error_message() as error_message
    return;
end catch
if (@retval != 0) begin
    select 
        'OPENAI' as error_source, 
        json_value(@response, '$.result.error.code') as error_code,
        json_value(@response, '$.result.error.message') as error_message,
        @response as error_response
    return;
end
-- Parse the embedding returned by Azure OpenAI
declare @json_embedding nvarchar(max) = json_query(@response, '$.result.data[0].embedding');

-- Convert the JSON array to a vector and set return parameter
set @embedding = CAST(@json_embedding AS VECTOR(1536));
END;