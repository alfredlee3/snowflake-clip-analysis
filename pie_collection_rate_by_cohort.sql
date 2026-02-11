-- PIE Collection Rate Analysis by Statement Cohort
-- Tracks how PIE (PRE_EVAL_APPROVED) accounts get collected within 8 statements

with driver1 as (
    -- Get initial population counts by cohort (specific statements)
    select
        date_trunc(month, statement_end_dt) as stmt_month,
        CASE
            WHEN clip.statement_number = 18 THEN 'Stmt 18'
            WHEN clip.statement_number = 26 THEN 'Stmt 26'
            WHEN clip.statement_number = 34 THEN 'Stmt 34'
            WHEN clip.statement_number = 42 THEN 'Stmt 42'
            WHEN clip.statement_number = 50 THEN 'Stmt 50'
        END as statement_cohort,
        count(distinct clip.account_id) as total_pop,
        sum(case when outcome = 'PRE_EVAL_APPROVED' then 1 else 0 end) as PRE_EVAL_APPROVED,
        sum(case when outcome = 'APPROVED' then 1 else 0 end) as APPROVED_INITIAL
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    where date_trunc(month, statement_end_dt) = '2024-11-01'
      and outcome in ('PRE_EVAL_APPROVED', 'APPROVED')
      and clip.statement_number IN (18, 26, 34, 42, 50)  -- Specific statements
    group by 1, 2
),

driver as (
    -- Track PRE_EVAL_APPROVED accounts and their next approval (specific statements)
    select
        date_trunc(month, statement_end_dt) as stmt_month,
        CASE
            WHEN pre_eval.statement_number = 18 THEN 'Stmt 18'
            WHEN pre_eval.statement_number = 26 THEN 'Stmt 26'
            WHEN pre_eval.statement_number = 34 THEN 'Stmt 34'
            WHEN pre_eval.statement_number = 42 THEN 'Stmt 42'
            WHEN pre_eval.statement_number = 50 THEN 'Stmt 50'
        END as statement_cohort,
        pre_eval.account_id,
        pre_eval.statement_number,
        pre_eval.outcome as pre_eval_outcome,
        pre_eval.evaluated_timestamp as pre_eval_timestamp,

        -- Next approval details
        next_eval_aprv.statement_number as next_eval_statement_number,
        next_eval_aprv.outcome as next_eval_aprv_outcome,
        next_eval_aprv.evaluated_timestamp as next_eval_aprv_evaluated_timestamp,
        next_eval_aprv.clip_amount as next_eval_aprv_clip_amount,
        next_eval_aprv.DECISION_DATA:assigned_line_increase as next_eval_aprv_assigned_line_increase,

        row_number() over (
            partition by pre_eval.account_id
            order by next_eval_aprv.evaluated_timestamp asc
        ) as row_num

    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval

    left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_aprv
        on pre_eval.account_id = next_eval_aprv.account_id
        and pre_eval.evaluated_timestamp < next_eval_aprv.evaluated_timestamp
        and pre_eval.statement_number + 8 >= next_eval_aprv.statement_number  -- Within 8 statements
        and next_eval_aprv.outcome = 'APPROVED'

    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = pre_eval.account_id
        and stmt.statement_num = pre_eval.statement_number

    where stmt.statement_end_dt between '2024-11-01' and '2024-11-30'
      and pre_eval.outcome = 'PRE_EVAL_APPROVED'
      and pre_eval.statement_number IN (18, 26, 34, 42, 50)  -- Specific statements
),

cal as (
    -- Calculate running collection totals by months since PRE_EVAL
    select
        stmt_month,
        statement_cohort,
        next_eval_statement_number - statement_number as months_since_pre_eval,
        sum(case when next_eval_aprv_outcome = 'APPROVED' then 1 else 0 end) as approval_count,
        SUM(approval_count) OVER (
            partition by stmt_month, statement_cohort
            ORDER BY months_since_pre_eval asc
        ) AS running_approval_count
    from driver
    group by 1, 2, 3
)

-- Final output with collection rate calculation
select
    a.stmt_month,
    a.statement_cohort,
    a.months_since_pre_eval,
    a.approval_count,
    a.running_approval_count,

    b.total_pop,
    b.PRE_EVAL_APPROVED,
    b.APPROVED_INITIAL,

    -- Accounts still not collected
    b.PRE_EVAL_APPROVED - a.running_approval_count as still_not_collected,

    -- Collection rate: (Initial Approved + Collected PIE) / (Initial Approved + Total PIE)
    ROUND(
        100.0 * (b.APPROVED_INITIAL + a.running_approval_count) /
        (b.APPROVED_INITIAL + b.PRE_EVAL_APPROVED),
        2
    ) as collection_rate_pct,

    -- PIE-only collection rate: How many PIE accounts got collected
    ROUND(
        100.0 * a.running_approval_count / NULLIF(b.PRE_EVAL_APPROVED, 0),
        2
    ) as pie_collection_rate_pct

from cal a
join driver1 b
    on a.stmt_month = b.stmt_month
    and a.statement_cohort = b.statement_cohort

order by 1, 2, 3;
