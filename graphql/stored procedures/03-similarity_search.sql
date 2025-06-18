CREATE OR ALTER PROCEDURE dbo.similarity_search(
    @search_query VARCHAR(5000),
    @top INT = 5,
    @metric VARCHAR(50) = 'cosine',
    @candidateLocation VARCHAR(1000) = NULL
)
AS
BEGIN
-- Normalize the candidateLocation input
IF @candidateLocation IS NOT NULL 
    AND (LTRIM(RTRIM(@candidateLocation)) = '' 
    OR LTRIM(RTRIM(LOWER(@candidateLocation))) in( 'any', 'usa', 'united states')) --default location passed by different llms
BEGIN
  SET @candidateLocation = NULL;
END

DECLARE @queryEmbedding VECTOR(1536);

exec dbo.create_embeddings @search_query, @queryEmbedding  OUTPUT WITH RESULT SETS NONE;

SELECT TOP(@top)
       DocumentLocation,
       CandidateName,
       Email,
       PhoneNumber,
       CandidateLocation,
       ChunkText,
       1-VECTOR_DISTANCE(@metric, @queryEmbedding, d.embedding) AS Score

FROM dbo.documents d   
WHERE (@candidateLocation IS NULL OR d.CandidateLocation = @candidateLocation)
ORDER BY Score DESC;
END