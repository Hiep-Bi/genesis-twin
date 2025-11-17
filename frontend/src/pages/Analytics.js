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
  Divider,
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

  const statusColorMap = {
    normal: 'success',
    warning: 'warning',
    critical: 'error',
  };

  const riskColorMap = {
    low: 'success',
    'medium-low': 'success',
    medium: 'warning',
    high: 'error',
  };

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
      const normalizedResults =
        response.data?.predictions || response.predictions || [];
      setAdvancedResult(normalizedResults);
      updateLocalHistoryFromResults(normalizedResults);
    } catch (error) {
      const fallbackResult = [
        {
          status: 'warning',
          result:
            error.response?.data?.detail ||
            'Prediction failed. Please verify AI Core is running.',
        },
      ];
      setAdvancedResult(fallbackResult);
      updateLocalHistoryFromResults(fallbackResult);
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

  const formatLabel = (label) =>
    label.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());

  const renderImpactChips = (impact) => {
    if (!impact || typeof impact !== 'object') return null;
    return (
      <Stack direction="row" spacing={1} flexWrap="wrap" mt={1}>
        {Object.entries(impact).map(([key, value]) =>
          key === 'risk_level' ? null : (
            <Chip
              key={key}
              label={`${formatLabel(key)}: ${value}`}
              size="small"
              variant="outlined"
            />
          ),
        )}
      </Stack>
    );
  };

  const JsonPreview = ({ data }) => (
    <Box
      component="pre"
      sx={{
        backgroundColor: 'grey.50',
        borderRadius: 1,
        p: 1,
        fontSize: 12,
        maxHeight: 200,
        overflow: 'auto',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      {JSON.stringify(data, null, 2)}
    </Box>
  );

  const renderSummaryValue = (value) => {
    if (value === null || value === undefined || value === '') {
      return (
        <Typography variant="body2" color="text.secondary">
          —
        </Typography>
      );
    }
    if (typeof value === 'object') {
      return <JsonPreview data={value} />;
    }
    return (
      <Typography variant="body2">
        {typeof value === 'number' ? value.toLocaleString() : String(value)}
      </Typography>
    );
  };

  const updateLocalHistoryFromResults = (results) => {
    if (!Array.isArray(results) || results.length === 0) return;
    const timestamp = new Date().toISOString();

    const syntheticPredictions = results
      .map((res, idx) => {
        const detail = res.detailed_analysis || {};
        const machineId =
          detail.machine_id || res.machine_id || advancedForm.machine_id;
        const status = (
          detail.status ||
          res.status ||
          'analysis'
        ).toLowerCase();
        const confidence =
          detail.diagnosis?.confidence ??
          res.confidence ??
          res.confidence_score ??
          0.5;

        return {
          id: `local-${timestamp}-${idx}`,
          prediction_type: status,
          target_id: machineId,
          confidence_score: confidence,
          created_at: timestamp,
          prediction_data: detail.diagnosis || res,
        };
      })
      .filter(Boolean);

    if (syntheticPredictions.length > 0) {
      setPredictions((prev) => {
        const base = prev.length > 0 ? prev : fallbackPredictions;
        return [...syntheticPredictions, ...base].slice(0, 6);
      });
    }

    const syntheticControls = results
      .map((res) => {
        const detail = res.detailed_analysis || {};
        const machineId =
          detail.machine_id || res.machine_id || advancedForm.machine_id;
        const recommendations =
          detail.recommendations ||
          res.recommendations ||
          (Array.isArray(res.fallback_instructions)
            ? res.fallback_instructions.map(
                (instruction) =>
                  instruction.title ||
                  instruction.description ||
                  instruction.action,
              )
            : []);

        if (!recommendations || recommendations.length === 0) {
          return null;
        }

        return {
          machine_code: machineId,
          status: res.status || detail.status || 'planned',
          timestamp,
          adjustments: {
            actions: recommendations.slice(0, 2),
            scenario: detail.scenarios?.[0]?.name,
          },
        };
      })
      .filter(Boolean);

    if (syntheticControls.length > 0) {
      setControlHistory((prev) => {
        const base = prev.length > 0 ? prev : fallbackControlHistory;
        return [...syntheticControls, ...base].slice(0, 10);
      });
    }
  };

  const renderAdvancedResultCard = (res, idx) => {
    const detail = res?.detailed_analysis;
    if (!detail) {
      const status = (res.status || 'info').toLowerCase();
      const statusColor = statusColorMap[status] || 'info';
      const fallbackInstructions = Array.isArray(res.fallback_instructions)
        ? res.fallback_instructions
        : [];
      const summaryEntries = Object.entries(res || {}).filter(
        ([key]) =>
          ![
            'status',
            'result',
            'fallback_instructions',
            'recommendations',
          ].includes(key),
      );
      const recommendations = Array.isArray(res.recommendations)
        ? res.recommendations
        : [];

      return (
        <Paper
          key={`advanced-result-${idx}`}
          variant="outlined"
          sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}
        >
          <Box
            display="flex"
            alignItems={{ xs: 'flex-start', md: 'center' }}
            justifyContent="space-between"
            flexWrap="wrap"
            gap={2}
          >
            <Typography variant="h6">Fallback plan</Typography>
            <Chip label={status.toUpperCase()} color={statusColor} />
          </Box>

          {res.result && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mt: 1, whiteSpace: 'pre-line' }}
            >
              {res.result}
            </Typography>
          )}

          {summaryEntries.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Stack spacing={1}>
                {summaryEntries.map(([key, value]) => (
                  <Box key={key}>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ textTransform: 'capitalize' }}
                    >
                      {formatLabel(key)}
                    </Typography>
                    {renderSummaryValue(value)}
                  </Box>
                ))}
              </Stack>
            </>
          )}

          {fallbackInstructions.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" color="text.secondary">
                Fallback Instructions
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                {fallbackInstructions.map((instruction, instructionIdx) => (
                  <Paper
                    key={`instruction-${instructionIdx}`}
                    variant="outlined"
                    sx={{ p: 1.5 }}
                  >
                    <Typography variant="subtitle2">
                      {instruction.title || `Step ${instruction.step}`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {instruction.description || instruction.action}
                    </Typography>
                  </Paper>
                ))}
              </Stack>
            </>
          )}

          {recommendations.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" color="text.secondary">
                Recommendations
              </Typography>
              <Stack component="ul" spacing={0.75} sx={{ pl: 3, mt: 0.5 }}>
                {recommendations.map((rec, recIdx) => (
                  <Typography
                    key={`fallback-rec-${recIdx}`}
                    component="li"
                    variant="body2"
                  >
                    {rec}
                  </Typography>
                ))}
              </Stack>
            </>
          )}
        </Paper>
      );
    }

    const status = (detail.status || res.status || 'info').toLowerCase();
    const statusColor = statusColorMap[status] || 'info';
    const diagnosis = detail.diagnosis || {};
    const reasoning = diagnosis.reasoning || {};
    const maintenance = detail.maintenance_recommendation || {};
    const scenarios = Array.isArray(detail.scenarios) ? detail.scenarios : [];
    const recommendations = Array.isArray(detail.recommendations)
      ? detail.recommendations
      : Array.isArray(res.recommendations)
      ? res.recommendations
      : [];
    const evidence = Array.isArray(reasoning.evidence)
      ? reasoning.evidence
      : [];
    const triggers = Array.isArray(reasoning.triggers)
      ? reasoning.triggers
      : [];
    const confidenceValue =
      typeof diagnosis.confidence === 'number'
        ? diagnosis.confidence
        : typeof res.confidence === 'number'
        ? res.confidence
        : null;
    const maintenanceWindow = maintenance.next_maintenance_window || {};
    const goldenSlot = maintenance.optimal_scheduling?.golden_slot;

    const machineId =
      detail.machine_id || res.machine_id || advancedForm.machine_id;
    const machineType =
      detail.machine_type || res.machine_type || advancedForm.machine_type;

    return (
      <Paper
        key={`advanced-result-${idx}`}
        variant="outlined"
        sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}
      >
        <Box
          display="flex"
          alignItems={{ xs: 'flex-start', md: 'center' }}
          justifyContent="space-between"
          flexWrap="wrap"
          gap={2}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              Machine
            </Typography>
            <Typography variant="h6">{machineId}</Typography>
            <Typography variant="body2" color="text.secondary">
              {machineType}
            </Typography>
          </Box>
          <Chip label={status.toUpperCase()} color={statusColor} />
        </Box>

        {confidenceValue !== null && (
          <Box mt={2}>
            <Typography variant="caption" color="text.secondary">
              AI Confidence
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <LinearProgress
                variant="determinate"
                value={Math.min(Math.max(confidenceValue, 0), 1) * 100}
                sx={{ flex: 1, height: 8, borderRadius: 4 }}
                color={statusColor}
              />
              <Typography variant="caption" fontWeight={700}>
                {(confidenceValue * 100).toFixed(1)}%
              </Typography>
            </Box>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" color="text.secondary">
          Diagnosis
        </Typography>
        <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
          {diagnosis.issue_detected || 'No issue detected'}
        </Typography>
        {diagnosis.root_cause && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Root cause: {diagnosis.root_cause}
          </Typography>
        )}
        {evidence.length > 0 && (
          <Stack spacing={0.5} sx={{ pl: 1 }}>
            {evidence.map((item, evidenceIdx) => (
              <Typography
                key={`evidence-${evidenceIdx}`}
                variant="body2"
                color="text.secondary"
              >
                • {item}
              </Typography>
            ))}
          </Stack>
        )}
        {reasoning.pattern_matching && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Pattern match: {reasoning.pattern_matching}
          </Typography>
        )}
        {triggers.length > 0 && (
          <Stack direction="row" spacing={1} flexWrap="wrap" mt={1}>
            {triggers.map((trigger, triggerIdx) => (
              <Chip
                key={`trigger-${triggerIdx}`}
                label={trigger}
                size="small"
                color="info"
                variant="outlined"
              />
            ))}
          </Stack>
        )}

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" color="text.secondary">
          Maintenance Window
        </Typography>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={12} md={4}>
            <Typography variant="caption" color="text.secondary">
              Avg cycle
            </Typography>
            <Typography variant="body1" fontWeight={700}>
              {maintenance.avg_maintenance_cycle_days ?? '—'} ngày
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="caption" color="text.secondary">
              Est. downtime
            </Typography>
            <Typography variant="body1" fontWeight={700}>
              {maintenance.estimated_downtime_hours ?? '—'} giờ
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="caption" color="text.secondary">
              Next window
            </Typography>
            <Typography variant="body1" fontWeight={700}>
              {maintenanceWindow.start || '—'} → {maintenanceWindow.end || '—'}
            </Typography>
          </Grid>
        </Grid>
        {goldenSlot && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <strong>Golden Slot:</strong> {goldenSlot.date}{' '}
            {goldenSlot.time_range} – {goldenSlot.reason}.{' '}
            {goldenSlot.cost_optimization}
          </Alert>
        )}

        {scenarios.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="text.secondary">
              Scenario Analysis
            </Typography>
            <Stack spacing={1.5} sx={{ mt: 1 }}>
              {scenarios.map((scenario, scenarioIdx) => {
                const riskColor =
                  riskColorMap[
                    String(scenario.impact?.risk_level).toLowerCase()
                  ] || 'default';
                return (
                  <Box
                    key={`scenario-${scenarioIdx}`}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      p: 1.5,
                    }}
                  >
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="center"
                      gap={1}
                      flexWrap="wrap"
                    >
                      <Typography variant="subtitle1" fontWeight={600}>
                        {scenario.name}
                      </Typography>
                      {scenario.impact?.risk_level && (
                        <Chip
                          label={`Risk: ${scenario.impact.risk_level}`}
                          size="small"
                          color={riskColor}
                          variant="outlined"
                        />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {scenario.description}
                    </Typography>
                    {renderImpactChips(scenario.impact)}
                  </Box>
                );
              })}
            </Stack>
          </>
        )}

        {recommendations.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="text.secondary">
              Recommended Actions
            </Typography>
            <Stack component="ul" spacing={0.75} sx={{ pl: 3, mt: 0.5 }}>
              {recommendations.map((rec, recIdx) => (
                <Typography
                  key={`recommendation-${recIdx}`}
                  component="li"
                  variant="body2"
                >
                  {rec}
                </Typography>
              ))}
            </Stack>
          </>
        )}

        {res.result && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="text.secondary">
              Narrative
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ whiteSpace: 'pre-line' }}
            >
              {res.result}
            </Typography>
          </>
        )}
      </Paper>
    );
  };

  const hasAdvancedResult =
    Array.isArray(advancedResult) && advancedResult.length > 0;

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
              {hasAdvancedResult ? (
                <Stack>
                  {advancedResult.map((res, idx) =>
                    renderAdvancedResultCard(res, idx),
                  )}
                </Stack>
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
