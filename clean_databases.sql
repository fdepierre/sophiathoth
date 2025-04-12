-- Clean Knowledge Base tables
TRUNCATE TABLE knowledge_revisions CASCADE;
TRUNCATE TABLE knowledge_attachments CASCADE;
TRUNCATE TABLE knowledge_tags CASCADE;
TRUNCATE TABLE knowledge_entries CASCADE;
TRUNCATE TABLE tags CASCADE;
TRUNCATE TABLE knowledge_categories CASCADE;

-- Clean Document Processor tables
TRUNCATE TABLE tender_responses CASCADE;
TRUNCATE TABLE tender_questions CASCADE;
TRUNCATE TABLE tender_sheets CASCADE;
TRUNCATE TABLE tender_documents CASCADE;

-- Confirm cleanup
SELECT 'Database cleaned successfully' AS status;
