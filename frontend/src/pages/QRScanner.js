import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Chip,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
  Alert,
  CircularProgress,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow
} from '@mui/material';
import {
  QrCodeScanner as QrIcon,
  Search as SearchIcon,
  CheckCircle as CheckIcon,
  LocalShipping as ShipIcon,
  Factory as FactoryIcon,
  Inventory as WarehouseIcon,
  Science as QCIcon,
  Eco as EcoIcon,
  Print as PrintIcon
} from '@mui/icons-material';
import api from '../services/api';

const QRScanner = () => {
  const [qrCode, setQrCode] = useState('');
  const [traceData, setTraceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!qrCode.trim()) {
      setError('Please enter a QR code');
      return;
    }

    setLoading(true);
    setError('');
    setTraceData(null);

    try {
      const response = await api.get(`/api/v1/traceability/trace/${qrCode}`);
      setTraceData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to trace QR code');
    } finally {
      setLoading(false);
    }
  };

  const handlePrintQR = () => {
    window.open(`/api/v1/traceability/qr-image/${qrCode}?size=500`, '_blank');
  };

  const getStepIcon = (step) => {
    switch (step) {
      case 'Receiving':
        return <WarehouseIcon />;
      case 'Warehousing':
        return <WarehouseIcon />;
      case 'Machining':
        return <FactoryIcon />;
      case 'QC':
        return <QCIcon />;
      case 'Shipping':
        return <ShipIcon />;
      default:
        return <CheckIcon />;
    }
  };

  const getStepColor = (step) => {
    switch (step) {
      case 'Receiving':
        return 'primary';
      case 'Warehousing':
        return 'secondary';
      case 'Machining':
        return 'warning';
      case 'QC':
        return 'success';
      case 'Shipping':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        <QrIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        QR Code Traceability
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Scan or enter QR code to trace complete product journey
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Search Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Enter QR Code"
                placeholder="e.g., PRD-20250113-ABC789"
                value={qrCode}
                onChange={(e) => setQrCode(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                disabled={loading}
              />
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                onClick={handleSearch}
                disabled={loading}
                sx={{ minWidth: 120 }}
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Trace Results */}
        {traceData && (
          <>
            {/* Digital Birth Certificate */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                      📜 Digital Birth Certificate
                    </Typography>
                    <Button
                      size="small"
                      startIcon={<PrintIcon />}
                      onClick={handlePrintQR}
                    >
                      Print QR
                    </Button>
                  </Box>

                  <Divider sx={{ mb: 2 }} />

                  <TableContainer>
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell><strong>QR Code</strong></TableCell>
                          <TableCell>
                            <Chip label={traceData.qr_code} color="primary" />
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell><strong>Born At</strong></TableCell>
                          <TableCell>
                            {new Date(traceData.digital_birth_certificate.born_at).toLocaleString()}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell><strong>Machine</strong></TableCell>
                          <TableCell>
                            {traceData.digital_birth_certificate.birthplace.machine}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell><strong>Factory</strong></TableCell>
                          <TableCell>
                            {traceData.digital_birth_certificate.birthplace.factory}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell><strong>Product Code</strong></TableCell>
                          <TableCell>
                            {traceData.digital_birth_certificate.dna.product_code}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell><strong>Serial Number</strong></TableCell>
                          <TableCell>
                            {traceData.digital_birth_certificate.dna.serial_number}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell><strong>Quality Status</strong></TableCell>
                          <TableCell>
                            <Chip
                              label={traceData.digital_birth_certificate.dna.quality_status}
                              color={
                                traceData.digital_birth_certificate.dna.quality_status === 'passed'
                                  ? 'success'
                                  : 'error'
                              }
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Environmental Impact */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <EcoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Environmental Impact
                  </Typography>

                  <Divider sx={{ mb: 2 }} />

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                        <Typography variant="h5" color="success.dark">
                          {traceData.environmental_impact.energy_consumed_kwh}
                        </Typography>
                        <Typography variant="body2">kWh Energy</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
                        <Typography variant="h5" color="info.dark">
                          {traceData.environmental_impact.carbon_footprint_kg}
                        </Typography>
                        <Typography variant="body2">kg CO₂</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                        <Typography variant="h5" color="primary.dark">
                          {traceData.environmental_impact.water_used_liters}
                        </Typography>
                        <Typography variant="body2">Liters Water</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
                        <Typography variant="h5" color="warning.dark">
                          {traceData.environmental_impact.waste_generated_kg}
                        </Typography>
                        <Typography variant="body2">kg Waste</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Journey Timeline */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  🚀 Product Journey ({traceData.total_steps} Steps)
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Current Location: <strong>{traceData.current_location}</strong>
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Timeline position="alternate">
                  {traceData.journey.map((step, index) => (
                    <TimelineItem key={index}>
                      <TimelineOppositeContent color="text.secondary">
                        {step.timestamp ? new Date(step.timestamp).toLocaleString() : 'Pending'}
                      </TimelineOppositeContent>
                      <TimelineSeparator>
                        <TimelineDot color={getStepColor(step.step)}>
                          {getStepIcon(step.step)}
                        </TimelineDot>
                        {index < traceData.journey.length - 1 && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent>
                        <Paper elevation={3} sx={{ p: 2 }}>
                          <Typography variant="h6" component="span">
                            {step.icon} {step.step}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Location: {step.location}
                          </Typography>
                          {step.scanned_by && (
                            <Typography variant="caption" display="block">
                              Scanned by: {step.scanned_by}
                            </Typography>
                          )}
                        </Paper>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              </Paper>
            </Grid>
          </>
        )}
      </Grid>
    </Container>
  );
};

export default QRScanner;

