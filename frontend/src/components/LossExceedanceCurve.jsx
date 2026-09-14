import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import {
  computeLossExceedancePoints,
  formatCurrency,
  formatCurrencyShort,
} from '../utils/lecTransformation';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="tooltip-title font-mono">
          Loss Magnitude: <strong className="text-white">{formatCurrency(data.loss)}</strong>
        </p>
        <div className="tooltip-details">
          <p className="text-amber">
            Baseline Exceedance: <strong>{data.baselineProb.toFixed(1)}%</strong>
          </p>
          {data.postOptProb !== null && data.postOptProb !== undefined && (
            <p className="text-emerald">
              Post-Opt Exceedance: <strong>{data.postOptProb.toFixed(1)}%</strong>
            </p>
          )}
        </div>
        <p className="tooltip-footnote">
          Interpretation: Probability that annual breach loss exceeds {formatCurrencyShort(data.loss)}.
        </p>
      </div>
    );
  }
  return null;
};

export default function LossExceedanceCurve({
  baselineLec = [],
  postOptLec = [],
  simulationResults = null,
  postOptSimulation = null,
  optimizationResults = null,
}) {
  const chartData = useMemo(() => {
    // If backend compact coordinates are available, use them directly
    if (baselineLec && baselineLec.length > 0) {
      return computeLossExceedancePoints(baselineLec, postOptLec);
    }
    // Fallback if raw array was passed
    if (simulationResults && simulationResults.loss_distribution) {
      return computeLossExceedancePoints(
        simulationResults.loss_distribution,
        postOptSimulation?.loss_distribution || []
      );
    }
    return [];
  }, [baselineLec, postOptLec, simulationResults, postOptSimulation]);

  if (chartData.length === 0) {
    return (
      <div className="chart-card empty-chart">
        <div className="chart-header">
          <h3>Loss Exceedance Curve (Empirical CCDF)</h3>
        </div>
        <p className="empty-message">No simulation exceedance curve data available.</p>
      </div>
    );
  }

  const baselineVar95 = simulationResults?.var_95 || 0;

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <h3>Loss Exceedance Curve (Empirical CCDF)</h3>
          <p className="chart-subtitle">
            Probability of annual breach losses exceeding financial thresholds (Compact backend empirical representation)
          </p>
        </div>
        <div className="chart-legend-badge font-mono">
          <span>X: Loss (₹)</span>
          <span>Y: P(Loss ≥ X) %</span>
        </div>
      </div>

      <div style={{ width: '100%', height: 380 }}>
        <ResponsiveContainer>
          <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
            <defs>
              <linearGradient id="baselineGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="postOptGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />

            <XAxis
              dataKey="loss"
              tickFormatter={formatCurrencyShort}
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
            />

            <YAxis
              unit="%"
              domain={[0, 100]}
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ paddingBottom: '10px' }}
            />

            <Area
              type="monotone"
              dataKey="baselineProb"
              name="Baseline Inherent Exposure"
              stroke="#f59e0b"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#baselineGradient)"
            />

            {postOptLec && postOptLec.length > 0 && (
              <Area
                type="monotone"
                dataKey="postOptProb"
                name="Post-Remediation Residual Exposure"
                stroke="#10b981"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#postOptGradient)"
              />
            )}

            {baselineVar95 > 0 && (
              <ReferenceLine
                x={baselineVar95}
                stroke="#ef4444"
                strokeDasharray="4 4"
                label={{
                  value: `Baseline VaR95: ${formatCurrencyShort(baselineVar95)}`,
                  fill: '#ef4444',
                  fontSize: 11,
                  position: 'top',
                }}
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-footer font-mono">
        <span>* Exceedance probability derived from 100,000 Monte Carlo trial years; compact backend coordinate representation.</span>
      </div>
    </div>
  );
}
