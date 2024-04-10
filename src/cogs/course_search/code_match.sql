SELECT
    courses.dept AS dept,
    courses.code_num AS code_num,
    courses.title AS title,
    REGEXP_LIKE(CONCAT(courses.dept, ' ', courses.code_num), %s, 'i') AS code_match
FROM
    courses
HAVING
    code_match > 0
ORDER BY
    2 ASC, 3 ASC
LIMIT 5;