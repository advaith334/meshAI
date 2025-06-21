import React, { useState } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
  List,
  ListItem,
  TextField,
  Button,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import WordCloud from 'react-d3-cloud';

// ---------------------------
// Mock data utilities
// ---------------------------

function randomBetween(min, max) {
  return Math.random() * (max - min) + min;
}

function sample(arr, n) {
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

const influencerPool = [
  '@news_flash',
  '@trend_watch',
  '@voice_usa',
  '@politico_daily',
  '@common_sense',
  '@left_field',
  '@center_stage',
  '@right_now',
  '@insiderbuzz',
  '@policy_guru',
];

const keywords = [
  'campaign',
  'policy',
  'crisis',
  'leadership',
  'economy',
  'health',
  'education',
  'social',
  'media',
  'reform',
  'election',
  'debate',
  'scandal',
  'growth',
];

function generateMockRound(id) {
  // Risk score 0-100
  const risk = Math.floor(randomBetween(0, 100));

  // Segment sentiment
  const segment = {
    Progressives: randomBetween(-1, 1),
    Moderates: randomBetween(-1, 1),
    Conservatives: randomBetween(-1, 1),
  };

  // Influencers
  const shuffled = sample(influencerPool, influencerPool.length);
  const influencers = shuffled.slice(0, 7).map((name, idx) => ({
    rank: idx + 1,
    name,
    followers: Math.floor(randomBetween(50_000, 2_000_000)),
    sentiment: randomBetween(-1, 1),
    virality: sample(['🚨 High', '⚠️ Medium', '🟢 Low'], 1)[0],
  }));

  // Narratives
  const narrativeWords = sample(keywords, 8);
  const narratives = narrativeWords.map((w) => ({ text: w, value: Math.floor(randomBetween(10, 100)) }));

  // Recommendations (top 3 negative influencers)
  const negative = influencers.filter((i) => i.sentiment < 0).sort((a, b) => a.sentiment - b.sentiment);
  const recommendations = negative.slice(0, 3).map((i) => `Engage directly with ${i.name} to address misinformation`);

  return { id, risk, segment, influencers, narratives, recommendations };
}

// Pre-generate rounds 1..3
const initialRounds = [1, 2, 3].map((id) => generateMockRound(id));

// ---------------------------
// Helper components
// ---------------------------

function SentimentChip({ value }) {
  if (value > 0.2) return <Chip label="Positive" color="success" size="small" />;
  if (value < -0.2) return <Chip label="Negative" color="error" size="small" />;
  return <Chip label="Neutral" color="warning" size="small" />;
}

function CrisisHealthBar({ risk }) {
  let color = 'success';
  if (risk > 66) color = 'error';
  else if (risk > 33) color = 'warning';
  return (
    <Box sx={{ width: '100%' }}>
      <LinearProgress variant="determinate" value={risk} color={color} sx={{ height: 15, borderRadius: 5 }} />
      <Box display="flex" justifyContent="space-between" mt={0.5} px={0.5}>
        <Typography variant="caption" color="error.main">
          Critical
        </Typography>
        <Typography variant="caption" color="warning.main">
          Moderate
        </Typography>
        <Typography variant="caption" color="success.main">
          Stable
        </Typography>
      </Box>
    </Box>
  );
}

function SegmentSentimentChart({ data }) {
  const chartData = Object.entries(data).map(([k, v]) => ({ segment: k, sentiment: Math.abs(v), raw: v }));
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
        <XAxis dataKey="segment" />
        <YAxis domain={[0, 1]} />
        <Tooltip formatter={(value, name, props) => props.payload.raw.toFixed(2)} />
        <Bar dataKey="sentiment" fill="#1976d2">
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.raw > 0 ? '#4caf50' : entry.raw < 0 ? '#d32f2f' : '#ffb300'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// ---------------------------
// Main App Component
// ---------------------------

export default function App() {
  const [rounds, setRounds] = useState(initialRounds);
  const [selectedRoundId, setSelectedRoundId] = useState(1);
  const [stimulus, setStimulus] = useState('');
  const [target, setTarget] = useState('Mass Media');

  const current = rounds.find((r) => r.id === selectedRoundId) || rounds[0];

  const runSimulation = () => {
    const newId = rounds[rounds.length - 1].id + 1;
    const newRound = generateMockRound(newId);
    setRounds([...rounds, newRound]);
    setSelectedRoundId(newId);
  };

  return (
    <Box p={2} sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <Typography variant="h4" gutterBottom>
        Crisis Command Console
      </Typography>

      {/* Live Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Live Crisis Sentiment Status
          </Typography>
          <CrisisHealthBar risk={current.risk} />
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        {/* Segment Sentiment */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Segment Sentiment
              </Typography>
              <SegmentSentimentChart data={current.segment} />
            </CardContent>
          </Card>
        </Grid>
        {/* Narrative Cloud */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Narrative Cloud
              </Typography>
              <Box sx={{ height: 260 }}>
                <WordCloud
                  data={current.narratives}
                  width={500}
                  height={250}
                  fontSize={(word) => word.value}
                  rotate={(word) => 0}
                  padding={2}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Influencer Leaderboard */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Influencer Leaderboard
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>Influencer Name</TableCell>
                    <TableCell>Followers</TableCell>
                    <TableCell>Sentiment</TableCell>
                    <TableCell>Virality</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {current.influencers.map((inf) => (
                    <TableRow key={inf.rank}>
                      <TableCell>{inf.rank}</TableCell>
                      <TableCell>
                        <Typography fontWeight="bold">{inf.name}</Typography>
                      </TableCell>
                      <TableCell>{inf.followers.toLocaleString()}</TableCell>
                      <TableCell>
                        <SentimentChip value={inf.sentiment} />
                      </TableCell>
                      <TableCell>{inf.virality}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>

        {/* Intervention Recommendations */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Intervention Recommendations
              </Typography>
              <List dense>
                {current.recommendations.map((rec, idx) => (
                  <ListItem key={idx}>
                    <Chip color="warning" label={rec} sx={{ width: '100%' }} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Scenario Controls */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Scenario Controls
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <TextField
              label="Enter campaign message"
              value={stimulus}
              onChange={(e) => setStimulus(e.target.value)}
              fullWidth
            />
            <FormControl sx={{ minWidth: 180 }}>
              <InputLabel id="target-label">Injection Target</InputLabel>
              <Select
                labelId="target-label"
                value={target}
                label="Injection Target"
                onChange={(e) => setTarget(e.target.value)}
              >
                <MenuItem value="Mass Media">Mass Media</MenuItem>
                <MenuItem value="Influencer Only">Influencer Only</MenuItem>
                <MenuItem value="Fringe Communities">Fringe Communities</MenuItem>
              </Select>
            </FormControl>
            <Button variant="contained" onClick={runSimulation}>
              Run Simulation
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {/* Timeline Playback */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Timeline Playback
          </Typography>
          <Stack direction="row" spacing={1}>
            {rounds.map((r) => (
              <Button
                key={r.id}
                variant={r.id === selectedRoundId ? 'contained' : 'outlined'}
                onClick={() => setSelectedRoundId(r.id)}
              >
                Round {r.id}
              </Button>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
} 