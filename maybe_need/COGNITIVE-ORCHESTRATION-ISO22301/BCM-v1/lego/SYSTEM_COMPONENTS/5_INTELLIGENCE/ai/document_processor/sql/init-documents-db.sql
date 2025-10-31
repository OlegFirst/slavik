-- Document Processor Database Initialization
-- BCM Platform Document Processing System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Document metadata table
CREATE TABLE IF NOT EXISTS document_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    company_id VARCHAR(100) NOT NULL,
    document_type VARCHAR(50),
    classification VARCHAR(50),
    language VARCHAR(10),
    page_count INTEGER,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_date TIMESTAMP WITH TIME ZONE,
    processing_status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document content table
CREATE TABLE IF NOT EXISTS document_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    raw_text TEXT,
    structured_content JSONB,
    extracted_entities JSONB DEFAULT '[]',
    key_phrases JSONB DEFAULT '[]',
    summary TEXT,
    topics JSONB DEFAULT '[]',
    compliance_tags JSONB DEFAULT '[]',
    word_count INTEGER,
    character_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- BCM document analysis table
CREATE TABLE IF NOT EXISTS bcm_document_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    bcm_category VARCHAR(50) NOT NULL,
    iso22301_clauses JSONB DEFAULT '[]',
    risk_indicators JSONB DEFAULT '[]',
    compliance_score DECIMAL(3,2) CHECK (compliance_score >= 0 AND compliance_score <= 1),
    recommendations JSONB DEFAULT '[]',
    critical_sections JSONB DEFAULT '[]',
    stakeholder_references JSONB DEFAULT '[]',
    process_mappings JSONB DEFAULT '[]',
    analysis_version VARCHAR(20) DEFAULT '1.0',
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document processing jobs table
CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL, -- extraction, analysis, classification, search_indexing
    status VARCHAR(20) DEFAULT 'queued', -- queued, running, completed, failed, cancelled
    priority INTEGER DEFAULT 5,
    parameters JSONB DEFAULT '{}',
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document relationships table (for document comparisons, references, etc.)
CREATE TABLE IF NOT EXISTS document_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    target_document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- references, updates, replaces, similar_to
    similarity_score DECIMAL(3,2),
    relationship_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source_document_id, target_document_id, relationship_type)
);

-- Document access log table (for audit purposes)
CREATE TABLE IF NOT EXISTS document_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    user_id VARCHAR(100),
    company_id VARCHAR(100) NOT NULL,
    access_type VARCHAR(50) NOT NULL, -- view, download, process, search
    ip_address INET,
    user_agent TEXT,
    access_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document versions table (for version control)
CREATE TABLE IF NOT EXISTS document_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    changes_description TEXT,
    changed_by VARCHAR(100),
    change_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, version_number)
);

-- Search indices table (for document search optimization)
CREATE TABLE IF NOT EXISTS document_search_index (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES document_metadata(id) ON DELETE CASCADE,
    search_vector TSVECTOR,
    keywords JSONB DEFAULT '[]',
    semantic_embedding VECTOR(384), -- For semantic search (requires pgvector extension)
    last_indexed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_document_metadata_company_id ON document_metadata(company_id);
CREATE INDEX IF NOT EXISTS idx_document_metadata_file_hash ON document_metadata(file_hash);
CREATE INDEX IF NOT EXISTS idx_document_metadata_document_type ON document_metadata(document_type);
CREATE INDEX IF NOT EXISTS idx_document_metadata_processing_status ON document_metadata(processing_status);
CREATE INDEX IF NOT EXISTS idx_document_metadata_upload_date ON document_metadata(upload_date);

CREATE INDEX IF NOT EXISTS idx_document_content_document_id ON document_content(document_id);
CREATE INDEX IF NOT EXISTS idx_bcm_analysis_document_id ON bcm_document_analysis(document_id);
CREATE INDEX IF NOT EXISTS idx_bcm_analysis_category ON bcm_document_analysis(bcm_category);
CREATE INDEX IF NOT EXISTS idx_bcm_analysis_compliance_score ON bcm_document_analysis(compliance_score);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_priority ON processing_jobs(priority);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_document_id ON processing_jobs(document_id);

CREATE INDEX IF NOT EXISTS idx_document_relationships_source ON document_relationships(source_document_id);
CREATE INDEX IF NOT EXISTS idx_document_relationships_target ON document_relationships(target_document_id);
CREATE INDEX IF NOT EXISTS idx_document_relationships_type ON document_relationships(relationship_type);

CREATE INDEX IF NOT EXISTS idx_access_log_document_id ON document_access_log(document_id);
CREATE INDEX IF NOT EXISTS idx_access_log_company_id ON document_access_log(company_id);
CREATE INDEX IF NOT EXISTS idx_access_log_timestamp ON document_access_log(access_timestamp);

CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON document_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_document_search_document_id ON document_search_index(document_id);

-- Full text search index
CREATE INDEX IF NOT EXISTS idx_document_search_vector ON document_search_index USING gin(search_vector);

-- JSON indices for better JSONB query performance
CREATE INDEX IF NOT EXISTS idx_document_content_entities ON document_content USING gin(extracted_entities);
CREATE INDEX IF NOT EXISTS idx_document_content_topics ON document_content USING gin(topics);
CREATE INDEX IF NOT EXISTS idx_bcm_analysis_iso_clauses ON bcm_document_analysis USING gin(iso22301_clauses);
CREATE INDEX IF NOT EXISTS idx_bcm_analysis_risk_indicators ON bcm_document_analysis USING gin(risk_indicators);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_document_metadata_updated_at 
    BEFORE UPDATE ON document_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_content_updated_at 
    BEFORE UPDATE ON document_content 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bcm_analysis_updated_at 
    BEFORE UPDATE ON bcm_document_analysis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up old processing jobs
CREATE OR REPLACE FUNCTION cleanup_old_processing_jobs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM processing_jobs 
    WHERE status IN ('completed', 'failed') 
    AND completed_at < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update document search index
CREATE OR REPLACE FUNCTION update_document_search_index(doc_id UUID)
RETURNS VOID AS $$
BEGIN
    INSERT INTO document_search_index (document_id, search_vector, keywords, last_indexed)
    SELECT 
        dc.document_id,
        to_tsvector('english', 
            COALESCE(dm.filename, '') || ' ' ||
            COALESCE(dc.raw_text, '') || ' ' ||
            COALESCE(dc.summary, '')
        ) as search_vector,
        dc.key_phrases as keywords,
        NOW()
    FROM document_content dc
    JOIN document_metadata dm ON dc.document_id = dm.id
    WHERE dc.document_id = doc_id
    ON CONFLICT (document_id) DO UPDATE SET
        search_vector = EXCLUDED.search_vector,
        keywords = EXCLUDED.keywords,
        last_indexed = EXCLUDED.last_indexed;
END;
$$ LANGUAGE plpgsql;

-- Insert initial BCM document categories
CREATE TABLE IF NOT EXISTS bcm_document_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    iso22301_mapping JSONB DEFAULT '[]',
    keywords JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO bcm_document_categories (category_name, description, iso22301_mapping, keywords) VALUES
('policy', 'BCM policies and governance documents', '["5.2", "4.4"]', '["policy", "governance", "framework", "standard"]'),
('procedure', 'BCM procedures and processes', '["7.5", "8.1"]', '["procedure", "process", "workflow", "instruction"]'),
('plan', 'Business continuity and recovery plans', '["8.3", "8.4"]', '["plan", "strategy", "continuity", "recovery", "response"]'),
('risk_assessment', 'Risk assessments and threat analyses', '["6.1", "8.2"]', '["risk", "assessment", "analysis", "threat", "vulnerability"]'),
('bia', 'Business impact analyses', '["8.2"]', '["business impact", "bia", "critical", "dependencies"]'),
('exercise', 'Exercise and testing documentation', '["8.5", "9.1"]', '["exercise", "drill", "test", "simulation", "tabletop"]'),
('audit', 'Audit reports and compliance documentation', '["9.2", "9.3"]', '["audit", "compliance", "review", "assessment"]'),
('training', 'Training materials and competency records', '["7.2"]', '["training", "competency", "awareness", "education"]')
ON CONFLICT (category_name) DO NOTHING;

-- Create a view for document analytics
CREATE OR REPLACE VIEW document_analytics AS
SELECT 
    dm.company_id,
    dm.document_type,
    bda.bcm_category,
    COUNT(*) as document_count,
    AVG(bda.compliance_score) as avg_compliance_score,
    COUNT(CASE WHEN dm.processing_status = 'completed' THEN 1 END) as processed_count,
    COUNT(CASE WHEN dm.processing_status = 'failed' THEN 1 END) as failed_count,
    MAX(dm.upload_date) as last_upload_date,
    SUM(dm.file_size) as total_file_size
FROM document_metadata dm
LEFT JOIN bcm_document_analysis bda ON dm.id = bda.document_id
GROUP BY dm.company_id, dm.document_type, bda.bcm_category;

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO docprocessor;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO docprocessor;
