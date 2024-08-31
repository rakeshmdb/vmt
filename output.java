
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.query.Criteria;

public class MongoDBQuery {
    public static Aggregation getAggregation() {
        return Aggregation.newAggregation(

    {
        Aggregation.match: new Aggregation.Stage({
            salary: { $gt: 50000 }),
            hire_date: new Aggregation.Stage({ $gte: ISODate("2015-01-01") })
        }
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "departments",
            localField: "department_id",
            foreignField: "department_id",
            as: "department"
        })
    },
    {
        Aggregation.unwind: "$department"
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "locations",
            localField: "department.location_id",
            foreignField: "location_id",
            as: "location"
        })
    },
    {
        Aggregation.unwind: "$location"
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "countries",
            localField: "location.country_id",
            foreignField: "country_id",
            as: "country"
        })
    },
    {
        Aggregation.unwind: "$country"
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "regions",
            localField: "country.region_id",
            foreignField: "region_id",
            as: "region"
        })
    },
    {
        Aggregation.unwind: "$region"
    },
    {
        Aggregation.match: {
            "region.region_name": "North America"
        }
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "jobs",
            localField: "job_id",
            foreignField: "job_id",
            as: "job"
        })
    },
    {
        Aggregation.unwind: new Aggregation.Stage({
            path: "$job",
            preserveNullAndEmptyArrays: true
        })
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "employees",
            localField: "manager_id",
            foreignField: "employee_id",
            as: "manager"
        })
    },
    {
        Aggregation.unwind: new Aggregation.Stage({
            path: "$manager",
            preserveNullAndEmptyArrays: true
        })
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "project_assignments",
            localField: "employee_id",
            foreignField: "employee_id",
            as: "project_assignments"
        })
    },
    {
        Aggregation.unwind: new Aggregation.Stage({
            path: "Aggregation.project_assignments",
            preserveNullAndEmptyArrays: true
        })
    },
    {
        Aggregation.lookup: new Aggregation.Stage({
            from: "projects",
            localField: "project_assignments.project_id",
            foreignField: "project_id",
            as: "projects"
        })
    },
    {
        Aggregation.unwind: new Aggregation.Stage({
            path: "Aggregation.projects",
            preserveNullAndEmptyArrays: true
        })
    },
    {
        Aggregation.groupBy: new Aggregation.Stage({
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
                manager_first_name: { $ifNull: ["$manager.first_name", null] }),
                manager_last_name: new Aggregation.Stage({ $ifNull: ["$manager.last_name", null] })
            },
            project_count: new Aggregation.Stage({ $sum: { $cond: [{ $ifNull: ["Aggregation.projects.project_id", false] }), 1, 0] } },
            total_project_budget: new Aggregation.Stage({ $sum: "Aggregation.projects.budget" }),
            avg_project_budget: new Aggregation.Stage({ $avg: "Aggregation.projects.budget" }),
            max_project_budget: new Aggregation.Stage({ $max: "Aggregation.projects.budget" }),
            min_project_budget: new Aggregation.Stage({ $min: "Aggregation.projects.budget" }),
            avg_project_budget_per_project: new Aggregation.Stage({
                $divide: [
                    { $sum: "Aggregation.projects.budget" }),
                    new Aggregation.Stage({ $sum: { $cond: [{ $ifNull: ["Aggregation.projects.project_id", false] }), 1, 0] } }
                ]
            },
            annual_salary: new Aggregation.Stage({ $multiply: ["$salary", 12] }),
            days_since_hire: new Aggregation.Stage({
                $divide: [
                    { $subtract: [new Date(), "$hire_date"] }),
                    86400000
                ]
            },
            full_name: new Aggregation.Stage({ $concat: ["$first_name", " ", "$last_name"] })
        }
    },
    {
        Aggregation.match: new Aggregation.Stage({
            project_count: { $gt: 2 })
        }
    },
    {
        Aggregation.sort: new Aggregation.Stage({
            salary: -1,
            region_name: 1,
            last_name: 1,
            first_name: 1
        })
    }

        ,
Aggregation.project: new Aggregation.Stage({
"e.employee_id": 1,
"e.first_name": 1,
"e.last_name": 1,
"e.email": 1,
"e.phone_number": 1,
"e.hire_date": 1,
"e.job_id": 1,
"e.salary": 1,
"e.manager_id": 1,
"e.department_id": 1,
"d.department_name": 1,
"d.location_id": 1,
"l.city": 1,
"l.state_province": 1,
"l.country_id": 1,
"c.country_name": 1,
"c.region_id": 1,
"r.region_name": 1,
"j.job_title": 1,
"j.min_salary": 1,
"j.max_salary": 1,
"m.first_name AS manager_first_name": 1,
"m.last_name AS manager_last_name": 1,
"COUNT(p.project_id) AS project_count": 1,
"SUM(p.budget) AS total_project_budget": 1,
"AVG(p.budget) AS avg_project_budget": 1,
"MAX(p.budget) AS max_project_budget": 1,
"MIN(p.budget) AS min_project_budget": 1,
"SUM(p.budget) / NULLIF(COUNT(p.project_id)": 1,
"0) AS avg_project_budget_per_project": 1,
"(e.salary * 12) AS annual_salary": 1,
"DATEDIFF(CURDATE()": 1,
"e.hire_date) AS days_since_hire": 1,
"CONCAT(e.first_name": 1,
"' '": 1,
"e.last_name) AS full_name": 1
})
        );
    }
}
