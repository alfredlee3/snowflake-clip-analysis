use database SANDBOX_DB;
use schema user_tb;


--15563100.00
select outcome, sum(clip_amount)
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA
where outcome in ('PRE_EVAL_APPROVED', 'APPROVED')
and evaluated_timestamp between '2026-01-01' and '2026-01-31'
group by 1
;


-- with pre_eval_deduped as (
-- select
-- *,
-- row_number() over (partition by account_id order by evaluated_timestamp desc) as row_num
-- from EDW_DB.PUBLIC.CLIP_RESULTS_DATA
-- where outcome = 'PRE_EVAL_APPROVED'
-- and evaluated_timestamp between '2025-02-01' and '2026-01-31'
-- )
select
avg(pre_eval.clip_amount) as avg_pre_elig_clip,
avg(next_eval_aprv.clip_amount) as avg_act_clip,
sum(pre_eval.clip_amount) as pre_elig_clip,
sum(next_eval_aprv.clip_amount) as act_clip_aprv,
-- sum(case when next_eval_dcln.account_id is not null then pre_eval.clip_amount else 0 end) as act_clip_dcln,
count(pre_eval.account_id) as pre_elig_clip_num,
count(next_eval_aprv.account_id) as act_clip_num,
count(distinct pre_eval.account_id) as pre_elig_clip_dist_num,
count(distinct next_eval_aprv.account_id) as act_clip_dist_num,
act_clip_aprv / pre_elig_clip as curr_clip_exp_perc,
act_clip_num / pre_elig_clip_num as curr_clip_num_perc,
act_clip_dist_num / pre_elig_clip_dist_num as curr_clip_dist_num_perc
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_aprv
on pre_eval.account_id = next_eval_aprv.account_id
-- and pre_eval.statement_number = next_eval_aprv.statement_number
and pre_eval.evaluated_timestamp < next_eval_aprv.evaluated_timestamp
and next_eval_aprv.outcome = 'APPROVED'
-- left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_dcln
-- on pre_eval.account_id = next_eval_dcln.account_id
-- and pre_eval.statement_number = next_eval_dcln.statement_number
-- and pre_eval.evaluated_timestamp < next_eval_dcln.evaluated_timestamp
-- and next_eval_dcln.outcome in ('DECLINED','INELIGIBLE')
where pre_eval.evaluated_timestamp between '2025-03-01' and '2025-03-31'
qualify row_number() over (partition by pre_eval.account_id order by next_eval_aprv.evaluated_timestamp desc) = 1
;


-- APPROVED	26550150.00
-- PRE_EVAL_APPROVED	14276350.00
select outcome, sum(clip_amount), count(distinct account_id)
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA
where outcome in ('PRE_EVAL_APPROVED', 'APPROVED')
and evaluated_timestamp between '2024-11-01' and '2024-11-30'
and statement_number=18
group by 1
;

-- 30656750

with driver as (
select pre_eval.*,  next_eval_aprv.evaluated_timestamp as  next_eval_aprv_evaluated_timestamp
, next_eval_aprv.clip_amount as next_eval_aprv_clip_amount
, next_eval_aprv.DECISION_DATA:assigned_line_increase as next_eval_aprv_clip_amount_assigned_approved
, row_number() over (partition by pre_eval.account_id order by next_eval_aprv.evaluated_timestamp asc) as row_num
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_aprv
on pre_eval.account_id = next_eval_aprv.account_id
and pre_eval.evaluated_timestamp < next_eval_aprv.evaluated_timestamp
and pre_eval.statement_number + 8 >= next_eval_aprv.statement_number
and next_eval_aprv.outcome in ('APPROVED')
-- and next_eval_aprv.DECISION_DATA:post_pie_evaluation::BOOLEAN = TRUE
where pre_eval.evaluated_timestamp between '2025-03-01' and '2025-03-31'
and pre_eval.outcome = 'PRE_EVAL_APPROVED'
)
select left(next_eval_aprv_evaluated_timestamp,7) as eval_month
, sum(next_eval_aprv_clip_amount) as act_clip_aprv, sum(act_clip_aprv) over () as total_in_8_month
, sum(next_eval_aprv_clip_amount_assigned_approved) as act_clip_assigned_approved, sum(act_clip_assigned_approved) over () as total_in_8_month_assigned_approved
from driver
-- where row_num = 1
group by 1 order by 1
;

with driver as (
select pre_eval.*,  next_eval_aprv.evaluated_timestamp as  next_eval_aprv_evaluated_timestamp
, next_eval_aprv.DECISION_DATA:assigned_line_increase as next_eval_aprv_clip_amount_assigned
, row_number() over (partition by pre_eval.account_id order by next_eval_aprv.evaluated_timestamp desc) as row_num
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_aprv
on pre_eval.account_id = next_eval_aprv.account_id
-- and pre_eval.evaluated_timestamp < next_eval_aprv.evaluated_timestamp
and pre_eval.statement_number + 8 = next_eval_aprv.statement_number
and next_eval_aprv.outcome in ('PRE_EVAL_APPROVED')
-- and next_eval_aprv.DECISION_DATA:post_pie_evaluation::BOOLEAN = TRUE
where pre_eval.evaluated_timestamp between '2025-03-01' and '2025-03-31'
and pre_eval.outcome = 'PRE_EVAL_APPROVED'
)
select left(next_eval_aprv_evaluated_timestamp,7) as eval_month
, sum(next_eval_aprv_clip_amount_assigned) as act_clip_assigned_approved, sum(act_clip_assigned_approved) over () as total_in_8_month_assigned_approved
from driver
where row_num = 1
group by 1 order by 1
;




select sum(pre_eval.clip_amount) as pre_eval_clip_amount
, sum(next_eval.clip_amount) as next_eval_clip_amount
-- , row_number() over (partition by pre_eval.account_id order by next_eval_aprv.evaluated_timestamp desc) as row_num
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval
on pre_eval.account_id = next_eval.account_id
and pre_eval.statement_number + 8 = next_eval.statement_number
and next_eval.outcome in ('PRE_EVAL_APPROVED')
where pre_eval.evaluated_timestamp between '2025-03-01' and '2025-03-31'
and pre_eval.outcome = 'PRE_EVAL_APPROVED'
;

select sum(pre_eval.clip_amount) as pre_eval_clip_amount
, sum(next_eval.clip_amount) as next_eval_clip_amount
-- , row_number() over (partition by pre_eval.account_id order by next_eval_aprv.evaluated_timestamp desc) as row_num
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval
on pre_eval.account_id = next_eval.account_id
and pre_eval.statement_number + 8 = next_eval.statement_number
and pre_eval.evaluated_timestamp < next_eval_aprv.evaluated_timestamp
and next_eval.outcome in ('PRE_EVAL_APPROVED')
where pre_eval.evaluated_timestamp between '2025-03-01' and '2025-03-31'
and pre_eval.outcome = 'PRE_EVAL_APPROVED'
;

SELECT
    SUM(pre_eval.clip_amount) AS pre_eval_clip_amount
FROM EDW_DB.PUBLIC.CLIP_RESULTS_DATA AS pre_eval
WHERE
    -- 1. Look at March 2025 evaluations
    pre_eval.evaluated_timestamp BETWEEN '2025-03-01' AND '2025-03-31'
    AND pre_eval.outcome = 'PRE_EVAL_APPROVED'

    -- 2. Ensure the "Next 8 Months" condition is met
    AND EXISTS (
        SELECT 1
        FROM EDW_DB.PUBLIC.CLIP_RESULTS_DATA AS future
        WHERE future.account_id = pre_eval.account_id
        AND future.evaluated_timestamp > pre_eval.evaluated_timestamp
        AND future.statement_number <= pre_eval.statement_number + 8
        HAVING
            COUNT(CASE WHEN outcome = 'PRE_EVAL_APPROVED' THEN 1 END) >= 1
            AND COUNT(CASE WHEN outcome = 'APPROVED' THEN 1 END) = 0
    );

SELECT SUM(clip_to_sum) AS total_pre_eval_clip_amount
FROM (
    SELECT
        pre_eval.clip_amount AS clip_to_sum
    FROM EDW_DB.PUBLIC.CLIP_RESULTS_DATA AS pre_eval
    LEFT JOIN EDW_DB.PUBLIC.CLIP_RESULTS_DATA AS next_eval
        ON pre_eval.account_id = next_eval.account_id
        -- Looking forward from the March timestamp up to 8 months later
        AND next_eval.evaluated_timestamp > pre_eval.evaluated_timestamp
        AND next_eval.evaluated_timestamp <= ADD_MONTHS(pre_eval.evaluated_timestamp, 8)
    WHERE pre_eval.evaluated_timestamp BETWEEN '2025-03-01' AND '2025-03-31'
        AND pre_eval.outcome = 'PRE_EVAL_APPROVED'
    GROUP BY
        pre_eval.account_id,
        pre_eval.evaluated_timestamp,
        pre_eval.clip_amount
    -- The "At least one PRE_EVAL but NEVER an APPROVED" logic
    HAVING COUNT(CASE WHEN next_eval.outcome = 'PRE_EVAL_APPROVED' THEN 1 END) >= 1
       AND COUNT(CASE WHEN next_eval.outcome = 'APPROVED' THEN 1 END) = 0
);

select left(next_eval_aprv_evaluated_timestamp,7) as eval_month
, sum(next_eval_aprv_clip_amount_assigned) as act_clip_assigned_approved, sum(act_clip_assigned_approved) over () as total_in_8_month_assigned_approved
from driver
where row_num = 1
group by 1 order by 1
;


use database EDW_DB;
use schema PUBLIC;

with pre_eval_deduped as (
select
*,
row_number() over (partition by account_id order by evaluated_timestamp desc) as row_num
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA
where outcome = 'PRE_EVAL_APPROVED'
and evaluated_timestamp between '2025-05-01' and '2025-12-31'
)
select
avg(pre_eval.clip_amount) as avg_pre_elig_clip,
avg(next_eval_aprv.clip_amount) as avg_act_clip,
sum(pre_eval.clip_amount) as pre_elig_clip,
sum(next_eval_aprv.clip_amount) as act_clip_aprv,
sum(case when next_eval_dcln.account_id is not null then pre_eval.clip_amount else 0 end) as act_clip_dcln,
count(pre_eval.account_id) as pre_elig_clip_num,
count(next_eval_aprv.account_id) as act_clip_aprv_num,
count(next_eval_dcln.account_id) as act_clip_dcln_num,
act_clip_aprv / pre_elig_clip as curr_clip_exp_perc,
act_clip_aprv_num / pre_elig_clip_num as curr_clip_num_perc
from pre_eval_deduped as pre_eval
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_aprv
on pre_eval.account_id = next_eval_aprv.account_id
and pre_eval.statement_number = next_eval_aprv.statement_number
and pre_eval.evaluated_timestamp < next_eval_aprv.evaluated_timestamp
and next_eval_aprv.outcome = 'APPROVED'
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_dcln
on pre_eval.account_id = next_eval_dcln.account_id
and pre_eval.statement_number = next_eval_dcln.statement_number
and pre_eval.evaluated_timestamp < next_eval_dcln.evaluated_timestamp
and next_eval_dcln.outcome in ('DECLINED','INELIGIBLE')
where pre_eval.row_num = 1
;





----dashboard


-- 245
with pies as (
    select
        stmt.account_id
    from EDW_DB.PUBLIC.account_statements stmt
             join EDW_DB.PUBLIC.clip_results_data clip
                  on stmt.account_id = clip.account_id
                      and stmt.statement_num = clip.statement_number
                      and clip.outcome = 'PRE_EVAL_APPROVED'
    where statement_num = 18
      -- and date_trunc(month, statement_end_dt) = '2024-11-1'
     -- and evaluated_timestamp between '2024-11-01' and '2024-11-30'
)
select clip.id is not null as had_real_evaluation,
       count(*) as cnt
from pies
    left join EDW_DB.PUBLIC.clip_results_data clip
        on clip.account_id = pies.account_id
        and clip.statement_number = 18
        and not clip.pre_evaluation
group by all
;

--1950
select count(distinct clip.account_id)
from EDW_DB.PUBLIC.account_statements stmt
    join EDW_DB.PUBLIC.clip_results_data clip
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
        and clip.outcome = 'APPROVED'
where statement_num = 18
and date_trunc(month, statement_end_dt) = '2024-11-1';


desc table EDW_DB.PUBLIC.CLIP_RESULTS_DATA;

select count(distinct account_id)
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
where pre_eval.evaluated_timestamp between '2024-11-01' and '2024-11-30'
and pre_eval.outcome = 'PRE_EVAL_APPROVED'
and pre_eval.statement_number=18
;


---there are two options, 1) count PRE_EVAL_APPROVED but not APPROVED as opportunity. 2) count PRE_EVAL_APPROVED but not evaluated (regardless of results) as opportunity.
---technically, 1) is more correct since if we had their income, we would've passed them in the first place but one may argue we don't want the opportunity from those who quickly becomes ineligbile
----single stmt at 18
with driver1 as (
select date_trunc(month, statement_end_dt) as stmt_month
, count(distinct clip.account_id) as total_pop
, sum(case when outcome in ('PRE_EVAL_APPROVED') then 1 else 0 end) as PRE_EVAL_APPROVED
, sum(case when outcome in ('APPROVED') then 1 else 0 end) as TOAL_APPROVED
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
join EDW_DB.PUBLIC.account_statements stmt
on  stmt.account_id = clip.account_id
and stmt.statement_num = clip.statement_number
where date_trunc(month, statement_end_dt) = '2024-10-1'
and outcome in ('PRE_EVAL_APPROVED','APPROVED')
and statement_number between 34 and 34
group by 1
)
, driver as (
select date_trunc(month, statement_end_dt) as stmt_month
, pre_eval.*
, next_eval_aprv.statement_number as next_eval_statement_number
, next_eval_aprv.outcome as next_eval_aprv_outcome
, next_eval_aprv.evaluated_timestamp as  next_eval_aprv_evaluated_timestamp
, next_eval_aprv.clip_amount as next_eval_aprv_clip_amount
, next_eval_aprv.DECISION_DATA:assigned_line_increase as next_eval_aprv_clip_amount_assigned_approved
, row_number() over (partition by pre_eval.account_id order by next_eval_aprv.evaluated_timestamp asc) as row_num
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval

left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as next_eval_aprv
on pre_eval.account_id = next_eval_aprv.account_id
and pre_eval.evaluated_timestamp < next_eval_aprv.evaluated_timestamp
-- and pre_eval.statement_number <= next_eval_aprv.statement_number
and pre_eval.statement_number + 8 > next_eval_aprv.statement_number
and next_eval_aprv.outcome in ('APPROVED')
-- and next_eval_aprv.DECISION_DATA:post_pie_evaluation::BOOLEAN = TRUE

join EDW_DB.PUBLIC.account_statements stmt
on  stmt.account_id = pre_eval.account_id
and stmt.statement_num = pre_eval.statement_number

where stmt.statement_end_dt between '2024-10-01' and '2024-10-31'
and pre_eval.outcome = 'PRE_EVAL_APPROVED'
and pre_eval.statement_number between 34 and 34
)
, cal as (
select stmt_month, next_eval_statement_number- statement_number as month_since_pre_eval
, sum(case when next_eval_aprv_outcome = 'APPROVED' then 1 else 0 end) as approval_count
, SUM(approval_count) OVER (partition by stmt_month ORDER BY month_since_pre_eval asc) AS running_approval_count_total
from driver a
group by 1,2
)
select a.*, b.total_pop, b.PRE_EVAL_APPROVED, b.TOAL_APPROVED
, b.PRE_EVAL_APPROVED-running_approval_count_total as missed_opportunity
, b.TOAL_APPROVED+missed_opportunity as total_approved_plus_missed_opportunity
, 1-missed_opportunity/total_pop as collection_rate
from cal a
join driver1 b
on a.stmt_month =b.stmt_month
order by 1,2
;

select * from datamart_db.tableau.rpt_clip_income_capture where original_statement_month='2024-11-01' and original_statement =26 order by statement_post_pie_eligibility;

select * from
EDW_DB.PUBLIC.CLIP_RESULTS_DATA as pre_eval
where pre_eval.evaluated_timestamp between '2025-03-01' and '2025-03-31'
and pre_eval.outcome = 'PRE_EVAL_APPROVED' limit 100;


with denominator as (
select date_trunc(month, statement_end_dt) as stmt_month, statement_number, count(distinct clip.account_id) as total_approved_or_PIE_count
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
join EDW_DB.PUBLIC.account_statements stmt
on  stmt.account_id = clip.account_id
and stmt.statement_num = clip.statement_number
where date_trunc(month, statement_end_dt) = '2025-04-01'
and outcome in ('APPROVED', 'PRE_EVAL_APPROVED')
and statement_number between 34 and 34
group by 1,2
)
, driver1 as (
select date_trunc(month, statement_end_dt) as stmt_month, clip.*
from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
join EDW_DB.PUBLIC.account_statements stmt
on  stmt.account_id = clip.account_id
and stmt.statement_num = clip.statement_number
where date_trunc(month, statement_end_dt) = '2025-04-01'
and outcome in ('PRE_EVAL_APPROVED')
and statement_number between 34 and 34
-- and clip.account_id in (10001573433, 10001575474)
)
, result_next_8_stmt as (
select stmt_month, a.account_id, a.statement_number as orig_statement_number, a.outcome as orig_outcome
, b.statement_number, b.outcome
from driver1  a
left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as b
on a.account_id = b.account_id
and a.evaluated_timestamp < b.evaluated_timestamp
and a.statement_number + 8 > b.statement_number
order by 1,2, b.statement_number
)
, summarize_counts as (
select stmt_month, account_id, orig_statement_number, count(distinct account_id) as pre_approved_count
, sum(case when outcome = 'APPROVED' then 1 else 0 end) as approved_acount
, sum(case when outcome in ('INELIGIBLE', 'DECLINED') then 1 else 0 end) as declined_count
from result_next_8_stmt
group by 1,2,3
), total_approved_post_pie as (
select stmt_month, orig_statement_number, sum(pre_approved_count) as pre_approved_count
, sum(approved_acount) as approved_count, sum(case when approved_acount+declined_count>0 then 1 else 0 end) as evaluated_again_count
from summarize_counts
group by 1,2
)
select a.*, b.total_approved_or_PIE_count
, pre_approved_count-approved_count as missed_opportunity
-- , b.total_approved_count+missed_opportunity as total_approved_plus_missed_opportunity
, 1-missed_opportunity/total_approved_or_PIE_count as collection_rate

from total_approved_post_pie a
join denominator b
on a.stmt_month = b.stmt_month and a.orig_statement_number = b.statement_number
;


--- get income flag for every statment (limit to 2024 Nov+ to speed up.

SET EVAL_START_DATE = '2024-11-01';
SET EVAL_END_DATE = '2025-12-31';

CREATE OR REPLACE TEMPORARY TABLE INCOME_VALIDATION AS (
WITH StatementAccounts AS (
    SELECT
        dm.statement_number AS STATEMENT_NUMBER,
        dm.statement_end_dt AS STATEMENT_END_DATE,
        acb.PERSON_ID,
        dm.account_id
    FROM datamart_db.dm_consolidated.account_statements_clip dm
    INNER JOIN EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE AS acb
        ON dm.account_id = acb.ACCOUNT_ID
    WHERE dm.statement_end_dt BETWEEN $EVAL_START_DATE AND $EVAL_END_DATE
        AND dm.statement_number >= 18  -- Year 2+ only
        AND dm.open_in_statement = 1
        -- and dm.account_id= '10000356348'
),
PersonLatestValidIncome AS (
    SELECT
        sa.STATEMENT_NUMBER,
        sa.STATEMENT_END_DATE,
        sa.PERSON_ID,
        sa.account_id,
        inc.CREATED_AT,
        -- We rank only after filtering for the 1-year window
        ROW_NUMBER() OVER (
            PARTITION BY sa.account_id, sa.STATEMENT_NUMBER
            ORDER BY inc.CREATED_AT DESC
        ) AS rn
    FROM StatementAccounts AS sa
    INNER JOIN EDW_DB.PUBLIC.CLIP_USER_INCOMES AS inc
        ON sa.PERSON_ID = inc.PERSON_ID
    WHERE inc.CREATED_AT <= sa.STATEMENT_END_DATE
      -- CRITICAL FIX: Only include income created within 365 days of the statement
      AND inc.CREATED_AT >= DATEADD(year, -1, sa.STATEMENT_END_DATE)
      -- Ensure we aren't pulling records where income was explicitly nulled/missing
      AND inc.annual_income IS NOT NULL
)
SELECT
    sa.STATEMENT_NUMBER,
    sa.STATEMENT_END_DATE,
    sa.PERSON_ID,
    sa.account_id,
    plvi.CREATED_AT AS INCOME_CREATED_AT,
    CASE
        WHEN plvi.CREATED_AT IS NOT NULL THEN 'Valid Income'
        ELSE 'No Valid Income Found'
    END AS INCOME_STATUS
FROM StatementAccounts sa
LEFT JOIN PersonLatestValidIncome plvi
    ON sa.account_id = plvi.account_id
    AND sa.STATEMENT_NUMBER = plvi.STATEMENT_NUMBER
    AND plvi.rn = 1
);


with denominator as (
    select
        date_trunc(month, statement_end_dt) as stmt_month,
        statement_number,
        count(distinct clip.account_id) as total_approved_or_PIE_count
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    where date_trunc(month, statement_end_dt) = '2025-04-01'
      and outcome in ('APPROVED', 'PRE_EVAL_APPROVED')
      and statement_number between 34 and 34
    group by 1, 2
),

driver1 as (
    select
        date_trunc(month, statement_end_dt) as stmt_month,
        clip.*,
        stmt.statement_end_dt,
        acb.PERSON_ID  -- Add PERSON_ID for income tracking
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    -- Join to get PERSON_ID
    INNER JOIN EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE AS acb
        ON clip.account_id = acb.ACCOUNT_ID
    where date_trunc(month, statement_end_dt) = '2025-04-01'
      and outcome in ('PRE_EVAL_APPROVED')
      and statement_number between 34 and 34
),

-- Track next CLIP outcomes (original logic)
result_next_8_stmt as (
    select
        a.stmt_month,
        a.account_id,
        a.statement_number as orig_statement_number,
        a.outcome as orig_outcome,
        a.evaluated_timestamp as orig_evaluated_timestamp,
        a.statement_end_dt as orig_statement_end_dt,
        a.PERSON_ID,
        b.statement_number,
        b.outcome,
        b.evaluated_timestamp as next_evaluated_timestamp
    from driver1 a
    left join EDW_DB.PUBLIC.CLIP_RESULTS_DATA as b
        on a.account_id = b.account_id
        and a.evaluated_timestamp < b.evaluated_timestamp
        and a.statement_number + 8 > b.statement_number
    order by 1, 2, b.statement_number
),

-- NEW: Track income updates after PRE_EVAL_APPROVED within 8 months
--Note that EFX income is deleted after 1-year so can only do this analysis with cohort within last 1 year
income_updates_after_pie as (
    select
        r.account_id,
        r.orig_statement_number,
        r.PERSON_ID,
        r.orig_evaluated_timestamp,
        inc.CREATED_AT as income_update_timestamp,
        -- Rank income updates by recency
        ROW_NUMBER() OVER (
            PARTITION BY r.account_id, r.orig_statement_number
            ORDER BY inc.CREATED_AT ASC  -- Get FIRST income update after PIE
        ) AS income_update_rank
    from (select distinct account_id, orig_statement_number, PERSON_ID, orig_evaluated_timestamp
          from result_next_8_stmt) r
    INNER JOIN EDW_DB.PUBLIC.CLIP_USER_INCOMES AS inc
        ON r.PERSON_ID = inc.PERSON_ID
    -- CRITICAL: Income must be updated AFTER the PRE_EVAL_APPROVED event
    WHERE inc.CREATED_AT > r.orig_evaluated_timestamp
      -- Income must be within 8 months (approximate with 8*30 days)
      AND inc.CREATED_AT <= DATEADD(day, 240, r.orig_evaluated_timestamp)
      AND inc.annual_income IS NOT NULL
),

summarize_counts as (
    select
        r.stmt_month,
        r.account_id,
        r.orig_statement_number,
        r.PERSON_ID,
        count(distinct r.account_id) as pre_approved_count,
        sum(case when r.outcome = 'APPROVED' then 1 else 0 end) as approved_count,
        sum(case when r.outcome in ('INELIGIBLE', 'DECLINED') then 1 else 0 end) as declined_count,
        -- NEW: Track income updates
        max(case when inc.income_update_rank = 1 then 1 else 0 end) as income_updated,
        min(inc.income_update_timestamp) as first_income_update_date
    from result_next_8_stmt r
    left join income_updates_after_pie inc
        on r.account_id = inc.account_id
        and r.orig_statement_number = inc.orig_statement_number
        and inc.income_update_rank = 1  -- Only first income update
    group by 1, 2, 3, 4
),

total_approved_post_pie as (
    select
        stmt_month,
        orig_statement_number,
        sum(pre_approved_count) as pre_approved_count,
        sum(approved_count) as approved_count,
        sum(case when approved_count + declined_count > 0 then 1 else 0 end) as evaluated_again_count,
        -- NEW: Income update metrics
        sum(income_updated) as income_updated_count,
        sum(case when income_updated = 1 and approved_count > 0 then 1 else 0 end) as income_updated_and_approved,
        sum(case when income_updated = 1 and approved_count = 0 then 1 else 0 end) as income_updated_but_not_approved,
        sum(case when income_updated = 0 and approved_count > 0 then 1 else 0 end) as approved_without_income_update
    from summarize_counts
    group by 1, 2
)

select
    a.*,
    b.total_approved_or_PIE_count,
    pre_approved_count - approved_count as missed_opportunity,
    1 - (pre_approved_count - approved_count) / b.total_approved_or_PIE_count as collection_rate,

    -- NEW: Income update metrics
    income_updated_count / pre_approved_count as income_update_rate,
    income_updated_and_approved / pre_approved_count as income_updated_then_approved_rate,
    income_updated_but_not_approved / pre_approved_count as income_updated_but_declined_rate,
    approved_without_income_update / pre_approved_count as approved_no_income_update_rate,

    -- Sanity check: approved should equal (income_updated_and_approved + approved_without_income_update)
    approved_count as total_approved,
    income_updated_and_approved + approved_without_income_update as income_breakdown_check
from total_approved_post_pie a
join denominator b
    on a.stmt_month = b.stmt_month
    and a.orig_statement_number = b.statement_number;

----------------------------------------
-------Overall Success Rate------------
----------------------------------------
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
      -- and clip.statement_number in (18, 26, 34, 42)  -- Key statement milestones
      and clip.statement_number>=18
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
    base.stmt_month,

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
group by all
order by all;



----------------------------------------
-------PIE Email collection rate------------
----------------------------------------


with pie_accounts as (
    select
        date_trunc(month, statement_end_dt) as stmt_month,
        clip.*,
        stmt.statement_end_dt,
        acb.PERSON_ID  -- Add PERSON_ID for income tracking
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    -- Join to get PERSON_ID
    INNER JOIN EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE AS acb
        ON clip.account_id = acb.ACCOUNT_ID
    where date_trunc(month, statement_end_dt) = '2025-04-01'
      and outcome in ('PRE_EVAL_APPROVED')
      -- and statement_number >= 18 --between 34 and 34
      and statement_number =26
), income_updates_after_pie as (
    -- Track income updates for PIE accounts
    select
        pie.account_id,
        pie.statement_number,
        pie.PERSON_ID,
        pie.evaluated_timestamp as pie_timestamp,
        inc.CREATED_AT as income_update_timestamp,
        inc.annual_income,
        ROW_NUMBER() OVER (
            PARTITION BY pie.account_id, pie.statement_number
            ORDER BY inc.CREATED_AT ASC
        ) AS income_update_rank
    from pie_accounts pie
    INNER JOIN EDW_DB.PUBLIC.CLIP_USER_INCOMES AS inc
        ON pie.PERSON_ID = inc.PERSON_ID
    WHERE inc.CREATED_AT > pie.evaluated_timestamp
      AND inc.CREATED_AT <= DATEADD(day, 30, pie.evaluated_timestamp)
      AND inc.annual_income IS NOT NULL
), driver_w_income as (
select a.*, inc.income_update_rank
    from pie_accounts a
    left join income_updates_after_pie inc
        on a.account_id = inc.account_id
        and a.statement_number = inc.statement_number
        and inc.income_update_rank = 1
    -- group by a.account_id, a.stmt_month, a.statement_number, a.outcome  --, a.had_pie_in_month
)
select stmt_month  --, statement_number
, count(distinct account_id) as total_pie_accounts, sum(income_update_rank) as collected_in_8_month, collected_in_8_month/total_pie_accounts as collection_rate
from driver_w_income
group by all;

desc table EDW_DB.PUBLIC.CLIP_RESULTS_DATA;

----------------------------
-------profiling------------
----------------------------

with base_population as (
    -- All APPROVED or PRE_EVAL_APPROVED accounts across multiple statements
    select
        date_trunc(month, stmt.statement_end_dt) as stmt_month,
        clip.account_id,
        clip.statement_number,
        clip.outcome,
        clip.evaluated_timestamp,
        clip.clip_risk_group,
        clip.util_group,
        clip.PRE_CLIP_LINE_LIMIT,
        clip.clip_amount,
        clip.decision_data:average_purchase_utilization_3_months as average_purchase_utilization_3_months,
        clip.decision_data:average_utilization_3_months as average_utilization_3_months,
        clip.decision_data:number_bankcard_trades_bc01s as number_bankcard_trades_bc01s,
        clip.decision_data:total_revolving_debt_re33s as total_revolving_debt_re33s,
        clip.decision_data:fico_08 as fico_08,
        clip.decision_data:vantage_30 as vantage_30,
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
      and clip.statement_number >=18 --between 19 and 26
    qualify row_number() over (
        partition by clip.account_id, date_trunc(month, stmt.statement_end_dt), clip.statement_number
        order by case when clip.outcome = 'PRE_EVAL_APPROVED' then 0 else 1 end, acb.PERSON_ID
    ) = 1
),

income_collected as (
    -- Track first income update after PIE (within 8 months)
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
, pie_category as (
select
    base.*,
    case when base.had_pie_in_month = 0 then 'approved_outright'
         when base.had_pie_in_month = 1 and inc.has_income_update = 1 then 'pie_income_collected'
         when base.had_pie_in_month = 1 and inc.has_income_update is null then 'pie_income_not_collected'
         ELSE 'TO BE INVESTIGAED' end category,

from base_population base
left join income_collected inc
    on base.account_id = inc.account_id
    and base.statement_number = inc.statement_number
)
select category, avg(clip_risk_group) as avg_RG, avg(util_group) as avg_UG, avg(PRE_CLIP_LINE_LIMIT) as avg_PCL
, avg(clip_amount) as avg_clip_amount
, avg(average_purchase_utilization_3_months)
, avg(average_utilization_3_months)
, avg(number_bankcard_trades_bc01s)
, avg(total_revolving_debt_re33s)
, avg(fico_08)
, avg(vantage_30)
from pie_category
group by all
order by all;


with pie_accounts as (
    select
        date_trunc(month, statement_end_dt) as stmt_month,
        clip.*,
        stmt.statement_end_dt,
        acb.PERSON_ID  -- Add PERSON_ID for income tracking
    from EDW_DB.PUBLIC.CLIP_RESULTS_DATA clip
    join EDW_DB.PUBLIC.account_statements stmt
        on stmt.account_id = clip.account_id
        and stmt.statement_num = clip.statement_number
    -- Join to get PERSON_ID
    INNER JOIN EDW_DB.PUBLIC.ACCOUNTS_CUSTOMERS_BRIDGE AS acb
        ON clip.account_id = acb.ACCOUNT_ID
    where date_trunc(month, statement_end_dt) = '2025-04-01'
      and outcome in ('PRE_EVAL_APPROVED')
      -- and statement_number between 34 and 34
      and statement_number>=18
), income_updates_after_pie as (
    -- Track income updates for PIE accounts
    select
        pie.account_id,
        pie.statement_number,
        pie.PERSON_ID,
        pie.evaluated_timestamp as pie_timestamp,
        inc.CREATED_AT as income_update_timestamp,
        inc.annual_income,
        ROW_NUMBER() OVER (
            PARTITION BY pie.account_id, pie.statement_number
            ORDER BY inc.CREATED_AT ASC
        ) AS income_update_rank
    from pie_accounts pie
    INNER JOIN EDW_DB.PUBLIC.CLIP_USER_INCOMES AS inc
        ON pie.PERSON_ID = inc.PERSON_ID
    WHERE inc.CREATED_AT >= pie.evaluated_timestamp
      AND inc.CREATED_AT <= DATEADD(day, 240, pie.evaluated_timestamp)
      AND inc.annual_income IS NOT NULL
), driver_w_income as (
select a.*, inc.income_update_rank
    from pie_accounts a
    left join income_updates_after_pie inc
        on a.account_id = inc.account_id
        and a.statement_number = inc.statement_number
        and inc.income_update_rank = 1
    -- group by a.account_id, a.stmt_month, a.statement_number, a.outcome  --, a.had_pie_in_month
)
select stmt_month--, statement_number
, count(distinct account_id) as total_pie_accounts, sum(income_update_rank) as collected_in_8_month
, total_pie_accounts-collected_in_8_month as not_collected_in_8_month
, collected_in_8_month/total_pie_accounts as collection_rate
from driver_w_income
group by all
order by all;


select distinct channel from  EDW_DB.PUBLIC.CLIP_USER_INCOMES ;


select channel, left(created_at,7), count(*) from  EDW_DB.PUBLIC.CLIP_USER_INCOMES
where channel ='equifax'
and annual_income is not null  -- toggle this
group by 1,2 order by 1,2;

select * from EDW_DB.PUBLIC.CLIP_RESULTS_DATA  limit 100;



-- ============================================================================
-- PIE Income Collection Over Time - ACCOUNT-LEVEL Analysis
-- ============================================================================
-- PURPOSE: Track how success rates evolve month-by-month over the 8-month
--          window, counting each ACCOUNT only once (not per statement)
--
-- KEY DIFFERENCE: If an account has PIE at multiple statements, count it
--                 once. If it collects income for any statement, count as success.
--
-- TIME WINDOWS: Uses 30-day rolling windows (not calendar months)
--   - Month 0: 0-30 days after PIE
--   - Month 1: 31-60 days after PIE
--   - Month 2: 61-90 days after PIE
--   - ... up to Month 8: 211-240 days after PIE
-- ============================================================================

with base_population as (
    -- ========================================================================
    -- BASE POPULATION: Get PIE accounts, deduplicated at account level
    -- ========================================================================
    select
        clip.account_id,
        min(clip.evaluated_timestamp) as earliest_pie_timestamp,  -- Use earliest PIE
        min(clip.statement_number) as first_pie_statement,
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

income_by_month as (
    -- ========================================================================
    -- INCOME COLLECTION: Track WHEN income was collected (30-day rolling window)
    -- ========================================================================
    select
        base.account_id,
        inc.CREATED_AT as income_collected_at,
        datediff(day, base.earliest_pie_timestamp, inc.CREATED_AT) as days_to_collection,
        -- 30-day rolling windows: 0-30=Month 0, 31-60=Month 1, etc.
        floor(datediff(day, base.earliest_pie_timestamp, inc.CREATED_AT) / 30) as months_to_collection

    from base_population base
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
    -- Generate series 0-8 representing months after PIE evaluation
    select 0 as month_offset union all
    select 1 union all select 2 union all select 3 union all select 4 union all
    select 5 union all select 6 union all select 7 union all select 8
),

cumulative_success as (
    -- ========================================================================
    -- CUMULATIVE CALCULATION: At each month mark, count total successes
    -- (ACCOUNT-LEVEL: each account counted once)
    -- ========================================================================
    select
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

    from base_population base
    cross join month_series m
    left join income_by_month inc
        on base.account_id = inc.account_id
    group by m.month_offset
)

-- ============================================================================
-- FINAL OUTPUT: Monthly progression (account-level)
-- ============================================================================
select
    month_offset+1 as post_pie_month,
    pie_total_count,
    pie_income_collected_by_month,

    -- CUMULATIVE PIE INCOME COLLECTION RATE at this month mark
    round(100.0 * pie_income_collected_by_month / nullif(pie_total_count, 0), 1) as pie_income_collection_rate_pct,

    -- INCREMENTAL: How many NEW income collections happened THIS month
    new_income_collections_this_month

from cumulative_success
where month_offset<=7
order by month_offset;

-- ============================================================================
-- EXPECTED OUTPUT:
--   Each row = one month offset (0-8)
--   Shows account-level metrics (each account counted once)
--
-- INTERPRETATION:
--   - pie_total_count: Unique accounts with PIE (constant across all months)
--   - pie_income_collected_by_month: Cumulative accounts that collected by month N
--   - pie_income_collection_rate_pct: % of PIE accounts that collected by month N
-- ============================================================================
