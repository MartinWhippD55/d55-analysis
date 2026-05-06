"""
Enumerate all 65 Glue jobs from the run-titanium-jobs stage.
Extracts source database, staging database, warehouse bucket, and script location for each.
Outputs a markdown table.
"""

import subprocess
import json

PROFILE = "bryt-inv-prod"
REGION = "eu-west-2"

# All 65 jobs from the run-titanium-jobs parallel stage
JOBS = [
    "rel-esg-prod-data-eng-phidex-billing-contract-mpan-volume",
    "rel-esg-prod-data-eng-phidex-billing-contract-mpan",
    "rel-esg-prod-data-eng-phidex-billing-customer",
    "rel-esg-prod-data-eng-phidex-billing-group",
    "rel-esg-prod-data-eng-centerstage-titanium-customer",
    "rel-esg-prod-data-eng-centerstage-titanium-customer-supply",
    "rel-esg-prod-data-eng-centerstage-titanium-constant-customer-supply-status",
    "rel-esg-prod-data-eng-centerstage-titanium-constant-payment-method",
    "rel-esg-prod-data-eng-centerstage-titanium-constant-payment-status",
    "rel-esg-prod-data-eng-centerstage-titanium-constant-refund-method",
    "rel-esg-prod-data-eng-centerstage-titanium-supply",
    "rel-esg-prod-data-eng-centerstage-titanium-supply-electricity",
    "rel-esg-prod-data-eng-centerstage-titanium-lookup-profile-class",
    "rel-esg-prod-data-eng-centerstage-titanium-lookup-measurement-class",
    "rel-esg-prod-data-eng-centerstage-titanium-site",
    "rel-esg-prod-data-eng-centerstage-titanium-address",
    "rel-esg-prod-data-eng-centerstage-titanium-meter",
    "rel-esg-prod-data-eng-centerstage-titanium-meter-electricity",
    "rel-esg-prod-data-eng-centerstage-titanium-lookup-meter-type",
    "rel-esg-prod-data-eng-centerstage-titanium-register",
    "rel-esg-prod-data-eng-centerstage-titanium-register-electricity",
    "rel-esg-prod-data-eng-centerstage-titanium-constant-tpr",
    "rel-esg-prod-data-eng-centerstage-titanium-supply-contract",
    "rel-esg-prod-data-eng-centerstage-titanium-contract",
    "rel-esg-prod-data-eng-centerstage-titanium-invoice-billing-raw-data",
    "rel-esg-prod-data-eng-centerstage-titanium-invoice-crm-data",
    "rel-esg-prod-data-eng-centerstage-titanium-document-data",
    "rel-esg-prod-data-eng-centerstage-titanium-generated-document",
    "rel-esg-prod-data-eng-centerstage-titanium-mpan-billing-raw-data",
    "rel-esg-prod-data-eng-centerstage-titanium-payment-association-map",
    "rel-esg-prod-data-eng-centerstage-titanium-payment",
    "rel-esg-prod-data-eng-centerstage-titanium-refund-association-map",
    "rel-esg-prod-data-eng-centerstage-titanium-refund",
    "rel-esg-prod-data-eng-centerstage-titanium-allocation",
    "rel-esg-prod-data-eng-centerstage-titanium-invoice-detail",
    "rel-esg-prod-data-eng-centerstage-titanium-payment-crm-data",
    "rel-esg-prod-data-eng-centerstage-titanium-site-billing-raw-data",
    "rel-esg-prod-data-eng-centerstage-titanium-site-crm-data",
    "rel-esg-prod-data-eng-centerstage-titanium-invoice-billing-header-raw-data",
    "rel-esg-prod-data-eng-centerstage-titanium-invoice-detail-note",
    "rel-esg-prod-data-eng-centerstage-titanium-customer-note",
    "rel-esg-prod-data-eng-centerstage-titanium-customer-note-history",
    "rel-esg-prod-data-eng-centerstage-titanium-customer-note-attachment",
    "rel-esg-prod-data-eng-centerstage-afmse-meter-register-reading",
    "rel-esg-prod-data-eng-centerstage-afmse-meter-register",
    "rel-esg-prod-data-eng-centerstage-afmse-meter",
    "rel-esg-prod-data-eng-centerstage-afmse-mpan",
    "rel-esg-prod-data-eng-centerstage-bol-xread-out-01-active-import-profile-data",
    "rel-esg-prod-data-eng-centerstage-bol-xread-out-01-meter",
    "rel-esg-prod-data-eng-centerstage-dcc-bol-device",
    "rel-esg-prod-data-eng-centerstage-billing-wide",
    "rel-esg-prod-data-eng-salesforce-account",
    "rel-esg-prod-data-eng-salesforce-loa-shell",
    "rel-esg-prod-data-eng-bryt-payment",
    "rel-esg-prod-data-eng-bryt-refund",
    "rel-esg-prod-data-eng-ensek-readings",
    "rel-esg-prod-data-eng-ensek-registers",
    "rel-esg-prod-data-eng-phidex-billing-contract-site",
    "rel-esg-prod-data-eng-centerstage-meter_register_reading_mhhs",
    "rel-esg-prod-data-eng-centerstage-mpan_mhhs",
    "rel-esg-prod-data-eng-centerstage-meter_mhhs",
    "rel-esg-prod-data-eng-centerstage-titanium_contact",
    "rel-esg-prod-data-eng-centerstage-titanium_sitecontact",
    "rel-esg-prod-data-eng-phidex-billing-contract-document",
    "rel-esg-prod-data-eng-phidex-billing-contract-meter",
    "rel-esg-prod-data-eng-phidex-billing-contract-mpan-line",
    "rel-esg-prod-data-eng-phidex-billing-contract-mpan-rate",
    "rel-esg-prod-data-eng-phidex-billing-contract-mpan-read",
    "rel-esg-prod-data-eng-phidex-billing-contract-register",
    "rel-esg-prod-data-eng-phidex-billing-invoice",
    "rel-esg-prod-data-eng-phidex-billing-invoice-document",
    "rel-esg-prod-data-eng-phidex-billing-invoice-error",
    "rel-esg-prod-data-eng-phidex-billing-invoice-line",
    "rel-esg-prod-data-eng-phidex-billing-invoice-mpan",
    "rel-esg-prod-data-eng-phidex-billing-invoice-site",
    "rel-esg-prod-data-eng-phidex-billing-invoice-vat",
    "rel-esg-prod-data-eng-phidex-billing-product",
    "rel-esg-prod-data-eng-phidex-billing-product-charge",
    "rel-esg-prod-data-eng-phidex-billing-product-section",
    "rel-esg-prod-data-eng-phidex-billing-product-timeband-group",
    "rel-esg-prod-data-eng-phidex-billing-run-group",
    "rel-esg-prod-data-eng-phidex-billing-trade-group",
    "rel-esg-prod-data-eng-phidex-process-queue",
    "rel-esg-prod-data-eng-phidex-project",
    "rel-esg-prod-data-eng-phidex-project-customer",
    "rel-esg-prod-data-eng-phidex-project-document",
    "rel-esg-prod-data-eng-phidex-project-mpan",
    "rel-esg-prod-data-eng-phidex-project-site",
    "rel-esg-prod-data-eng-phidex-project-unit-rate",
    "rel-esg-prod-data-eng-centerstage-titanium-supply-contact",
    "rel-esg-prod-data-eng-centerstage-titanium-customer-contact",
    "rel-esg-prod-data-eng-centerstage-titanium-supply-registration-history",
    "rel-esg-prod-data-eng-phidex-billing-contract",
    "rel-esg-prod-data-eng-salesforce-case",
]


def get_job_details(job_name):
    """Get source/target details for a Glue job."""
    cmd = [
        "aws", "glue", "get-job",
        "--job-name", job_name,
        "--profile", PROFILE,
        "--region", REGION,
        "--output", "json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    data = json.loads(result.stdout)
    job = data.get("Job", {})
    args = job.get("DefaultArguments", {})
    conf = args.get("--conf", "")

    # Extract warehouse bucket from conf
    warehouse = ""
    if "warehouse=" in conf:
        warehouse = conf.split("warehouse=")[1].split(" ")[0].strip()

    # Extract source and staging databases
    source_db = ""
    staging_db = args.get("--STAGING_DATABASE", "")

    # Different jobs use different source DB arg names
    for key in ["--CENTRESTAGE_DATABASE", "--PHIDEX_DATABASE", "--SALESFORCE_DATABASE",
                "--BRYT_DATABASE", "--ENSEK_DATABASE"]:
        if key in args:
            source_db = args[key]
            break

    return {
        "job_name": job_name,
        "source_db": source_db,
        "staging_db": staging_db,
        "warehouse": warehouse,
        "workers": f"{job.get('NumberOfWorkers', '?')}x {job.get('WorkerType', '?')}",
        "script": job.get("Command", {}).get("ScriptLocation", ""),
    }


def main():
    print(f"Fetching details for {len(JOBS)} jobs...\n")

    results = []
    for i, job_name in enumerate(JOBS):
        print(f"  [{i+1}/{len(JOBS)}] {job_name}")
        details = get_job_details(job_name)
        results.append(details)

    # Now resolve source bucket locations by checking the Glue catalog
    # Group by source_db to minimize API calls
    source_dbs = set(r.get("source_db", "") for r in results if r.get("source_db"))
    db_locations = {}
    for db in source_dbs:
        cmd = [
            "aws", "glue", "get-database",
            "--name", db,
            "--profile", PROFILE,
            "--region", REGION,
            "--output", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            loc = data.get("Database", {}).get("LocationUri", "unknown")
            db_locations[db] = loc
        else:
            db_locations[db] = "error"

    # Write markdown table
    output_path = "analysis/BRYT/data-engineering/glue-iceberg-throttles/job-inventory.md"
    with open(output_path, "w") as f:
        f.write("# Glue Job Inventory — run-titanium-jobs stage\n\n")
        f.write(f"Total jobs: {len(JOBS)}\n\n")

        f.write("## Source Database Locations\n\n")
        f.write("| Source Database | Location |\n")
        f.write("|---|---|\n")
        for db, loc in sorted(db_locations.items()):
            f.write(f"| `{db}` | `{loc}` |\n")

        f.write("\n## Job Details\n\n")
        f.write("| # | Job Name | Source DB | Staging DB | Warehouse | Workers |\n")
        f.write("|---|---|---|---|---|---|\n")
        for i, r in enumerate(results):
            if "error" in r:
                f.write(f"| {i+1} | `{JOBS[i]}` | ERROR | - | - | - |\n")
            else:
                # Shorten names for readability
                short_name = r["job_name"].replace("rel-esg-prod-data-eng-", "")
                f.write(f"| {i+1} | `{short_name}` | `{r['source_db']}` | `{r['staging_db']}` | `{r['warehouse']}` | {r['workers']} |\n")

    print(f"\n✓ Written to {output_path}")


if __name__ == "__main__":
    main()
