WITH session_data AS (
    SELECT
        sessionId,
        ts
    FROM dev.raw_data.session_timestamp
    where sessionId is not null
)

-- Now you can query the CTE
SELECT * FROM session_data