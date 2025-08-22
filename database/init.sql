-- InvestAI Database Initialization Script
-- This script sets up the initial database structure and seed data

-- Create database if it doesn't exist
-- Note: This is handled by Docker Compose environment variables

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE risk_profile AS ENUM ('conservative', 'moderate', 'aggressive', 'very_aggressive');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE investment_experience AS ENUM ('beginner', 'intermediate', 'advanced', 'expert');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE asset_type AS ENUM ('stock', 'mutual_fund', 'etf', 'bond', 'commodity', 'crypto', 'real_estate', 'cash', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transaction_type AS ENUM ('buy', 'sell', 'dividend', 'bonus', 'split', 'rights');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE goal_type AS ENUM ('retirement', 'education', 'home_purchase', 'emergency_fund', 'vacation', 'wedding', 'vehicle', 'business', 'debt_payoff', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE goal_status AS ENUM ('active', 'completed', 'paused', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE goal_priority AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
-- These will be created automatically by SQLAlchemy, but we can add custom ones here

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Insert seed data for Indian market sectors
INSERT INTO sectors (name, description) VALUES
('Technology', 'Information Technology and Software companies'),
('Banking', 'Banking and Financial Services'),
('Pharmaceuticals', 'Pharmaceutical and Healthcare companies'),
('FMCG', 'Fast Moving Consumer Goods'),
('Automobile', 'Automotive and Auto Components'),
('Energy', 'Oil, Gas and Energy companies'),
('Infrastructure', 'Infrastructure and Construction'),
('Metals', 'Metals and Mining companies'),
('Telecom', 'Telecommunications companies'),
('Textiles', 'Textile and Apparel companies')
ON CONFLICT (name) DO NOTHING;

-- Insert seed data for mutual fund categories
INSERT INTO mutual_fund_categories (category, sub_category, description) VALUES
('Equity', 'Large Cap', 'Investments in large-cap stocks'),
('Equity', 'Mid Cap', 'Investments in mid-cap stocks'),
('Equity', 'Small Cap', 'Investments in small-cap stocks'),
('Equity', 'Multi Cap', 'Investments across market capitalizations'),
('Equity', 'Sectoral', 'Sector-specific equity investments'),
('Debt', 'Liquid', 'Short-term debt instruments'),
('Debt', 'Ultra Short Duration', 'Very short-term debt investments'),
('Debt', 'Short Duration', 'Short-term debt investments'),
('Debt', 'Medium Duration', 'Medium-term debt investments'),
('Debt', 'Long Duration', 'Long-term debt investments'),
('Hybrid', 'Conservative', 'Conservative hybrid funds'),
('Hybrid', 'Balanced', 'Balanced hybrid funds'),
('Hybrid', 'Aggressive', 'Aggressive hybrid funds')
ON CONFLICT (category, sub_category) DO NOTHING;

-- Insert seed data for tax brackets (FY 2024-25)
INSERT INTO tax_brackets (financial_year, income_from, income_to, tax_rate, description) VALUES
('2024-25', 0, 250000, 0, 'No tax'),
('2024-25', 250001, 500000, 5, '5% tax'),
('2024-25', 500001, 750000, 10, '10% tax'),
('2024-25', 750001, 1000000, 15, '15% tax'),
('2024-25', 1000001, 1250000, 20, '20% tax'),
('2024-25', 1250001, 1500000, 25, '25% tax'),
('2024-25', 1500001, 999999999, 30, '30% tax')
ON CONFLICT (financial_year, income_from) DO NOTHING;

-- Insert seed data for Section 80C investments
INSERT INTO tax_saving_options (section, option_name, max_limit, description) VALUES
('80C', 'PPF', 150000, 'Public Provident Fund'),
('80C', 'ELSS', 150000, 'Equity Linked Savings Scheme'),
('80C', 'EPF', 150000, 'Employee Provident Fund'),
('80C', 'NSC', 150000, 'National Savings Certificate'),
('80C', 'Tax Saver FD', 150000, 'Tax Saving Fixed Deposit'),
('80C', 'Life Insurance Premium', 150000, 'Life Insurance Premium'),
('80C', 'Home Loan Principal', 150000, 'Home Loan Principal Repayment'),
('80D', 'Health Insurance Premium', 25000, 'Health Insurance Premium for Self and Family'),
('80D', 'Health Insurance Premium (Parents)', 50000, 'Health Insurance Premium for Parents'),
('80E', 'Education Loan Interest', 999999999, 'Interest on Education Loan'),
('80G', 'Donations', 999999999, 'Donations to Charitable Organizations')
ON CONFLICT (section, option_name) DO NOTHING;

-- Create sample risk assessment questions
INSERT INTO risk_assessment_questions (question, question_type, options, weightage) VALUES
('What is your age group?', 'single_choice', '["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]', 10),
('What is your investment experience?', 'single_choice', '["Beginner", "Some experience", "Experienced", "Expert"]', 15),
('What is your investment time horizon?', 'single_choice', '["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "More than 10 years"]', 20),
('How would you react to a 20% drop in your portfolio value?', 'single_choice', '["Sell everything", "Sell some holdings", "Hold", "Buy more"]', 25),
('What percentage of your income can you invest?', 'single_choice', '["Less than 10%", "10-20%", "20-30%", "More than 30%"]', 15),
('What is your primary investment goal?', 'single_choice', '["Capital preservation", "Regular income", "Moderate growth", "High growth"]', 15)
ON CONFLICT (question) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON holdings(symbol);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_id ON transactions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_exchange ON market_data(exchange);
CREATE INDEX IF NOT EXISTS idx_financial_goals_user_id ON financial_goals(user_id);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_stocks_company_name_fts ON stocks USING gin(to_tsvector('english', company_name));
CREATE INDEX IF NOT EXISTS idx_mutual_funds_scheme_name_fts ON mutual_funds USING gin(to_tsvector('english', scheme_name));

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO investai_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO investai_user;

-- Create a function to calculate portfolio returns
CREATE OR REPLACE FUNCTION calculate_portfolio_returns(portfolio_id_param INTEGER)
RETURNS TABLE(
    total_invested DECIMAL,
    current_value DECIMAL,
    total_returns DECIMAL,
    returns_percentage DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(h.invested_amount), 0) as total_invested,
        COALESCE(SUM(h.current_value), 0) as current_value,
        COALESCE(SUM(h.current_value) - SUM(h.invested_amount), 0) as total_returns,
        CASE 
            WHEN SUM(h.invested_amount) > 0 THEN 
                ((SUM(h.current_value) - SUM(h.invested_amount)) / SUM(h.invested_amount)) * 100
            ELSE 0
        END as returns_percentage
    FROM holdings h
    WHERE h.portfolio_id = portfolio_id_param;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get asset allocation
CREATE OR REPLACE FUNCTION get_asset_allocation(portfolio_id_param INTEGER)
RETURNS TABLE(
    asset_type VARCHAR,
    allocation_percentage DECIMAL,
    current_value DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.asset_type::VARCHAR,
        CASE 
            WHEN SUM(h.current_value) OVER() > 0 THEN 
                (SUM(h.current_value) / SUM(h.current_value) OVER()) * 100
            ELSE 0
        END as allocation_percentage,
        SUM(h.current_value) as current_value
    FROM holdings h
    WHERE h.portfolio_id = portfolio_id_param
    GROUP BY h.asset_type;
END;
$$ LANGUAGE plpgsql;

-- Insert completion message
INSERT INTO system_logs (log_level, message, created_at) VALUES 
('INFO', 'Database initialization completed successfully', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;
