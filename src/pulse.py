from pydantic import BaseModel
from datetime import datetime as dt
import fastapi


class Pulse(BaseModel):
    date: dt


router = fastapi.APIRouter()


@router.get('/pulse', operation_id='get_pulse', response_model=Pulse)
async def get_pulse():
    return {'date': dt.now()}
