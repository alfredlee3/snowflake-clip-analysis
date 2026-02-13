-- ============================================================================
-- PIE Income Collection Over Time - ACCOUNT-LEVEL Analysis (All Statements)
-- ============================================================================
-- PURPOSE: Track how success rates evolve month-by-month over the 8-month
--          window, counting each ACCOUNT only once per statement
--
-- OUTPUT: Individual statement lines (18, 26, 34, 42) + Overall Stmt 18+
--         ALL using account-level methodology
--
-- TIME WINDOWS: Uses 30-day rolling windows (not calendar months)
--   - Month 0: 0-30 days after PIE
--   - Month 1: 31-60 days after PIE
--   - Month 2: 61-90 days after PIE
--   - ... up to Month 8: 211-240 days after PIE
-- ============================================================================

with base_population_by_statement as (
    -- ========================================================================
    -- BASE POPULATION: Get PIE accounts at each statement, deduplicated
    -- ========================================================================
    select
        clip.statement_number,
        clip.account_id,
        min(clip.evaluated_timestamp) as earliest_pie_timestamp,  -- Use earliest PIE at this statement
        acb.PERSON_ID
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    join EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE acb
        on clip.account_id = acb.ACCOUNT_ID
    where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'  -- April 2025 cohort
      and clip.outcome = 'PRE_EVAL_APPROVED'
      and clip.statement_number in (18, 26, 34, 42)
    group by clip.statement_number, clip.account_id, acb.PERSON_ID
),

base_population_overall as (
    -- ========================================================================
    -- OVERALL BASE: Get PIE accounts across all Stmt 18+, deduplicated
    -- ========================================================================
    select
        clip.account_id,
        min(clip.evaluated_timestamp) as earliest_pie_timestamp,  -- Use earliest PIE across all statements
        acb.PERSON_ID
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    join EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE acb
        on clip.account_id = acb.ACCOUNT_ID
    where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'  -- April 2025 cohort
      and clip.outcome = 'PRE_EVAL_APPROVED'
      and clip.statement_number >= 18
    group by clip.account_id, acb.PERSON_ID
),

income_by_month_statement as (
    -- ========================================================================
    -- INCOME COLLECTION: Track WHEN income was collected per statement
    -- ========================================================================
    select
        base.statement_number,
        base.account_id,
        inc.CREATED_AT as income_collected_at,
        datediff(day, base.earliest_pie_timestamp, inc.CREATED_AT) as days_to_collection,
        -- 30-day rolling windows: 0-30=Month 0, 31-60=Month 1, etc.
        floor(datediff(day, base.earliest_pie_timestamp, inc.CREATED_AT) / 30) as months_to_collection

    from base_population_by_statement base
    left join EDW_DB.PUBLIC.CLIP_USER_INCOMES inc
        on base.PERSON_ID = inc.PERSON_ID
        and inc.CREATED_AT > base.earliest_pie_timestamp  -- Income AFTER PIE event
        and inc.CREATED_AT <= DATEADD(day, 240, base.earliest_pie_timestamp)  -- Within 240 days (8x30)
        and inc.annual_income IS NOT NULL

    -- Keep only FIRST income update per account at each statement
    qualify row_number() over (
        partition by base.statement_number, base.account_id
        order by inc.CREATED_AT
    ) = 1
),

income_by_month_overall as (
    -- ========================================================================
    -- INCOME COLLECTION: Track WHEN income was collected overall
    -- ========================================================================
    select
        base.account_id,
        inc.CREATED_AT as income_collected_at,
        datediff(day, base.earliest_pie_timestamp, inc.CREATED_AT) as days_to_collection,
        -- 30-day rolling windows: 0-30=Month 0, 31-60=Month 1, etc.
        floor(datediff(day, base.earliest_pie_timestamp, inc.CREATED_AT) / 30) as months_to_collection

    from base_population_overall base
    left join EDW_DB.PUBLIC.CLIP_USER_INCOMES inc
        on base.PERSON_ID = inc.PERSON_ID
        and inc.CREATED_AT > base.earliest_pie_timestamp  -- Income AFTER PIE event
        and inc.CREATED_AT <= DATEADD(day, 240, base.earliest_pie_timestamp)  -- Within 240 days (8x30)
        and inc.annual_income IS NOT NULL

    -- Keep only FIRST income update per account
    qualify row_number() over (
        partition by base.account_id
        order by inc.CREATED_AT
    ) = 1
),

month_series as (
    -- Generate series 0-7 representing months after PIE evaluation
    -- Will be displayed as Month 1-8 (Month 1 = 0-30 days, Month 8 = 211-240 days)
    select 0 as month_offset union all
    select 1 union all select 2 union all select 3 union all select 4 union all
    select 5 union all select 6 union all select 7
),

cumulative_by_statement as (
    -- ========================================================================
    -- CUMULATIVE CALCULATION: Per statement (account-level)
    -- ========================================================================
    select
        base.statement_number,
        m.month_offset,

        -- Total unique accounts with PIE at this statement
        count(distinct base.account_id) as pie_total_count,

        -- Accounts that collected income BY this month offset
        count(distinct case
            when inc.months_to_collection is not null
            and inc.months_to_collection <= m.month_offset
            then base.account_id
        end) as pie_income_collected_by_month,

        -- NEW income collections THIS month
        count(distinct case
            when inc.months_to_collection = m.month_offset
            then base.account_id
        end) as new_income_collections_this_month

    from base_population_by_statement base
    cross join month_series m
    left join income_by_month_statement inc
        on base.statement_number = inc.statement_number
        and base.account_id = inc.account_id
    group by base.statement_number, m.month_offset
),

cumulative_overall as (
    -- ========================================================================
    -- CUMULATIVE CALCULATION: Overall Stmt 18+ (account-level)
    -- ========================================================================
    select
        999 as statement_number,  -- Use 999 as indicator for "Overall"
        m.month_offset,

        -- Total unique accounts with PIE
        count(distinct base.account_id) as pie_total_count,

        -- Accounts that collected income BY this month offset
        count(distinct case
            when inc.months_to_collection is not null
            and inc.months_to_collection <= m.month_offset
            then base.account_id
        end) as pie_income_collected_by_month,

        -- NEW income collections THIS month
        count(distinct case
            when inc.months_to_collection = m.month_offset
            then base.account_id
        end) as new_income_collections_this_month

    from base_population_overall base
    cross join month_series m
    left join income_by_month_overall inc
        on base.account_id = inc.account_id
    group by m.month_offset
),

combined as (
    select * from cumulative_by_statement
    union all
    select * from cumulative_overall
)

-- ============================================================================
-- FINAL OUTPUT: Monthly progression (account-level) for all statements
-- ============================================================================
select
    case
        when statement_number = 999 then 'Overall Stmt 18+'
        else 'Stmt ' || statement_number
    end as statement_label,
    statement_number,
    month_offset,
    pie_total_count,
    pie_income_collected_by_month,

    -- CUMULATIVE PIE INCOME COLLECTION RATE at this month mark
    round(100.0 * pie_income_collected_by_month / nullif(pie_total_count, 0), 1) as pie_income_collection_rate_pct,

    -- INCREMENTAL: How many NEW income collections happened THIS month
    new_income_collections_this_month

from combined
order by statement_number, month_offset;

-- ============================================================================
-- EXPECTED OUTPUT:
--   Each row = one statement + one month offset (0-8)
--   Shows account-level metrics (each account counted once per statement)
--
-- INTERPRETATION:
--   - Stmt 18, 26, 34, 42: Unique accounts at each statement
--   - Overall Stmt 18+: Unique accounts across all statements 18+
--   - All using account-level deduplication methodology
-- ============================================================================
