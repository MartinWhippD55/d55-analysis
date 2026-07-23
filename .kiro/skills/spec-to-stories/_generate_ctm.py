"""
One-off: decompose the contract-note-template-management spec into user stories
and emit the decomposition (graph.yaml, jira-import.*, README.md, manifests).

Run from the bundle root:  python _generate_ctm.py
"""
from pathlib import Path

from engine.build_outputs import build_outputs
from engine.models import Component as C
from engine.models import JiraMeta, Story, SubTask

PARENT = "contract-note-template-management"
EPIC = PARENT
REPO = Path(__file__).resolve().parents[3]
OUT = REPO / ".kiro" / "specs" / PARENT / "decomposition"


def comp(refs):
    return [C.parse(r) for r in refs]


stories = [
    Story(
        id="US-01",
        title="Foundation: infrastructure & shared types",
        user_story=("As a developer, I want the base table, buckets, API Gateway routes, shared "
                    "types and the specification-tree validator, so that every other story has a "
                    "stable foundation to build on."),
        covers_requirements=["1", "5", "10", "14"],
        exports=comp([
            "shared-lib:types",
            "shared-lib:spec-validation",
            "data-table:ContractNoteTemplates",
            "gsi:PriorityIndex",
            "s3-bucket:schema-json",
            "s3-bucket:error-output",
            "cdk-construct:ApiGatewayRoutes",
        ]),
        subtasks=[
            SubTask("US-01-1", "CDK: DynamoDB table + PriorityIndex GSI, S3 buckets, API Gateway routes", ["1", "5", "14"]),
            SubTask("US-01-2", "Shared TypeScript interfaces and DynamoDB record types", ["10"]),
            SubTask("US-01-3", "Specification tree validation utility", ["10"]),
            SubTask("US-01-4", "Property tests for specification validation", ["10"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["infra", "backend"], estimate_days=2.5),
    ),
    Story(
        id="US-02",
        title="Template CRUD API",
        user_story=("As a Business_User, I want to create, list, edit, delete and reorder templates, "
                    "so that I can manage contract note template definitions."),
        covers_requirements=["1", "2", "3", "4", "5"],
        exports=comp([
            "api-endpoint:GET /contract-note-templates",
            "api-endpoint:POST /contract-note-templates",
            "api-endpoint:PUT /contract-note-templates/{id}",
            "api-endpoint:DELETE /contract-note-templates/{id}",
            "api-endpoint:PUT /contract-note-templates/reorder",
            "lambda:template-handlers",
        ]),
        depends_on=comp([
            "shared-lib:types",
            "data-table:ContractNoteTemplates",
            "gsi:PriorityIndex",
            "cdk-construct:ApiGatewayRoutes",
        ]),
        subtasks=[
            SubTask("US-02-1", "list-templates handler (priority-ordered)", ["1"]),
            SubTask("US-02-2", "create-template handler (validation, duplicate check, priority)", ["2"]),
            SubTask("US-02-3", "get/update/delete-template handlers", ["3", "4"]),
            SubTask("US-02-4", "reorder-templates handler", ["5"]),
            SubTask("US-02-5", "Property tests for template API logic", ["1", "2", "3", "4", "5"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend", "api"], estimate_days=1.5),
    ),
    Story(
        id="US-03",
        title="Section, shared-section, version history & change log API",
        user_story=("As a Business_User, I want to compose sections, edit their schema with version "
                    "history, manage shared sections and see a change log, so that I can build and "
                    "maintain template content."),
        covers_requirements=["3", "6", "7", "8", "9", "16", "17"],
        exports=comp([
            "api-endpoint:sections-crud",
            "api-endpoint:section-schema",
            "api-endpoint:section-versions",
            "api-endpoint:shared-sections-crud",
            "api-endpoint:template-changelog",
            "lambda:section-handlers",
        ]),
        depends_on=comp([
            "shared-lib:types",
            "data-table:ContractNoteTemplates",
            "s3-bucket:schema-json",
            "cdk-construct:ApiGatewayRoutes",
        ]),
        subtasks=[
            SubTask("US-03-1", "list/add/remove/reorder-section handlers (incl. T&C positioning)", ["3", "6", "9"]),
            SubTask("US-03-2", "get/save-section-schema handlers (writes a new version)", ["7", "16"]),
            SubTask("US-03-3", "section version history handlers (list/get/revert)", ["16"]),
            SubTask("US-03-4", "shared section CRUD handlers + references", ["8", "9"]),
            SubTask("US-03-5", "template change log", ["17"]),
            SubTask("US-03-6", "Property tests for section API logic", ["3", "6", "7", "8", "9", "16", "17"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend", "api"], estimate_days=2.0),
    ),
    Story(
        id="US-04",
        title="Section version publishing & variants API",
        user_story=("As a Business_User, I want to publish a section version to all linked templates "
                    "and define rule-driven section variants, so that I control rollout and can render "
                    "alternatives from one section slot."),
        covers_requirements=["18", "19"],
        exports=comp([
            "api-endpoint:section-publish",
            "api-endpoint:section-variants-crud",
            "api-endpoint:variant-rule",
            "lambda:variant-publish-handlers",
        ]),
        depends_on=comp([
            "shared-lib:types",
            "shared-lib:spec-validation",
            "data-table:ContractNoteTemplates",
            "api-endpoint:section-versions",
        ]),
        subtasks=[
            SubTask("US-04-1", "get-linked-templates + publish-section-version handlers", ["18"]),
            SubTask("US-04-2", "section variant CRUD handlers (order, default)", ["19"]),
            SubTask("US-04-3", "variant rule get/save handlers (reuse validation)", ["19"]),
            SubTask("US-04-4", "Property tests for publishing and variants", ["18", "19"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend", "api"], estimate_days=1.0),
    ),
    Story(
        id="US-05",
        title="Template selection rules API",
        user_story=("As a Business_User, I want to get and save a template's selection rule, so that the "
                    "pipeline can pick the right template automatically."),
        covers_requirements=["10"],
        exports=comp([
            "api-endpoint:template-rule",
            "lambda:rules-handlers",
        ]),
        depends_on=comp([
            "shared-lib:types",
            "shared-lib:spec-validation",
            "data-table:ContractNoteTemplates",
            "cdk-construct:ApiGatewayRoutes",
        ]),
        subtasks=[
            SubTask("US-05-1", "get-rule handler", ["10"]),
            SubTask("US-05-2", "save-rule handler (validate specification)", ["10"]),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend", "api"], estimate_days=0.5),
    ),
    Story(
        id="US-06",
        title="Render pipeline (Step Functions)",
        user_story=("As a Business_User, I want contract data to be rendered to a PDF automatically via "
                    "an orchestrated pipeline that selects the template, resolves pinned versions, picks "
                    "section variants, renders and stitches, so that contract notes are produced reliably."),
        covers_requirements=["11", "12", "13", "14", "18", "19", "20"],
        exports=comp([
            "state-machine:RenderStateMachine",
            "shared-lib:spec-evaluator",
            "lambda:parse-input",
            "lambda:select-template",
            "lambda:render-section",
            "lambda:stitch",
            "lambda:write-output",
            "lambda:handle-failure",
            "s3-bucket:input-xml",
            "s3-bucket:output-pdf",
        ]),
        depends_on=comp([
            "shared-lib:types",
            "data-table:ContractNoteTemplates",
            "gsi:PriorityIndex",
            "s3-bucket:schema-json",
            "s3-bucket:error-output",
        ]),
        subtasks=[
            SubTask("US-06-1", "Specification evaluator", ["11"]),
            SubTask("US-06-2", "Template selection (first-match-wins)", ["11"]),
            SubTask("US-06-3", "Section renderer (pdf-me) + pinned-version resolution", ["12", "18"]),
            SubTask("US-06-4", "Section variant selection (first match, default fallback)", ["19"]),
            SubTask("US-06-5", "PDF stitcher (pdf-lib)", ["13"]),
            SubTask("US-06-6", "Step Functions state handlers + Map state + failure state", ["20"]),
            SubTask("US-06-7", "XML-to-JSON parse + S3 trigger", ["14"]),
            SubTask("US-06-8", "Property tests: evaluation, variants, stitching, failure isolation", ["11", "12", "13", "14", "19", "20"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["backend", "pipeline", "infra"], estimate_days=3.0),
    ),
    Story(
        id="US-07",
        title="pdf-me Designer web component",
        user_story=("As a Business_User, I want an embedded visual designer, so that I can position "
                    "fields on a section layout without developer help."),
        covers_requirements=["7"],
        exports=comp([
            "web-component:pdfme-designer",
        ]),
        subtasks=[
            SubTask("US-07-1", "<pdfme-designer> web component wrapping the React pdf-me Designer", ["7"]),
            SubTask("US-07-2", "schema-json in / schema-save event out; on-demand bundle load", ["7"]),
        ],
        jira=JiraMeta(epic=EPIC, labels=["frontend"], estimate_days=1.0),
    ),
    Story(
        id="US-08",
        title="Angular module, routing & services",
        user_story=("As a Business_User, I want the contract-note admin module wired into the portal "
                    "with auth-guarded routes and API services, so that the screens have data and access "
                    "is restricted."),
        covers_requirements=["15"],
        exports=comp([
            "frontend-component:ContractNoteModule",
            "service:TemplateService",
            "service:SectionService",
            "service:RulesService",
        ]),
        depends_on=comp([
            "shared-lib:types",
            "api-endpoint:GET /contract-note-templates",
            "api-endpoint:sections-crud",
            "api-endpoint:section-versions",
            "api-endpoint:section-publish",
            "api-endpoint:section-variants-crud",
            "api-endpoint:variant-rule",
            "api-endpoint:shared-sections-crud",
            "api-endpoint:template-rule",
        ]),
        subtasks=[
            SubTask("US-08-1", "ContractNoteModule with routes + Cognito group route guard", ["15"]),
            SubTask("US-08-2", "TemplateService, SectionService, RulesService wired to the API", ["15"]),
        ],
        jira=JiraMeta(epic=EPIC, labels=["frontend"], estimate_days=1.0),
    ),
    Story(
        id="US-09",
        title="Angular screens & components",
        user_story=("As a Business_User, I want the full set of screens (template list, template edit, "
                    "rules config, section editor, shared sections, version history, variants, publish) "
                    "and navigation, so that I can manage everything from the portal."),
        covers_requirements=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "16", "17", "18", "19", "21"],
        exports=comp([
            "frontend-screen:TemplateList",
            "frontend-screen:TemplateEdit",
            "frontend-screen:SharedSectionsLibrary",
            "frontend-component:RulesConfigComponent",
            "frontend-component:SectionEditorComponent",
            "frontend-component:SectionVersionHistoryComponent",
            "frontend-component:SectionVariantsComponent",
            "frontend-component:SectionPublishComponent",
            "frontend-component:Navigation",
        ]),
        depends_on=comp([
            "frontend-component:ContractNoteModule",
            "service:TemplateService",
            "service:SectionService",
            "service:RulesService",
            "web-component:pdfme-designer",
        ]),
        subtasks=[
            SubTask("US-09-1", "TemplateListComponent (landing page)", ["1", "4", "5"]),
            SubTask("US-09-2", "TemplateEditComponent + change log + variant list", ["2", "3", "6", "17", "19"]),
            SubTask("US-09-3", "RulesConfigComponent (shared by template + variant rules)", ["10"]),
            SubTask("US-09-4", "SectionEditorComponent host (modal)", ["7"]),
            SubTask("US-09-5", "SharedSectionsComponent + detail", ["8", "9"]),
            SubTask("US-09-6", "SectionVersionHistoryComponent + SectionPublishComponent", ["16", "18"]),
            SubTask("US-09-7", "Navigation + landing pages (page vs modal)", ["21"]),
            SubTask("US-09-8", "Component unit tests", ["1", "10", "18", "19"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["frontend"], estimate_days=3.0),
    ),
    Story(
        id="US-10",
        title="Integration wiring & end-to-end validation",
        user_story=("As a developer, I want all components deployed and wired (IAM, S3 trigger, API "
                    "Gateway, portal navigation) with end-to-end tests, so that the feature works as a whole."),
        covers_requirements=["14", "15", "20"],
        exports=comp([
            "cdk-instance:deployment",
        ]),
        depends_on=comp([
            "lambda:template-handlers",
            "lambda:section-handlers",
            "lambda:variant-publish-handlers",
            "lambda:rules-handlers",
            "state-machine:RenderStateMachine",
            "frontend-component:Navigation",
        ]),
        subtasks=[
            SubTask("US-10-1", "CDK deployment wiring: IAM, S3-triggered state machine, API routes, CORS", ["14", "20"]),
            SubTask("US-10-2", "Portal sidebar navigation entry (Cognito-gated)", ["15"]),
            SubTask("US-10-3", "End-to-end pipeline integration tests", ["14"], optional=True),
        ],
        jira=JiraMeta(epic=EPIC, labels=["infra", "integration"], estimate_days=1.0),
    ),
]

all_reqs = [str(i) for i in range(1, 22)]
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
