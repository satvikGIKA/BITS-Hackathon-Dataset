CREATE TABLE IF NOT EXISTS works (
    work_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT NOT NULL,
    category TEXT NOT NULL,
    value_inr INTEGER NOT NULL,
    completion_date TEXT NOT NULL,
    project_manager TEXT NOT NULL,
    grade TEXT,
    role TEXT,
    has_reference_letter INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS personnel_certs (
    doc_id TEXT PRIMARY KEY,
    person_name TEXT NOT NULL,
    credential_type TEXT NOT NULL,
    credential_id TEXT,
    issued_date TEXT
);

CREATE INDEX IF NOT EXISTS idx_works_client ON works(client);
CREATE INDEX IF NOT EXISTS idx_works_pm ON works(project_manager);
CREATE INDEX IF NOT EXISTS idx_works_grade ON works(grade);
CREATE INDEX IF NOT EXISTS idx_certs_person ON personnel_certs(person_name);
