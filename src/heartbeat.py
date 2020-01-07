from pydantic import BaseModel
from datetime import datetime as dt
import fastapi


class HeartBeat(BaseModel):
    date: dt


router = fastapi.APIRouter()


@router.get('/heartbeat', operation_id='get_pulse', response_model=HeartBeat)
async def get_heartbeat():
    return {'date': dt.now()}
