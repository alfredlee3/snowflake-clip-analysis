-- Compare Statement 26 populations between your DBT model and my direct query

-- YOUR APPROACH: Grouped statements 26-33
with your_population_base as (
    select
        clip.account_id,
        clip.statement_number,
        stmt.statement_end_dt,
        clip.outcome,
        case
            when clip.statement_number between 26 and 33 then 26
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
      and clip.statement_number between 26 and 33
      and clip.outcome in ('APPROVED', 'PRE_EVAL_APPROVED')
    -- Only include accounts where first statement in this group = 26
    qualify min(statement_number) over (partition by account_id, original_statement_group) = 26
),

your_categorization as (
    select
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
    from your_population_base
),

your_final_counts as (
    select
        'Your DBT Logic' as method,
        capture_category,
        count(distinct account_id) as accounts
    from your_categorization
    where capture_category is not null
    group by 1, 2
),

-- MY APPROACH: Exact statement 26 only
my_population_base as (
    select
        clip.account_id,
        clip.statement_number,
        stmt.statement_end_dt,
        clip.outcome
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on clip.account_id = stmt.account_id
        and clip.statement_number = stmt.statement_num
    where date_trunc(month, stmt.statement_end_dt) = '2024-11-01'
      and clip.statement_number = 26  -- EXACT stmt 26
      and clip.outcome in ('APPROVED', 'PRE_EVAL_APPROVED')
),

my_final_counts as (
    select
        'My Direct Query' as method,
        case
            when outcome = 'APPROVED' then 'Initially Approved'
            when outcome = 'PRE_EVAL_APPROVED' then 'PIE Approved'
        end as capture_category,
        count(distinct account_id) as accounts
    from my_population_base
    group by 1, 2
)

-- Compare the populations
select * from your_final_counts
union all
select * from my_final_counts
order by method, capture_category;

-- Show the difference in statement distribution
select
    'Your Population (26-33 group, first=26)' as analysis,
    statement_number,
    count(distinct account_id) as accounts,
    round(100.0 * count(distinct account_id) / sum(count(distinct account_id)) over (), 1) as pct
from your_population_base
group by 2
order by 2;

-- Check: Are there accounts in your population NOT at exact stmt 26?
select
    'Accounts NOT at exact stmt 26' as category,
    count(distinct account_id) as accounts
from your_population_base
where statement_number != 26;

-- Most importantly: What's the total population size difference?
select
    'Your DBT Model' as source,
    count(distinct account_id) as total_accounts
from your_population_base

union all

select
    'My Direct Query' as source,
    count(distinct account_id) as total_accounts
from my_population_base;
