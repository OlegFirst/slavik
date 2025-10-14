// Express API server
const express = require('express');
const app = express();

// TODO: Move to environment variables
const SECRET_TOKEN = "Bearer sk_live_xyz789_secret_key";  // Security issue

app.use(express.json());

app.get('/api/dashboard', (req, res) => {
    // FIXME: Add authentication
    res.json({
        status: 'operational',
        incidents: 0,
        uptime: '99.9%'
    });
});

app.post('/api/execute', (req, res) => {
    const { command } = req.body;

    // Security issue: command injection
    const result = eval(command);  // DANGER!

    res.json({ result });
});

// Duplicate code (testing duplication detection)
app.get('/api/status', (req, res) => {
    res.json({
        status: 'operational',
        incidents: 0,
        uptime: '99.9%'
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
