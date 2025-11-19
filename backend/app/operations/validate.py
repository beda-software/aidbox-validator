import json
import logging
import uuid

import fhirpy_types_r4b as r4b
from aidbox_python_sdk.types import SDKOperation, SDKOperationRequest
from aiohttp import web
from fhirpy import AsyncFHIRClient

from app import app_keys as ak
from app.sdk import sdk


@sdk.operation(["POST"], ["validate"], public=True)
async def validate_op(_operation: SDKOperation, request: SDKOperationRequest) -> web.Response:
    fhir_client = request["app"][ak.fhir_client]
    request_data = request["resource"]
    await save_request(fhir_client, request_data)
    logging.error("Validation request: %s", request_data)
    formatted_request = official_format_to_aidbox(request_data)
    resource_to_validate = formatted_request["resource"]
    resource_type = resource_to_validate.get("resourceType", "Patient")
    file_info = formatted_request["file_info"]
    session_id = formatted_request["session_id"]

    logging.error("Resource to validate: %s", resource_to_validate)

    validation_results = await fhir_client.execute(
        f"{resource_type}/$validate", method="POST", data=resource_to_validate
    )
    validation_results = aidbox_response_to_official_format(
        validation_results, file_info, session_id, resource_type
    )

    logging.error("Validation results: %s", validation_results)

    return web.json_response(validation_results)


def official_format_to_aidbox(data: dict) -> dict:
    profiles = data.get("cliContext", {}).get("profiles", [])
    files_to_validate = data.get("filesToValidate", [])
    session_id = data.get("sessionId")
    session_id = session_id if session_id else str(uuid.uuid4())

    if not files_to_validate:
        return {"resource": {}, "file_info": {}, "session_id": session_id}

    if len(files_to_validate) == 1:
        try:
            resource_data = files_to_validate[0].get("fileContent", {})
            resource_data = json.loads(resource_data)
        except (json.JSONDecodeError, TypeError) as e:
            return {
                "resource": {},
                "file_info": files_to_validate[0],
                "session_id": session_id,
                "error": f"Invalid JSON: {e!s}",
            }

        if "meta" not in resource_data:
            resource_data["meta"] = {}

        resource_data["meta"]["profile"] = [profile.split("|")[0] for profile in profiles]

        return {
            "resource": resource_data,
            "file_info": files_to_validate[0],
            "session_id": session_id,
        }

    return {
        "resource": {},
        "file_info": files_to_validate[0] if files_to_validate else {},
        "session_id": session_id,
    }


def aidbox_response_to_official_format(
    data: dict, file_info: dict, session_id: str, location: str
) -> dict:
    aidbox_issue_codes_to_ignore = ["invalid-target-profile", "non-existent-resource"]
    issues = data.get("issue", [])
    if len(issues) == 1:
        if issues[0].get("diagnostics") == "all ok":
            return {
                "outcomes": [{"fileInfo": file_info, "issues": []}],
                "sessionId": session_id,
                "validationTimes": {},
            }

    issues = [
        format_issue(issue, location)
        for issue in issues
        if get_aidbox_issue_code(issue) not in aidbox_issue_codes_to_ignore
    ]

    return {
        "outcomes": [{"fileInfo": file_info, "issues": issues}],
        "sessionId": session_id,
        "validationTimes": {},
    }


def format_issue(aidbox_issue: dict, location: str) -> dict:
    logging.error("Aidbox issue: %s", aidbox_issue)
    code = get_aidbox_issue_code(aidbox_issue)
    diagnostics = aidbox_issue.get("diagnostics", "")
    expressions = aidbox_issue.get("expression", [])
    message = f"{expressions[0]}: {diagnostics}" if len(expressions) > 0 else diagnostics

    return {
        "source": "InstanceValidator",
        "line": 1,
        "col": 28,
        "location": location,
        "message": message,
        "messageId": code,
        "type": "STRUCTURE",
        "level": "ERROR",
        "html": message,
        "slicingHint": False,
        "signpost": False,
        "criticalSignpost": False,
        "matched": False,
        "ignorableError": False,
        "count": 0,
    }


def get_aidbox_issue_code(aidbox_issue: dict) -> str:
    issue_coding = aidbox_issue.get("details", {}).get("coding", [])
    if len(issue_coding) == 0:
        return ""

    return issue_coding[0].get("code", "")


async def save_request(fhir_client: AsyncFHIRClient, data: str) -> r4b.DocumentReference:
    doc_ref_r = r4b.DocumentReference(
        status="current",
        content=[
            r4b.DocumentReferenceContent(
                attachment=r4b.Attachment(contentType="text/plain", data=str(data))
            )
        ],
    )

    return await fhir_client.save(doc_ref_r)
