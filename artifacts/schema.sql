CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    hashed_password TEXT,
    oauth_provider TEXT,
    oauth_id TEXT,
    role TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    current_version INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_prds_user_id ON prds(user_id);

CREATE TABLE prd_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    title TEXT,
    description TEXT,
    content TEXT,
    changelog TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_prd_versions_prd_id ON prd_versions(prd_id);

CREATE TABLE problem_statements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    input_text TEXT,
    source_type TEXT NOT NULL,
    source_url TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_problem_statements_prd_id ON problem_statements(prd_id);

CREATE TABLE input_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    filetype TEXT NOT NULL,
    filesize INTEGER NOT NULL,
    content BLOB,
    extracted_text TEXT,
    uploaded_by INTEGER,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE,
    FOREIGN KEY(uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_input_documents_prd_id ON input_documents(prd_id);

CREATE TABLE personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    role TEXT,
    demographics TEXT,
    characteristics TEXT,
    description TEXT,
    is_ai_generated INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_personas_prd_id ON personas(prd_id);

CREATE TABLE requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    req_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT,
    is_implicit INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_requirements_prd_id ON requirements(prd_id);
CREATE INDEX idx_requirements_type ON requirements(req_type);

CREATE TABLE user_stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    persona_id INTEGER,
    story_text TEXT NOT NULL,
    benefit TEXT,
    priority TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE,
    FOREIGN KEY(persona_id) REFERENCES personas(id) ON DELETE SET NULL
);

CREATE INDEX idx_user_stories_prd_id ON user_stories(prd_id);

CREATE TABLE acceptance_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_story_id INTEGER NOT NULL,
    criteria_text TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_story_id) REFERENCES user_stories(id) ON DELETE CASCADE
);

CREATE INDEX idx_acceptance_criteria_user_story_id ON acceptance_criteria(user_story_id);

CREATE TABLE technical_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    technology_stack TEXT,
    integrations TEXT,
    constraints TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_technical_requirements_prd_id ON technical_requirements(prd_id);

CREATE TABLE success_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    goal TEXT NOT NULL,
    kpi TEXT NOT NULL,
    target_value TEXT,
    measurement_method TEXT,
    target_timeline TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_success_metrics_prd_id ON success_metrics(prd_id);

CREATE TABLE milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    phase TEXT NOT NULL,
    deliverables TEXT,
    dependencies TEXT,
    estimated_date DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_milestones_prd_id ON milestones(prd_id);

CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    user_id INTEGER,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_chat_sessions_prd_id ON chat_sessions(prd_id);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL,
    sender_id INTEGER,
    message_text TEXT NOT NULL,
    message_type TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);

CREATE TABLE refinement_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    user_id INTEGER,
    action_type TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    change_details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_refinement_actions_prd_id ON refinement_actions(prd_id);

CREATE TABLE export_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    user_id INTEGER,
    export_format TEXT NOT NULL,
    exported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_url TEXT,
    integration_type TEXT,
    integration_status TEXT,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_export_history_prd_id ON export_history(prd_id);

CREATE TABLE background_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    error_message TEXT,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_background_jobs_prd_id ON background_jobs(prd_id);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    prd_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_prd_id ON audit_logs(prd_id);

CREATE TABLE risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    risk_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT,
    mitigation TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_risks_prd_id ON risks(prd_id);

CREATE TABLE enhancement_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    suggestion_text TEXT NOT NULL,
    ai_generated INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_selected INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_enhancement_suggestions_prd_id ON enhancement_suggestions(prd_id);

CREATE TABLE clarifying_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    ai_generated INTEGER NOT NULL DEFAULT 1,
    answered INTEGER NOT NULL DEFAULT 0,
    answer_text TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    answered_at DATETIME,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_clarifying_questions_prd_id ON clarifying_questions(prd_id);

CREATE TABLE nonfunctional_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prd_id INTEGER NOT NULL,
    nfr_category TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_id) REFERENCES prds(id) ON DELETE CASCADE
);

CREATE INDEX idx_nonfunctional_requirements_prd_id ON nonfunctional_requirements(prd_id);