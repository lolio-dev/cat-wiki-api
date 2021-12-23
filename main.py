from fastapi import FastAPI

from .app.routers import breeds

app = FastAPI()

app.include_router(
    breeds.router,
    prefix='/breeds',
    tags=['breeds'],
    responses={
        404: {'error:': 'Sorry, there is an error in the process'},
        200: {'hello': 'world'}
    })


@app.get('/')
async def root():
    return {'Welcome to the cat api :)'}
