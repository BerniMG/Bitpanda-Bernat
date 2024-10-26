WITH ticket_times AS (
    -- Ensure each ticket has valid creation and resolution dates
    SELECT 
        ticket_id,
        COALESCE(MIN(CASE WHEN value_status = 'new' THEN created_at END), '2024-04-14 13:00:00') AS created_at,
        COALESCE(MAX(CASE WHEN value_status IN ('solved', 'closed') THEN created_at END), '2024-05-01 13:00:00') AS solved_closed_at
    FROM DATASET
    GROUP BY ticket_id
),
waiting_times AS (
    -- Calculate waiting time in 'new', 'open', and 'hold' states
    SELECT
        ticket_id,
        SUM((JULIANDAY(next_created_at) - JULIANDAY(created_at)) * 24 * 60) AS waiting_time_minutes
    FROM (
        SELECT 
            ticket_id,
            value_status,
            created_at,
            LEAD(created_at) OVER (PARTITION BY ticket_id ORDER BY created_at) AS next_created_at
        FROM DATASET
        WHERE value_status IN ('new', 'open', 'hold')
    ) AS state_changes
    GROUP BY ticket_id
),
first_reply_time AS (
    -- Calculate first reply time, ensuring different Updater_id
    SELECT
        t1.ticket_id,
        MIN((JULIANDAY(t2.created_at) - JULIANDAY(t1.created_at)) * 24 * 60) AS first_reply_time_minutes
    FROM DATASET t1
    LEFT JOIN DATASET t2
    ON t1.ticket_id = t2.ticket_id AND t1.created_at < t2.created_at
    WHERE t1.value_status = 'new' AND t1.Updater_id != t2.Updater_id
    GROUP BY t1.ticket_id
)
-- Calculate the averages by day of ticket resolution
SELECT
    DATE(tt.solved_closed_at) AS Solved_date,
    AVG((JULIANDAY(tt.solved_closed_at) - JULIANDAY(tt.created_at)) * 24 * 60) AS AVG_Total_time,
    AVG(wt.waiting_time_minutes) AS AVG_Waiting_time,
    AVG(frt.first_reply_time_minutes) AS AVG_FRT
FROM ticket_times tt
LEFT JOIN waiting_times wt ON tt.ticket_id = wt.ticket_id
LEFT JOIN first_reply_time frt ON tt.ticket_id = frt.ticket_id
WHERE (JULIANDAY(tt.solved_closed_at) - JULIANDAY(tt.created_at)) * 24 * 60 >= 60 -- Exclude tickets with total time less than 1 hour
GROUP BY Solved_date
ORDER BY Solved_date;
