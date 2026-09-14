/**
 * Pure statistical utility to compute empirical Loss Exceedance Curve (CCDF) data points
 * for Recharts from raw Monte Carlo loss distribution arrays.
 *
 * Mathematical definition:
 * - X axis = Loss Magnitude S (in INR / ₹)
 * - Y axis = Exceedance Probability P(Loss >= S) in percentage (0% to 100%)
 * - Derived directly as empirical Complementary Cumulative Distribution Function (CCDF).
 */

export function computeLossExceedancePoints(
  baselineDistribution = [],
  postOptDistribution = [],
  maxPoints = 60
) {
  if (!baselineDistribution || baselineDistribution.length === 0) {
    return [];
  }

  // 1. Process Baseline Distribution
  const sortedBaseline = [...baselineDistribution].sort((a, b) => a - b);
  const nBase = sortedBaseline.length;

  const baselinePoints = downsampleDistribution(sortedBaseline, nBase, maxPoints);

  // 2. Process Post-Opt Distribution if available
  let postOptPointsMap = new Map();
  if (postOptDistribution && postOptDistribution.length > 0) {
    const sortedPost = [...postOptDistribution].sort((a, b) => a - b);
    const nPost = sortedPost.length;
    const rawPostPoints = downsampleDistribution(sortedPost, nPost, maxPoints);
    
    // Create interpolation map for matching loss values
    rawPostPoints.forEach(p => {
      postOptPointsMap.set(p.loss, p.prob);
    });
  }

  // 3. Align and construct combined chart points
  const points = baselinePoints.map((basePt) => {
    const lossVal = basePt.loss;
    let postProb = null;

    if (postOptDistribution && postOptDistribution.length > 0) {
      const sortedPost = [...postOptDistribution].sort((a, b) => a - b);
      postProb = interpolateExceedanceProb(sortedPost, lossVal);
    }

    return {
      loss: lossVal,
      lossFormatted: formatCurrencyShort(lossVal),
      baselineProb: Number(basePt.prob.toFixed(2)),
      postOptProb: postProb !== null ? Number(postProb.toFixed(2)) : null,
    };
  });

  return points;
}

function downsampleDistribution(sortedArray, N, targetPoints) {
  if (N <= targetPoints) {
    return sortedArray.map((val, idx) => ({
      loss: val,
      prob: ((N - idx) / N) * 100,
    }));
  }

  const result = [];
  const step = Math.max(1, Math.floor(N / targetPoints));

  for (let i = 0; i < N; i += step) {
    const lossVal = sortedArray[i];
    const probVal = ((N - i) / N) * 100;
    result.push({ loss: lossVal, prob: probVal });
  }

  // Include the max value at 0% exceedance
  const maxLoss = sortedArray[N - 1];
  if (result.length === 0 || result[result.length - 1].loss !== maxLoss) {
    result.push({ loss: maxLoss, prob: 0.0 });
  }

  return result;
}

function interpolateExceedanceProb(sortedArray, targetLoss) {
  const N = sortedArray.length;
  if (N === 0) return 0.0;
  if (targetLoss <= sortedArray[0]) return 100.0;
  if (targetLoss >= sortedArray[N - 1]) return 0.0;

  // Binary search for position
  let low = 0;
  let high = N - 1;
  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (sortedArray[mid] < targetLoss) {
      low = mid + 1;
    } else {
      high = mid - 1;
    }
  }

  // low is index of first element >= targetLoss
  const exceedCount = N - low;
  return (exceedCount / N) * 100;
}

export function formatCurrency(amount) {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatCurrencyShort(amount) {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  if (Math.abs(amount) >= 1_000_000_000) {
    return `₹${(amount / 1_000_000_000).toFixed(2)}B`;
  }
  if (Math.abs(amount) >= 100_000) {
    return `₹${(amount / 100_000).toFixed(2)}L`;
  }
  if (Math.abs(amount) >= 1_000) {
    return `₹${(amount / 1_000).toFixed(1)}K`;
  }
  return `₹${amount.toFixed(0)}`;
}
