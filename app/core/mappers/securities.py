import pandas as pd
from app.models.security import Security





def security_to_dict(security: Security) -> dict:
    return {
        "id": security.id,
        "name": security.name,
        "platform": security.platform,
        "type": security.type,
        "status": security.status,
    }

def securities_to_df(securities: list[Security]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": s.id,
                "name": s.name,
                "platform": s.platform,
                "type": s.type,
                "status": s.status,
            }
            for s in securities
        ]
    )