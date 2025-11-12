
from fastapi import APIRouter, Depends, HTTPException, Query
from app.deps import get_current_uid
from httpx import HTTPStatusError

from app.mem0_client import mem0
from app.config import settings

router = APIRouter(prefix="/memory", tags=["memory"])

def handle_mem0_error(e: HTTPStatusError):
    if settings.IS_DEV:
        return {"status_code": e.response.status_code, "detail": e.response.json() if e.response.content else str(e)}
    else:
        detail_map = {400: "Bad request", 403: "Not allowed", 404: "Request error"}
        return {"status_code": e.response.status_code, "detail": detail_map.get(e.response.status_code, "Request error")}

def handle_generic_error(e: Exception):
    if settings.IS_DEV:
        return {"status_code": 500, "detail": str(e)}
    else:
        return {"status_code": 500, "detail": "Internal server error"}

@router.get("/all")
async def get_all_memory(
    uid: str = Depends(get_current_uid),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200)
):
    """
    Get all memory belonging to the current user.
    """
    try:
        filters = {
            "user_id": uid
        }
        result = await mem0.get_all(filters=filters, page=page, page_size=page_size)
        
        memories = result.get("results") or []
        
        sanitized_memories = [
            {k: v for k, v in mem.items() if k != "user_id"} for mem in memories
        ]
        
        return {
            "count": result.get("count"),
            "page": page,
            "page_size": page_size,
            "results": sanitized_memories
        }
    except HTTPStatusError as e:
        raise HTTPException(**handle_mem0_error(e))

    except Exception as e:
        raise HTTPException(**handle_generic_error(e))
    
        


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, uid: str = Depends(get_current_uid)):
    """
    Delete a specific memory of the current user
    """
    try:
        mem = await mem0.get(memory_id=memory_id)
        if not mem:
            raise HTTPException(status_code=404, detail="Memory not found")

        if mem.get("user_id") != uid:
            raise HTTPException(status_code=403, detail="Not allowed")

        result = await mem0.delete(memory_id=memory_id)
        return result
    except HTTPStatusError as e:
        raise HTTPException(**handle_mem0_error(e))
            
    except Exception as e:
        raise HTTPException(**handle_generic_error(e))
