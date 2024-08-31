To rewrite the SQL query in MongoDB Aggregation Pipeline, we need to follow these steps:

1. Convert the tables into collections.
2. Replace the JOIN operations with `$lookup` stages.
3. Replace the WHERE clause with `$match` stages.
4. Replace the GROUP BY clause with `$group` stages.
5. Replace the HAVING clause with another `$match` stage.
6. Replace the ORDER BY clause with a `$sort` stage.
7. Replace the aggregate functions (COUNT, SUM, AVG, MAX, MIN) with their MongoDB equivalents.
8. Replace the SQL functions (DATEDIFF, CONCAT, NULLIF) with their MongoDB equivalents or use expressions.

Here's the MongoDB Aggregation Pipeline equivalent:

```javascript
db.employees.aggregate([
    {
        $match: {
            salary: { $gt: 50000 },
            hire_date: { $gte: ISODate("2015-01-01") }
        }
    },
    {
        $lookup: {
            from: "departments",
            localField: "department_id",
            foreignField: "department_id",
            as: "department"
        }
    },
    {
        $unwind: "$department"
    },
    {
        $lookup: {
            from: "locations",
            localField: "department.location_id",
            foreignField: "location_id",
            as: "location"
        }
    },
    {
        $unwind: "$location"
    },
    {
        $lookup: {
            from: "countries",
            localField: "location.country_id",
            foreignField: "country_id",
            as: "country"
        }
    },
    {
        $unwind: "$country"
    },
    {
        $lookup: {
            from: "regions",
            localField: "country.region_id",
            foreignField: "region_id",
            as: "region"
        }
    },
    {
        $unwind: "$region"
    },
    {
        $match: {
            "region.region_name": "North America"
        }
    },
    {
        $lookup: {
            from: "jobs",
            localField: "job_id",
            foreignField: "job_id",
            as: "job"
        }
    },
    {
        $unwind: {
            path: "$job",
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $lookup: {
            from: "employees",
            localField: "manager_id",
            foreignField: "employee_id",
            as: "manager"
        }
    },
    {
        $unwind: {
            path: "$manager",
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $lookup: {
            from: "project_assignments",
            localField: "employee_id",
            foreignField: "employee_id",
            as: "project_assignments"
        }
    },
    {
        $unwind: {
            path: "$project_assignments",
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $lookup: {
            from: "projects",
            localField: "project_assignments.project_id",
            foreignField: "project_id",
            as: "projects"
        }
    },
    {
        $unwind: {
            path: "$projects",
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group: {
            _id: {
                employee_id: "$employee_id",
                first_name: "$first_name",
                last_name: "$last_name",
                email: "$email",
                phone_number: "$phone_number",
                hire_date: "$hire_date",
                job_id: "$job_id",
                salary: "$salary",
                manager_id: "$manager_id",
                department_id: "$department_id",
                department_name: "$department.department_name",
                location_id: "$department.location_id",
                city: "$location.city",
                state_province: "$location.state_province",
                country_id: "$location.country_id",
                country_name: "$country.country_name",
                region_id: "$country.region_id",
                region_name: "$region.region_name",
                job_title: "$job.job_title",
                min_salary: "$job.min_salary",
                max_salary: "$job.max_salary",
                manager_first_name: { $ifNull: ["$manager.first_name", null] },
                manager_last_name: { $ifNull: ["$manager.last_name", null] }
            },
            project_count: { $sum: { $cond: [{ $ifNull: ["$projects.project_id", false] }, 1, 0] } },
            total_project_budget: { $sum: "$projects.budget" },
            avg_project_budget: { $avg: "$projects.budget" },
            max_project_budget: { $max: "$projects.budget" },
            min_project_budget: { $min: "$projects.budget" },
            avg_project_budget_per_project: {
                $divide: [
                    { $sum: "$projects.budget" },
                    { $sum: { $cond: [{ $ifNull: ["$projects.project_id", false] }, 1, 0] } }
                ]
            },
            annual_salary: { $multiply: ["$salary", 12] },
            days_since_hire: {
                $divide: [
                    { $subtract: [new Date(), "$hire_date"] },
                    86400000
                ]
            },
            full_name: { $concat: ["$first_name", " ", "$last_name"] }
        }
    },
    {
        $match: {
            project_count: { $gt: 2 }
        }
    },
    {
        $sort: {
            salary: -1,
            region_name: 1,
            last_name: 1,
            first_name: 1
        }
    }
])
```

This pipeline performs the following steps:

1. Matches employees with a salary greater than 50000 and a hire date on or after 2015-01-01.
2. Joins the employees collection with the departments, locations, countries, regions, jobs, and projects collections using `$lookup` stages.
3. Groups the data by employee details and calculates the project-related aggregations.
4. Filters the results to include only employees with more than 2 projects.
5. Sorts the results by salary in descending order, region name in ascending order, last name in ascending order, and first name in ascending order.

Note: This pipeline assumes that the collections have the same structure as the SQL tables, and the field names match. If there are any differences, you may need to adjust the pipeline accordingly.