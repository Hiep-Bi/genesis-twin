import {
    SmartToy as AIIcon,
    CheckCircle,
    Error as ErrorIcon,
    History as HistoryIcon,
    Info as InfoIcon,
    Lightbulb as RecommendationIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Container,
    Divider,
    Grid,
    LinearProgress,
    Paper,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tabs,
    Typography
} from '@mui/material';
import { useEffect, useState } from 'react';
import { aiPredictionsAPI } from '../services/api';

const AIPredictions = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  // Mock data for alerts (if backend doesn't have alerts endpoint)
  const mockAlerts = [
    {
      id: 1,
      type: 'defect',
      severity: 'critical',
      title: 'Predictive Maintenance Alert',
      message: 'Conveyor B2 bearing failure predicted in 12h with 97.8% confidence',
      confidence: 97.8,
      machineId: 'MACHINE-003',
      timestamp: new Date().toISOString(),
      recommendation: 'Schedule preventive maintenance immediately',
    },
    {
      id: 2,
      type: 'quality',
      severity: 'warning',
      title: 'Quality Control Warning',
      message: 'Welding stage showing 28% increase in defect rate',
      confidence: 94.2,
      machineId: 'MACHINE-007',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      recommendation: 'Inspect welding parameters and material quality',
    },
    {
      id: 3,
      type: 'energy',
      severity: 'info',
      title: 'Energy Optimization Suggestion',
      message: 'Peak hour consumption can be reduced by 15% with load balancing',
      confidence: 87.5,
      machineId: 'ALL',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      recommendation: 'Consider shifting non-critical operations to off-peak hours',
    },
  ];

  // Mock recommendations
  const mockRecommendations = [
    {
      id: 1,
      type: 'maintenance',
      title: 'Schedule Maintenance Window',
      description: 'Optimal maintenance window identified: Tomorrow 2-4 AM',
      impact: 'high',
      cost: '$500',
      benefit: 'Prevent $50k downtime loss',
      confidence: 95.5,
    },
    {
      id: 2,
      type: 'production',
      title: 'Adjust Production Schedule',
      description: 'Reorganize production order for optimal material flow',
      impact: 'medium',
      cost: '$0',
      benefit: 'Increase throughput by 12%',
      confidence: 88.3,
    },
    {
      id: 3,
      type: 'energy',
      title: 'Energy Load Balancing',
      description: 'Redistribute energy load across 3 shifts for cost savings',
      impact: 'medium',
      cost: '$200',
      benefit: 'Save $2k/month in energy costs',
      confidence: 82.1,
    },
  ];

  useEffect(() => {
    fetchPredictions();
    // Use mock data if backend doesn't have alerts endpoint
    setAlerts(mockAlerts);
    setRecommendations(mockRecommendations);
  }, []);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const response = await aiPredictionsAPI.getHistory({ limit: 50 });
      if (response.data) {
        setPredictions(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch AI predictions:', error);
      // Use mock data if API fails
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'info';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon />;
      case 'warning':
        return <WarningIcon />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={3}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: 'primary.main' }}>
          <AIIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          AI Predictions & Recommendations
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time AI-powered insights, alerts, and actionable recommendations
        </Typography>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab icon={<WarningIcon />} label="Alerts" iconPosition="start" />
          <Tab icon={<RecommendationIcon />} label="Recommendations" iconPosition="start" />
          <Tab icon={<HistoryIcon />} label="Prediction History" iconPosition="start" />
        </Tabs>
      </Box>

      {/* Tab 1: AI Alerts */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mb: 3 }}>
              <strong>AI-Powered Alerts:</strong> Real-time anomaly detection and predictive warnings
              from our AI system monitoring all factory operations.
            </Alert>
          </Grid>

          {alerts.length === 0 ? (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box textAlign="center" py={4}>
                    <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      No active alerts
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      All systems operating normally
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ) : (
            alerts.map((alert) => (
              <Grid item xs={12} key={alert.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="flex-start" gap={2}>
                      <Box>
                        {getSeverityIcon(alert.severity)}
                      </Box>
                      <Box flex={1}>
                        <Box display="flex" alignItems="center" gap={2} mb={1}>
                          <Typography variant="h6" sx={{ fontWeight: 700 }}>
                            {alert.title}
                          </Typography>
                          <Chip
                            label={alert.severity.toUpperCase()}
                            color={getSeverityColor(alert.severity)}
                            size="small"
                          />
                          {alert.confidence && (
                            <Chip
                              label={`${alert.confidence.toFixed(1)}% Confidence`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {alert.message}
                        </Typography>
                        {alert.confidence && (
                          <Box mb={2}>
                            <Box display="flex" alignItems="center" gap={1} mb={1}>
                              <Typography variant="caption" color="text.secondary">
                                AI Confidence:
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={alert.confidence}
                                sx={{ flex: 1, height: 8, borderRadius: 4 }}
                                color={getSeverityColor(alert.severity)}
                              />
                              <Typography variant="caption" fontWeight={700}>
                                {alert.confidence.toFixed(1)}%
                              </Typography>
                            </Box>
                          </Box>
                        )}
                        {alert.recommendation && (
                          <Alert severity={getSeverityColor(alert.severity)} sx={{ mt: 2 }}>
                            <strong>Recommendation:</strong> {alert.recommendation}
                          </Alert>
                        )}
                        <Box mt={2} display="flex" gap={1} alignItems="center">
                          <Typography variant="caption" color="text.secondary">
                            Machine: {alert.machineId}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            • {new Date(alert.timestamp).toLocaleString()}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Tab 2: Recommendations */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mb: 3 }}>
              <strong>AI Recommendations:</strong> Data-driven suggestions to optimize operations,
              reduce costs, and improve efficiency.
            </Alert>
          </Grid>

          {recommendations.length === 0 ? (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box textAlign="center" py={4}>
                    <InfoIcon sx={{ fontSize: 64, color: 'info.main', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      No recommendations at this time
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ) : (
            recommendations.map((rec) => (
              <Grid item xs={12} md={6} key={rec.id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" alignItems="flex-start" gap={2} mb={2}>
                      <RecommendationIcon color="primary" />
                      <Box flex={1}>
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Typography variant="h6" sx={{ fontWeight: 700 }}>
                            {rec.title}
                          </Typography>
                          <Chip
                            label={rec.impact}
                            size="small"
                            color={rec.impact === 'high' ? 'error' : 'default'}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {rec.description}
                        </Typography>
                        <Divider sx={{ my: 2 }} />
                        <Grid container spacing={2}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Cost
                            </Typography>
                            <Typography variant="body1" fontWeight={700}>
                              {rec.cost}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Expected Benefit
                            </Typography>
                            <Typography variant="body1" fontWeight={700} color="success.main">
                              {rec.benefit}
                            </Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="caption" color="text.secondary">
                                Confidence:
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={rec.confidence}
                                sx={{ flex: 1, height: 6, borderRadius: 3 }}
                              />
                              <Typography variant="caption" fontWeight={700}>
                                {rec.confidence.toFixed(1)}%
                              </Typography>
                            </Box>
                          </Grid>
                          <Grid item xs={12}>
                            <Button
                              variant="contained"
                              size="small"
                              fullWidth
                              startIcon={<CheckCircle />}
                            >
                              Apply Recommendation
                            </Button>
                          </Grid>
                        </Grid>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Tab 3: Prediction History */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Prediction History
              </Typography>
              <Button variant="outlined" onClick={fetchPredictions} disabled={loading}>
                Refresh
              </Button>
            </Box>
          </Grid>

          {loading ? (
            <Grid item xs={12}>
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            </Grid>
          ) : predictions.length === 0 ? (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box textAlign="center" py={4}>
                    <HistoryIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      No prediction history available
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Historical predictions will appear here
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ) : (
            <Grid item xs={12}>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Target</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell>Created At</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {predictions.map((pred) => (
                      <TableRow key={pred.id}>
                        <TableCell>
                          <Chip label={pred.prediction_type} size="small" />
                        </TableCell>
                        <TableCell>{pred.target_id || 'N/A'}</TableCell>
                        <TableCell>
                          {pred.confidence_score ? (
                            <Box display="flex" alignItems="center" gap={1}>
                              <LinearProgress
                                variant="determinate"
                                value={pred.confidence_score * 100}
                                sx={{ width: 100, height: 8, borderRadius: 4 }}
                              />
                              <Typography variant="caption">
                                {(pred.confidence_score * 100).toFixed(1)}%
                              </Typography>
                            </Box>
                          ) : (
                            'N/A'
                          )}
                        </TableCell>
                        <TableCell>
                          {new Date(pred.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          {pred.actual_outcome ? (
                            <Chip label="Completed" color="success" size="small" />
                          ) : (
                            <Chip label="Pending" color="default" size="small" />
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          )}
        </Grid>
      )}
    </Container>
  );
};

export default AIPredictions;

