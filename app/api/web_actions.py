from fastapi import APIRouter

from fastapi import HTTPException

from app.schemas import WebActionExecuteRequest, WebActionExecuteResponse, WebActionPlanRequest, WebActionPlanResponse
from app.services.web_actions import open_website
from app.services.web_action_planner import make_web_action_plan

router = APIRouter(prefix="/api/web-actions", tags=["web-actions"])


# ==============================================================================
# PHASE 4: THE HANDS (Safe Web Actions Route)
# ==============================================================================
@router.post("/plan", response_model=WebActionPlanResponse)
async def plan_web_action(request: WebActionPlanRequest) -> WebActionPlanResponse:
    """
    TODO (Phase 4 - Step 9):
    Return planned destination URL for frontend user confirmation.
    """
    plan = make_web_action_plan(request.text)
    return WebActionPlanResponse(**plan)


@router.post("/execute", response_model=WebActionExecuteResponse)
async def execute_web_action(request: WebActionExecuteRequest) -> WebActionExecuteResponse:
    try:
        result = open_website(request.url, request.browser, request.new_tab)
    except (FileNotFoundError, OSError, ValueError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    browser_name = "Chrome" if result.browser == "chrome" else "your default browser"
    return WebActionExecuteResponse(success=True, action=request.kind, message=f"Opened the website in {browser_name}.")
