-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store your documents
create table
  diagrams_documents (
    id uuid primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1024) -- 1536 works for OpenAI embeddings, change if needed
  );

-- Create a function to search for documents
create function match_diagrams_documents (
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
    1 - (diagrams_documents.embedding <=> query_embedding) as similarity
  from diagrams_documents
  where metadata @> filter
  order by diagrams_documents.embedding <=> query_embedding;
end;
$$;

-- Create a table to store your documents
create table
  aws_documents (
    id uuid primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1024) -- 1536 works for OpenAI embeddings, change if needed
  );

-- Create a function to search for documents
create function match_aws_documents (
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
    1 - (aws_documents.embedding <=> query_embedding) as similarity
  from aws_documents
  where metadata @> filter
  order by aws_documents.embedding <=> query_embedding;
end;
$$;
