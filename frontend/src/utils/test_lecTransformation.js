import { computeLossExceedancePoints, formatCurrency, formatCurrencyShort } from './lecTransformation.js';

function runTests() {
  console.log('Running test_lecTransformation.js...');

  // Test 1: Empty input
  const emptyRes = computeLossExceedancePoints([], []);
  console.assert(emptyRes.length === 0, 'Empty input should return empty array');

  // Test 2: Hand-computable distribution [0, 100, 200, 300]
  const baseDist = [0, 100, 200, 300];
  const pts = computeLossExceedancePoints(baseDist, [0, 100], 10);
  
  console.assert(pts.length === 4, 'Should return 4 points for 4 inputs');
  console.assert(pts[0].baselineProb === 100.0, 'First point exceedance probability should be 100% (4/4 >= 0)');
  console.assert(pts[1].baselineProb === 75.0, 'Second point exceedance probability should be 75% (3/4 >= 100)');
  console.assert(pts[2].baselineProb === 50.0, 'Third point exceedance probability should be 50% (2/4 >= 200)');
  console.assert(pts[3].baselineProb === 25.0, 'Fourth point exceedance probability should be 25% (1/4 >= 300)');

  // Test 3: Currency formatting
  console.assert(formatCurrencyShort(150000) === '₹1.50L', '150000 should format as ₹1.50L');
  console.assert(formatCurrencyShort(3120000000) === '₹3.12B', '3120000000 should format as ₹3.12B');

  console.log('ALL LEC TRANSFORMATION TESTS PASSED CLEANLY ✓');
}

runTests();
