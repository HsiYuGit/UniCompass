import { getEligibility, type Programme, type StudentProfile } from "./fixture-data";

export type ProgrammePrecheck = {
  programmeId: string;
  degreeCheck: boolean;
  creditCheck: boolean;
  englishCheck: boolean;
  needsCourseAllocationReview: true;
  verificationStatus: string;
};

/** A transparent UI precheck, not the backend agent's final ranking. */
export function createProgrammePrecheck(student: StudentProfile, programme: Programme): ProgrammePrecheck {
  const checks = getEligibility(student, programme);
  return { programmeId: programme.id, ...checks, needsCourseAllocationReview: true, verificationStatus: programme.verificationStatus };
}
