-- 深远涉外律所初始化迁移 schema
-- 1. 核心线索表 intakes
CREATE TABLE IF NOT EXISTS intakes (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254),
    phone VARCHAR(50),
    matter VARCHAR(50) NOT NULL,
    summary TEXT NOT NULL,
    country_or_region VARCHAR(100),
    language VARCHAR(10) DEFAULT 'zh' NOT NULL,
    user_agent TEXT,
    status VARCHAR(20) DEFAULT 'new' NOT NULL,
    note TEXT,
    consent_at TIMESTAMPTZ,
    score INTEGER DEFAULT 0 NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intakes_status ON intakes (status);
CREATE INDEX IF NOT EXISTS idx_intakes_created_at ON intakes (created_at);
CREATE INDEX IF NOT EXISTS idx_intakes_source ON intakes (source);

-- 2. 材料附件表 intake_files
CREATE TABLE IF NOT EXISTS intake_files (
    id BIGSERIAL PRIMARY KEY,
    intake_id BIGINT NOT NULL REFERENCES intakes(id) ON DELETE CASCADE,
    original_name VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    size BIGINT NOT NULL,
    content_type VARCHAR(100),
    uploaded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intake_files_intake_id ON intake_files (intake_id);

-- 3. CMS 文章表 content_articles
CREATE TABLE IF NOT EXISTS content_articles (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(200) UNIQUE NOT NULL,
    title_zh VARCHAR(255) DEFAULT '' NOT NULL,
    title_en VARCHAR(255) DEFAULT '' NOT NULL,
    description_zh TEXT DEFAULT '' NOT NULL,
    description_en TEXT DEFAULT '' NOT NULL,
    body_zh TEXT DEFAULT '' NOT NULL,
    body_en TEXT DEFAULT '' NOT NULL,
    business VARCHAR(50) DEFAULT 'general' NOT NULL,
    intent VARCHAR(10) DEFAULT 'I' NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_content_articles_status ON content_articles (status);
CREATE INDEX IF NOT EXISTS idx_content_articles_slug ON content_articles (slug);

-- 4. CMS 文章版本控制表 content_article_versions
CREATE TABLE IF NOT EXISTS content_article_versions (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL REFERENCES content_articles(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    snapshot JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(article_id, version)
);

-- 5. 审计与日志表
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    ip INET,
    action VARCHAR(100) NOT NULL,
    detail TEXT
);

CREATE TABLE IF NOT EXISTS page_views (
    id BIGSERIAL PRIMARY KEY,
    viewed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS search_log (
    id BIGSERIAL PRIMARY KEY,
    q VARCHAR(255) NOT NULL,
    results INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
