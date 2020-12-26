from pydantic import BaseModel
from datetime import datetime as dt
import fastapi
from fastapi.responses import ORJSONResponse


class HeartBeat(BaseModel):
    date: dt


router = fastapi.APIRouter()


@router.get(
    '/heartbeat',
    operation_id='get_heartbeat',
    response_model=HeartBeat,
    response_class=ORJSONResponse,
)
async def get_heartbeat():
    data = {
        'date': dt.now(),
    }
    return data
