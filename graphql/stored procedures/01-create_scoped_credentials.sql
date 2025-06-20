
-- Create a master key for the database
if not exists(select * from sys.symmetric_keys where [name] = '##MS_DatabaseMasterKey##')
begin
    create master key encryption by password = '<<YOUR_STRONG_PASSWORD>>' -- Set a strong password here
end
go

-- Create the database scoped credential for Azure OpenAI
if not exists(select * from sys.database_scoped_credentials where [name] = '<<AZURE_OPEN_AI_ENDPOINT>>')
begin
    create database scoped credential [<<AZURE_OPEN_AI_ENDPOINT>>]
    with identity = 'HTTPEndpointHeaders', secret = '{"api-key":"<<AZURE_OPEN_AI_API_KEY>>"}';
end
go