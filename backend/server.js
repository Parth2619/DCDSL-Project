// File: backend/server.js
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import dashboardRoutes from './routes/dashboard.js';
import citiesRoutes from './routes/cities.js';
import stationsRoutes from './routes/stations.js';
import reportsRoutes from './routes/reports.js';
import adminRoutes from './routes/admin.js';
import playgroundRoutes from './routes/playground.js';
import errorHandler from './middleware/errorHandler.js';
import { authenticateAdmin } from './middleware/auth.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Public Routes
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/cities', citiesRoutes);
app.use('/api/stations', stationsRoutes);
app.use('/api/reports', reportsRoutes);
app.use('/api/playground', playgroundRoutes);

// Admin Routes (protected)
app.use('/api/admin', authenticateAdmin, adminRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log(`📊 API Base: http://localhost:${PORT}/api`);
});
