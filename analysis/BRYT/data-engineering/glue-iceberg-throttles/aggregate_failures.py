"""
Aggregate Glue job failures from Step Functions execution history.
Identifies which jobs fail most frequently and extracts error details.
"""

import subprocess
import json
from collections import Counter, defaultdict

PROFILE = "bryt-inv-prod"
REGION = "eu-west-2"
ORCHESTRATION_ARN = "arn:aws:states:eu-west-2:837413265725:stateMachine:rel-esg-prod-data-eng--data-orchestration"
RUN_GLUE_JOB_ARN = "arn:aws:states:eu-west-2:837413265725:stateMachine:rel-esg-prod-data-eng--run-glue-job"


def run_aws_cmd(args):
    """Run an AWS CLI command and return parsed JSON."""
    cmd = ["aws"] + args + ["--profile", PROFILE, "--region", REGION, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
        return None
    return json.loads(result.stdout)


def get_failed_executions(max_items=30):
    """Get recent failed orchestration executions."""
    data = run_aws_cmd([
        "stepfunctions", "list-executions",
        "--state-machine-arn", ORCHESTRATION_ARN,
        "--status-filter", "FAILED",
        "--max-items", str(max_items)
    ])
    if not data:
        return []
    return data.get("executions", [])


def get_failed_jobs_from_execution(execution_arn):
    """Extract failed job names and error details from an orchestration execution."""
    data = run_aws_cmd([
        "stepfunctions", "get-execution-history",
        "--execution-arn", execution_arn,
        "--query", "events[?type=='TaskFailed'].taskFailedEventDetails"
    ])
    if not data:
        return []

    failed_jobs = []
    for event in data:
        cause_str = event.get("cause", "")
        try:
            cause = json.loads(cause_str)
            sub_exec_arn = cause.get("ExecutionArn", "")
            input_str = cause.get("Input", "{}")
            input_data = json.loads(input_str)
            job_name = input_data.get("jobName", "unknown")
            failed_jobs.append({
                "jobName": job_name,
                "subExecutionArn": sub_exec_arn
            })
        except (json.JSONDecodeError, KeyError):
            failed_jobs.append({"jobName": "parse_error", "subExecutionArn": ""})

    return failed_jobs


def get_glue_error_from_sub_execution(sub_exec_arn):
    """Get the actual Glue error message from a sub-execution."""
    data = run_aws_cmd([
        "stepfunctions", "get-execution-history",
        "--execution-arn", sub_exec_arn,
        "--query", "events[?type=='FailStateEntered'].stateEnteredEventDetails"
    ])
    if not data or len(data) == 0:
        return None

    try:
        input_str = data[0].get("input", "{}")
        input_data = json.loads(input_str)
        job_status = input_data.get("jobStatus", {}).get("JobRun", {})
        return {
            "errorMessage": job_status.get("ErrorMessage", "unknown"),
            "executionTime": job_status.get("ExecutionTime"),
            "workerType": job_status.get("WorkerType"),
            "numberOfWorkers": job_status.get("NumberOfWorkers"),
            "glueVersion": job_status.get("GlueVersion"),
            "startedOn": job_status.get("StartedOn"),
            "completedOn": job_status.get("CompletedOn"),
        }
    except (json.JSONDecodeError, KeyError):
        return None


def main():
    print("=" * 70)
    print("GLUE JOB FAILURE AGGREGATION REPORT")
    print("=" * 70)

    # Get failed executions
    print("\nFetching failed orchestration executions...")
    executions = get_failed_executions(max_items=30)
    print(f"Found {len(executions)} failed executions\n")

    # Track failures
    job_failure_count = Counter()
    job_errors = defaultdict(list)
    error_categories = Counter()

    for i, execution in enumerate(executions):
        exec_arn = execution["executionArn"]
        start_date = execution.get("startDate", "unknown")
        print(f"  [{i+1}/{len(executions)}] Processing execution started at {start_date}...")

        failed_jobs = get_failed_jobs_from_execution(exec_arn)

        for job in failed_jobs:
            job_name = job["jobName"]
            job_failure_count[job_name] += 1

            # Get detailed error from sub-execution (sample first 10 for speed)
            if job["subExecutionArn"] and i < 10:
                error_detail = get_glue_error_from_sub_execution(job["subExecutionArn"])
                if error_detail:
                    job_errors[job_name].append(error_detail)
                    # Categorize error
                    err_msg = error_detail.get("errorMessage", "")
                    if "SlowDown" in err_msg or "503" in err_msg:
                        error_categories["S3_THROTTLE_503"] += 1
                    elif "THROTTLING" in err_msg:
                        error_categories["THROTTLING_OTHER"] += 1
                    elif "ConcurrentRunsExceeded" in err_msg:
                        error_categories["GLUE_CONCURRENCY"] += 1
                    else:
                        error_categories[f"OTHER: {err_msg[:60]}"] += 1

    # Print results
    print("\n" + "=" * 70)
    print("FAILURE FREQUENCY BY JOB (sorted by count)")
    print("=" * 70)
    for job_name, count in job_failure_count.most_common():
        print(f"  {count:3d}x  {job_name}")

    print(f"\n{'=' * 70}")
    print("ERROR CATEGORIES")
    print("=" * 70)
    for category, count in error_categories.most_common():
        print(f"  {count:3d}x  {category}")

    print(f"\n{'=' * 70}")
    print("DETAILED ERROR SAMPLES")
    print("=" * 70)
    for job_name, errors in sorted(job_errors.items()):
        print(f"\n  {job_name}:")
        for err in errors[:2]:  # Show max 2 samples per job
            print(f"    Error: {err['errorMessage'][:100]}")
            print(f"    Workers: {err['numberOfWorkers']}x {err['workerType']}, "
                  f"Glue {err['glueVersion']}, Runtime: {err['executionTime']}s")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total failed executions analysed: {len(executions)}")
    print(f"  Total job failures: {sum(job_failure_count.values())}")
    print(f"  Unique jobs that failed: {len(job_failure_count)}")
    print(f"  Date range: {executions[-1].get('startDate', '?')} to {executions[0].get('startDate', '?')}")


if __name__ == "__main__":
    main()
