import {
  Analytics as AnalyticsIcon,
  SmartToy,
  WarningAmber,
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
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import {
  advancedFeaturesAPI,
  aiPredictionsAPI,
  factoryOperationsAPI,
} from '../services/api';

const fallbackPredictions = [
  {
    id: 'mock-1',
    prediction_type: 'defect',
    confidence_score: 0.94,
    created_at: new Date().toISOString(),
    target_id: 'MACHINE-001',
    prediction_data: { diagnosis: 'Bearing vibration anomaly detected' },
  },
];

const fallbackControlHistory = [
  {
    timestamp: new Date().toISOString(),
    machine_code: 'CNC-001',
    status: 'completed',
    adjustments: { feed_rate: '+3%', coolant: '+5%' },
  },
];

const fallbackAgvFallback = {
  summary: 'Manual fallback required for LINE-01 and LINE-02.',
  recommended_sequence: [
    { step: 1, action: 'Switch LINE-01 to manual AGV mode' },
    { step: 2, action: 'Re-route materials from external staging' },
  ],
  resource_requirements: ['2 operators', '1 forklift', 'QA standby'],
};

const Analytics = () => {
  const [predictions, setPredictions] = useState([]);
  const [controlHistory, setControlHistory] = useState([]);
  const [agvFallback, setAgvFallback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [advancedForm, setAdvancedForm] = useState({
    machine_id: 'MACHINE-001',
    machine_type: 'CNC',
    temperature: 82,
    vibration_level: 4.8,
    power_consumption: 24,
  });
  const [advancedResult, setAdvancedResult] = useState(null);
  const [advancedLoading, setAdvancedLoading] = useState(false);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const [predictionRes, controlHistoryRes] = await Promise.all([
        aiPredictionsAPI.getHistory({ limit: 6 }),
        advancedFeaturesAPI.getAdjustmentHistory(10),
      ]);

      setPredictions(predictionRes.data ?? fallbackPredictions);
      setControlHistory(
        controlHistoryRes.data?.history ?? fallbackControlHistory,
      );
    } catch (error) {
      console.warn('Analytics data fallback due to error:', error);
      setPredictions(fallbackPredictions);
      setControlHistory(fallbackControlHistory);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateAgvFallback = async () => {
    setLoading(true);
    try {
      const response = await factoryOperationsAPI.analyzeAGVFallback({
        estimated_recovery_time_minutes: 60,
        affected_lines: ['LINE-01', 'LINE-02'],
      });
      setAgvFallback(response.data || response || fallbackAgvFallback);
    } catch (error) {
      console.warn('AGV fallback simulation failed; using mock data.', error);
      setAgvFallback(fallbackAgvFallback);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAdvancedPrediction = async () => {
    setAdvancedLoading(true);
    setAdvancedResult(null);
    try {
      const payload = [
        {
          timestamp: new Date().toISOString(),
          machine_id: advancedForm.machine_id,
          machine_type: advancedForm.machine_type,
          temperature: Number(advancedForm.temperature),
          vibration_level: Number(advancedForm.vibration_level),
          power_consumption: Number(advancedForm.power_consumption),
          pressure: 5.1,
          material_flow_rate: 18.2,
          cycle_time: 110,
          error_rate: 0.85,
          downtime: 0,
          maintenance_flag: 0,
          efficiency_score: 8,
          production_status: 0,
        },
      ];
      const response = await aiPredictionsAPI.predictAdvancedDefect(payload);
      setAdvancedResult(response.data?.predictions || response.predictions);
    } catch (error) {
      setAdvancedResult([
        {
          status: 'warning',
          result:
            error.response?.data?.detail ||
            'Prediction failed. Please verify AI Core is running.',
        },
      ]);
    } finally {
      setAdvancedLoading(false);
    }
  };

  const resourceRequirements = Array.isArray(agvFallback?.resource_requirements)
    ? agvFallback.resource_requirements
    : Array.isArray(fallbackAgvFallback.resource_requirements)
    ? fallbackAgvFallback.resource_requirements
    : agvFallback?.resource_requirements
    ? [String(agvFallback.resource_requirements)]
    : fallbackAgvFallback.resource_requirements.map((item) => String(item));

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        <AnalyticsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Advanced Analytics
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        AI predictions, autonomous control history, and AGV fallback
        simulations.
      </Typography>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 2,
                }}
              >
                <Box display="flex" alignItems="center" gap={1}>
                  <SmartToy color="primary" />
                  <Typography variant="h6" fontWeight={700}>
                    Run Advanced Defect Prediction
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  onClick={handleRunAdvancedPrediction}
                  disabled={advancedLoading}
                >
                  {advancedLoading ? 'Analyzing...' : 'Analyze'}
                </Button>
              </Box>
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} mb={2}>
                <TextField
                  label="Machine ID"
                  value={advancedForm.machine_id}
                  onChange={(e) =>
                    setAdvancedForm((prev) => ({
                      ...prev,
                      machine_id: e.target.value,
                    }))
                  }
                  size="small"
                  fullWidth
                />
                <TextField
                  label="Machine Type"
                  value={advancedForm.machine_type}
                  onChange={(e) =>
                    setAdvancedForm((prev) => ({
                      ...prev,
                      machine_type: e.target.value,
                    }))
                  }
                  size="small"
                  fullWidth
                />
                <TextField
                  label="Temperature (°C)"
                  type="number"
                  value={advancedForm.temperature}
                  onChange={(e) =>
                    setAdvancedForm((prev) => ({
                      ...prev,
                      temperature: e.target.value,
                    }))
                  }
                  size="small"
                />
                <TextField
                  label="Vibration"
                  type="number"
                  value={advancedForm.vibration_level}
                  onChange={(e) =>
                    setAdvancedForm((prev) => ({
                      ...prev,
                      vibration_level: e.target.value,
                    }))
                  }
                  size="small"
                />
                <TextField
                  label="Power (kW)"
                  type="number"
                  value={advancedForm.power_consumption}
                  onChange={(e) =>
                    setAdvancedForm((prev) => ({
                      ...prev,
                      power_consumption: e.target.value,
                    }))
                  }
                  size="small"
                />
              </Stack>
              {advancedResult ? (
                advancedResult.map((res, idx) => (
                  <Alert
                    key={idx}
                    severity={res.status === 'warning' ? 'warning' : 'info'}
                    sx={{ mb: 1 }}
                  >
                    {res.result || JSON.stringify(res)}
                  </Alert>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Provide quick sensor readings above and click Analyze to run
                  the Gemini-based reasoning endpoint.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <SmartToy color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Latest AI Predictions
                </Typography>
              </Box>
              {predictions.length === 0 ? (
                <Alert severity="info">
                  No predictions in the last 24 hours.
                </Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Target</TableCell>
                        <TableCell>Confidence</TableCell>
                        <TableCell>Timestamp</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {predictions.map((pred) => (
                        <TableRow key={pred.id}>
                          <TableCell>
                            <Chip
                              label={pred.prediction_type}
                              size="small"
                              color={
                                pred.prediction_type === 'defect'
                                  ? 'error'
                                  : 'info'
                              }
                            />
                          </TableCell>
                          <TableCell>{pred.target_id || '—'}</TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              {(pred.confidence_score * 100 || 0).toFixed(1)}%
                              <LinearProgress
                                variant="determinate"
                                value={(pred.confidence_score || 0) * 100}
                                sx={{ width: 70 }}
                              />
                            </Box>
                          </TableCell>
                          <TableCell>
                            {new Date(pred.created_at).toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <AnalyticsIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Autonomous Control History
                </Typography>
              </Box>
              {controlHistory.length === 0 ? (
                <Alert severity="success">
                  No control adjustments were required recently.
                </Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Machine</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Adjustments</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {controlHistory.map((entry, index) => (
                        <TableRow key={index}>
                          <TableCell>{entry.machine_code}</TableCell>
                          <TableCell>
                            <Chip
                              label={entry.status}
                              color={
                                entry.status === 'completed'
                                  ? 'success'
                                  : 'warning'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {entry.timestamp
                              ? new Date(entry.timestamp).toLocaleString()
                              : '—'}
                          </TableCell>
                          <TableCell>
                            {entry.adjustments
                              ? JSON.stringify(entry.adjustments)
                              : '—'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 2,
              }}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <WarningAmber color="warning" />
                <Typography variant="h6" fontWeight={700}>
                  AGV Fallback Simulation
                </Typography>
              </Box>
              <Button
                variant="contained"
                onClick={handleSimulateAgvFallback}
                disabled={loading}
              >
                Simulate Failure
              </Button>
            </Box>

            {agvFallback ? (
              <Box>
                <Alert severity="warning" sx={{ mb: 2 }}>
                  {agvFallback.summary || fallbackAgvFallback.summary}
                </Alert>

                <Typography variant="subtitle2" gutterBottom>
                  Recommended Sequence
                </Typography>
                {agvFallback.recommended_sequence?.length ? (
                  agvFallback.recommended_sequence.map((step, idx) => (
                    <Alert key={idx} severity="info" sx={{ mb: 1 }}>
                      Step {step.step}: {step.action}
                    </Alert>
                  ))
                ) : (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    No specific line sequence provided. Check resource
                    requirements below for guidance.
                  </Alert>
                )}

                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Resource Requirements
                </Typography>
                {Array.isArray(resourceRequirements) ? (
                  resourceRequirements.length ? (
                    <Typography variant="body2">
                      {resourceRequirements.join(' • ')}
                    </Typography>
                  ) : (
                    <Alert severity="info">
                      No additional resources required for this scenario.
                    </Alert>
                  )
                ) : (
                  <TableContainer sx={{ mb: 2 }}>
                    <Table size="small">
                      <TableBody>
                        {Object.entries(resourceRequirements).map(
                          ([key, value]) => (
                            <TableRow key={key}>
                              <TableCell sx={{ textTransform: 'capitalize' }}>
                                {key.replace(/_/g, ' ')}
                              </TableCell>
                              <TableCell>
                                {typeof value === 'number'
                                  ? value
                                  : String(value)}
                              </TableCell>
                            </TableRow>
                          ),
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}

                {agvFallback.fallback_instructions?.length && (
                  <>
                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                      Fallback Instructions
                    </Typography>
                    {agvFallback.fallback_instructions.map((item) => (
                      <Alert key={item.step} severity="success" sx={{ mb: 1 }}>
                        <strong>{item.title}</strong>: {item.description} (
                        {item.action})
                      </Alert>
                    ))}
                  </>
                )}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Click “Simulate Failure” to see the fallback plan generated by
                the backend Factory Operations service.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Analytics;
