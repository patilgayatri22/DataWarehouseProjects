WITH user_session_data AS (
    SELECT
        userId,
        sessionId,
        channel
    FROM {{ source('raw_data', 'user_session_channel') }}
    where sessionid is not null
)

-- Now you can query the CTE
SELECT * FROM user_session_data

