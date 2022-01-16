import sys
sys.path.append("..")

from fastapi import APIRouter

router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={401:{"user": "Not authorized"}}
)


@router.get("/")
async def test():
    return {'message': 'Welcome to your test page'}
