CREATE TABLE conversation (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE,
    title TEXT,
    current_prd_version_id INTEGER,
    status TEXT NOT NULL DEFAULT 'active',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(current_prd_version_id) REFERENCES prd_version(id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX idx_conversation_session_id ON conversation (session_id);

CREATE TABLE message (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    sender TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    status TEXT NOT NULL DEFAULT 'sent',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversation_id) REFERENCES conversation(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_message_conversation_id ON message (conversation_id);

CREATE TABLE clarifying_question (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    message_id INTEGER,
    question TEXT NOT NULL,
    category TEXT,
    priority INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',
    answer TEXT,
    answered_at DATETIME,
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversation_id) REFERENCES conversation(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(message_id) REFERENCES message(id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX idx_clarifying_question_conversation_id ON clarifying_question (conversation_id);

CREATE TABLE file_attachment (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    storage_path TEXT NOT NULL,
    extracted_content TEXT,
    status TEXT NOT NULL DEFAULT 'uploaded',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversation_id) REFERENCES conversation(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_file_attachment_conversation_id ON file_attachment (conversation_id);

CREATE TABLE prd_version (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    change_summary TEXT,
    status TEXT NOT NULL DEFAULT 'generated',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversation_id) REFERENCES conversation(id) ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE(conversation_id, version_number)
);

CREATE INDEX idx_prd_version_conversation_id ON prd_version (conversation_id);

CREATE TABLE prd_change (
    id INTEGER PRIMARY KEY,
    prd_version_id INTEGER NOT NULL,
    previous_prd_version_id INTEGER,
    changed_sections TEXT NOT NULL,
    change_reason TEXT,
    diff_json TEXT,
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_version(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(previous_prd_version_id) REFERENCES prd_version(id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX idx_prd_change_prd_version_id ON prd_change (prd_version_id);

CREATE TABLE export (
    id INTEGER PRIMARY KEY,
    prd_version_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    export_format TEXT NOT NULL,
    export_path TEXT,
    status TEXT NOT NULL DEFAULT 'completed',
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_version(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(conversation_id) REFERENCES conversation(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_export_prd_version_id ON export (prd_version_id);
CREATE INDEX idx_export_conversation_id ON export (conversation_id);