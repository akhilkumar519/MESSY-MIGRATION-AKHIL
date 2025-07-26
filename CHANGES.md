When I first saw the  user management API, it was clear that the codebase needed serious work. It was messy and  had critical security issues, poor structure, and a lot of things that made it hard to maintain or scale. My main goal throughout this refactoring process was to fix the problems while preserving all the existing functionality, and to do it all within the limited time I had.


MAJOR ISSUES I'VE NOTICED:

1) The first thing I noticed was how fragile the system was. SQL injection risks were everywhere—user inputs were being directly inserted into SQL queries using f-strings. This meant that anyone with malicious intent could run arbitrary queries on the database.

2) Passwords were stored in plain text, which is a major issue. If the database were exposed, every user’s password would be readable format.

3) There was almost no input validation. Any kind of malicious data could get into the system without being checked.

4) Sensitive data was being sent back in API responses without any filtering.

5) From a code structure perspective. Everything—routing, database access, logic—was fit into a single file.

6) The database connection was being handled globally, which is a bad idea in web apps where multiple threads can be in play.

7) no proper error handling and responses from the API were a mix of plain text, JSON, and incorrect HTTP status codes. It was hard to know what was going wrong, or even if something was going wrong.

CHANGES I MADE AND REASONS:

1) So I started by refactoring  the code. I broke the project into a proper  structure. There’s now a clear separation of problems: models handle all the database interactions, services contain the core  logic, routes act as controllers to deal with incoming requests and return proper responses, and utility functions handle things like password hashing. The original app.py now simply serves as the entry point to the Flask app, and the database initialization has been moved into its own script.

2) Security was the next big thing. I rewrote every database query to use parameterized statements so that SQL injection is no longer a risk. I added password hashing using Werkzeug’s built-in tools, so now passwords are stored securely and compared safely during login. I also introduced proper validation across the board—checking for required fields, verifying email formats, and enforcing password security. And I made sure that only safe user fields (like name, email, and ID) are returned in API responses—no more leaking hashed passwords or other sensitive data.

3) At the database level, I added unique constraints on name and email to make sure we don’t get duplicates, even if something get over app-level checks. For the API responses, I standardized everything: all error messages now follow a consistent JSON format, and every response uses the correct HTTP status code—so clients can easily tell what happened and why.

4) To improve maintainability, I built reusable validation functions and kept all business logic in the service layer. I also adopted Flask’s recommended pattern for managing database connections per request, which avoids global variables and ensures resources are properly cleaned up after each request.

TRADE OFFS OR ASSUMPTIONS:

1) For example, I stuck with SQLite for simplicity, even though something like PostgreSQL would be better for production.

2) I didn’t add any new features. All validation is done manually using standard Python pnly, without other libraries.

3) Also, while I did write tests for core functionality, I didn’t aim for 100% test coverage—just enough to be confident in the refactored code.

IF I HAD MORE TIME:

1) The first would be implementing proper authentication using JWTs, so users could securely log in and access protected routes. Depending on the use case, I’d also look at adding role-based access control to handle different permission levels cleanly.

2) Another big one would be setting up structured logging. Right now, there’s not much visibility into what’s happening under the hood—especially in a production environment. With better logging, it’d be much easier to monitor activity, debug issues, and keep track of unusual behavior.

3) Database migrations are another area that could be improved. At the moment, any schema changes have to be applied manually using SQL scripts, which isn’t scalable. Introducing a migration tool would make that process smoother and safer.

4) I'd also move all sensitive configurations—like secret keys or database credentials—into environment variables. That’s just good practice for any application heading toward production. And of course, containerizing the app using Docker would make it easier to deploy and run consistently across environments.

5) Finally, I’d add proper API documentation using something like  OpenAPI. That would make it a lot easier for other developers or even myself later on to understand how to use the API without digging into the code.

All in all, this refactor wasn’t about adding good  features. It was about cleaning up serious issues, putting a solid structure in place, and setting a strong foundation for anything that comes next. Now the code is more secure, much easier to maintain, and ready to scale if needed.