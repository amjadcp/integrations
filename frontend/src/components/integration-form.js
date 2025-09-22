import { useState } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
} from '@mui/material';
import { OAuthIntegrationButton } from './oauth-button';
import { DataForm } from './data-form';

const integrationTypes = [
    'Notion',
    'Airtable',
    'Hubspot'
];

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);

  return (
    <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' sx={{ width: '100%' }}>
        <Box display='flex' flexDirection='column'>
        <TextField
            label="User"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            sx={{mt: 2}}
        />
        <TextField
            label="Organization"
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            sx={{mt: 2}}
        />
        <Autocomplete
            id="integration-type"
            options={integrationTypes}
            sx={{ width: 300, mt: 2 }}
            renderInput={(params) => <TextField {...params} label="Integration Type" />}
            onChange={(e, value) => setCurrType(value)}
        />
        </Box>
        {currType && 
        <Box>
            <OAuthIntegrationButton user={user} org={org} integrationParams={integrationParams} setIntegrationParams={setIntegrationParams} integrationType={currType.toLowerCase()} label={currType} />
        </Box>
        }
        {integrationParams?.credentials && 
        <Box sx={{mt: 2}}>
            <DataForm integrationType={integrationParams?.type} credentials={integrationParams?.credentials} />
        </Box>
        }
    </Box>
  );
}
