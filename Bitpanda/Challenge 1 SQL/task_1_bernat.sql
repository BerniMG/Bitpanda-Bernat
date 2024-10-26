WITH backlog AS (
    SELECT
        DATE(CREATED_AT) AS day,                     -- Extract the date (day) from the timestamp
        strftime('%H', CREATED_AT) AS hour,          -- Extract the hour from the timestamp
        value_status                                 -- Current status of each ticket
    FROM DATASET
    WHERE created_at BETWEEN '2024-04-15 00:00:00' AND '2024-04-30 23:59:59'
        OR created_at < '2024-04-15 00:00:00'        -- Include tickets created before the extraction period
)
SELECT
    day || ' ' || hour || ':00:00' AS "Date",       -- Concatenate day and hour to create timestamp for output
    SUM(CASE WHEN value_status = 'open' THEN 1 ELSE 0 END) AS Tickets_Open,   -- Count tickets in 'open' status
    SUM(CASE WHEN value_status = 'new' THEN 1 ELSE 0 END) AS Tickets_New,     -- Count tickets in 'new' status
    SUM(CASE WHEN value_status IN ('open', 'new') THEN 1 ELSE 0 END) AS Total -- Count tickets in both 'open' and 'new' statuses
FROM backlog
WHERE hour IN ('00', '07')                          -- Filter for the hours 00:00 and 07:00 each day
GROUP BY day, hour                                  -- Group by day and hour for daily snapshots
ORDER BY "Date";                                   