import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress
} from '@mui/material';
import {
  SmartToy as AIIcon,
  DirectionsCar as AGVIcon,
  Eco as ESGIcon,
  TrendingUp as OptimizeIcon,
  Settings as ControlIcon,
  LocalShipping as FleetIcon
} from '@mui/icons-material';
import api from '../services/api';

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
      const response = await api.get('/api/v1/advanced/orchestration/fleet-status');
      setFleetStatus(response.data);
    } catch (err) {
      console.error('Failed to fetch fleet status:', err);
    }
  };

  const fetchESGSimulation = async () => {
    try {
      const response = await api.get('/api/v1/advanced/esg/simulate-scenarios');
      setParetoResults(response.data);
    } catch (err) {
      console.error('Failed to fetch ESG simulation:', err);
    }
  };

  const fetchActiveControls = async () => {
    try {
      const response = await api.get('/api/v1/advanced/autonomous-control/active');
      setActiveControls(response.data.controls);
    } catch (err) {
      console.error('Failed to fetch active controls:', err);
    }
  };

  const handleTestAGVAssignment = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/v1/advanced/orchestration/assign-agv', {
        task_type: 'transport_material',
        from_location: { x: 40, y: 50 },
        to_location: { x: 120, y: 75 },
        priority: 8,
        payload: { material_code: 'MAT-TEST-001' }
      });
      
      alert(`AGV Assigned!\n${response.data.message}\nTask ID: ${response.data.task?.task_id}`);
      await fetchFleetStatus();
    } catch (err) {
      alert('Failed to assign AGV: ' + (err.response?.data?.detail || err.message));
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
              <strong>🤖 Autonomous Control Loop:</strong> System automatically detects anomalies and adjusts machine parameters without human intervention.
            </Alert>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Features
                </Typography>
                <ul>
                  <li>Real-time anomaly detection</li>
                  <li>Auto-calculate optimal parameters</li>
                  <li>Safety validation</li>
                  <li>Closed-loop feedback monitoring</li>
                </ul>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Active Control Loops</Typography>
                <Button variant="outlined" size="small" onClick={fetchActiveControls}>
                  Refresh
                </Button>
              </Box>

              {activeControls.length === 0 ? (
                <Alert severity="success">No active control interventions - all machines operating normally</Alert>
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
                            <Chip label={control.status} color="primary" size="small" />
                          </TableCell>
                          <TableCell>{new Date(control.timestamp).toLocaleString()}</TableCell>
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
              <strong>🚚 Orchestration Engine:</strong> Intelligent coordination of AGVs, robots, and machines for optimal factory throughput.
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
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
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
                                color={agv.status === 'idle' ? 'success' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              ({agv.current_position.x}, {agv.current_position.y})
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {agv.battery_percent}%
                                <LinearProgress
                                  variant="determinate"
                                  value={agv.battery_percent}
                                  sx={{ width: 60 }}
                                />
                              </Box>
                            </TableCell>
                            <TableCell>
                              {agv.current_task ? agv.current_task.task_id : 'None'}
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
              <strong>🌍 ESG Optimizer:</strong> Real-time Environmental, Social, Governance scoring with Pareto optimization for Cost/Productivity/Carbon balance.
            </Alert>
          </Grid>

          {paretoResults && (
            <>
              {/* Recommended Scenario */}
              <Grid item xs={12}>
                <Card sx={{ bgcolor: 'success.light' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <OptimizeIcon sx={{ mr: 1 }} />
                      ✅ Recommended Operating Mode (Pareto Optimal)
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
                          {paretoResults.current_recommendation?.carbon_kg} kg CO₂
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
                  <Typography variant="body2" color="text.secondary" gutterBottom>
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
                          const isOptimal = paretoResults.optimization_result.pareto_solutions.includes(scenario);
                          const isRecommended = scenario.name === paretoResults.current_recommendation?.name;
                          
                          return (
                            <TableRow
                              key={index}
                              sx={{ 
                                bgcolor: isRecommended ? 'success.light' : 'inherit',
                                fontWeight: isRecommended ? 'bold' : 'normal'
                              }}
                            >
                              <TableCell>
                                <strong>{scenario.name}</strong>
                              </TableCell>
                              <TableCell>{scenario.description}</TableCell>
                              <TableCell align="right">{scenario.cost}</TableCell>
                              <TableCell align="right">{scenario.productivity}</TableCell>
                              <TableCell align="right">{scenario.carbon_kg}</TableCell>
                              <TableCell align="right">{scenario.energy_kwh}</TableCell>
                              <TableCell>
                                {isOptimal && (
                                  <Chip
                                    label={isRecommended ? "Recommended" : "Pareto"}
                                    color={isRecommended ? "success" : "primary"}
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
                    <strong>Pareto Optimal Solutions:</strong> {paretoResults.optimization_result.pareto_optimal_count} out of {paretoResults.optimization_result.total_scenarios} scenarios are Pareto-optimal (no single objective can be improved without worsening another).
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

