import json
import logging

from aidbox_python_sdk.types import SDKOperation, SDKOperationRequest
from aiohttp import web

from app import app_keys as ak
from app.sdk import sdk


@sdk.operation(["POST"], ["validate"], public=True)
async def validate_op(_operation: SDKOperation, request: SDKOperationRequest) -> web.Response:
    fhir_client = request["app"][ak.fhir_client]
    request_data = request["resource"]
    logging.info("Validation request: %s", request_data)
    formatted_request = official_format_to_aidbox(request_data)
    resource_to_validate = formatted_request["resource"]
    resource_type = resource_to_validate["resourceType"]
    file_info = formatted_request["file_info"]
    session_id = formatted_request["session_id"]

    validation_results = await fhir_client.execute(
        f"{resource_type}/$validate", method="POST", data=resource_to_validate
    )
    validation_results = aidbox_response_to_official_format(
        validation_results, file_info, session_id, resource_type
    )

    logging.info("Validation results: %s", validation_results)

    return web.json_response(validation_results)


def official_format_to_aidbox(data: dict) -> dict:
    profiles = data.get("cliContext", {}).get("profiles", [])
    files_to_validate = data.get("filesToValidate", [])
    session_id = data.get("sessionId", "")
    if len(files_to_validate) == 1:
        resource_data = files_to_validate[0].get("fileContent", {})
        resource_data = json.loads(resource_data)
        resource_data_meta = resource_data.get("meta", {})
        resource_data["meta"] = {**resource_data_meta, "profile": profiles}

        return {
            "resource": resource_data,
            "file_info": files_to_validate[0],
            "session_id": session_id,
        }
    return {"resource": {}, "file_info": files_to_validate[0], "session_id": session_id}


def aidbox_response_to_official_format(
    data: dict, file_info: dict, session_id: str, location: str
) -> dict:
    issues = data.get("issue", [])
    issues = [format_issue(issue, location) for issue in issues]

    return {
        "outcomes": [{"fileInfo": file_info, "issues": issues}],
        "sessionId": session_id,
        "validationTimes": {},
    }


def format_issue(aidbox_issue: dict, location: str) -> dict:
    expression = aidbox_issue.get("expression", [])[0]
    code = aidbox_issue.get("details", {}).get("coding", [])[0].get("code", "")
    diagnostics = aidbox_issue.get("diagnostics", "")
    message = f"{expression}: {diagnostics}"

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
