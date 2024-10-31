
  
    

        create or replace transient table dev.analytics.session_summary
         as
        (WITH  __dbt__cte__user_session_channel as (
WITH user_session_data AS (
    SELECT
        userId,
        sessionId,
        channel
    FROM dev.raw_data.user_session_channel
    where sessionid is not null
)

-- Now you can query the CTE
SELECT * FROM user_session_data
),  __dbt__cte__session_timestamp as (
WITH session_data AS (
    SELECT
        sessionId,
        ts
    FROM dev.raw_data.session_timestamp
    where sessionId is not null
)

-- Now you can query the CTE
SELECT * FROM session_data
), u AS (
    SELECT * FROM __dbt__cte__user_session_channel
), st AS (
    SELECT * FROM __dbt__cte__session_timestamp
)
SELECT u.userId, u.sessionId, u.channel, st.ts
FROM u
JOIN st ON u.sessionId = st.sessionId
        );
      
  