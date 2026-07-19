const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const {
  convertBavariaGrade,
  writeBavariaGradeConversionJson,
} = require('../grade_conversion/bavariaGradeConversion');

test('converts GPA screenshot values from backend grade conversion module', () => {
  const result = convertBavariaGrade({
    normalDurationYears: 4,
    totalUniversityCredits: 128,
    highestPossibleGrade: 4,
    lowestPassingGrade: 2,
    currentOverallGrade: 3.88,
  });

  assert.equal(result.gradeConversion.germanGradeExact, 1.18);
  assert.equal(result.gradeConversion.germanGradeDisplay, 1.1);
});

test('converts credit screenshot values from backend grade conversion module', () => {
  const result = convertBavariaGrade({
    normalDurationYears: 4,
    totalUniversityCredits: 128,
    highestPossibleGrade: 4,
    lowestPassingGrade: 2,
    currentOverallGrade: 3.88,
    courses: [
      {
        module: 'Applied Statistics',
        credits: 5,
        grade: 7,
      },
    ],
  });

  assert.equal(result.creditConversion.targetEctsCredits, 240);
  assert.equal(result.creditConversion.conversionFactorExact, 1.875);
  assert.equal(result.creditConversion.conversionFactorDisplay, 1.88);
  assert.equal(result.courses[0].convertedCreditsDisplay, 9.38);
  assert.equal(result.courses[0].weightedGradePointsDisplay, 65.63);
});

test('writes backend grade conversion output as JSON', () => {
  const outputPath = path.join(os.tmpdir(), `backend-bavaria-conversion-${Date.now()}.json`);

  writeBavariaGradeConversionJson({
    outputPath,
    input: {
      normalDurationYears: 4,
      totalUniversityCredits: 128,
      highestPossibleGrade: 4,
      lowestPassingGrade: 2,
      currentOverallGrade: 3.88,
    },
  });

  const written = JSON.parse(fs.readFileSync(outputPath, 'utf8'));

  assert.equal(written.gradeConversion.germanGradeExact, 1.18);
  assert.equal(written.creditConversion.conversionFactorDisplay, 1.88);
});
