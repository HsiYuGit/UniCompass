import { getEligibility, type Programme, type StudentProfile } from "./fixture-data";

export type ProgrammePrecheck = {
  programmeId: string;
  degreeCheck: boolean;
  creditCheck: boolean;
  englishCheck: boolean;
  needsCourseAllocationReview: true;
  verificationStatus: string;
};

export type RecommendationCandidate = {
  programme: Programme;
  precheck: ProgrammePrecheck;
  state: "ready_for_agent" | "needs_prerequisite";
  blockers: string[];
};

export type RecommendationPreview = {
  readyForAgent: RecommendationCandidate[];
  needsPrerequisite: RecommendationCandidate[];
};

/**
 * A transparent local precheck, not the backend agent's final ranking.
 * The Python agent remains responsible for course allocation, deterministic
 * eligibility aggregation, and fit-based ranking.
 */
export function createProgrammePrecheck(student: StudentProfile, programme: Programme): ProgrammePrecheck {
  const checks = getEligibility(student, programme);
  return {
    programmeId: programme.id,
    degreeCheck: checks.degree,
    creditCheck: checks.credits,
    englishCheck: checks.english,
    needsCourseAllocationReview: true,
    verificationStatus: programme.verificationStatus,
  };
}

export function buildRecommendationPreview(student: StudentProfile, programmes: Programme[]): RecommendationPreview {
  const candidates = programmes.map((programme) => {
    const precheck = createProgrammePrecheck(student, programme);
    const blockers: string[] = [];

    if (!precheck.degreeCheck) blockers.push("學位層級或申請學程不符");
    if (!precheck.creditCheck) blockers.push("已知總學分不足");
    if (!precheck.englishCheck) blockers.push("英語成績未達目前門檻");

    return {
      programme,
      precheck,
      state: blockers.length === 0 ? "ready_for_agent" : "needs_prerequisite",
      blockers,
    } satisfies RecommendationCandidate;
  });

  return {
    readyForAgent: candidates.filter((candidate) => candidate.state === "ready_for_agent"),
    needsPrerequisite: candidates.filter((candidate) => candidate.state === "needs_prerequisite"),
  };
}