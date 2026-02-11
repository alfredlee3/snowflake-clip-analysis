-- Combined Success Rate: Immediate Approval OR Income Collection After PIE
-- Success = (Approved Outright + PIE with Income Collected) / (Total Approved + PIE)

with base_population as (
    -- All APPROVED or PRE_EVAL_APPROVED accounts, with PIE flag
    -- If an account has both PIE and APPROVED in the same month/statement, this keeps the PIE row. If only one outcome exists, it keeps that row.
    select
        date_trunc(month, stmt.statement_end_dt) as stmt_month,
        clip.account_id,
        clip.statement_number,
        clip.outcome,
        clip.evaluated_timestamp,
        acb.PERSON_ID,
        max(case when clip.outcome = 'PRE_EVAL_APPROVED' then 1 else 0 end) over (
            partition by clip.account_id, date_trunc(month, stmt.statement_end_dt), clip.statement_number
        ) as had_pie_in_month
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    join EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE acb
        on clip.account_id = acb.ACCOUNT_ID
    where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'
      and clip.outcome in ('APPROVED', 'PRE_EVAL_APPROVED')
      and clip.statement_number = 34
    qualify row_number() over (
        partition by clip.account_id, date_trunc(month, stmt.statement_end_dt), clip.statement_number
        order by case when clip.outcome = 'PRE_EVAL_APPROVED' then 0 else 1 end, acb.PERSON_ID
    ) = 1
),

income_collected as (
    -- Track first income update after PIE (within 8 months)
    -- Note that EFX income will disappear after one year so this analysis is only applicable for cohort in last year
    select
        base.account_id,
        base.statement_number,
        1 as has_income_update
    from base_population base
    join EDW_DB.PUBLIC.CLIP_USER_INCOMES inc
        on base.PERSON_ID = inc.PERSON_ID
    where base.had_pie_in_month = 1
      and inc.CREATED_AT > base.evaluated_timestamp
      and inc.CREATED_AT <= DATEADD(day, 240, base.evaluated_timestamp)
      and inc.annual_income IS NOT NULL
    qualify row_number() over (
        partition by base.account_id, base.statement_number
        order by inc.CREATED_AT
    ) = 1
)

select
    base.stmt_month,
    base.statement_number,
    count(distinct base.account_id) as total_population,

    -- Approved outright (never had PIE)
    count(distinct case when base.had_pie_in_month = 0 then base.account_id end) as approved_outright_count,

    -- PIE accounts
    count(distinct case when base.had_pie_in_month = 1 then base.account_id end) as pie_total_count,
    count(distinct case when base.had_pie_in_month = 1 and inc.has_income_update = 1 then base.account_id end) as pie_income_collected_count,
    count(distinct case when base.had_pie_in_month = 1 and inc.has_income_update is null then base.account_id end) as pie_income_not_collected_count,

    -- Overall success
    count(distinct case when base.had_pie_in_month = 0 or inc.has_income_update = 1 then base.account_id end) as success_count,

    -- Rates
    round(100.0 * count(distinct case when base.had_pie_in_month = 0 or inc.has_income_update = 1 then base.account_id end) / count(distinct base.account_id), 1) as success_rate_pct,
    round(100.0 * count(distinct case when base.had_pie_in_month = 0 then base.account_id end) / count(distinct base.account_id), 1) as approved_outright_rate_pct,
    round(100.0 * count(distinct case when base.had_pie_in_month = 1 and inc.has_income_update = 1 then base.account_id end) / nullif(count(distinct case when base.had_pie_in_month = 1 then base.account_id end), 0), 1) as pie_income_collection_rate_pct,
    round(100.0 * count(distinct case when base.had_pie_in_month = 1 and inc.has_income_update is null then base.account_id end) / nullif(count(distinct case when base.had_pie_in_month = 1 then base.account_id end), 0), 1) as pie_income_miss_rate_pct
from base_population base
left join income_collected inc
    on base.account_id = inc.account_id
    and base.statement_number = inc.statement_number
group by base.stmt_month, base.statement_number;
