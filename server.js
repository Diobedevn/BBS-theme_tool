const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8000;

// Serve static files from current directory
app.use(express.static('.'));

// Serve index.html for root path
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});