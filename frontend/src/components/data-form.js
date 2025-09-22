import { useState } from 'react';
import {
   Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography
} from '@mui/material';
import { backendClient } from '../utils/axios';

const endpointMapping = {
    'Notion': 'notion',
    'Airtable': 'airtable',
    'Hubspot': 'hubspot'
};

const columnMappings = {
  Notion: [
    { key: 'id', label: 'ID' },
    { key: 'type', label: 'Type' },
    { key: 'parent_id', label: 'Parent ID' },
    { key: 'name', label: 'Name' },
    { key: 'creation_time', label: 'Creation Time' },
    { key: 'last_modified_time', label: 'Last Modified Time' },
  ],
  Airtable: [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'type', label: 'Type' },
    { key: 'parent_id', label: 'Parent ID' },
    { key: 'parent_path_or_name', label: 'Parent Path/Name' },
  ],
  Hubspot: [
    { key: 'id', label: 'ID' },
    { key: 'type', label: 'Type' },
    { key: 'created_at', label: 'Created At' },
    { key: 'updated_at', label: 'Updated At' },
    { key: 'archived', label: 'Archived' },
    { key: 'archived_at', label: 'Archived At' },

    // Contact
    { key: 'firstname', label: 'First Name' },
    { key: 'lastname', label: 'Last Name' },
    { key: 'email', label: 'Email' },

    // Company
    { key: 'company_name', label: 'Company Name' },
    { key: 'domain', label: 'Domain' },

    // Deal
    { key: 'dealname', label: 'Deal Name' },
    { key: 'amount', label: 'Amount' },
    { key: 'stage', label: 'Stage' },

    // Ticket
    { key: 'subject', label: 'Subject' },
    { key: 'status', label: 'Status' },
  ]
};

export const DataForm = ({ integrationType, credentials }) => {
  const [loadedData, setLoadedData] = useState([]);
  const endpoint = endpointMapping[integrationType];

  const handleLoad = async () => {
    try {
      const formData = new FormData();
      formData.append('credentials', JSON.stringify(credentials));
      const response = await backendClient.post(`/integrations/${endpoint}/load`, formData);
      setLoadedData(response.data || []);
    } catch (e) {
      alert(e?.response?.data?.detail || 'Failed to load data');
    }
  };

  const handleClear = () => setLoadedData([]);

  const columns = columnMappings[integrationType] || [];

  return (
    <Box display="flex" flexDirection="column" alignItems="center" width="100%">
      <Box width="100%" mb={2}>
        <Button onClick={handleLoad} variant="contained" sx={{ mr: 1 }}>
          Load Data
        </Button>
        <Button onClick={handleClear} variant="outlined">
          Clear Data
        </Button>
      </Box>

      {loadedData.length > 0 ? (
        <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
          <Table>
            <TableHead>
              <TableRow>
                {columns.map((col) => (
                  <TableCell key={col.key}>{col.label}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {loadedData.map((item, index) => (
                <TableRow key={index}>
                  {columns.map((col) => (
                    <TableCell key={col.key}>
                      {item[col.key] !== null && item[col.key] !== undefined
                        ? String(item[col.key])
                        : '-'}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Typography variant="body2" color="text.secondary" mt={2}>
          No data loaded yet.
        </Typography>
      )}
    </Box>
  );
};
