CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    source TEXT,
    department TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER,
    page_number INTEGER,
    department TEXT,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx 
ON chunks USING ivfflat (embedding vector_cosine_ops);
-- RBAC: users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP DEFAULT NOW()
);

-- RBAC: role permissions table
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role TEXT NOT NULL,
    department TEXT NOT NULL,
    UNIQUE(role, department)
);

-- Seed default roles and permissions
INSERT INTO role_permissions (role, department) VALUES
    ('admin',         'hr'),
    ('admin',         'finance'),
    ('admin',         'legal'),
    ('admin',         'general'),
    ('hr_staff',      'hr'),
    ('hr_staff',      'general'),
    ('finance_staff', 'finance'),
    ('finance_staff', 'general'),
    ('legal_staff',   'legal'),
    ('legal_staff',   'general'),
    ('employee',      'general')
ON CONFLICT DO NOTHING;

-- Seed test users
INSERT INTO users (user_id, role) VALUES
    ('admin_user',    'admin'),
    ('hr_user',       'hr_staff'),
    ('finance_user',  'finance_staff'),
    ('legal_user',    'legal_staff'),
    ('test_user',     'employee')
ON CONFLICT DO NOTHING;
