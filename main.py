from fastapi import FastAPI
from .app.routers.breeds import router

app = FastAPI()

app.include_router(
    router=router,
    prefix='/breeds',
    tags=['breeds'],
    responses={
        404: {'error:': 'Sorry, there is an error in the process'},
        200: {'hello': 'world'}
    })


@app.get('/')
async def root():
    return {'Welcome to the cat api :)'}
