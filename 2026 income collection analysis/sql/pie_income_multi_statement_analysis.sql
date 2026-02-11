-- ============================================================================
-- PIE Income Collection Analysis - Multi-Statement Comparison
-- ============================================================================
-- PURPOSE: Compare success rates and income collection performance across
--          different statement cohorts (18, 26, 34, 42)
--
-- KEY METRICS:
--   1. success_rate_pct: % of accounts that were either approved outright
--                        OR collected income after PIE (overall success)
--   2. pie_income_collection_rate_pct: % of PIE accounts that updated income
--                                      within 8 months
--
-- BUSINESS CONTEXT:
--   - Statement 18+ requires income to be <12 months old (income requirement)
--   - PIE (PRE_EVAL_APPROVED) = account blocked ONLY by stale income
--   - Accounts can be PIE and then APPROVED in same month if income updated quickly
--   - EFX income records expire after 1 year, so use recent cohorts (Apr 2025)
-- ============================================================================

with base_population as (
    -- ========================================================================
    -- BASE POPULATION: Get all APPROVED or PRE_EVAL_APPROVED accounts
    -- ========================================================================
    -- LOGIC:
    --   1. Pull all accounts with APPROVED or PIE outcome at target statements
    --   2. Join to PERSON_ID for income tracking
    --   3. Flag accounts that had PIE at any point in the month/statement
    --   4. Deduplicate: if account has both PIE and APPROVED, keep PIE row
    --
    -- WHY DEDUPLICATE TO PIE?
    --   An account can get PIE, update income same month, then get APPROVED.
    --   We want to count this as "PIE → Income Collected", NOT "Approved Outright"
    -- ========================================================================
    select
        date_trunc(month, stmt.statement_end_dt) as stmt_month,
        clip.account_id,
        clip.statement_number,
        clip.outcome,
        clip.evaluated_timestamp,
        acb.PERSON_ID,  -- Required for income tracking via CLIP_USER_INCOMES

        -- PIE Flag: 1 if this account had PIE at any point this month/statement
        -- Uses window function to check all rows for this account/month/statement
        max(case when clip.outcome = 'PRE_EVAL_APPROVED' then 1 else 0 end) over (
            partition by clip.account_id, date_trunc(month, stmt.statement_end_dt), clip.statement_number
        ) as had_pie_in_month

    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    join EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE acb
        on clip.account_id = acb.ACCOUNT_ID
    where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'  -- April 2025 cohort
      and clip.outcome in ('APPROVED', 'PRE_EVAL_APPROVED')
      and clip.statement_number in (18, 26, 34, 42)  -- Key statement milestones

    -- DEDUPLICATION: Keep only 1 row per account/month/statement
    -- Priority: PIE first (order by 0), then APPROVED (order by 1)
    -- This ensures accounts with both outcomes are classified as PIE
    qualify row_number() over (
        partition by clip.account_id, date_trunc(month, stmt.statement_end_dt), clip.statement_number
        order by case when clip.outcome = 'PRE_EVAL_APPROVED' then 0 else 1 end, acb.PERSON_ID
    ) = 1
),

income_collected as (
    -- ========================================================================
    -- INCOME COLLECTION: Track which PIE accounts updated income
    -- ========================================================================
    -- LOGIC:
    --   1. Only look at PIE accounts (had_pie_in_month = 1)
    --   2. Find income updates in CLIP_USER_INCOMES after PIE timestamp
    --   3. Income must be within 8 months (240 days) of PIE event
    --   4. Take only the FIRST income update (earliest CREATED_AT)
    --
    -- NOTE: EFX income records disappear after 1 year, so this only works
    --       for cohorts within the last 12 months
    -- ========================================================================
    select
        base.account_id,
        base.statement_number,
        1 as has_income_update  -- Simple flag: this account collected income
    from base_population base
    join EDW_DB.PUBLIC.CLIP_USER_INCOMES inc
        on base.PERSON_ID = inc.PERSON_ID
    where base.had_pie_in_month = 1  -- Only track PIE accounts
      and inc.CREATED_AT > base.evaluated_timestamp  -- Income AFTER PIE event
      and inc.CREATED_AT <= DATEADD(day, 240, base.evaluated_timestamp)  -- Within 8 months
      and inc.annual_income IS NOT NULL  -- Valid income value

    -- Keep only FIRST income update per account/statement
    qualify row_number() over (
        partition by base.account_id, base.statement_number
        order by inc.CREATED_AT  -- Earliest update
    ) = 1
)

-- ============================================================================
-- FINAL OUTPUT: Metrics by statement
-- ============================================================================
select
    base.statement_number,

    -- POPULATION COUNTS
    count(distinct base.account_id) as total_population,
    count(distinct case when base.had_pie_in_month = 0 then base.account_id end) as approved_outright_count,  -- Never had PIE
    count(distinct case when base.had_pie_in_month = 1 then base.account_id end) as pie_total_count,          -- Had PIE
    count(distinct case when base.had_pie_in_month = 1 and inc.has_income_update = 1 then base.account_id end) as pie_income_collected_count,     -- PIE + collected income
    count(distinct case when base.had_pie_in_month = 1 and inc.has_income_update is null then base.account_id end) as pie_income_not_collected_count,  -- PIE + NO income
    count(distinct case when base.had_pie_in_month = 0 or inc.has_income_update = 1 then base.account_id end) as success_count,  -- Approved OR PIE+Income

    -- KEY PERFORMANCE METRICS
    -- ========================================================================
    -- SUCCESS RATE: (Approved Outright + PIE with Income) / Total Population
    --   = Overall % of accounts that achieved a positive outcome
    --   = "No barrier" + "Had barrier but cleared it"
    -- ========================================================================
    round(100.0 * count(distinct case when base.had_pie_in_month = 0 or inc.has_income_update = 1 then base.account_id end) / count(distinct base.account_id), 1) as success_rate_pct,

    -- ========================================================================
    -- PIE INCOME COLLECTION RATE: PIE with Income / Total PIE
    --   = Of PIE accounts, what % successfully updated income?
    --   = Measures effectiveness of income collection process
    -- ========================================================================
    round(100.0 * count(distinct case when base.had_pie_in_month = 1 and inc.has_income_update = 1 then base.account_id end) / nullif(count(distinct case when base.had_pie_in_month = 1 then base.account_id end), 0), 1) as pie_income_collection_rate_pct

from base_population base
left join income_collected inc
    on base.account_id = inc.account_id
    and base.statement_number = inc.statement_number
group by base.statement_number
order by base.statement_number;

-- ============================================================================
-- EXPECTED OUTPUT:
--   Each row = one statement cohort
--   Columns show population breakdown and two key performance metrics
--
-- INTERPRETATION:
--   - Higher success_rate_pct = better overall performance
--   - Higher pie_income_collection_rate_pct = more effective income collection
--   - Gap between the two = opportunity from PIE accounts not collecting income
-- ============================================================================
