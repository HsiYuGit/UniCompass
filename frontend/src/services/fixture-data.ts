export type StudentProfile = {
  student_id: string;
  name: string;
  education_level: string;
  target_degree: string;
  gpa: number;
  gpa_scale: number;
  transcript_subjects: Array<{ name: string; grade: string; credits: number }>;
  experiences: string[];
  interests: string[];
  german_level: string;
  language_scores: { ielts?: number; toefl?: number; gre?: number };
  graduation_credits: number;
  ects_multiplier: number;
  budget_usd_per_year: number;
};

type ProgrammeRecord = {
  status: string;
  collection_metadata: { verification_status: string };
  data: {
    school: { name: string };
    program: { name: string; degree_level: string };
    entrance_requirements: {
      academic_degree: { required: boolean; degree_type: string; field: string };
      coursework_credits: { required: boolean; minimum_total: number; unit: string; groups: Array<{ id: string; minimum_credits: number; topics: string[] }> };
      language_requirements: Array<{ language: string; required: boolean; minimum_level: string | null; accepted_proofs: Array<{ proof_type: string; minimum_result: string }> }>;
      unmodeled_requirements: string[];
    };
  };
};

export type Programme = ProgrammeRecord["data"] & { id: string; verificationStatus: string };

const programmeModules = import.meta.glob("../../../data/schools/*.json", { eager: true, import: "default" }) as Record<string, ProgrammeRecord>;
const profileModules = import.meta.glob("../../../data/transcripts/*_experience.json", { eager: true, import: "default" }) as Record<string, StudentProfile>;

export const programmes: Programme[] = Object.entries(programmeModules)
  .map(([path, record]) => ({ ...record.data, id: path, verificationStatus: record.collection_metadata.verification_status }))
  .sort((left, right) => left.program.name.localeCompare(right.program.name));

export const studentProfiles: StudentProfile[] = Object.values(profileModules)
  .sort((left, right) => left.student_id.localeCompare(right.student_id));

export function ectsEstimate(student: StudentProfile) {
  return student.graduation_credits * student.ects_multiplier;
}

export function getEligibility(student: StudentProfile, programme: Programme) {
  const requirements = programme.entrance_requirements;
  const english = requirements.language_requirements.find((item) => item.language === "english");
  const ielts = english?.accepted_proofs.find((proof) => proof.proof_type === "ielts");
  const toefl = english?.accepted_proofs.find((proof) => proof.proof_type === "toefl_ibt");
  const meetsEnglish = !english || !english.required
    || (student.language_scores.ielts ?? 0) >= Number(ielts?.minimum_result ?? Infinity)
    || (student.language_scores.toefl ?? 0) >= Number(toefl?.minimum_result ?? Infinity);

  return {
    degree: student.education_level === "bachelor_graduate" && student.target_degree === programme.program.degree_level,
    credits: ectsEstimate(student) >= requirements.coursework_credits.minimum_total,
    english: meetsEnglish,
  };
}
