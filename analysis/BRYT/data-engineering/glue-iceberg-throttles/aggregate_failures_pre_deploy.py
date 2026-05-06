"""
Aggregate Glue job failures from Step Functions execution history.
Focuses on pre-deployment failures (before 2026-05-05) to identify true root cause.
"""

import subprocess
import json
from collections import Counter, defaultdict

PROFILE = "bryt-inv-prod"
REGION = "eu-west-2"
ORCHESTRATION_ARN = "arn:aws:states:eu-west-2:837413265725:stateMachine:rel-esg-prod-data-eng--data-orchestration"

# Pre-deployment execution ARNs (before 2026-05-05)
PRE_DEPLOY_ARNS = [
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:3c69f8d5-a122-42b7-b868-cb6aa2ba4c20",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:8e69f873-31b8-44fe-94d4-fdfd6ba0174c",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:5169f4e1-21dd-4d51-bb5f-1c3071ec46f4",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:6969f4c5-012b-4e93-aaca-9dcdfc7fb29d",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:b769f4b6-f12f-4449-9ba8-58603a0a916d",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:7769f4a8-e18f-42a5-aa2f-bbbafcd0b43f",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:ac69f49a-d1d2-4fab-87ba-eefe391c8f7a",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:e569f48c-c1a2-4a62-9ab3-d99bad2f95a7",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:3669f47e-b170-4863-a152-a1f3d87d7bda",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:8d69f470-a15b-4c71-8c56-5229ad1942dc",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:4e69f462-910a-40b0-a2fe-94c192e7666c",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:3f69f39d-b1b9-484c-9a1c-f5499f60eea8",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:a969f38f-a1d4-4870-9e89-99070ee00307",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:6767f373-81ab-40a7-8077-50c56366369e",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:6464f357-61f8-40b6-9b86-af66e87d53de",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:6269f34c-9936-4159-ac92-d099b145ed19",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:72169dba-b2c6-47c7-9a01-e6ad2b5c173e",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:7b7e8ac1-4025-4e74-930c-a848227c6b7b",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:ef69f31f-216e-4143-9c89-c6c40f94a178",
    "arn:aws:states:eu-west-2:837413265725:execution:rel-esg-prod-data-eng--data-orchestration:4f69f311-1170-4758-8c68-3f9b7a336b7c",
]


def run_aws_cmd(args):
    """Run an AWS CLI command and return parsed JSON."""
    cmd = ["aws"] + args + ["--profile", PROFILE, "--region", REGION, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def get_failed_jobs_from_execution(execution_arn):
    """Extract failed job names from an orchestration execution."""
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
            failed_jobs.append({"jobName": job_name, "subExecutionArn": sub_exec_arn})
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
        }
    except (json.JSONDecodeError, KeyError):
        return None


def main():
    print("=" * 70)
    print("PRE-DEPLOYMENT FAILURE ANALYSIS (before 2026-05-05)")
    print("=" * 70)

    job_failure_count = Counter()
    job_errors = defaultdict(list)
    error_categories = Counter()
    all_error_messages = []

    for i, exec_arn in enumerate(PRE_DEPLOY_ARNS):
        short_id = exec_arn.split(":")[-1][:8]
        print(f"  [{i+1}/{len(PRE_DEPLOY_ARNS)}] {short_id}...")

        failed_jobs = get_failed_jobs_from_execution(exec_arn)

        for job in failed_jobs:
            job_name = job["jobName"]
            job_failure_count[job_name] += 1

            # Get detailed error from all sub-executions
            if job["subExecutionArn"]:
                error_detail = get_glue_error_from_sub_execution(job["subExecutionArn"])
                if error_detail:
                    job_errors[job_name].append(error_detail)
                    err_msg = error_detail.get("errorMessage", "")
                    all_error_messages.append(err_msg)

                    # Categorize error
                    if "SlowDown" in err_msg or "503" in err_msg:
                        error_categories["S3_THROTTLE_503"] += 1
                    elif "THROTTLING_ERROR" in err_msg:
                        error_categories["THROTTLING_ERROR"] += 1
                    elif "LFCredential" in err_msg:
                        error_categories["LAKE_FORMATION_CREDENTIAL"] += 1
                    elif "TIMEOUT_ERROR" in err_msg or "Timeout" in err_msg:
                        error_categories["TIMEOUT"] += 1
                    elif "ConcurrentRunsExceeded" in err_msg:
                        error_categories["GLUE_CONCURRENCY"] += 1
                    elif "OutOfMemory" in err_msg or "OOM" in err_msg:
                        error_categories["OUT_OF_MEMORY"] += 1
                    else:
                        error_categories[f"OTHER: {err_msg[:80]}"] += 1

    # Print results
    print(f"\n{'=' * 70}")
    print("FAILURE FREQUENCY BY JOB")
    print("=" * 70)
    for job_name, count in job_failure_count.most_common():
        print(f"  {count:3d}x  {job_name}")

    print(f"\n{'=' * 70}")
    print("ERROR CATEGORIES")
    print("=" * 70)
    for category, count in error_categories.most_common():
        print(f"  {count:3d}x  {category}")

    print(f"\n{'=' * 70}")
    print("FULL ERROR MESSAGES (deduplicated)")
    print("=" * 70)
    unique_errors = set()
    for msg in all_error_messages:
        # Truncate but keep enough to identify the error
        key = msg[:200]
        if key not in unique_errors:
            unique_errors.add(key)
            print(f"\n  {msg[:300]}")

    print(f"\n{'=' * 70}")
    print("DETAILED SAMPLES BY JOB")
    print("=" * 70)
    for job_name, errors in sorted(job_errors.items()):
        print(f"\n  {job_name}:")
        for err in errors[:2]:
            print(f"    Error: {err['errorMessage'][:150]}")
            print(f"    Workers: {err['numberOfWorkers']}x {err['workerType']}, "
                  f"Glue {err['glueVersion']}, Runtime: {err['executionTime']}s")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"  Executions analysed: {len(PRE_DEPLOY_ARNS)}")
    print(f"  Total job failures: {sum(job_failure_count.values())}")
    print(f"  Unique jobs that failed: {len(job_failure_count)}")


if __name__ == "__main__":
    main()
