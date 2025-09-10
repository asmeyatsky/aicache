const express = require('express');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json({
  verify: (req, res, buf) => {
    // Store raw body for webhook token verification
    req.rawBody = buf.toString();
  }
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Webhook endpoint
app.post('/webhook', (req, res) => {
  // TODO: Implement webhook handling
  console.log('Webhook received:', req.body);
  res.status(200).json({ status: 'processed' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`aicache GitLab App listening on port ${PORT}`);
});

module.exports = app;