import { computeLossExceedancePoints, formatCurrency, formatCurrencyShort } from './lecTransformation.js';

function runTests() {
  console.log('Running test_lecTransformation.js...');

  // Test 1: Empty input
  const emptyRes = computeLossExceedancePoints([], []);
  console.assert(emptyRes.length === 0, 'Empty input should return empty array');

  // Test 2: Compact backend coordinate points
  const compactBaseline = [
    { loss: 0, exceedance_probability: 100.0 },
    { loss: 100000, exceedance_probability: 75.0 },
    { loss: 500000, exceedance_probability: 50.0 },
    { loss: 1000000, exceedance_probability: 25.0 },
  ];
  const compactPost = [
    { loss: 0, exceedance_probability: 100.0 },
    { loss: 100000, exceedance_probability: 40.0 },
    { loss: 500000, exceedance_probability: 10.0 },
    { loss: 1000000, exceedance_probability: 0.0 },
  ];

  const pts = computeLossExceedancePoints(compactBaseline, compactPost);
  
  console.assert(pts.length === 4, 'Should return 4 points');
  console.assert(pts[0].baselineProb === 100.0, 'First point baseline prob should be 100%');
  console.assert(pts[1].postOptProb === 40.0, 'Second point post-opt prob should be 40%');
  console.assert(pts[3].postOptProb === 0.0, 'Fourth point post-opt prob should be 0%');

  // Test 3: Currency formatting
  console.assert(formatCurrencyShort(150000) === '₹1.50L', '150000 should format as ₹1.50L');
  console.assert(formatCurrencyShort(3120000000) === '₹3.12B', '3120000000 should format as ₹3.12B');

  console.log('ALL LEC TRANSFORMATION TESTS PASSED CLEANLY ✓');
}

runTests();
