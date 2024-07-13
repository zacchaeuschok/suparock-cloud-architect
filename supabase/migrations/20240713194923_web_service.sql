-- Create a table to store your documents
create table
  web_service_documents (
    id uuid primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1024) -- 1536 works for OpenAI embeddings, change if needed
  );

-- Create a function to search for documents
create function match_web_service_documents (
  query_embedding vector (1024),
  filter jsonb default '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
) language plpgsql as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (web_service_documents.embedding <=> query_embedding) as similarity
  from web_service_documents
  where metadata @> filter
  order by web_service_documents.embedding <=> query_embedding;
end;
$$;