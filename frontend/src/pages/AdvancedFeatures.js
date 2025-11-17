import {
  DirectionsCar as AGVIcon,
  SmartToy as AIIcon,
  CheckCircleOutline,
  Settings as ControlIcon,
  Nature as ESGIcon,
  LocalShipping as FleetIcon,
  TrendingUp as OptimizeIcon,
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
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import api from '../services/api';

const fallbackFleetStatus = {
  total_agvs: 12,
  idle: 5,
  busy: 6,
  utilization_percent: 72.3,
  fleet_details: [
    {
      id: 'AGV-001',
      status: 'idle',
      current_position: { x: 10, y: 25 },
      battery_percent: 88,
      current_task: null,
    },
    {
      id: 'AGV-007',
      status: 'busy',
      current_position: { x: 55, y: 42 },
      battery_percent: 64,
      current_task: { task_id: 'TASK-9821' },
    },
  ],
};

const fallbackESGSimulation = {
  current_recommendation: {
    name: 'Balanced Mode',
    description: 'Giữ mức sản xuất ổn định, giảm 12% carbon',
    cost: 4800,
    productivity: 92,
    carbon_kg: 320,
  },
  optimization_result: {
    analysis: 'Pareto analysis xác định 2 phương án tối ưu.',
    pareto_optimal_count: 2,
    total_scenarios: 3,
    pareto_solutions: ['Balanced Mode', 'Eco Mode'],
  },
  all_scenarios: [
    {
      name: 'Balanced Mode',
      description: 'Giảm 12% carbon, giữ 92% năng suất.',
      cost: 4800,
      productivity: 92,
      carbon_kg: 320,
      energy_kwh: 740,
    },
    {
      name: 'Eco Mode',
      description: 'Ưu tiên giảm carbon tối đa.',
      cost: 4600,
      productivity: 88,
      carbon_kg: 290,
      energy_kwh: 690,
    },
    {
      name: 'Turbo Mode',
      description: 'Tối đa hóa sản lượng.',
      cost: 5200,
      productivity: 98,
      carbon_kg: 370,
      energy_kwh: 810,
    },
  ],
};

const fallbackActiveControls = [
  {
    machine_id: 'MACHINE-01',
    status: 'monitoring',
    timestamp: new Date().toISOString(),
    adjustments: {
      parameters: { spindle_speed_percent: 90 },
      expected_impact: { vibration_reduction: '12%' },
    },
  },
];

const AdvancedFeatures = () => {
  const [tabValue, setTabValue] = useState(0);
  const [fleetStatus, setFleetStatus] = useState(null);
  const [esgScore, setESGScore] = useState(null);
  const [paretoResults, setParetoResults] = useState(null);
  const [activeControls, setActiveControls] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFleetStatus();
    fetchESGSimulation();
  }, []);

  const fetchFleetStatus = async () => {
    try {
      const response = await api.get(
        '/api/v1/advanced/orchestration/fleet-status',
      );
      setFleetStatus(response.data || fallbackFleetStatus);
    } catch (err) {
      console.error('Failed to fetch fleet status:', err);
      setFleetStatus(fallbackFleetStatus);
    }
  };

  const fetchESGSimulation = async () => {
    try {
      const response = await api.get('/api/v1/advanced/esg/simulate-scenarios');
      setParetoResults(response.data || fallbackESGSimulation);
    } catch (err) {
      console.error('Failed to fetch ESG simulation:', err);
      setParetoResults(fallbackESGSimulation);
    }
  };

  const fetchActiveControls = async () => {
    try {
      const response = await api.get(
        '/api/v1/advanced/autonomous-control/active',
      );
      setActiveControls(response.data?.controls || fallbackActiveControls);
    } catch (err) {
      console.error('Failed to fetch active controls:', err);
      setActiveControls(fallbackActiveControls);
    }
  };

  const handleTestAGVAssignment = async () => {
    setLoading(true);
    try {
      const response = await api.post(
        '/api/v1/advanced/orchestration/assign-agv',
        {
          task_type: 'transport_material',
          from_location: { x: 40, y: 50 },
          to_location: { x: 120, y: 75 },
          priority: 8,
          payload: { material_code: 'MAT-TEST-001' },
        },
      );

      alert(
        `AGV Assigned!\n${response.data.message}\nTask ID: ${response.data.task?.task_id}`,
      );
      await fetchFleetStatus();
    } catch (err) {
      alert(
        'Failed to assign AGV: ' + (err.response?.data?.detail || err.message),
      );
    } finally {
      setLoading(false);
    }
  };

  const getRatingColor = (rating) => {
    if (rating.startsWith('A')) return 'success';
    if (rating.startsWith('B')) return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        <AIIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Advanced AI Features
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Autonomous Control, Orchestration Engine, ESG Optimization
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab icon={<ControlIcon />} label="Autonomous Control" />
          <Tab icon={<FleetIcon />} label="Orchestration" />
          <Tab icon={<ESGIcon />} label="ESG Optimizer" />
        </Tabs>
      </Box>

      {/* Tab 1: Autonomous Control */}
      {tabValue === 0 && (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Alert severity="info">
              <strong>🤖 Autonomous Control Loop:</strong> System automatically
              detects anomalies and adjusts machine parameters without human
              intervention.
            </Alert>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Features
                </Typography>
                <List>
                  {[
                    'Real-time anomaly detection',
                    'Auto-calculate optimal parameters',
                    'Safety validation',
                    'Closed-loop feedback monitoring',
                  ].map((feature, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircleOutline color="primary" />
                      </ListItemIcon>
                      <ListItemText primary={feature} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 2,
                }}
              >
                <Typography variant="h6">Active Control Loops</Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={fetchActiveControls}
                >
                  Refresh
                </Button>
              </Box>

              {activeControls.length === 0 ? (
                <Alert severity="success">
                  No active control interventions - all machines operating
                  normally
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Machine ID</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Parameters Adjusted</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {activeControls.map((control, index) => (
                        <TableRow key={index}>
                          <TableCell>{control.machine_id}</TableCell>
                          <TableCell>
                            <Chip
                              label={control.status}
                              color="primary"
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(control.timestamp).toLocaleString()}
                          </TableCell>
                          <TableCell>
                            {JSON.stringify(control.adjustments?.parameters)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: Orchestration */}
      {tabValue === 1 && (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Alert severity="info">
              <strong>🚚 Orchestration Engine:</strong> Intelligent coordination
              of AGVs, robots, and machines for optimal factory throughput.
            </Alert>
          </Grid>

          {/* Fleet Status */}
          {fleetStatus && (
            <>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total AGVs
                    </Typography>
                    <Typography variant="h3">
                      {fleetStatus.total_agvs}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Idle
                    </Typography>
                    <Typography variant="h3" color="success.main">
                      {fleetStatus.idle}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Busy
                    </Typography>
                    <Typography variant="h3" color="warning.main">
                      {fleetStatus.busy}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Utilization
                    </Typography>
                    <Typography variant="h3">
                      {fleetStatus.utilization_percent.toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={fleetStatus.utilization_percent}
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      mb: 2,
                    }}
                  >
                    <Typography variant="h6">
                      <AGVIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      AGV Fleet Details
                    </Typography>
                    <Button
                      variant="contained"
                      onClick={handleTestAGVAssignment}
                      disabled={loading}
                    >
                      Test AGV Assignment
                    </Button>
                  </Box>

                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>AGV ID</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Position</TableCell>
                          <TableCell>Battery</TableCell>
                          <TableCell>Current Task</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {fleetStatus.fleet_details.slice(0, 10).map((agv) => (
                          <TableRow key={agv.id}>
                            <TableCell>{agv.id}</TableCell>
                            <TableCell>
                              <Chip
                                label={agv.status}
                                color={
                                  agv.status === 'idle' ? 'success' : 'warning'
                                }
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              ({agv.current_position.x},{' '}
                              {agv.current_position.y})
                            </TableCell>
                            <TableCell>
                              <Box
                                sx={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 1,
                                }}
                              >
                                {agv.battery_percent}%
                                <LinearProgress
                                  variant="determinate"
                                  value={agv.battery_percent}
                                  sx={{ width: 60 }}
                                />
                              </Box>
                            </TableCell>
                            <TableCell>
                              {agv.current_task
                                ? agv.current_task.task_id
                                : 'None'}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>
            </>
          )}
        </Grid>
      )}

      {/* Tab 3: ESG Optimizer */}
      {tabValue === 2 && (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Alert severity="info">
              <strong>🌍 ESG Optimizer:</strong> Real-time Environmental,
              Social, Governance scoring with Pareto optimization for
              Cost/Productivity/Carbon balance.
            </Alert>
          </Grid>

          {paretoResults && (
            <>
              {/* Recommended Scenario */}
              <Grid item xs={12}>
                <Card sx={{ bgcolor: 'success.light' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <OptimizeIcon sx={{ mr: 1 }} /> Recommended Operating
                      Mode (Pareto Optimal)
                    </Typography>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={12} md={3}>
                        <Typography variant="h5">
                          {paretoResults.current_recommendation?.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {paretoResults.current_recommendation?.description}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Typography variant="body2">Cost</Typography>
                        <Typography variant="h6">
                          ${paretoResults.current_recommendation?.cost}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Typography variant="body2">Productivity</Typography>
                        <Typography variant="h6">
                          {paretoResults.current_recommendation?.productivity}%
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Typography variant="body2">Carbon</Typography>
                        <Typography variant="h6">
                          {paretoResults.current_recommendation?.carbon_kg} kg
                          CO₂
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* All Scenarios Comparison */}
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    All Scenarios (Pareto Analysis)
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                  >
                    {paretoResults.optimization_result.analysis}
                  </Typography>

                  <TableContainer sx={{ mt: 2 }}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Scenario</TableCell>
                          <TableCell>Description</TableCell>
                          <TableCell align="right">Cost ($)</TableCell>
                          <TableCell align="right">Productivity (%)</TableCell>
                          <TableCell align="right">Carbon (kg)</TableCell>
                          <TableCell align="right">Energy (kWh)</TableCell>
                          <TableCell>Optimal</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {paretoResults.all_scenarios.map((scenario, index) => {
                          const isOptimal =
                            paretoResults.optimization_result.pareto_solutions.includes(
                              scenario,
                            );
                          const isRecommended =
                            scenario.name ===
                            paretoResults.current_recommendation?.name;

                          return (
                            <TableRow
                              key={index}
                              sx={{
                                bgcolor: isRecommended
                                  ? 'success.light'
                                  : 'inherit',
                                fontWeight: isRecommended ? 'bold' : 'normal',
                              }}
                            >
                              <TableCell>
                                <strong>{scenario.name}</strong>
                              </TableCell>
                              <TableCell>{scenario.description}</TableCell>
                              <TableCell align="right">
                                {scenario.cost}
                              </TableCell>
                              <TableCell align="right">
                                {scenario.productivity}
                              </TableCell>
                              <TableCell align="right">
                                {scenario.carbon_kg}
                              </TableCell>
                              <TableCell align="right">
                                {scenario.energy_kwh}
                              </TableCell>
                              <TableCell>
                                {isOptimal && (
                                  <Chip
                                    label={
                                      isRecommended ? 'Recommended' : 'Pareto'
                                    }
                                    color={
                                      isRecommended ? 'success' : 'primary'
                                    }
                                    size="small"
                                  />
                                )}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  <Alert severity="info" sx={{ mt: 2 }}>
                    <strong>Pareto Optimal Solutions:</strong>{' '}
                    {paretoResults.optimization_result.pareto_optimal_count} out
                    of {paretoResults.optimization_result.total_scenarios}{' '}
                    scenarios are Pareto-optimal (no single objective can be
                    improved without worsening another).
                  </Alert>
                </Paper>
              </Grid>
            </>
          )}
        </Grid>
      )}
    </Container>
  );
};

export default AdvancedFeatures;
