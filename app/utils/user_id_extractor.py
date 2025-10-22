from ag_ui.core.types import RunAgentInput

from app.auth import verify_token

def user_id_extractor(input_data: RunAgentInput) -> str | None:
    """
    Extracts user_id by verifying the token from forwarded_props["authorization"].
    Replaces token with user_id in forwarded_props.
    """
    props = input_data.forwarded_props
    if not props or not isinstance(props, dict):
        return None

    token = props.get("authorization", None)
    if not token:
        return None

    try:
        user_id = verify_token(token)
        if user_id:
            return user_id
    except Exception:
        return None

    return None