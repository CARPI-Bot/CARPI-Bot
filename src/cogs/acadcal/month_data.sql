SELECT
    date_start,
    date_end,
    title
FROM
    acad_cal_events
WHERE
    (
        MONTH(date_start) = %s
        OR MONTH(date_end) = %s
    )
    AND (
        YEAR(date_start) = %s
        OR YEAR(date_end) = %s
    )
ORDER BY
    date_start;