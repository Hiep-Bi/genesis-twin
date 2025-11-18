import {
  CheckCircle as CheckIcon,
  Error as DefectIcon,
  Bolt as EnergyIcon,
  Build as MachineIcon,
  Speed as OEEIcon,
  Inventory2 as ProductionIcon,
  TrendingDown,
  TrendingUp,
  Warning as WarningIcon,
} from '@mui/icons-material';
import {
  Alert,
  Avatar,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Grid,
  LinearProgress,
  Typography,
} from '@mui/material';
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js';
import { useCallback, useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  aiPredictionsAPI,
  analyticsAPI,
  factoriesAPI,
  materialsAPI,
  settingsAPI,
  suppliersAPI,
} from '../services/api';
import websocket from '../services/websocket';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
);

const MetricCard = ({
  title,
  value = '0',
  unit,
  icon: Icon,
  change,
  subtitle,
}) => (
  <Card
    sx={{
      height: '100%',
      backgroundColor: '#fff', // nền trắng
      border: '2px solid #ff6666', // viền đỏ
      borderRadius: 8, // bo góc nhẹ
      boxShadow: '0 2px 6px rgba(0,0,0,0.1)', // bóng nhẹ
      position: 'relative',
      overflow: 'hidden',
    }}
  >
    <CardContent>
      <Box
        display="flex"
        alignItems="flex-start"
        justifyContent="space-between"
        mb={2}
      >
        <Box sx={{ zIndex: 1 }}>
          <Typography
            variant="body2"
            sx={{
              color: '#d32f2f', // đỏ đậm để nổi trên nền trắng
              mb: 1,
              textTransform: 'uppercase',
              fontSize: '0.85rem',
              fontWeight: 700,
              letterSpacing: '1px',
            }}
          >
            {title}
          </Typography>
          <Box display="flex" alignItems="baseline" gap={1}>
            <Typography
              variant="h3"
              sx={{ fontWeight: 800, color: '#333' }} // chữ chính tối, dễ đọc
            >
              {value}
            </Typography>
            {unit && (
              <Typography
                variant="h6"
                sx={{ color: '#666', fontWeight: 600 }} // chữ phụ nhẹ
              >
                {unit}
              </Typography>
            )}
          </Box>
        </Box>
        <Avatar
          sx={{
            width: 56,
            height: 56,
            bgcolor: 'rgba(255, 102, 102, 0.2)', // nền icon đỏ nhạt
          }}
        >
          <Icon sx={{ color: '#d32f2f', fontSize: 28 }} /> {/* icon đỏ đậm */}
        </Avatar>
      </Box>

      <Box display="flex" alignItems="center" gap={1}>
        {change !== undefined && (
          <>
            {change > 0 ? (
              <TrendingUp sx={{ color: '#d32f2f', fontSize: 18 }} />
            ) : (
              <TrendingDown sx={{ color: '#888', fontSize: 18 }} />
            )}
            <Typography
              variant="caption"
              sx={{
                color: change > 0 ? '#d32f2f' : '#888',
                fontWeight: 700,
              }}
            >
              {change > 0 ? '+' : ''}
              {change}%
            </Typography>
          </>
        )}
        {subtitle && (
          <Typography variant="caption" sx={{ color: '#999' }}>
            {subtitle}
          </Typography>
        )}
      </Box>
    </CardContent>
  </Card>
);

const AlertCard = ({ severity, title, message, confidence, action }) => {
  const getColors = () => {
    switch (severity) {
      case 'critical':
        return {
          bg: 'rgba(255, 0, 0, 0.1)',
          border: '#FF0000',
          icon: '#FF0000',
          text: '#fff',
        };
      case 'warning':
        return {
          bg: 'rgba(255, 165, 0, 0.1)',
          border: '#FFA500',
          icon: '#FFA500',
          text: '#fff',
        };
      case 'info':
        return {
          bg: 'rgba(255, 255, 255, 0.1)',
          border: '#CCC',
          icon: '#CCC',
          text: '#fff',
        };
      default:
        return {
          bg: 'rgba(255, 255, 255, 0.1)',
          border: '#CCC',
          icon: '#CCC',
          text: '#fff',
        };
    }
  };

  const colors = getColors();

  return (
    <Card
      sx={{
        bgcolor: colors.bg,
        border: `2px solid ${colors.border}`,
        mb: 2,
        boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" gap={2}>
          <Box>
            <Chip
              label={severity.toUpperCase()}
              size="small"
              sx={{
                bgcolor: colors.icon,
                color: colors.text,
                fontWeight: 700,
                fontSize: '0.7rem',
                height: 24,
              }}
            />
          </Box>
          <Box flex={1}>
            <Typography
              variant="h6"
              sx={{ fontWeight: 700, mb: 0.5, color: '#fff' }}
            >
              {title}
            </Typography>
            <Typography variant="body2" sx={{ mb: 1, color: '#ccc' }}>
              {message}
            </Typography>
            {confidence && (
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Typography variant="caption" sx={{ color: '#bbb' }}>
                  AI Confidence:
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={confidence}
                  sx={{
                    flex: 1,
                    height: 6,
                    borderRadius: 3,
                    bgcolor: 'rgba(255,255,255,0.1)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: colors.icon,
                    },
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{ fontWeight: 700, color: colors.icon }}
                >
                  {confidence}%
                </Typography>
              </Box>
            )}
            {action && (
              <Chip
                label={action}
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.1)',
                  color: '#fff',
                  borderRadius: 1,
                  fontSize: '0.75rem',
                }}
              />
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

// Mock alerts data (if backend doesn't have alerts endpoint)
const mockAlerts = [
  {
    id: 1,
    severity: 'critical',
    title: 'Predictive Maintenance Alert',
    message:
      'Conveyor B2 bearing failure predicted in 12h with 97.8% confidence',
    confidence: 97.8,
    action: 'Create Work Order',
  },
  {
    id: 2,
    severity: 'warning',
    title: 'Quality Control Warning',
    message: 'Welding stage showing 28% increase in defect rate',
    confidence: 94.2,
    action: 'Inspect Line',
  },
  {
    id: 3,
    severity: 'info',
    title: 'Energy Optimization Suggestion',
    message: 'Peak hour consumption can be reduced by 15% with load balancing',
    confidence: 87.5,
    action: 'Review Energy Plan',
  },
];

const Dashboard = () => {
  const fallbackFactories = [
    { id: 'factory-alpha', name: 'Factory Alpha', location: 'Industrial Park East' },
    { id: 'factory-beta', name: 'Factory Beta', location: 'Innovation Hub West' },
  ];
  const fallbackSuppliers = [
    { id: 'sup-001', name: 'Global Components', supplier_code: 'SUP-001' },
    { id: 'sup-002', name: 'Local Raw Materials', supplier_code: 'SUP-002' },
  ];
  const fallbackMaterials = [
    { id: 'mat-001', name: 'Linh kiện A', material_code: 'MAT-001' },
    { id: 'mat-002', name: 'Linh kiện B', material_code: 'MAT-002' },
  ];
  const fallbackSystemSettings = [
    { key: 'dashboard_refresh_interval_sec', value: { interval: 10 } },
    { key: 'anomaly_detection_threshold', value: { threshold: 0.85 } },
  ];
  const fallbackOEEByMachine = [
    { machine_code: 'CNC-001', oee: 91.2 },
    { machine_code: 'ROB-002', oee: 87.5 },
  ];

  const [metrics, setMetrics] = useState({
    oee: 0,
    production_count: 0,
    defect_count: 0,
    energy_consumption_kwh: 0,
    carbon_emissions_kg: 0,
    machines_running: 0,
    machines_total: 0,
  });
  const [energyTrend, setEnergyTrend] = useState(null);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState(mockAlerts);
  const [factories, setFactories] = useState(fallbackFactories);
  const [suppliers, setSuppliers] = useState(fallbackSuppliers);
  const [materials, setMaterials] = useState(fallbackMaterials);
  const [systemSettings, setSystemSettings] = useState(fallbackSystemSettings);
  const [aiPredictions, setAiPredictions] = useState([]);
  const [oeeByMachine, setOeeByMachine] = useState(fallbackOEEByMachine);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);

      // Fetch all dashboard metrics
      const dashboardMetrics = await analyticsAPI.getDashboard();
      if (dashboardMetrics.data) {
        setMetrics(dashboardMetrics.data);
      }

      // Fetch energy trend data
      const energyResponse = await analyticsAPI.getEnergyTrend();
      if (energyResponse.data) {
        setEnergyTrend(energyResponse.data);
      }

      // Fetch OEE by machine data
      const oeeResponse = await analyticsAPI.getOEEByMachine();
      if (oeeResponse.data?.length) {
        setOeeByMachine(oeeResponse.data);
      } else {
        setOeeByMachine(fallbackOEEByMachine);
      }

      // Fetch Factories
      const factoriesResponse = await factoriesAPI.getAll();
      setFactories(
        factoriesResponse.data?.length ? factoriesResponse.data : fallbackFactories,
      );

      // Fetch Suppliers
      const suppliersResponse = await suppliersAPI.getAll();
      setSuppliers(
        suppliersResponse.data?.length ? suppliersResponse.data : fallbackSuppliers,
      );

      // Fetch Materials
      const materialsResponse = await materialsAPI.getAll();
      setMaterials(
        materialsResponse.data?.length ? materialsResponse.data : fallbackMaterials,
      );

      // Fetch System Settings
      const settingsResponse = await settingsAPI.getAll();
      setSystemSettings(
        settingsResponse.data?.length
          ? settingsResponse.data
          : fallbackSystemSettings,
      );

      // Fetch AI Predictions History
      try {
        const aiPredictionsResponse = await aiPredictionsAPI.getHistory({
          limit: 10,
        });
        if (
          aiPredictionsResponse.data &&
          aiPredictionsResponse.data.length > 0
        ) {
          setAiPredictions(aiPredictionsResponse.data);
          // Process AI predictions into alerts for display
          const newAlerts = aiPredictionsResponse.data
            .filter(
              (pred) => pred.confidence_score && pred.confidence_score > 0.8,
            )
            .map((pred) => ({
              severity:
                pred.prediction_type === 'defect' ? 'critical' : 'warning',
              title: `AI Prediction: ${pred.prediction_type}`,
              message:
                pred.prediction_data?.diagnosis ||
                JSON.stringify(pred.prediction_data),
              confidence: pred.confidence_score
                ? Math.round(pred.confidence_score * 100)
                : undefined,
              action: 'Review Prediction',
            }));
          // Merge with mock alerts if API returned predictions
          setAlerts(newAlerts);
        }
      } catch (error) {
        console.error('Failed to fetch AI predictions:', error);
        // Use mock alerts if API fails
        setAlerts(mockAlerts);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setFactories(fallbackFactories);
      setSuppliers(fallbackSuppliers);
      setMaterials(fallbackMaterials);
      setSystemSettings(fallbackSystemSettings);
      setOeeByMachine(fallbackOEEByMachine);
      setAlerts(mockAlerts);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();

    // Subscribe to real-time updates
    websocket.subscribe('dashboard');
    websocket.on('metrics', (data) => {
      setMetrics((prevMetrics) => ({ ...prevMetrics, ...data }));
    });

    const intervalId = setInterval(fetchDashboardData, 30000);

    return () => {
      websocket.unsubscribe('dashboard');
      clearInterval(intervalId);
    };
  }, [fetchDashboardData]);

  const energyChartData = {
    labels:
      energyTrend?.labels ||
      energyTrend?.hourly?.map((d) => new Date(d.hour).getHours() + ':00') ||
      [],
    datasets: [
      {
        label: 'Energy (kWh)',
        data:
          energyTrend?.data ||
          energyTrend?.hourly?.map((d) => d.total_kwh) ||
          [],
        borderColor: '#d32f2f',
        backgroundColor: 'rgba(211, 47, 47, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#d32f2f',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false,
        },
        ticks: {
          font: {
            size: 11,
          },
        },
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false,
        },
        ticks: {
          font: {
            size: 11,
          },
        },
      },
    },
  };

  if (loading && !metrics) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 800,
            color: 'primary.main',
            mb: 2,
          }}
        >
          Factory Command Center
        </Typography>
        <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
          <Chip
            icon={<CheckIcon />}
            label="AI Online: 98.5%"
            color="success"
            variant="outlined"
          />
          <Chip label="Morning Shift A" variant="outlined" />
          <Chip label="Network: Stable" color="success" variant="outlined" />
        </Box>
      </Box>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Factory OEE"
            value={metrics.oee?.toFixed(1) || '0.0'}
            unit="%"
            icon={OEEIcon}
            change={2.3}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Production Output"
            value={metrics.production_count?.toLocaleString() || '0'}
            unit="units"
            icon={ProductionIcon}
            change={5.1}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Defect Rate"
            value={
              metrics.defect_count
                ? (
                    (metrics.defect_count / metrics.production_count) *
                    100
                  ).toFixed(1)
                : '0.0'
            }
            unit="%"
            icon={DefectIcon}
            change={-0.3}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Energy Consumption"
            value={metrics.energy_consumption_kwh?.toFixed(0) || '0'}
            unit="kWh"
            icon={EnergyIcon}
            change={-1.8}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Carbon Emissions"
            value={metrics.carbon_emissions_kg?.toFixed(1) || '0.0'}
            unit="kg"
            icon={MachineIcon}
            change={-2.1}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Machines Running"
            value={`${metrics.machines_running || 0}/${
              metrics.machines_total || 0
            }`}
            icon={WarningIcon}
            change={1.2}
            subtitle="from last hour"
          />
        </Grid>

        {/* AI Alerts & Recommendations */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={3}>
                <WarningIcon color="primary" />
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    flex: 1,
                  }}
                >
                  AI Alerts & Recommendations
                </Typography>
                <Chip label={alerts.length} size="small" color="primary" />
              </Box>
              {alerts.length === 0 ? (
                <Alert severity="success">
                  No active alerts. All systems operating normally.
                </Alert>
              ) : (
                alerts.map((alert, index) => (
                  <AlertCard key={index} {...alert} />
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Energy Trend Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <EnergyIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Energy Consumption (24h)
                </Typography>
              </Box>
              {energyTrend ? (
                <Box sx={{ height: 300 }}>
                  <Line data={energyChartData} options={chartOptions} />
                </Box>
              ) : (
                <Box
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                  height={300}
                >
                  <CircularProgress />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Factories List */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography
                variant="h6"
                sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }}
              >
                Factories
              </Typography>
              {factories.length > 0 ? (
                factories.map((factory) => (
                  <Typography
                    key={factory.id}
                    variant="body2"
                    color="text.secondary"
                  >
                    - {factory.name} ({factory.location})
                  </Typography>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No factories found.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Suppliers List */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography
                variant="h6"
                sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }}
              >
                Suppliers
              </Typography>
              {suppliers.length > 0 ? (
                suppliers.map((supplier) => (
                  <Typography
                    key={supplier.id}
                    variant="body2"
                    color="text.secondary"
                  >
                    - {supplier.name} ({supplier.supplier_code})
                  </Typography>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No suppliers found.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Materials List */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography
                variant="h6"
                sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }}
              >
                Materials
              </Typography>
              {materials.length > 0 ? (
                materials.map((material) => (
                  <Typography
                    key={material.id}
                    variant="body2"
                    color="text.secondary"
                  >
                    - {material.name} ({material.material_code})
                  </Typography>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No materials found.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Settings List */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography
                variant="h6"
                sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }}
              >
                System Settings
              </Typography>
              {systemSettings.length > 0 ? (
                systemSettings.map((setting) => (
                  <Typography
                    key={setting.key}
                    variant="body2"
                    color="text.secondary"
                  >
                    - {setting.key}: {JSON.stringify(setting.value)}
                  </Typography>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No system settings found.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* OEE by Machine */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography
                variant="h6"
                sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }}
              >
                OEE by Machine (Last 24h)
              </Typography>
              <Grid container spacing={2}>
                {oeeByMachine.length > 0 ? (
                  oeeByMachine.map((oeeItem) => (
                    <Grid item xs={12} sm={6} md={3} key={oeeItem.machine_code}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography
                            variant="subtitle1"
                            sx={{ fontWeight: 700 }}
                          >
                            {oeeItem.machine_code}
                          </Typography>
                          <Typography
                            variant="h5"
                            sx={{ color: 'primary.main', fontWeight: 800 }}
                          >
                            {oeeItem.oee}%
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))
                ) : (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      No OEE data available.
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
