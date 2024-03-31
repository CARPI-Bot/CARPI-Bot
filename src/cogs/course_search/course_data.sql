SELECT
    courses.dept AS dept,
    courses.code_num AS code_num,
    courses.title AS title,
    courses.desc_text AS desc_text,
    MIN(sections.credit_min) AS credit_min,
    MAX(sections.credit_max) AS credit_max,
    GROUP_CONCAT(DISTINCT prerequisites.prereqs) AS prereqs,
    GROUP_CONCAT(DISTINCT prerequisites.coreqs) AS coreqs,
    GROUP_CONCAT(DISTINCT prerequisites.cross_list) AS cross_list,
    GROUP_CONCAT(DISTINCT prerequisites.restr_major) AS restrictions,
    REGEXP_LIKE(CONCAT(courses.dept, ' ', courses.code_num), %s, 'i') AS code_match,
    REGEXP_LIKE(courses.title, %s, 'i') AS title_exact_match,
    REGEXP_LIKE(courses.title, %s, 'i') AS title_start_match,
    REGEXP_LIKE(courses.title, %s, 'i') AS title_match,
    REGEXP_LIKE(courses.title, %s, 'i') AS title_acronym,
    REGEXP_LIKE(courses.title, %s, 'i') AS title_abbrev
FROM
    courses
    LEFT JOIN sections ON courses.dept = sections.dept AND courses.code_num = sections.code_num
    LEFT JOIN prerequisites ON sections.crn = prerequisites.crn
GROUP BY
    1, 2
HAVING
    code_match > 0
    OR title_exact_match > 0
    OR title_start_match > 0
    OR title_match > 0
    OR title_acronym > 0
    OR title_abbrev > 0
ORDER BY
    11 DESC, 12 DESC, 13 DESC, 14 DESC, 15 DESC, 16 DESC, 2 ASC, 3 ASC
LIMIT 6;
