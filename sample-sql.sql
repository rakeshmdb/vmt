SELECT 
    e.employee_id,
    e.first_name,
    e.last_name,
    e.email,
    e.phone_number,
    e.hire_date,
    e.job_id,
    e.salary,
    e.manager_id,
    e.department_id,
    d.department_name,
    d.location_id,
    l.city,
    l.state_province,
    l.country_id,
    c.country_name,
    c.region_id,
    r.region_name,
    j.job_title,
    j.min_salary,
    j.max_salary,
    m.first_name AS manager_first_name,
    m.last_name AS manager_last_name,
    COUNT(p.project_id) AS project_count,
    SUM(p.budget) AS total_project_budget
FROM 
    employees e
INNER JOIN 
    departments d ON e.department_id = d.department_id
INNER JOIN 
    locations l ON d.location_id = l.location_id
INNER JOIN 
    countries c ON l.country_id = c.country_id
INNER JOIN 
    regions r ON c.region_id = r.region_id
LEFT JOIN 
    jobs j ON e.job_id = j.job_id
LEFT JOIN 
    employees m ON e.manager_id = m.employee_id
LEFT JOIN 
    project_assignments pa ON e.employee_id = pa.employee_id
LEFT JOIN 
    projects p ON pa.project_id = p.project_id
WHERE
    e.salary > 50000
    AND e.hire_date >= '2015-01-01'
    AND r.region_name = 'North America'
GROUP BY
    e.employee_id,
    e.first_name,
    e.last_name,
    e.email,
    e.phone_number,
    e.hire_date,
    e.job_id,
    e.salary,
    e.manager_id,
    e.department_id,
    d.department_name,
    d.location_id,
    l.city,
    l.state_province,
    l.country_id,
    c.country_name,
    c.region_id,
    r.region_name,
    j.job_title,
    j.min_salary,
    j.max_salary,
    m.first_name,
    m.last_name
HAVING
    COUNT(p.project_id) > 2
ORDER BY
    e.last_name ASC,
    e.first_name ASC;
