CREATE TABLE conversation (
    id INTEGER PRIMARY KEY,
    title TEXT,
    current_prd_version_id INTEGER,
    status TEXT NOT NULL DEFAULT 'active',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_prd_version_id) REFERENCES prd_version(id) ON DELETE SET NULL
);

CREATE TABLE message (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    sender TEXT NOT NULL, -- 'user' or 'ai'
    message_type TEXT NOT NULL, -- 'text', 'system', 'file', etc.
    content TEXT NOT NULL,
    metadata TEXT,
    status TEXT NOT NULL DEFAULT 'delivered',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE
);

CREATE TABLE file_attachment (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    original_filename TEXT NOT NULL,
    file_type TEXT NOT NULL, -- 'txt', 'md', 'docx'
    file_size INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    extracted_text TEXT,
    status TEXT NOT NULL DEFAULT 'uploaded',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE
);

CREATE TABLE clarifying_question (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    prd_version_id INTEGER,
    question_text TEXT NOT NULL,
    category TEXT, -- 'functional', 'non-functional', 'user', etc.
    priority INTEGER DEFAULT 0,
    ai_message_id INTEGER,
    user_message_id INTEGER,
    answer TEXT,
    status TEXT NOT NULL DEFAULT 'unanswered', -- 'unanswered', 'answered', 'dismissed'
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
    FOREIGN KEY (prd_version_id) REFERENCES prd_version(id) ON DELETE SET NULL,
    FOREIGN KEY (ai_message_id) REFERENCES message(id) ON DELETE SET NULL,
    FOREIGN KEY (user_message_id) REFERENCES message(id) ON DELETE SET NULL
);

CREATE TABLE prd_version (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    generated_by_ai_message_id INTEGER,
    trigger_type TEXT, -- 'initial', 'clarification', 'edit', 'suggestion', etc.
    status TEXT NOT NULL DEFAULT 'complete',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by_ai_message_id) REFERENCES message(id) ON DELETE SET NULL,
    UNIQUE (conversation_id, version_number)
);

CREATE TABLE prd_change (
    id INTEGER PRIMARY KEY,
    prd_version_id INTEGER NOT NULL,
    previous_prd_version_id INTEGER,
    section TEXT NOT NULL, -- e.g., 'executive_summary', 'user_stories', etc.
    change_type TEXT NOT NULL, -- 'added', 'modified', 'removed'
    old_content TEXT,
    new_content TEXT,
    reason TEXT,
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prd_version_id) REFERENCES prd_version(id) ON DELETE CASCADE,
    FOREIGN KEY (previous_prd_version_id) REFERENCES prd_version(id) ON DELETE CASCADE
);

CREATE TABLE export (
    id INTEGER PRIMARY KEY,
    prd_version_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    export_format TEXT NOT NULL, -- 'markdown', 'pdf', 'word', 'json'
    file_path TEXT,
    status TEXT NOT NULL DEFAULT 'completed',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prd_version_id) REFERENCES prd_version(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE
);

CREATE INDEX idx_message_conversation_id ON message (conversation_id);
CREATE INDEX idx_file_attachment_conversation_id ON file_attachment (conversation_id);
CREATE INDEX idx_clarifying_question_conversation_id ON clarifying_question (conversation_id);
CREATE INDEX idx_prd_version_conversation_id ON prd_version (conversation_id);
CREATE INDEX idx_prd_change_prd_version_id ON prd_change (prd_version_id);
CREATE INDEX idx_export_prd_version_id ON export (prd_version_id);
CREATE INDEX idx_export_conversation_id ON export (conversation_id);