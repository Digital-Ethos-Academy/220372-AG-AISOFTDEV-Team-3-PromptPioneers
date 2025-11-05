CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    full_name TEXT,
    role TEXT NOT NULL,
    auth_provider TEXT NOT NULL,
    provider_id TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    current_version_id TEXT,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(current_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_projects_user_id ON projects(user_id);

CREATE TABLE prd_versions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    summary TEXT,
    status TEXT NOT NULL,
    created_by TEXT NOT NULL,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(created_by) REFERENCES users(id)
);

CREATE INDEX idx_prd_versions_project_id ON prd_versions(project_id);

CREATE TABLE input_sources (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    type TEXT NOT NULL,
    source_url TEXT,
    file_name TEXT,
    file_size INTEGER,
    file_type TEXT,
    text_content TEXT,
    uploaded_by TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id),
    FOREIGN KEY(uploaded_by) REFERENCES users(id)
);

CREATE INDEX idx_input_sources_prd_version_id ON input_sources(prd_version_id);

CREATE TABLE personas (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT,
    demographics TEXT,
    characteristics TEXT,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_personas_prd_version_id ON personas(prd_version_id);

CREATE TABLE requirements (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT,
    source TEXT,
    is_implicit INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_requirements_prd_version_id ON requirements(prd_version_id);

CREATE TABLE user_stories (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    persona_id TEXT,
    title TEXT NOT NULL,
    story TEXT NOT NULL,
    benefit TEXT,
    priority TEXT,
    status TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id),
    FOREIGN KEY(persona_id) REFERENCES personas(id)
);

CREATE INDEX idx_user_stories_prd_version_id ON user_stories(prd_version_id);

CREATE TABLE acceptance_criteria (
    id TEXT PRIMARY KEY,
    user_story_id TEXT NOT NULL,
    criteria TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_story_id) REFERENCES user_stories(id)
);

CREATE INDEX idx_acceptance_criteria_user_story_id ON acceptance_criteria(user_story_id);

CREATE TABLE clarifying_questions (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    question TEXT NOT NULL,
    ai_detected INTEGER NOT NULL DEFAULT 1,
    answered INTEGER NOT NULL DEFAULT 0,
    answer TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    answered_at DATETIME,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_clarifying_questions_prd_version_id ON clarifying_questions(prd_version_id);

CREATE TABLE technical_requirements (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_technical_requirements_prd_version_id ON technical_requirements(prd_version_id);

CREATE TABLE goals (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_goals_prd_version_id ON goals(prd_version_id);

CREATE TABLE success_metrics (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    kpi TEXT NOT NULL,
    measurement_method TEXT,
    target_value TEXT,
    target_timeline TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(goal_id) REFERENCES goals(id)
);

CREATE INDEX idx_success_metrics_goal_id ON success_metrics(goal_id);

CREATE TABLE milestones (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    estimated_date DATE,
    phase TEXT,
    dependencies TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_milestones_prd_version_id ON milestones(prd_version_id);

CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    started_by TEXT NOT NULL,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id),
    FOREIGN KEY(started_by) REFERENCES users(id)
);

CREATE INDEX idx_chat_sessions_prd_version_id ON chat_sessions(prd_version_id);

CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    sender_type TEXT NOT NULL,
    sender_id TEXT,
    message TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);

CREATE TABLE feature_suggestions (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    suggestion TEXT NOT NULL,
    rationale TEXT,
    is_selected INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_feature_suggestions_prd_version_id ON feature_suggestions(prd_version_id);

CREATE TABLE risks (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    risk_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    mitigation TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_risks_prd_version_id ON risks(prd_version_id);

CREATE TABLE exports (
    id TEXT PRIMARY KEY,
    prd_version_id TEXT NOT NULL,
    exported_by TEXT NOT NULL,
    export_type TEXT NOT NULL,
    file_format TEXT NOT NULL,
    export_status TEXT NOT NULL,
    external_system TEXT,
    external_reference TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id),
    FOREIGN KEY(exported_by) REFERENCES users(id)
);

CREATE INDEX idx_exports_prd_version_id ON exports(prd_version_id);

CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    prd_version_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(prd_version_id) REFERENCES prd_versions(id)
);

CREATE INDEX idx_audit_logs_prd_version_id ON audit_logs(prd_version_id);

CREATE TABLE integration_connections (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX idx_integration_connections_user_id ON integration_connections(user_id);