import { getEligibility, programme, type StudentProfile } from "./fixture-data";

export type ProgrammePrecheck = {
  schoolName: string;
  programmeName: string;
  degreeCheck: boolean;
  creditCheck: boolean;
  englishCheck: boolean;
  needsCourseAllocationReview: true;
};

/**
 * The fixture has one programme and individual student JSON files. This is a
 * transparent precheck only, not a recommendation score or admission result.
 */
export function createProgrammePrecheck(student: StudentProfile): ProgrammePrecheck {
  const checks = getEligibility(student);
  return {
    schoolName: programme.school.name,
    programmeName: programme.program.name,
    degreeCheck: checks.degree,
    creditCheck: checks.credits,
    englishCheck: checks.english,
    needsCourseAllocationReview: true,
  };
}
