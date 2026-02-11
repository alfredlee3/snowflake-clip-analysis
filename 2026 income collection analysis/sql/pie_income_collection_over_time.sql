-- ============================================================================
-- PIE Income Collection Over Time - Monthly Progression Analysis
-- ============================================================================
-- PURPOSE: Track how success rates evolve month-by-month over the 8-month
--          window after PIE evaluation
--
-- OUTPUT: For each statement cohort, show cumulative success rate at each
--         month (0-8) after the initial PIE evaluation
--
-- SIMILAR TO: pie_collection_cohort_visualization.png top-left chart
-- ============================================================================

with base_population as (
    -- ========================================================================
    -- BASE POPULATION: PIE accounts at specific statements in April 2025
    -- ========================================================================
    select
        date_trunc(month, stmt.statement_end_dt) as stmt_month,
        clip.account_id,
        clip.statement_number,
        clip.outcome,
        clip.evaluated_timestamp,
        acb.PERSON_ID,

        -- PIE Flag: 1 if this account had PIE at any point this month/statement
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
      and clip.statement_number in (18, 26, 34, 42)

    -- Deduplicate: prioritize PIE if account has both PIE and APPROVED
    qualify row_number() over (
        partition by clip.account_id, date_trunc(month, stmt.statement_end_dt), clip.statement_number
        order by case when clip.outcome = 'PRE_EVAL_APPROVED' then 0 else 1 end, acb.PERSON_ID
    ) = 1
),

income_by_month as (
    -- ========================================================================
    -- INCOME COLLECTION: Track WHEN income was collected (which month)
    -- ========================================================================
    select
        base.account_id,
        base.statement_number,
        base.had_pie_in_month,
        inc.CREATED_AT as income_collected_at,

        -- Calculate months elapsed from PIE evaluation to income collection
        datediff(month, base.evaluated_timestamp, inc.CREATED_AT) as months_to_collection

    from base_population base
    left join EDW_DB.PUBLIC.CLIP_USER_INCOMES inc
        on base.PERSON_ID = inc.PERSON_ID
        and base.had_pie_in_month = 1  -- Only track PIE accounts
        and inc.CREATED_AT > base.evaluated_timestamp  -- Income AFTER PIE event
        and inc.CREATED_AT <= DATEADD(day, 240, base.evaluated_timestamp)  -- Within 8 months
        and inc.annual_income IS NOT NULL

    -- Keep only FIRST income update per account/statement
    qualify row_number() over (
        partition by base.account_id, base.statement_number
        order by inc.CREATED_AT
    ) = 1
),

month_series as (
    -- Generate series 0-8 representing months after PIE evaluation
    select 0 as month_offset union all
    select 1 union all select 2 union all select 3 union all select 4 union all
    select 5 union all select 6 union all select 7 union all select 8
),

cumulative_success as (
    -- ========================================================================
    -- CUMULATIVE CALCULATION: At each month mark, count total successes
    -- ========================================================================
    select
        base.statement_number,
        m.month_offset,

        -- Total population
        count(distinct base.account_id) as total_population,

        -- Accounts that were approved outright (no PIE barrier)
        count(distinct case when base.had_pie_in_month = 0 then base.account_id end) as approved_outright_count,

        -- PIE accounts that collected income BY this month offset
        count(distinct case
            when base.had_pie_in_month = 1
            and inc.months_to_collection is not null
            and inc.months_to_collection <= m.month_offset
            then base.account_id
        end) as pie_income_collected_by_month,

        -- Total PIE accounts
        count(distinct case when base.had_pie_in_month = 1 then base.account_id end) as pie_total_count,

        -- SUCCESS COUNT: Approved Outright + PIE with Income Collected by this month
        count(distinct case
            when base.had_pie_in_month = 0  -- Approved outright
            or (base.had_pie_in_month = 1 and inc.months_to_collection is not null and inc.months_to_collection <= m.month_offset)  -- PIE + income collected
            then base.account_id
        end) as success_count

    from base_population base
    cross join month_series m
    left join income_by_month inc
        on base.account_id = inc.account_id
        and base.statement_number = inc.statement_number
    group by base.statement_number, m.month_offset
)

-- ============================================================================
-- FINAL OUTPUT: Monthly progression of success rates
-- ============================================================================
select
    statement_number,
    month_offset,
    total_population,
    approved_outright_count,
    pie_total_count,
    pie_income_collected_by_month,
    success_count,

    -- CUMULATIVE SUCCESS RATE at this month mark
    round(100.0 * success_count / total_population, 1) as success_rate_pct,

    -- CUMULATIVE PIE INCOME COLLECTION RATE at this month mark
    round(100.0 * pie_income_collected_by_month / nullif(pie_total_count, 0), 1) as pie_income_collection_rate_pct,

    -- INCREMENTAL: How many NEW income collections happened THIS month
    pie_income_collected_by_month - lag(pie_income_collected_by_month, 1, 0) over (
        partition by statement_number order by month_offset
    ) as new_income_collections_this_month

from cumulative_success
order by statement_number, month_offset;

-- ============================================================================
-- EXPECTED OUTPUT:
--   Each row = one statement + one month offset combination
--   Month 0 = initial evaluation month
--   Month 1-8 = subsequent months
--
-- INTERPRETATION:
--   - success_rate_pct shows cumulative success at each month mark
--   - pie_income_collection_rate_pct shows % of PIE accounts that collected by month N
--   - new_income_collections_this_month shows incremental progress
--   - Watch for plateau to identify when most income collection activity stops
-- ============================================================================
