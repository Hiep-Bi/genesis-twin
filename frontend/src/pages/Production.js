import {
  Assignment,
  AutoGraph,
  BuildCircle,
  PlaylistAddCheck,
} from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { factoryOperationsAPI } from '../services/api';

const mockWorkflowStats = {
  total_orders: 18,
  completed_steps: 92,
  pending_steps: 7,
  bottlenecks: ['Assembly', 'Packaging'],
};

const mockRecoveryPlan = {
  prioritized_lines: [
    {
      line_code: 'LINE-01',
      priority_score: 0.92,
      estimated_recovery_minutes: 45,
    },
    {
      line_code: 'LINE-02',
      priority_score: 0.74,
      estimated_recovery_minutes: 70,
    },
  ],
  recommendations: [
    'Use materials from external staging for LINE-01 to reduce downtime.',
    'Assign maintenance crew B to LINE-02 after LINE-01 completes.',
  ],
};

const mockAvailability = {
  requests: [{ material_code: 'MAT-001', required_quantity: 2.5 }],
  locations: [
    { location: 'external_staging', available_quantity: 3 },
    { location: 'main_warehouse', available_quantity: 12 },
  ],
  is_sufficient: true,
};

const Production = () => {
  const [workflowStats, setWorkflowStats] = useState(null);
  const [recoveryLines, setRecoveryLines] = useState('LINE-01, LINE-02');
  const [recoveryPlan, setRecoveryPlan] = useState(null);
  const [availabilityInput, setAvailabilityInput] = useState({
    material_code: 'MAT-001',
    required_quantity: 2,
  });
  const [availabilityResult, setAvailabilityResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchWorkflowStats();
  }, []);

  const fetchWorkflowStats = async () => {
    try {
      const response = await factoryOperationsAPI.getWorkflowStatistics();
      setWorkflowStats(response.data || mockWorkflowStats);
    } catch (err) {
      console.warn('Failed to fetch workflow stats, using mock data.', err);
      setWorkflowStats(mockWorkflowStats);
    }
  };

  const handleAnalyzeRecovery = async () => {
    const lines = recoveryLines
      .split(',')
      .map((line) => line.trim())
      .filter(Boolean);
    if (lines.length === 0) {
      setRecoveryPlan(null);
      return;
    }

    setLoading(true);
    try {
      const response = await factoryOperationsAPI.analyzeRecovery({
        affected_lines: lines,
        agv_server_status: 'down',
      });
      setRecoveryPlan(response.data || response || mockRecoveryPlan);
    } catch (err) {
      console.warn('Failed to analyze recovery, using mock data', err);
      setRecoveryPlan(mockRecoveryPlan);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckAvailability = async () => {
    setLoading(true);
    try {
      const response = await factoryOperationsAPI.checkMaterialAvailability(
        availabilityInput.material_code,
        availabilityInput.required_quantity,
      );
      setAvailabilityResult(response.data || response || mockAvailability);
    } catch (err) {
      console.warn('Failed to check availability, using mock data', err);
      setAvailabilityResult(mockAvailability);
    } finally {
      setLoading(false);
    }
  };

  const workflowChips = useMemo(() => {
    if (!workflowStats?.bottlenecks) return null;
    return workflowStats.bottlenecks.map((step) => (
      <Chip
        key={step}
        label={step}
        color="warning"
        size="small"
        sx={{ mr: 1 }}
      />
    ));
  }, [workflowStats]);

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        <Assignment sx={{ mr: 1, verticalAlign: 'middle' }} />
        Production Operations
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Workflow orchestration, inventory availability and recovery planning.
      </Typography>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Total Production Orders
              </Typography>
              <Typography variant="h3" fontWeight={700}>
                {workflowStats?.total_orders ?? mockWorkflowStats.total_orders}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed Steps:{' '}
                {workflowStats?.completed_steps ??
                  mockWorkflowStats.completed_steps}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pending Steps:{' '}
                {workflowStats?.pending_steps ??
                  mockWorkflowStats.pending_steps}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Bottlenecks: {workflowChips || 'None'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 2,
              }}
            >
              <Typography variant="h6">
                <PlaylistAddCheck sx={{ mr: 1, verticalAlign: 'middle' }} />
                Recovery Planner
              </Typography>
              <Button
                variant="contained"
                onClick={handleAnalyzeRecovery}
                disabled={loading}
              >
                Analyze Recovery
              </Button>
            </Box>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} mb={2}>
              <TextField
                label="Affected lines"
                helperText="Comma separated line codes"
                value={recoveryLines}
                onChange={(e) => setRecoveryLines(e.target.value)}
                fullWidth
                size="small"
              />
            </Stack>

            {recoveryPlan ? (
              <Grid container spacing={2}>
                {recoveryPlan.prioritized_lines?.map((line) => (
                  <Grid item xs={12} md={6} key={line.line_code}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2" color="text.secondary">
                          {line.line_code}
                        </Typography>
                        <Typography variant="h5" fontWeight={700}>
                          Priority {(line.priority_score * 100).toFixed(0)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          ETA Recovery: {line.estimated_recovery_minutes} min
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
                <Grid item xs={12}>
                  <Alert severity="info">
                    {recoveryPlan.recommendations?.join(' • ') ||
                      'No recommendations provided'}
                  </Alert>
                </Grid>
              </Grid>
            ) : (
              <Alert severity="info">
                Provide affected lines and click “Analyze Recovery” to see
                suggested restart order.
              </Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <AutoGraph sx={{ mr: 1, verticalAlign: 'middle' }} />
              Workflow Statistics
            </Typography>
            {workflowStats ? (
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Resync to get the latest throughput metrics.
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  sx={{ mt: 2 }}
                  onClick={fetchWorkflowStats}
                >
                  Refresh Stats
                </Button>
              </Box>
            ) : (
              <Alert severity="info">
                Workflow statistics unavailable. Please try refreshing.
              </Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <BuildCircle sx={{ mr: 1, verticalAlign: 'middle' }} />
              Material Availability
            </Typography>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} mb={2}>
              <TextField
                label="Material Code"
                value={availabilityInput.material_code}
                onChange={(e) =>
                  setAvailabilityInput((prev) => ({
                    ...prev,
                    material_code: e.target.value,
                  }))
                }
                size="small"
                fullWidth
              />
              <TextField
                label="Required Qty"
                type="number"
                value={availabilityInput.required_quantity}
                onChange={(e) =>
                  setAvailabilityInput((prev) => ({
                    ...prev,
                    required_quantity: parseFloat(e.target.value || '0'),
                  }))
                }
                size="small"
                fullWidth
              />
              <Button
                variant="contained"
                onClick={handleCheckAvailability}
                disabled={loading}
              >
                Check
              </Button>
            </Stack>

            {availabilityResult ? (
              <Box>
                <Alert
                  severity={
                    availabilityResult.is_sufficient ? 'success' : 'warning'
                  }
                  sx={{ mb: 2 }}
                >
                  {availabilityResult.is_sufficient
                    ? 'Sufficient stock available'
                    : 'Insufficient stock across locations'}
                </Alert>
                {availabilityResult.locations?.map((loc) => (
                  <Card key={loc.location} variant="outlined" sx={{ mb: 1 }}>
                    <CardContent>
                      <Typography variant="subtitle2">
                        {loc.location}
                      </Typography>
                      <Typography variant="h6" fontWeight={700}>
                        {loc.available_quantity}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Enter a material code to check real-time availability by
                location.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Production;
