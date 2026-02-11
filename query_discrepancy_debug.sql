-- Debug Query: Find the 48 accounts that differ between the two approaches

-- Query 1 Population (using statement_end_dt)
CREATE TEMP TABLE query1_accounts AS
SELECT DISTINCT
    stmt.account_id,
    stmt.statement_end_dt,
    clip.evaluated_timestamp,
    clip.outcome,
    DATEDIFF(day, stmt.statement_end_dt, clip.evaluated_timestamp) as days_between_stmt_and_eval
FROM EDW_DB.PUBLIC.account_statements stmt
JOIN EDW_DB.PUBLIC.clip_results_data clip
    ON stmt.account_id = clip.account_id
    AND stmt.statement_num = clip.statement_number
    AND clip.outcome = 'PRE_EVAL_APPROVED'
WHERE stmt.statement_num = 18
  AND date_trunc(month, stmt.statement_end_dt) = '2024-11-01';

-- Query 2 Population (using evaluated_timestamp)
CREATE TEMP TABLE query2_accounts AS
SELECT DISTINCT
    pre_eval.account_id,
    stmt.statement_end_dt,
    pre_eval.evaluated_timestamp,
    pre_eval.outcome,
    DATEDIFF(day, stmt.statement_end_dt, pre_eval.evaluated_timestamp) as days_between_stmt_and_eval
FROM EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
LEFT JOIN EDW_DB.PUBLIC.account_statements stmt
    ON pre_eval.account_id = stmt.account_id
    AND pre_eval.statement_number = stmt.statement_num
WHERE pre_eval.evaluated_timestamp BETWEEN '2024-11-01' AND '2024-11-30'
  AND pre_eval.outcome = 'PRE_EVAL_APPROVED'
  AND pre_eval.statement_number = 18;

-- Show counts
SELECT 'Query 1 (stmt_end_dt filter)' as source, COUNT(*) as cnt FROM query1_accounts
UNION ALL
SELECT 'Query 2 (eval_timestamp filter)' as source, COUNT(*) as cnt FROM query2_accounts
UNION ALL
SELECT 'In Both' as source, COUNT(*) as cnt
FROM query1_accounts q1
INNER JOIN query2_accounts q2 ON q1.account_id = q2.account_id
UNION ALL
SELECT 'Only in Query 1 (stmt end Nov, eval Dec)' as source, COUNT(*) as cnt
FROM query1_accounts q1
LEFT JOIN query2_accounts q2 ON q1.account_id = q2.account_id
WHERE q2.account_id IS NULL
UNION ALL
SELECT 'Only in Query 2 (stmt end Oct, eval Nov)' as source, COUNT(*) as cnt
FROM query2_accounts q2
LEFT JOIN query1_accounts q1 ON q1.account_id = q2.account_id
WHERE q1.account_id IS NULL;

-- Show the accounts only in Query 1
SELECT
    'Only in Query 1' as category,
    account_id,
    statement_end_dt,
    evaluated_timestamp,
    days_between_stmt_and_eval,
    TO_CHAR(statement_end_dt, 'YYYY-MM') as stmt_month,
    TO_CHAR(evaluated_timestamp, 'YYYY-MM') as eval_month
FROM query1_accounts q1
LEFT JOIN query2_accounts q2 ON q1.account_id = q2.account_id
WHERE q2.account_id IS NULL
ORDER BY evaluated_timestamp
LIMIT 20;

-- Show the accounts only in Query 2
SELECT
    'Only in Query 2' as category,
    account_id,
    statement_end_dt,
    evaluated_timestamp,
    days_between_stmt_and_eval,
    TO_CHAR(statement_end_dt, 'YYYY-MM') as stmt_month,
    TO_CHAR(evaluated_timestamp, 'YYYY-MM') as eval_month
FROM query2_accounts q2
LEFT JOIN query1_accounts q1 ON q1.account_id = q2.account_id
WHERE q1.account_id IS NULL
ORDER BY evaluated_timestamp
LIMIT 20;

-- Summary statistics on timing differences
SELECT
    'Timing Analysis' as analysis,
    AVG(days_between_stmt_and_eval) as avg_days_between,
    MIN(days_between_stmt_and_eval) as min_days_between,
    MAX(days_between_stmt_and_eval) as max_days_between,
    MEDIAN(days_between_stmt_and_eval) as median_days_between
FROM query1_accounts
UNION ALL
SELECT
    'Query 2 Timing',
    AVG(days_between_stmt_and_eval),
    MIN(days_between_stmt_and_eval),
    MAX(days_between_stmt_and_eval),
    MEDIAN(days_between_stmt_and_eval)
FROM query2_accounts;
