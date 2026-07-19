import schoolRecords from "../../../data/schools/schools.json";
import s001 from "../../../data/transcripts/student_profile_S001.json";
import s002 from "../../../data/transcripts/student_profile_S002.json";
import s003 from "../../../data/transcripts/student_profile_S003.json";
import s004 from "../../../data/transcripts/student_profile_S004.json";
import s005 from "../../../data/transcripts/student_profile_S005.json";
import s006 from "../../../data/transcripts/student_profile_S006.json";
import s007 from "../../../data/transcripts/student_profile_S007.json";
import s008 from "../../../data/transcripts/student_profile_S008.json";
import s009 from "../../../data/transcripts/student_profile_S009.json";
import s010 from "../../../data/transcripts/student_profile_S010.json";
import s011 from "../../../data/transcripts/student_profile_S011.json";
import s012 from "../../../data/transcripts/student_profile_S012.json";
import s013 from "../../../data/transcripts/student_profile_S013.json";
import s014 from "../../../data/transcripts/student_profile_S014.json";
import s015 from "../../../data/transcripts/student_profile_S015.json";

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
  data: {
    school: { name: string };
    program: { name: string; degree_level: string };
    entrance_requirements: {
      academic_degree: { required: boolean; degree_type: string; field: string };
      coursework_credits: { required: boolean; minimum_total: number; unit: string; groups: Array<{ id: string; minimum_credits: number; topics: string[] }> };
      language_requirements: Array<{ language: string; required: boolean; minimum_level: string | null; accepted_proofs: Array<{ proof_type: string; minimum_result: string }> }>;
    };
  };
};

export const studentProfiles: StudentProfile[] = [s001, s002, s003, s004, s005, s006, s007, s008, s009, s010, s011, s012, s013, s014, s015];
export const programme = (schoolRecords as ProgrammeRecord[])[0].data;

export function ectsEstimate(student: StudentProfile) {
  return student.graduation_credits * student.ects_multiplier;
}

export function getEligibility(student: StudentProfile) {
  const requirements = programme.entrance_requirements;
  const english = requirements.language_requirements.find((item) => item.language === "english");
  const ieltsProof = english?.accepted_proofs.find((proof) => proof.proof_type === "ielts");
  const toeflProof = english?.accepted_proofs.find((proof) => proof.proof_type === "toefl_ibt");
  const meetsEnglish = (student.language_scores.ielts ?? 0) >= Number(ieltsProof?.minimum_result ?? Infinity)
    || (student.language_scores.toefl ?? 0) >= Number(toeflProof?.minimum_result ?? Infinity);

  return {
    degree: student.education_level === "bachelor_graduate" && student.target_degree === programme.program.degree_level,
    credits: ectsEstimate(student) >= requirements.coursework_credits.minimum_total,
    english: meetsEnglish,
  };
}
