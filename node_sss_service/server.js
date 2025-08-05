// node_sss_service/server.js

const express = require("express");
const sss = require("shamirs-secret-sharing");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.json());

function sendError(res, message, status = 400) {
  console.error(message);
  res.status(status).json({ error: message });
}

// --- /split endpoint ---
app.post("/split", (req, res) => {
  const { secret, shares, threshold } = req.body;

  if (!secret || typeof secret !== 'string' || !/^[0-9a-fA-F]+$/.test(secret)) {
    return sendError(res, "Invalid 'secret'. Must be a non-empty hex string.");
  }
  if (typeof shares !== 'number' || shares < 2 || !Number.isInteger(shares)) {
    return sendError(res, "Invalid 'shares'. Must be an integer >= 2.");
  }
  if (typeof threshold !== 'number' || threshold < 2 || threshold > shares || !Number.isInteger(threshold)) {
    return sendError(res, `Invalid 'threshold'. Must be an integer >= 2 and <= shares (${shares}).`);
  }

  try {
    const buffer = Buffer.from(secret, 'hex');
    const splitShares = sss.split(buffer, { shares, threshold });
    res.json({ shares: splitShares.map(s => s.toString('hex')) });
  } catch (e) {
    sendError(res, `Failed to split secret: ${e.message}`, 500);
  }
});

// --- /combine endpoint ---
app.post("/combine", (req, res) => {
  const { shares } = req.body;

  if (!Array.isArray(shares) || shares.length < 2) {
    return sendError(res, "Invalid 'shares'. Must be an array of at least 2 hex strings.");
  }
  if (!shares.every(s => typeof s === 'string' && /^[0-9a-fA-F]+$/.test(s))) {
    return sendError(res, "Invalid 'shares'. All shares must be valid hex strings.");
  }

  try {
    const buffers = shares.map(h => Buffer.from(h, 'hex'));
    const secret = sss.combine(buffers);
    res.json({ secret: secret.toString('hex') });
  } catch (e) {
    sendError(res, `Failed to combine shares: ${e.message}`, 500);
  }
});

const PORT = 31415;
app.listen(PORT, () => {
  console.log(`SSS server running on http://localhost:${PORT}`);
});
