
  create or replace   view dev.analytics.user_session_channel
  
   as (
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
  );

