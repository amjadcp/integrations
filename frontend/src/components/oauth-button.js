import { useState, useEffect } from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import { backendClient } from '../utils/axios';

export const OAuthIntegrationButton = ({
  user,
  org,
  integrationType,
  label,
  integrationParams,
  setIntegrationParams,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnectClick = async () => {
    try {
      setIsConnecting(true);
      const formData = new FormData();
      formData.append('user_id', user);
      formData.append('org_id', org);
      const { data: authURL } = await backendClient.post(`/integrations/${integrationType}/authorize`, formData);

      const newWindow = window.open(authURL, `${label} Authorization`, 'width=600,height=600');

      const pollTimer = window.setInterval(() => {
        if (newWindow?.closed !== false) {
          window.clearInterval(pollTimer);
          handleWindowClosed();
        }
      }, 200);
    } catch (e) {
      setIsConnecting(false);
      alert(e?.response?.data?.detail || `Failed to connect to ${label}`);
    }
  };

  const handleWindowClosed = async () => {
    try {
      const formData = new FormData();
      formData.append('user_id', user);
      formData.append('org_id', org);
      const { data: credentials } = await backendClient.post(`/integrations/${integrationType}/credentials`, formData);

      if (credentials) {
        setIsConnecting(false);
        setIsConnected(true);
        setIntegrationParams(prev => ({ ...prev, credentials, type: label }));
      }
    } catch (e) {
      alert(e?.response?.data?.detail || `Could not fetch ${label} credentials`);
    } finally {
      setIsConnecting(false);
    }
  };

  useEffect(() => {
    setIsConnected(Boolean(integrationParams?.credentials));
  }, [integrationParams]);

  return (
    <Box sx={{ mt: 2 }}>
      Parameters
      <Box display="flex" alignItems="center" justifyContent="center" sx={{ mt: 2 }}>
        <Button
          variant="contained"
          onClick={isConnected ? () => {} : handleConnectClick}
          color={isConnected ? 'success' : 'primary'}
          disabled={isConnecting}
          style={{
            pointerEvents: isConnected ? 'none' : 'auto',
            cursor: isConnected ? 'default' : 'pointer',
            opacity: isConnected ? 1 : undefined,
          }}
        >
          {isConnected
            ? `${label} Connected`
            : isConnecting
            ? <CircularProgress size={20} />
            : `Connect to ${label}`}
        </Button>
      </Box>
    </Box>
  );
};
