from pydantic import BaseModel
from datetime import datetime as dt
import fastapi


class Pulse(BaseModel):
    date: dt


router = fastapi.APIRouter()


@router.get('/pulse', response_model=Pulse)
async def pulse():
    return {'date': dt.now()}
