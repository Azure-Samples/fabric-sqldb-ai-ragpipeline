
-- Create a master key for the database
if not exists(select * from sys.symmetric_keys where [name] = '##MS_DatabaseMasterKey##')
begin
    create master key encryption by password = '<<YOUR_STRONG_PASSWORD>>' -- Set a strong password here
end
go

-- Create the database scoped credential for Azure OpenAI
if not exists(select * from sys.database_scoped_credentials where [name] = 'https://<<AZURE_OPEN_AI_RESOURCE>>.openai.azure.com/')
begin
    create database scoped credential [https://<<AZURE_OPEN_AI_RESOURCE>>.openai.azure.com/]
    with identity = 'HTTPEndpointHeaders', secret = '{"api-key":"<<AZURE_OPEN_AI_API_KEY>>"}';
end
go