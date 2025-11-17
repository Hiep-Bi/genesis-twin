import { DeviceHub, Bolt as EnergyIcon, Storage } from '@mui/icons-material';
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js';
import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { analyticsAPI, factoryOperationsAPI } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
);

const fallbackEnergyTrend = {
  labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
  data: [120, 135, 180, 210, 190, 160],
  summary: {
    total_energy_kwh: 995,
    carbon_kg: 420,
    average_power_kw: 42,
  },
};

const fallbackInventory = {
  summary: {
    total_items: 4200,
    critical_materials: 12,
    external_staging_percent: 38,
  },
  locations: [
    { location: 'main_warehouse', total_quantity: 2700, material_count: 120 },
    { location: 'external_staging', total_quantity: 1500, material_count: 45 },
  ],
};

const fallbackIotDevices = [
  {
    id: 'IOT-USB-001',
    machine_code: 'CNC-001',
    status: 'online',
    last_sync: new Date().toISOString(),
    battery_percent: 94,
  },
  {
    id: 'IOT-USB-002',
    machine_code: 'ROB-001',
    status: 'offline',
    last_sync: new Date(Date.now() - 3600000).toISOString(),
    battery_percent: 0,
  },
];

const Energy = () => {
  const [loading, setLoading] = useState(true);
  const [energyTrend, setEnergyTrend] = useState(null);
  const [inventoryStatus, setInventoryStatus] = useState(null);
  const [iotDevices, setIotDevices] = useState([]);

  useEffect(() => {
    fetchEnergyData();
  }, []);

  const fetchEnergyData = async () => {
    setLoading(true);
    try {
      const [energyRes, inventoryRes, iotRes] = await Promise.all([
        analyticsAPI.getEnergyTrend(),
        factoryOperationsAPI.getInventoryStatus(),
        factoryOperationsAPI.getIotDeviceStatus(),
      ]);

      setEnergyTrend(
        energyRes.data && (energyRes.data.hourly || energyRes.data.data)
          ? {
              labels:
                energyRes.data.labels ||
                energyRes.data.hourly?.map(
                  (point) => `${new Date(point.hour).getHours()}:00`,
                ),
              data:
                energyRes.data.data ||
                energyRes.data.hourly?.map((point) => point.total_kwh),
              summary: {
                total_energy_kwh: energyRes.data.total_energy_kwh ?? 0,
                carbon_kg: energyRes.data.total_carbon_kg ?? 0,
                average_power_kw: energyRes.data.average_power_kw ?? 0,
              },
            }
          : fallbackEnergyTrend,
      );

      setInventoryStatus(
        inventoryRes.data && inventoryRes.data.summary
          ? inventoryRes.data
          : fallbackInventory,
      );

      setIotDevices(
        Array.isArray(iotRes.data?.devices) && iotRes.data.devices.length > 0
          ? iotRes.data.devices
          : fallbackIotDevices,
      );
    } catch (error) {
      console.error('Failed to fetch energy data:', error);
      setEnergyTrend(fallbackEnergyTrend);
      setInventoryStatus(fallbackInventory);
      setIotDevices(fallbackIotDevices);
    } finally {
      setLoading(false);
    }
  };

  const energyChartData = {
    labels: energyTrend?.labels || fallbackEnergyTrend.labels,
    datasets: [
      {
        label: 'Energy (kWh)',
        data: energyTrend?.data || fallbackEnergyTrend.data,
        borderColor: '#d32f2f',
        backgroundColor: 'rgba(211, 47, 47, 0.1)',
        fill: true,
        tension: 0.3,
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderWidth: 1,
        borderColor: '#d32f2f',
      },
    },
    scales: {
      x: { grid: { color: 'rgba(0,0,0,0.1)' } },
      y: { grid: { color: 'rgba(0,0,0,0.1)' } },
    },
  };

  if (loading) {
    return (
      <Box
        sx={{
          minHeight: '70vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Typography variant="h4" fontWeight={700}>
          <EnergyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Energy & IoT Operations
        </Typography>
        <Chip label="Live" color="success" variant="outlined" />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Total Energy (24h)
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {energyTrend?.summary?.total_energy_kwh?.toLocaleString() ||
                  fallbackEnergyTrend.summary.total_energy_kwh}
                <Typography
                  component="span"
                  variant="h6"
                  color="text.secondary"
                >
                  {' '}
                  kWh
                </Typography>
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min(
                  (energyTrend?.summary?.total_energy_kwh || 0) / 15,
                  100,
                )}
                sx={{ mt: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Carbon Footprint
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {energyTrend?.summary?.carbon_kg?.toFixed(1) ||
                  fallbackEnergyTrend.summary.carbon_kg}
                <Typography
                  component="span"
                  variant="h6"
                  color="text.secondary"
                >
                  {' '}
                  kg CO₂
                </Typography>
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                Carbon intensity:{' '}
                {energyTrend?.summary?.total_energy_kwh
                  ? (
                      energyTrend.summary.carbon_kg /
                      energyTrend.summary.total_energy_kwh
                    ).toFixed(2)
                  : '0.42'}{' '}
                kg/kWh
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Average Power Draw
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {energyTrend?.summary?.average_power_kw?.toFixed(1) ||
                  fallbackEnergyTrend.summary.average_power_kw}
                <Typography
                  component="span"
                  variant="h6"
                  color="text.secondary"
                >
                  {' '}
                  kW
                </Typography>
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Includes CNC, robotics and HVAC loads.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card sx={{ height: 360 }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <EnergyIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Energy Consumption Trend
                </Typography>
              </Box>
              <Box sx={{ height: 280 }}>
                <Line data={energyChartData} options={chartOptions} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: 360 }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Storage color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Inventory Snapshot
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight={800}>
                {inventoryStatus?.summary?.total_items ??
                  fallbackInventory.summary.total_items}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Total items across warehouses
              </Typography>
              <Alert severity="warning" sx={{ mb: 2 }}>
                Critical materials:{' '}
                {inventoryStatus?.summary?.critical_materials ??
                  fallbackInventory.summary.critical_materials}
              </Alert>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {(
                      inventoryStatus?.locations || fallbackInventory.locations
                    ).map((loc) => (
                      <TableRow key={loc.location}>
                        <TableCell>{loc.location}</TableCell>
                        <TableCell align="right">
                          {loc.total_quantity?.toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <DeviceHub color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  IoT Device Status
                </Typography>
              </Box>
              {iotDevices.length === 0 ? (
                <Alert severity="info">
                  No IoT devices have reported data in the last 24 hours.
                </Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Device ID</TableCell>
                        <TableCell>Machine</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Battery</TableCell>
                        <TableCell>Last Sync</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {iotDevices.map((device) => (
                        <TableRow key={device.id}>
                          <TableCell>{device.id}</TableCell>
                          <TableCell>{device.machine_code}</TableCell>
                          <TableCell>
                            <Chip
                              label={device.status}
                              color={
                                device.status === 'online'
                                  ? 'success'
                                  : 'default'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box
                              sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1,
                              }}
                            >
                              {device.battery_percent ?? 0}%
                              <LinearProgress
                                variant="determinate"
                                value={device.battery_percent ?? 0}
                                sx={{ width: 80 }}
                              />
                            </Box>
                          </TableCell>
                          <TableCell>
                            {device.last_sync
                              ? new Date(device.last_sync).toLocaleString()
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
      </Grid>
    </Container>
  );
};

export default Energy;
