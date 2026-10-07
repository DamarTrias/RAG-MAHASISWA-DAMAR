-- Jalankan di Supabase > SQL Editor
create extension if not exists vector;

drop table if exists students cascade;
;
create table if not exists students (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  nim text unique
);

create table documents (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references students on delete cascade,
  name text not null,
  file_type text,
  created_at timestamptz default now()
);

create table chunks (
  id bigserial primary key,
  document_id uuid not null references documents on delete cascade,
  student_id uuid not null references students on delete cascade,
  content text not null,
  citation text not null,
  embedding vector(3072)
);

-- Pencarian vektor SELALU dibatasi p_student_id (isolasi data)
create function match_chunks(
  query_embedding vector(3072),
  p_student_id uuid,
  p_document_id uuid default null,
  match_count int default 5
)
returns table (content text, citation text, similarity float)
language sql stable as $$
  select content, citation, 1 - (embedding <=> query_embedding)
  from chunks
  where student_id = p_student_id
    and (p_document_id is null or document_id = p_document_id)
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- Kunci tabel dari akses publik (app memakai service key di server)
alter table students  enable row level security;
alter table documents enable row level security;
alter table chunks    enable row level security;

-- Data contoh
insert into students (name, nim) values
  ('Damar Trias (Mahasiswa 1)', '21001'),
  ('Fara Ayu (Mahasiswa 2)', '21002');
