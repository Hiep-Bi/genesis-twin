import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
} from '@mui/material';
import { machinesAPI } from '../services/api';

const Machines = () => {
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMachines();
  }, []);

  const fetchMachines = async () => {
    try {
      const response = await machinesAPI.getAll();
      setMachines(response.data);
    } catch (error) {
      console.error('Failed to fetch machines:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'success';
      case 'idle': return 'warning';
      case 'maintenance': return 'info';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Machines
      </Typography>

      <Grid container spacing={3}>
        {machines.map((machine) => (
          <Grid item xs={12} sm={6} md={4} key={machine.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">{machine.name}</Typography>
                  <Chip
                    label={machine.status}
                    color={getStatusColor(machine.status)}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Code: {machine.machine_code}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Type: {machine.machine_type}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Machines;

