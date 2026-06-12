CREATE TABLE IF NOT EXISTS categories (
    category_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    sub_title TEXT,
    slug VARCHAR(255),
    summary TEXT,
    image VARCHAR(500),
    image_source TEXT,
    category VARCHAR(100),
    category_id INT,
    posted_at TIMESTAMP,
    is_hydro BOOLEAN DEFAULT FALSE,
    scraped_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS research_reports (
    id SERIAL PRIMARY KEY,
    expert_id INT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    sub_title TEXT,
    slug VARCHAR(255),
    summary TEXT,
    image VARCHAR(500),
    image_source TEXT,
    posted_by INT,
    is_premium BOOLEAN DEFAULT FALSE,
    posted_at TIMESTAMP,
    is_hydro BOOLEAN DEFAULT FALSE,
    scraped_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(255),
    symbol VARCHAR(50),
    is_hydro BOOLEAN DEFAULT FALSE,
    scraped_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    company_name VARCHAR(255),
    ltp DECIMAL(15, 2),
    point_change DECIMAL(15, 2),
    percent_change DECIMAL(10, 2),
    volume BIGINT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_hydro ON news_articles(is_hydro);
CREATE INDEX IF NOT EXISTS idx_news_posted_at ON news_articles(posted_at);
CREATE INDEX IF NOT EXISTS idx_research_hydro ON research_reports(is_hydro);
CREATE INDEX IF NOT EXISTS idx_research_posted_at ON research_reports(posted_at);
