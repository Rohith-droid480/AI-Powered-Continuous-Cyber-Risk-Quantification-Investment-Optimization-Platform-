/**
 * Lightweight frontend formatting and alignment utility for Loss Exceedance Curve (CCDF) points.
 *
 * Primary mode: Consumes compact backend-generated LEC coordinate arrays ({ loss, exceedance_probability }).
 * Fallback mode: Processes raw distribution arrays if provided.
 */

export function computeLossExceedancePoints(
  baselineLecOrDist = [],
  postOptLecOrDist = []
) {
  if (!baselineLecOrDist || baselineLecOrDist.length === 0) {
    return [];
  }

  // Check if inputs are already compact coordinate objects { loss, exceedance_probability }
  const isCompactBaseline = typeof baselineLecOrDist[0] === 'object' && baselineLecOrDist[0] !== null && 'exceedance_probability' in baselineLecOrDist[0];
  const isCompactPost = postOptLecOrDist && postOptLecOrDist.length > 0 && typeof postOptLecOrDist[0] === 'object' && postOptLecOrDist[0] !== null && 'exceedance_probability' in postOptLecOrDist[0];

  if (isCompactBaseline) {
    // 1. Process Compact Backend Points directly (Zero heavy browser sorting)
    const postMap = new Map();
    if (isCompactPost) {
      postOptLecOrDist.forEach((p) => {
        postMap.set(p.loss, p.exceedance_probability);
      });
    }

    return baselineLecOrDist.map((basePt) => {
      const lossVal = basePt.loss;
      let postProb = null;

      if (isCompactPost) {
        postProb = interpolateCompactProb(postOptLecOrDist, lossVal);
      }

      return {
        loss: lossVal,
        lossFormatted: formatCurrencyShort(lossVal),
        baselineProb: Number(basePt.exceedance_probability.toFixed(2)),
        postOptProb: postProb !== null ? Number(postProb.toFixed(2)) : null,
      };
    });
  }

  // 2. Fallback for raw numerical arrays if passed
  const sortedBaseline = [...baselineLecOrDist].sort((a, b) => a - b);
  const nBase = sortedBaseline.length;

  return sortedBaseline.map((val, idx) => {
    const prob = ((nBase - idx) / nBase) * 100;
    return {
      loss: val,
      lossFormatted: formatCurrencyShort(val),
      baselineProb: Number(prob.toFixed(2)),
      postOptProb: null,
    };
  });
}

function interpolateCompactProb(compactPoints, targetLoss) {
  if (!compactPoints || compactPoints.length === 0) return 0.0;
  if (targetLoss <= compactPoints[0].loss) return compactPoints[0].exceedance_probability;
  if (targetLoss >= compactPoints[compactPoints.length - 1].loss) return compactPoints[compactPoints.length - 1].exceedance_probability;

  // Linear interpolation between closest points
  for (let i = 0; i < compactPoints.length - 1; i++) {
    const p1 = compactPoints[i];
    const p2 = compactPoints[i + 1];
    if (targetLoss >= p1.loss && targetLoss <= p2.loss) {
      if (p2.loss === p1.loss) return p1.exceedance_probability;
      const ratio = (targetLoss - p1.loss) / (p2.loss - p1.loss);
      return p1.exceedance_probability + ratio * (p2.exceedance_probability - p1.exceedance_probability);
    }
  }
  return 0.0;
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
