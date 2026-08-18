"""
One-off: decompose the contract-note-data-source-extensibility spec (Estimate 3b)
into user stories and emit the decomposition (graph.yaml, jira-import.*, README.md,
manifests).

Run from the bundle root:  python _generate_dsx.py
"""
from pathlib import Path

from engine.build_outputs import build_outputs
from engine.models import Component as C
from engine.models import JiraMeta, Story, SubTask

PARENT = "contract-note-data-source-extensibility"
EPIC = PARENT
REPO = Path(__file__).resolve().parents[3]
OUT = REPO / ".kiro" / "specs" / PARENT / "decomposition"


def comp(refs):
    return [C.parse(r) for r in refs]


stories = [
    Story(
        id="US-01",
        title="Foundation: shared data-source types & infrastructure",
        user_story=(
            "As a developer, I want the shared data-source TypeScript types + DynamoDB "
            "record shapes, the Unified Studio Project Role trust-policy change, and the "
            "Athena workgroup + results bucket, so that every other story has a stable "
            "foundation to build on."
        ),
        covers_requirements=["6"],
        exports=comp([
            "shared-lib:data-source-types",
            "cdk-construct:project-role-trust-policy",
            "cdk-construct:athena-workgroup",
        ]),
        subtasks=[
            SubTask("US-01-1", "Extend shared-lib/types.ts with data source entities (TemplateDataSource, SharedSectionDataSourceDependency entity types + records + AvailableDataSource/DataSourceColumn/SectionDataSourceDependency interfaces + SK aliases)", ["2", "4"]),
            SubTask("US-01-2", "Modify Project Role trust policy to allow the data-source + enrich Lambda execution roles to assume it; expose PROJECT_ROLE_ARN as a CDK param/env var", ["6"]),
            SubTask("US-01-3", "Configure Athena workgroup and S3 results bucket; grant the Project Role access to both", ["5"]),
        ],
        jira=JiraMeta(epic=EPIC, labels=["infra", "backend"], estimate_days=1.5),
    ),
    Story(
        id="US-02",
        title="Glue Data Catalog discovery client",
        user_story=(
            "As a Business_User, I want the system to discover the Glue tables available to "
            "the Project Role (filtered to those joinable by bryt_number) with their columns, "
            "so that subscribed data sources become usable without code changes."
        ),
        covers_requirements=["1"],
        exports=comp([
            "shared-lib:glue-catalog-client",
        ]),
        depends_on=comp([
            "shared-lib:data-source-types",
            "cdk-construct:project-role-trust-policy",
        ]),
        subtasks=[
            SubTask("US-02-1", "Implement Glue catalog client: AssumeRole -> Project Role creds, list databases/tables, filter to bryt_number tables, return AvailableDataSource[] with columns", ["1"]),
            SubTask("US-02-2", "Implement column detail fetcher: full column list (name, type) for a specific {database}/{table}", ["3", "7"]),
            SubTask("US-02-3", "Property tests for discovery (Property 1: only bryt_number tables discoverable; Property 11: new subscriptions immediately discoverable)", ["1", "6"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend"], estimate_days=1.0),
    ),
    Story(
        id="US-04",
        title="Data source dependency scanner",
        user_story=(
            "As a Business_User, I want shared sections to automatically track which data "
            "sources they depend on, derived from the namespaced fields used across all of a "
            "section's variant schemas, so that templates using them can be checked."
        ),
        covers_requirements=["4"],
        exports=comp([
            "shared-lib:dependency-scanner",
        ]),
        depends_on=comp([
            "shared-lib:data-source-types",
        ]),
        subtasks=[
            SubTask("US-04-1", "Implement pdf-me schema field-reference scanner: walk all pages of { schemas: [[...]] }, collect element names containing '.', map prefix -> table name", ["4"]),
            SubTask("US-04-2", "Implement shared-section dependency recompute: on variant schema save / version publish, scan all variants' schemas, compute union of referenced data sources, reconcile DATASOURCE_DEP records", ["4"]),
            SubTask("US-04-3", "Property tests for dependency tracking (Property 5: dependency = union across variants)", ["4"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend"], estimate_days=1.0),
    ),
    Story(
        id="US-03",
        title="Data Source API handlers + routing",
        user_story=(
            "As a frontend developer, I want API endpoints to list available data sources, get "
            "their columns, and attach/detach/list data sources on a template (plus a shared "
            "section's tracked dependencies), so that the Admin Portal can manage attachments."
        ),
        covers_requirements=["2", "7"],
        exports=comp([
            "api-endpoint:GET /contract-note-data-sources",
            "api-endpoint:GET /contract-note-data-sources/{database}/{table}/columns",
            "api-endpoint:GET /contract-note-templates/{templateId}/data-sources",
            "api-endpoint:POST /contract-note-templates/{templateId}/data-sources",
            "api-endpoint:DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}",
            "api-endpoint:GET /contract-note-shared-sections/{sharedSectionId}/data-source-dependencies",
            "cdk-construct:DataSourceApi",
        ]),
        depends_on=comp([
            "shared-lib:data-source-types",
            "shared-lib:glue-catalog-client",
            "cdk-construct:project-role-trust-policy",
        ]),
        subtasks=[
            SubTask("US-03-1", "Declare routes in contract-note-foundation.ts: contract-note-data-sources root (+ {database}/{table}/columns), data-sources under templates/{templateId}, data-source-dependencies under shared-sections/{id}; extend ContractNoteApiRoutes with DataSourceRouteResources", ["7"]),
            SubTask("US-03-2", "Implement list-available handler (Glue client -> [{database, tableName, columnCount}])", ["1", "7"]),
            SubTask("US-03-3", "Implement get-columns handler (column names + types for a table)", ["7"]),
            SubTask("US-03-4", "Implement attach-data-source handler (validate table exists + has bryt_number; write DATASOURCE record)", ["2", "7"]),
            SubTask("US-03-5", "Implement detach-data-source handler (scan all sections' variants for referencing fields; 409 with affected section+variant list, else remove)", ["2", "7"]),
            SubTask("US-03-6", "Implement list-attached handler (query DATASOURCE records for a template)", ["2", "7"]),
            SubTask("US-03-7", "Implement list-shared-section-deps handler (query DATASOURCE_DEP records)", ["4"]),
            SubTask("US-03-8", "Create DataSourceApi CDK construct (per-op NodejsFunctions, grant table/Glue/Athena/AssumeRole, wire LambdaIntegrations, pass PROJECT_ROLE_ARN + Athena config); instantiate in contract-note-stack.ts", ["6", "7"]),
            SubTask("US-03-9", "Property tests for data source API (Property 2: attachment round-trip; Property 3: detachment with variant-field-in-use warning)", ["2"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend", "api"], estimate_days=2.0),
    ),
    Story(
        id="US-05",
        title="Render pipeline enrichment (new Step Functions state)",
        user_story=(
            "As a system operator, I want a new enrich-data-sources state between select-template "
            "and render-sections that queries each attached data source by BrytNumber via Athena "
            "and merges the results into ContractData, so that data source fields populate on the PDF."
        ),
        covers_requirements=["5"],
        exports=comp([
            "shared-lib:athena-client",
            "lambda:enrich-data-sources",
            "state-machine:render-pipeline-enrichment",
        ]),
        depends_on=comp([
            "shared-lib:data-source-types",
            "shared-lib:glue-catalog-client",
            "cdk-construct:project-role-trust-policy",
            "cdk-construct:athena-workgroup",
        ]),
        subtasks=[
            SubTask("US-05-1", "Implement Athena query executor (api/src/render/athena-client.ts): assume Project Role; run SELECT * FROM {db}.{table} WHERE bryt_number = ? LIMIT 1; parse rows; no rows -> empty, multiple -> first+warn, error -> throw", ["5"]),
            SubTask("US-05-2", "Implement enrich-data-sources handler (api/src/render/enrich-data-sources.ts): read template DATASOURCE records; none -> pass through; extract customerreference; query each source concurrently; merge under {table}.{column}", ["5"]),
            SubTask("US-05-3", "Wire the state into render-pipeline.ts: add EnrichDataSourcesHandler NodejsFunction, insert between selectTemplate and renderSections, add to handle-failure catch array, grant table read + Athena/AssumeRole", ["5"]),
            SubTask("US-05-4", "Property tests for enrichment (Property 7: namespaced data; 8: empty pass-through; 9: empty rows continue; 10: failure routes to handle-failure)", ["5"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend", "pipeline"], estimate_days=1.5),
    ),
    Story(
        id="US-06",
        title="Frontend: Template Edit data sources panel",
        user_story=(
            "As a Business_User, I want a Data Sources panel on the template edit screen to view, "
            "attach and detach data sources (with an in-use warning), so that a template's sections "
            "can reference their fields."
        ),
        covers_requirements=["2"],
        exports=comp([
            "service:DataSourceService",
            "frontend-component:template-edit-data-sources-panel",
            "frontend-component:data-source-picker-dialog",
        ]),
        depends_on=comp([
            "shared-lib:data-source-types",
            "api-endpoint:GET /contract-note-data-sources",
            "api-endpoint:GET /contract-note-templates/{templateId}/data-sources",
            "api-endpoint:POST /contract-note-templates/{templateId}/data-sources",
            "api-endpoint:DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}",
        ]),
        subtasks=[
            SubTask("US-06-1", "Implement DataSourceService (list available, get columns, attach/detach, list attached, list shared-section deps) wired to the API Gateway endpoints", ["1", "2"]),
            SubTask("US-06-2", "Extend template-edit component with a Data Sources panel (show attached; [+ Attach] picker; detach with confirmation warning if a variant references its fields; available regardless of DRAFT/PUBLISHED)", ["2"]),
            SubTask("US-06-3", "Implement data source picker dialog (available sources excluding attached, with table/database/column count)", ["2"]),
        ],
        jira=JiraMeta(epic=EPIC, labels=["frontend"], estimate_days=1.5),
    ),
    Story(
        id="US-07",
        title="Frontend: section-variant editor field browser & shared-section deps",
        user_story=(
            "As a Business_User, I want data source fields in the section-variant editor palette, a "
            "missing-dependency prompt when adding a shared section, and dependencies shown on the "
            "shared section detail screen, so that I can design enriched sections safely."
        ),
        covers_requirements=["3", "4"],
        exports=comp([
            "frontend-component:section-variant-field-browser",
            "frontend-component:shared-section-dependency-check",
            "frontend-component:shared-section-deps-display",
        ]),
        depends_on=comp([
            "service:DataSourceService",
            "api-endpoint:GET /contract-note-data-sources/{database}/{table}/columns",
            "api-endpoint:GET /contract-note-shared-sections/{sharedSectionId}/data-source-dependencies",
            "shared-lib:dependency-scanner",
        ]),
        subtasks=[
            SubTask("US-07-1", "Surface data source fields in the pdfme-designer palette for the edited variant: collapsible groups per data source; fields labelled {table}.{column} with type, visually distinct; placed fields use the namespaced name", ["3"]),
            SubTask("US-07-2", "Implement shared section attachment dependency check: on adding a shared section, read its DATASOURCE_DEP records; if the template is missing required sources, prompt to add them first", ["4"]),
            SubTask("US-07-3", "Display data source dependencies on the shared section detail screen", ["4"]),
            SubTask("US-07-4", "Property tests for frontend logic (Property 4: field availability scoped to attachments; Property 6: missing dependency enforcement)", ["2", "3", "4"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["frontend"], estimate_days=1.5),
    ),
    Story(
        id="US-08",
        title="Integration wiring & end-to-end validation",
        user_story=(
            "As a developer, I want all components deployed and wired (API Gateway routes, "
            "Lambda->Project Role assume, Athena workgroup/results bucket, env vars) with end-to-end "
            "tests, so that the data source feature works as a whole."
        ),
        covers_requirements=["6"],
        exports=comp([
            "cdk-instance:deployment",
        ]),
        depends_on=comp([
            "cdk-construct:DataSourceApi",
            "lambda:enrich-data-sources",
            "state-machine:render-pipeline-enrichment",
            "frontend-component:template-edit-data-sources-panel",
            "frontend-component:section-variant-field-browser",
        ]),
        subtasks=[
            SubTask("US-08-1", "Finalise CDK deployment: confirm API Gateway routes, Lambda->Project Role assume, Athena workgroup/results bucket, and env vars are all wired in the stack", ["6"]),
            SubTask("US-08-2", "Integration tests: subscribe Glue table -> appears; attach -> drop XML -> enriched fields render; remove bryt_number -> filtered out; force Athena error -> handle-failure", ["1", "5"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["infra", "integration"], estimate_days=1.0),
    ),
]

all_reqs = [str(i) for i in range(1, 8)]
dec = build_outputs(PARENT, stories, OUT, all_requirement_ids=all_reqs)
print("ok:", dec.ok)
print("stories:", len(stories))
print("waves:")
for i, w in enumerate(dec.waves, 1):
    print(f"  wave {i}: {', '.join(w)}")
print("issues:")
for iss in dec.issues:
    print(f"  [{iss.kind}] {iss.detail}")
print("output:", OUT)
