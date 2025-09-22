# hubspot.py

import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
from urllib.parse import quote

from config.settings import get_settings
from integrations.integration_item import HubspotItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

# Load settings
settings = get_settings()
CLIENT_ID = settings.HUBSPOT_CLIENT_ID
CLIENT_SECRET = settings.HUBSPOT_CLIENT_SECRET
print(f"HubSpot Client ID: {CLIENT_ID}")
print(f"HubSpot Client Secret: {CLIENT_SECRET}")
ROOT_URL = settings.ROOT_URL
REDIRECT_URI = f'{ROOT_URL}/integrations/hubspot/oauth2callback'

authorization_url = f'https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={quote(REDIRECT_URI)}'
scope = quote('oauth crm.objects.companies.read crm.objects.contacts.read crm.objects.deals.read tickets')

async def authorize(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)

    return f'{authorization_url}&state={encoded_state}&scope={scope}'

async def oauth2callback(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')
    
    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        )
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    print(f"HubSpot credentials: {credentials}")
    return credentials

async def create_integration_item_metadata_object(
    response_json: dict, item_type: str, parent_id=None, parent_name=None
) -> HubspotItem:
    """Creates an integration item metadata object from the response"""
    
    item_id = response_json.get("id")
    created_at = response_json.get("createdAt")
    updated_at = response_json.get("updatedAt")
    archived = response_json.get("archived", False)
    archived_at = response_json.get("archivedAt")
    
    props = response_json.get("properties", {})
    assocs = response_json.get("associations", {})

    firstname = props.get("firstname")
    lastname = props.get("lastname")
    email = props.get("email")

    company_name = props.get("name")
    domain = props.get("domain")

    dealname = props.get("dealname")
    amount = props.get("amount") 
    stage = props.get("stage")

    subject = props.get("subject")
    status = props.get("status")
    
   
    integration_item_metadata = HubspotItem(
        id=item_id,
        type=item_type,
        created_at=created_at,
        updated_at=updated_at,
        archived=archived,
        archived_at=archived_at,
        
        firstname=firstname,
        lastname=lastname,
        email=email,
        
        company_name=company_name,
        domain=domain,
        
        dealname=dealname,
        amount=float(amount) if amount not in (None, "") else None,
        stage=stage,
        
        subject=subject,
        status=status,
        
        associations=assocs,
        raw_properties=props,
    )
    
    return integration_item_metadata


async def fetch_items(
    access_token: str, url: str, item_type: str, 
    list_of_integration_item_metadata: list, 
    after=None, limit=100
) -> None:
    """Fetching paginated items from HubSpot API endpoints"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {'limit': limit}
    if after:
        params['after'] = after
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for item in results:
                    integration_item = await create_integration_item_metadata_object(
                        item, item_type
                    )
                    list_of_integration_item_metadata.append(integration_item)
                
                # Check if there are more pages
                next_page = data.get('paging', {}).get('next', {}).get('after')
                if next_page:
                    await fetch_items(
                        access_token, url, item_type, 
                        list_of_integration_item_metadata,
                        next_page, limit
                    )
    except Exception as e:
        print(f"Error fetching {item_type}: {e}")

async def get_items(credentials) -> list[HubspotItem]:
    """Aggregates all metadata relevant for a HubSpot integration"""
    credentials = json.loads(credentials)
    access_token = credentials.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token found in credentials")
    
    list_of_integration_item_metadata = []
    
    tasks = [
        fetch_items(
            access_token,
            'https://api.hubapi.com/crm/v3/objects/contacts',
            'Contact',
            list_of_integration_item_metadata
        ),
        fetch_items(
            access_token,
            'https://api.hubapi.com/crm/v3/objects/companies',
            'Company',
            list_of_integration_item_metadata
        ),
        fetch_items(
            access_token,
            'https://api.hubapi.com/crm/v3/objects/deals',
            'Deal',
            list_of_integration_item_metadata
        ),
        fetch_items(
            access_token,
            'https://api.hubapi.com/crm/v3/objects/tickets',
            'Ticket',
            list_of_integration_item_metadata
        )
    ]
    
    await asyncio.gather(*tasks)
    
    print(f"HubSpot Integration Items: {list_of_integration_item_metadata}")
    
    return list_of_integration_item_metadata