const fs = require('node:fs');
const path = require('node:path');

const DEFAULT_ECTS_PER_YEAR = 60;

function convertBavariaGrade(input) {
  const values = normalizeInput(input);
  const targetEctsCredits = round(values.normalDurationYears * DEFAULT_ECTS_PER_YEAR, 2);
  const conversionFactorExact = round(targetEctsCredits / values.totalUniversityCredits, 6);
  const germanGradeExact = round(
    1 + (3 * (values.highestPossibleGrade - values.currentOverallGrade)) /
      (values.highestPossibleGrade - values.lowestPassingGrade),
    2
  );

  return {
    input: {
      normalDurationYears: values.normalDurationYears,
      totalUniversityCredits: values.totalUniversityCredits,
      highestPossibleGrade: values.highestPossibleGrade,
      lowestPassingGrade: values.lowestPassingGrade,
      currentOverallGrade: values.currentOverallGrade,
    },
    creditConversion: {
      ectsPerAcademicYear: DEFAULT_ECTS_PER_YEAR,
      targetEctsCredits,
      conversionFactorExact,
      conversionFactorDisplay: round(conversionFactorExact, 2),
      formula: 'normalDurationYears * 60 / totalUniversityCredits',
    },
    gradeConversion: {
      germanGradeExact,
      germanGradeDisplay: truncateToDecimalPlaces(germanGradeExact, 1),
      formula:
        '1 + 3 * ((highestPossibleGrade - currentOverallGrade) / (highestPossibleGrade - lowestPassingGrade))',
    },
    courses: values.courses.map((course) => convertCourse(course, conversionFactorExact)),
  };
}

function writeBavariaGradeConversionJson({ input, outputPath }) {
  if (!outputPath || typeof outputPath !== 'string') {
    throw new TypeError('outputPath must be a non-empty string');
  }

  const result = convertBavariaGrade(input);

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, 'utf8');

  return {
    outputPath,
    result,
  };
}

function convertCourse(course, conversionFactorExact) {
  const convertedCreditsExact = round(course.credits * conversionFactorExact, 6);
  const weightedGradePointsExact =
    course.grade === null ? null : round(convertedCreditsExact * course.grade, 6);

  return {
    module: course.module,
    originalCredits: course.credits,
    convertedCreditsExact,
    convertedCreditsDisplay: round(convertedCreditsExact, 2),
    grade: course.grade,
    weightedGradePointsExact,
    weightedGradePointsDisplay:
      weightedGradePointsExact === null ? null : round(weightedGradePointsExact, 2),
  };
}

function normalizeInput(input) {
  if (!input || typeof input !== 'object') {
    throw new TypeError('input must be an object');
  }

  const values = {
    normalDurationYears: numberFrom(input.normalDurationYears, 'normalDurationYears'),
    totalUniversityCredits: numberFrom(input.totalUniversityCredits, 'totalUniversityCredits'),
    highestPossibleGrade: numberFrom(input.highestPossibleGrade, 'highestPossibleGrade'),
    lowestPassingGrade: numberFrom(input.lowestPassingGrade, 'lowestPassingGrade'),
    currentOverallGrade: numberFrom(input.currentOverallGrade, 'currentOverallGrade'),
    courses: Array.isArray(input.courses) ? input.courses.map(normalizeCourse) : [],
  };

  if (values.normalDurationYears <= 0) {
    throw new RangeError('normalDurationYears must be greater than 0');
  }

  if (values.totalUniversityCredits <= 0) {
    throw new RangeError('totalUniversityCredits must be greater than 0');
  }

  if (values.highestPossibleGrade === values.lowestPassingGrade) {
    throw new RangeError('highestPossibleGrade and lowestPassingGrade cannot be equal');
  }

  const minGrade = Math.min(values.highestPossibleGrade, values.lowestPassingGrade);
  const maxGrade = Math.max(values.highestPossibleGrade, values.lowestPassingGrade);

  if (values.currentOverallGrade < minGrade || values.currentOverallGrade > maxGrade) {
    throw new RangeError('currentOverallGrade must be between highestPossibleGrade and lowestPassingGrade');
  }

  return values;
}

function normalizeCourse(course, index) {
  if (!course || typeof course !== 'object') {
    throw new TypeError(`courses[${index}] must be an object`);
  }

  const credits = numberFrom(course.credits, `courses[${index}].credits`);

  if (credits < 0) {
    throw new RangeError(`courses[${index}].credits cannot be negative`);
  }

  return {
    module: course.module || course.name || `Course ${index + 1}`,
    credits,
    grade:
      course.grade === undefined || course.grade === null
        ? null
        : numberFrom(course.grade, `courses[${index}].grade`),
  };
}

function numberFrom(value, fieldName) {
  const parsed = typeof value === 'number' ? value : Number(value);

  if (!Number.isFinite(parsed)) {
    throw new TypeError(`${fieldName} must be a finite number`);
  }

  return parsed;
}

function round(value, decimalPlaces) {
  const factor = 10 ** decimalPlaces;
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

function truncateToDecimalPlaces(value, decimalPlaces) {
  const factor = 10 ** decimalPlaces;
  return Math.trunc(value * factor) / factor;
}

module.exports = {
  convertBavariaGrade,
  writeBavariaGradeConversionJson,
};
