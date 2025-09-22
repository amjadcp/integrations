from fastapi import FastAPI, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from integrations.integration_interface import integration_interface

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_valid_integration_interface(integration_name):
    return integration_interface(integration_name)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

# Four standardized endpoints for all integrations
@app.post('/integrations/{integration_name}/authorize')
async def authorize_integration(user_id = Form(...), org_id = Form(...), integration_module = Depends(get_valid_integration_interface)):
    return await integration_module.authorize(user_id, org_id)

@app.get('/integrations/{integration_name}/oauth2callback')
async def oauth2callback_integration(request: Request, integration_module = Depends(get_valid_integration_interface)):
    return await integration_module.oauth2callback(request)

@app.post('/integrations/{integration_name}/credentials')
async def get_integration_credentials(user_id = Form(...), org_id = Form(...), integration_module = Depends(get_valid_integration_interface)):
    return await integration_module.get_credentials(user_id, org_id)

@app.post('/integrations/{integration_name}/load')
async def load_integration_items(credentials = Form(...), integration_module = Depends(get_valid_integration_interface)):
    return await integration_module.get_items(credentials)
