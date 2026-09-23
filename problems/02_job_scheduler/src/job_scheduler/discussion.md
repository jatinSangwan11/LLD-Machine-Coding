# Discussion

Entities that I can find here is 

- Schedular (class) more of a orchestrator class 
1) dict of job right - based on the unique id provided by the schedular to the USER
4) also takes the retry policy (dependency injection) - there can be multiple policy strategy
3) to add the jon to the schedular - return the unique id
2) query the status of a specific job 
- job (class) - it has it's own state as in what state it is in right now -->
1)scheduled time
2) STATUS = schedule, scheduled, PROCESS, completed, RETRY, FAILED
3) METHOD = the mechanism of the execution of that job
- now the job can be of two type ----> so we can have a job interface here 
-> that sepecifies what kind of job it is - like one time or recurring (INTERFACE)

- WORKER - that takes the jobs and then execute the job and returns the result
1) STATUS - IDLE , WORKING
2) workerID
3) JOB_ID - which job is delegated to this worker


--> If I want to take the happy flow right now it can be like- the client sends the JOB(interface) -> one time job,recurring job --> schedular.schedule() is called with the job, timeStamp -> then it will be added to the job queue ->
and return uniqueJobID

- now we come at the IJob --> oneTimeJob and Recurring job, so the job will take the execution and also its time of execution run_at, so a methos providing run_at