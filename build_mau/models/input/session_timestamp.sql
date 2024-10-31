WITH session_data AS (
    SELECT
        sessionId,
        ts
    FROM {{ source('raw_data', 'session_timestamp') }}
    where sessionId is not null
)

-- Now you can query the CTE
SELECT * FROM session_data

