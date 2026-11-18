scenario_id,title,category,severity,table_b4_clear_intent,table_b4_observable,table_b4_reader_agreement,table_b4_reliable,table_b4_non_duplicate,decision,rejection_reason
SCN-001,Register new account with valid trimmed username and untrimmed password,Accounts & Sessions,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-002,Register duplicate username with different casing,Accounts & Sessions,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-003,Register with invalid characters in username,Validation,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-004,Sign in with case-insensitive username and exact password,Access Control,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-005,Verify identical error message for unknown user and wrong password,Accounts & Sessions,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-006,Sign out terminates active session cleanly,Validation,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-007,Unauthenticated access to protected routes redirects to signin,Accounts & Sessions,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-008,Protected pages include Cache-Control no-store header,Access Control,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-009,Signed-in user accessing signin or register redirects to tasks,Validation,Low,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-010,Create task with valid trimmed title and optional fields,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-011,Reject task creation with whitespace-only title,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-012,Simulate concurrent multi-tab token race condition during logout,Access Control,High,Yes,Yes,No,No,Yes,REJECTED,"Fails Table B4 reliable execution and reader agreement; timing-dependent race condition in headless browser."
SCN-013,Edit own task title and description within length bounds,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-014,Reject edit when updated title exceeds 100 characters,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-015,Reject impossible calendar date 2026-02-30 on task creation,Validation,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-016,Accept valid past due date in YYYY-MM-DD format,Access Control,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-017,Toggle own task status from open to completed on detail page,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-018,Reopen completed task back to open status,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-019,Verify visual pixel alignment of flash banner across mobile viewports,Core Workflow,Low,No,Yes,No,No,Yes,REJECTED,"Fails Table B4 clear intent and reader agreement; subjective CSS layout check outside functional spec."
SCN-020,Delete own task and verify single-display flash confirmation,Access Control,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-021,Verify flash confirmation disappears after page reload,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-022,Task list displays only owner tasks ordered by descending ID,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-023,Search tasks using case-insensitive substring in title,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-024,Search tasks using literal regex metacharacter parenthesis,Access Control,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-025,Combine keyword query and status filter parameters simultaneously,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-026,Unrecognized status query parameter defaults to all tasks,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-027,Empty state renders No tasks found in empty-message container,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-028,Evaluate readability and tone of custom user task descriptions,Access Control,Low,No,No,No,Yes,Yes,REJECTED,"Fails Table B4 observable execution and reader agreement; subjective content quality judgment."
SCN-029,Direct GET request to another user task ID returns 404 without data leak,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-030,Direct POST edit to another user task ID is rejected without mutation,Validation,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-031,Direct POST delete to another user task ID is rejected without deletion,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-032,Direct POST toggle to another user task ID leaves status unchanged,Access Control,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-033,Measure database query execution latency under 50ms threshold,Validation,Medium,No,No,No,No,Yes,REJECTED,"Fails Table B4 observable execution and reliable execution; non-deterministic hardware timing."
SCN-034,Search query matching another user task returns empty result,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-035,Direct GET to another user task edit form returns 404,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-036,Compare response status and body between other user task and missing ID,Access Control,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-037,Compare POST edit response between other user task and missing ID,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-038,Compare POST delete response between other user task and missing ID,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-039,Compare POST toggle response between other user task and missing ID,Validation,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-040,Server rejects direct POST registration bypassing HTML attributes,Access Control,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-041,Test browser autocomplete popup styling on signin form,Core Workflow,Low,No,No,No,No,Yes,REJECTED,"Fails Table B4 observable execution and reliable execution; browser-native UI outside DOM control."
SCN-042,Server rejects direct POST task creation with 101-character title,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-043,Server rejects direct POST task edit with malformed due date,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-044,Rejected server edit preserves original task title and description,Access Control,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-045,Check color contrast ratio of error message text against background,Validation,Low,No,Yes,No,Yes,Yes,REJECTED,"Fails Table B4 clear intent and reader agreement; accessibility styling not defined in v1.1 spec."
SCN-046,Register username at maximum 20-character boundary,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-047,Reject username at 21 characters after trimming,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-048,Register password at minimum 8-character boundary,Access Control,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-049,Register password at maximum 128-character boundary,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-050,Reject password at 129 characters,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-051,Create task with description at 500-character trimmed boundary,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-052,Verify keyboard tab focus ring order across task list rows,Access Control,Low,No,Yes,No,No,Yes,REJECTED,"Fails Table B4 reader agreement and reliable execution; browser focus behavior varies across runners."
SCN-053,Reject task creation when description exceeds 500 characters,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-054,Search tasks using substring located in task description,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-055,Search tasks with empty query parameter returns all user tasks,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-056,Filter tasks by status=open excludes completed tasks,Access Control,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-057,Filter tasks by status=completed excludes open tasks,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-058,Verify newly created task receives strictly higher ID than prior tasks,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-059,Simulate network packet drop mid-form submission,Core Workflow,Medium,No,No,No,No,Yes,REJECTED,"Fails Table B4 reliable execution and clear intent; infrastructure fault injection outside app scope."
SCN-060,Verify deleted task ID is never reassigned to subsequent tasks,Access Control,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-061,Unauthenticated POST to task creation redirects to signin,Core Workflow,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-062,Unauthenticated POST to task deletion redirects to signin,Core Workflow,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-063,Verify favicon.ico loads with HTTP 200 without authentication,Validation,Low,No,Yes,No,Yes,Yes,REJECTED,"Fails Table B4 clear intent and reader agreement; trivial static asset check with no behavioral value."
SCN-064,Unauthenticated POST to task toggle redirects to signin,Access Control,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-065,Verify Back button after signout does not expose cached task list,Core Workflow,Critical,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-066,Sign in with leading/trailing spaces in username fails authentication,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-067,Create task without optional description or due date succeeds,Core Workflow,Medium,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-068,Check HTML source indentation and closing tag formatting,Access Control,Low,No,Yes,No,Yes,Yes,REJECTED,"Fails Table B4 clear intent and reader agreement; markup formatting check irrelevant to satisfaction."
SCN-069,Edit task to clear previously set optional due date,Validation,High,Yes,Yes,Yes,Yes,Yes,ACCEPTED,
SCN-070,Verify session cookie expiration after 24 hours of inactivity,Core Workflow,Medium,Yes,No,No,No,Yes,REJECTED,"Fails Table B4 observable execution and reliable execution; impractical 24-hour wait time."
SCN-071,Duplicate check of R04 case-insensitive username signin,Core Workflow,Low,Yes,Yes,Yes,Yes,No,REJECTED,"Fails Table B4 non-duplication; exact duplicate of SCN-004."
SCN-072,Duplicate check of R09 blank title rejection on create,Validation,Low,Yes,Yes,Yes,Yes,No,REJECTED,"Fails Table B4 non-duplication; exact duplicate of SCN-011."
SCN-073,Duplicate check of R17 viewing another user task returns 404,Core Workflow,Low,Yes,Yes,Yes,Yes,No,REJECTED,"Fails Table B4 non-duplication; exact duplicate of SCN-029."
SCN-074,Verify session referencing deleted user account is invalidated,Access Control,Medium,Yes,No,No,No,Yes,REJECTED,"Fails Table B4 observable execution; R27 user deletion is out of scope in §7 so state is unreachable."