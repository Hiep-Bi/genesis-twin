import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
  Alert,
  LinearProgress,
  Avatar,
} from '@mui/material';
import {
  Speed as OEEIcon,
  Bolt as EnergyIcon,
  Co2 as CarbonIcon,
  Inventory as ProductionIcon,
  Error as DefectIcon,
  Precision as MachineIcon,
  TrendingUp,
  TrendingDown,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { analyticsAPI } from '../services/api';
import websocket from '../services/websocket';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Modern Metric Card with Gradient
const MetricCard = ({ title, value, unit, icon: Icon, gradient, change, subtitle }) => (
  <Card 
    sx={{ 
      height: '100%',
      background: `linear-gradient(135deg, ${gradient[0]} 0%, ${gradient[1]} 100%)`,
      border: '1px solid rgba(255, 255, 255, 0.1)',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        right: 0,
        width: '150px',
        height: '150px',
        background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
        borderRadius: '50%',
        transform: 'translate(50%, -50%)',
      }
    }}
  >
    <CardContent>
      <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={2}>
        <Box sx={{ zIndex: 1 }}>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1, textTransform: 'uppercase', fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.5px' }}>
            {title}
          </Typography>
          <Box display="flex" alignItems="baseline" gap={1}>
            <Typography variant="h3" sx={{ fontWeight: 700, color: '#fff' }}>
              {value}
            </Typography>
            {unit && (
              <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.8)', fontWeight: 500 }}>
                {unit}
              </Typography>
            )}
          </Box>
        </Box>
        <Avatar
          sx={{
            width: 56,
            height: 56,
            bgcolor: 'rgba(255,255,255,0.2)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <Icon sx={{ color: '#fff', fontSize: 28 }} />
        </Avatar>
      </Box>
      
      <Box display="flex" alignItems="center" gap={1}>
        {change !== undefined && (
          <>
            {change > 0 ? (
              <TrendingUp sx={{ color: '#00ff88', fontSize: 18 }} />
            ) : (
              <TrendingDown sx={{ color: '#ff4757', fontSize: 18 }} />
            )}
            <Typography variant="caption" sx={{ color: change > 0 ? '#00ff88' : '#ff4757', fontWeight: 600 }}>
              {change > 0 ? '+' : ''}{change}%
            </Typography>
          </>
        )}
        {subtitle && (
          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
            {subtitle}
          </Typography>
        )}
      </Box>
    </CardContent>
  </Card>
);

// Alert Card Component
const AlertCard = ({ severity, title, message, confidence, action }) => {
  const getColors = () => {
    switch(severity) {
      case 'critical': return { bg: 'rgba(255, 71, 87, 0.1)', border: '#ff4757', icon: '#ff4757' };
      case 'warning': return { bg: 'rgba(255, 184, 0, 0.1)', border: '#ffb800', icon: '#ffb800' };
      case 'info': return { bg: 'rgba(0, 217, 255, 0.1)', border: '#00d9ff', icon: '#00d9ff' };
      default: return { bg: 'rgba(0, 255, 136, 0.1)', border: '#00ff88', icon: '#00ff88' };
    }
  };

  const colors = getColors();

  return (
    <Card 
      sx={{ 
        bgcolor: colors.bg,
        border: `1px solid ${colors.border}`,
        mb: 2
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
                color: '#000',
                fontWeight: 700,
                fontSize: '0.7rem',
                height: 24
              }}
            />
          </Box>
          <Box flex={1}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              {title}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {message}
            </Typography>
            {confidence && (
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Typography variant="caption" color="text.secondary">
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
                      bgcolor: colors.icon
                    }
                  }} 
                />
                <Typography variant="caption" sx={{ fontWeight: 600, color: colors.icon }}>
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
                  borderRadius: 1,
                  fontSize: '0.75rem'
                }}
              />
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    oee: 85.7,
    production: 12847,
    defectRate: 1.2,
    energy: 4892,
    carbon: 2.15,
    downtime: 6
  });
  const [energyTrend, setEnergyTrend] = useState(null);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([
    {
      severity: 'critical',
      title: 'Predictive Maintenance',
      message: 'Conveyor B2 bearing failure predicted in 12h',
      confidence: 97.8,
      action: 'Create Work Order'
    },
    {
      severity: 'warning',
      title: 'Quality Control',
      message: 'Welding stage showing 28% more defects',
      confidence: 94.2,
      action: 'Inspect Line'
    },
    {
      severity: 'info',
      title: 'Supply Chain',
      message: 'Shipment delay risk - Storm affecting Supplier B route',
      confidence: 89.5,
      action: 'Notify Supplier'
    }
  ]);

  useEffect(() => {
    fetchDashboardData();
    
    // Subscribe to real-time updates
    websocket.subscribe('dashboard');
    websocket.on('metrics', (data) => {
      setMetrics(prevMetrics => ({...prevMetrics, ...data}));
    });
    
    return () => {
      websocket.unsubscribe('dashboard');
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch energy trend data
      const energyResponse = await analyticsAPI.getEnergyAnalytics({
        start_date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        end_date: new Date().toISOString()
      });
      
      if (energyResponse.data) {
        setEnergyTrend(energyResponse.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const energyChartData = {
    labels: energyTrend?.hourly?.map(d => new Date(d.hour).getHours() + ':00') || [],
    datasets: [
      {
        label: 'Energy (kWh)',
        data: energyTrend?.hourly?.map(d => d.total_kwh) || [],
        borderColor: '#00d9ff',
        backgroundColor: 'rgba(0, 217, 255, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(21, 25, 50, 0.95)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(0, 217, 255, 0.3)',
        borderWidth: 1,
        padding: 12,
        displayColors: false
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
          drawBorder: false
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
          font: {
            size: 11
          }
        }
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
          drawBorder: false
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
          font: {
            size: 11
          }
        }
      }
    }
  };

  if (loading && !metrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 700,
            background: 'linear-gradient(135deg, #00d9ff 0%, #00ff88 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1
          }}
        >
          AI Factory Command Center
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Chip 
            icon={<CheckIcon sx={{ color: '#00ff88 !important' }} />}
            label="AI Online: 98.5%" 
            sx={{ 
              bgcolor: 'rgba(0, 255, 136, 0.1)', 
              color: '#00ff88',
              fontWeight: 600,
              border: '1px solid rgba(0, 255, 136, 0.3)'
            }} 
          />
          <Chip 
            label="Morning Shift A" 
            sx={{ 
              bgcolor: 'rgba(0, 217, 255, 0.1)', 
              color: '#00d9ff',
              fontWeight: 600,
              border: '1px solid rgba(0, 217, 255, 0.3)'
            }} 
          />
          <Chip 
            label={`Network: Stable`} 
            sx={{ 
              bgcolor: 'rgba(255, 255, 255, 0.05)', 
              color: 'rgba(255, 255, 255, 0.7)',
              fontWeight: 600
            }} 
          />
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Factory OEE"
            value={metrics.oee}
            unit="%"
            icon={OEEIcon}
            gradient={['#667eea', '#764ba2']}
            change={2.3}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Production Output"
            value={metrics.production.toLocaleString()}
            unit="units"
            icon={ProductionIcon}
            gradient={['#f093fb', '#f5576c']}
            change={5.1}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Defect Rate"
            value={metrics.defectRate}
            unit="%"
            icon={DefectIcon}
            gradient={['#fa709a', '#fee140']}
            change={-0.3}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Energy Efficiency"
            value={metrics.energy.toLocaleString()}
            unit="kWh"
            icon={EnergyIcon}
            gradient={['#30cfd0', '#330867']}
            change={-1.8}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Supply Chain OTIF"
            value="94.2"
            unit="%"
            icon={MachineIcon}
            gradient={['#a8edea', '#fed6e3']}
            change={1.8}
            subtitle="from last hour"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Unplanned Downtime"
            value={metrics.downtime}
            unit="hrs/month"
            icon={WarningIcon}
            gradient={['#ff9a56', '#ff6a88']}
            change={-1.2}
            subtitle="from last hour"
          />
        </Grid>

        {/* AI Alerts & Recommendations */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <WarningIcon sx={{ color: '#ff4757' }} />
                AI Alerts & Recommendations
                <Chip label={alerts.length} size="small" sx={{ ml: 'auto', bgcolor: '#ff4757', color: '#fff', fontWeight: 700 }} />
              </Typography>
              {alerts.map((alert, index) => (
                <AlertCard key={index} {...alert} />
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Energy Trend Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                <EnergyIcon sx={{ verticalAlign: 'middle', mr: 1, color: '#00d9ff' }} />
                Energy Consumption (24h)
              </Typography>
              {energyTrend ? (
                <Box sx={{ height: 300 }}>
                  <Line data={energyChartData} options={chartOptions} />
                </Box>
              ) : (
                <Box display="flex" justifyContent="center" alignItems="center" height={300}>
                  <CircularProgress />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
