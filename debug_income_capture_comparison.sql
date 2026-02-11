-- Debug query to compare your DBT approach vs my direct approach
-- This will help identify where the discrepancies arise

with your_approach_base as (
    -- Replicate your grouping logic
    select
        clip.account_id,
        clip.statement_number,
        stmt.statement_end_dt,
        clip.outcome,
        case
            when clip.statement_number between 18 and 25 then 18
            when clip.statement_number between 26 and 33 then 26
            when clip.statement_number between 34 and 41 then 34
        end as original_statement_group,
        case
            when clip.outcome = 'APPROVED' then 'APPROVED'
            when clip.outcome = 'PRE_EVAL_APPROVED' then 'PIE-APPROVED'
        end as type_of_approval
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on clip.account_id = stmt.account_id
        and clip.statement_number = stmt.statement_num
    where date_trunc(month, stmt.statement_end_dt) = '2024-11-01'
      and clip.statement_number between 18 and 41
),

your_approach_metrics as (
    select
        original_statement_group,
        account_id,
        statement_number,
        type_of_approval,
        case
            when count_if(type_of_approval = 'APPROVED') over (
                partition by account_id, original_statement_group
                order by statement_number) > 0
                then 'Approved'
            when type_of_approval = 'PIE-APPROVED'
                then 'PIE Approved'
        end as capture_category
    from your_approach_base
    where original_statement_group is not null
    -- Only include if this is the first statement in the group for this account
    qualify min(statement_number) over (
        partition by account_id, original_statement_group
    ) = original_statement_group
),

my_approach_base as (
    -- My exact statement approach
    select
        clip.account_id,
        clip.statement_number,
        stmt.statement_end_dt,
        clip.outcome,
        clip.statement_number as exact_statement,
        case
            when clip.outcome = 'APPROVED' then 'APPROVED'
            when clip.outcome = 'PRE_EVAL_APPROVED' then 'PIE-APPROVED'
        end as type_of_approval
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on clip.account_id = stmt.account_id
        and clip.statement_number = stmt.statement_num
    where date_trunc(month, stmt.statement_end_dt) = '2024-11-01'
      and clip.statement_number IN (18, 26, 34)
),

my_approach_metrics as (
    select
        exact_statement as original_statement,
        account_id,
        statement_number,
        type_of_approval,
        case
            when type_of_approval = 'APPROVED' then 'Initially Approved'
            when type_of_approval = 'PIE-APPROVED' then 'PIE Approved'
        end as capture_category
    from my_approach_base
),

-- Compare populations
comparison as (
    select
        'Your Approach (Grouped)' as method,
        original_statement_group as statement,
        capture_category,
        count(distinct account_id) as accounts,
        count(*) as total_evaluations
    from your_approach_metrics
    where capture_category is not null
    group by 1, 2, 3

    union all

    select
        'My Approach (Exact)' as method,
        original_statement as statement,
        capture_category,
        count(distinct account_id) as accounts,
        count(*) as total_evaluations
    from my_approach_metrics
    where capture_category is not null
    group by 1, 2, 3
)

select * from comparison
order by statement, method, capture_category;

-- Show specific examples of accounts that differ
with your_stmt18 as (
    select distinct account_id, 'Your Approach' as source
    from your_approach_metrics
    where original_statement_group = 18
      and capture_category = 'PIE Approved'
),

my_stmt18 as (
    select distinct account_id, 'My Approach' as source
    from my_approach_metrics
    where original_statement = 18
      and capture_category = 'PIE Approved'
)

select
    'Only in Your Approach (stmt 18-25 group)' as category,
    count(*) as account_count
from your_stmt18
where account_id not in (select account_id from my_stmt18)

union all

select
    'Only in My Approach (stmt 18 exact)' as category,
    count(*) as account_count
from my_stmt18
where account_id not in (select account_id from your_stmt18)

union all

select
    'In Both Approaches' as category,
    count(*) as account_count
from your_stmt18
where account_id in (select account_id from my_stmt18);

-- Show breakdown by exact statement within your groups
select
    'Statement Distribution in "18" Group' as analysis,
    statement_number,
    count(distinct account_id) as accounts,
    sum(count(distinct account_id)) over () as total_in_group,
    round(100.0 * count(distinct account_id) / sum(count(distinct account_id)) over (), 1) as pct_of_group
from your_approach_metrics
where original_statement_group = 18
  and capture_category = 'PIE Approved'
group by 2
order by 2;
