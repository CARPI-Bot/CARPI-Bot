SELECT
    courses.dept,
    courses.code_num,
    courses.title,
    courses.desc_text,
    MIN(sections.credit_min) AS credit_min,
    MAX(sections.credit_max) AS credit_max,
    NULL AS prereqs,
    NULL AS coreqs,
    NULL AS crosslist,
    NULL AS restrictions,
    REGEXP_LIKE(CONCAT(courses.dept, " ", courses.code_num), %s, 'i') AS code_match,
    REGEXP_LIKE(courses.title, %s, 'i') AS title_match,
    REGEXP_LIKE(courses.title, %s, 'i') AS title_similar
FROM
    courses
    LEFT JOIN sections ON courses.dept = sections.dept AND courses.code_num = sections.code_num
    LEFT JOIN prerequisites ON sections.crn = prerequisites.crn
GROUP BY
    1, 2, 3, 4, 7, 8, 9, 10
HAVING
    title_match > 0
    OR title_similar > 0
    OR code_match > 0
ORDER BY
    `name` ASC, code_match DESC, title_match DESC, title_similar DESC
LIMIT 6;
