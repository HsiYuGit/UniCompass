"use client";

import { useMemo, useState } from "react";
import { ectsEstimate, getEligibility, programme, studentProfiles } from "../src/services/fixture-data";
import "./data.css";

const displayDegree: Record<string, string> = { master: "碩士", bachelor_graduate: "已取得學士" };

export default function Home() {
  const [studentId, setStudentId] = useState(studentProfiles[0].student_id);
  const student = useMemo(() => studentProfiles.find((item) => item.student_id === studentId) ?? studentProfiles[0], [studentId]);
  const checks = getEligibility(student);
  const requirements = programme.entrance_requirements;
  const english = requirements.language_requirements.find((item) => item.language === "english");
  const estimate = ectsEstimate(student);

  return <main className="data-shell">
    <header className="data-header">
      <a className="data-brand" href="#top"><span aria-hidden="true">U</span>UniCompass</a>
      <p>德國選校陪跑 · 目前使用同步的假資料</p>
    </header>

    <section className="data-hero" id="top">
      <div><p className="data-kicker">從資料看懂下一步</p><h1>先認識這位申請者，再一起檢視課程條件。</h1><p>這不是錄取預測。UniCompass 只顯示 JSON 已提供的事實，以及仍需要後端判定的部分。</p></div>
      <label className="profile-picker" htmlFor="student">選擇假資料中的申請者<select id="student" value={studentId} onChange={(event) => setStudentId(event.target.value)}>{studentProfiles.map((item) => <option key={item.student_id} value={item.student_id}>{item.student_id} · {item.name}</option>)}</select></label>
    </section>

    <section className="programme-banner" aria-label="目標課程"><p>目前唯一課程資料</p><div><span>{programme.program.degree_level}</span><h2>{programme.program.name}</h2><strong>{programme.school.name}</strong></div></section>

    <section className="profile-grid" aria-label="申請者背景">
      <div className="identity"><p className="section-label">申請者輪廓</p><h2>{student.name}</h2><p>{student.student_id} · {displayDegree[student.education_level] ?? student.education_level} · 目標 {displayDegree[student.target_degree] ?? student.target_degree}</p><div className="interest-list">{student.interests.map((interest) => <span key={interest}>{interest}</span>)}</div></div>
      <dl className="facts"><div><dt>GPA</dt><dd>{student.gpa} <small>/ {student.gpa_scale}</small></dd></div><div><dt>推估 ECTS</dt><dd>{estimate} <small>ECTS</small></dd></div><div><dt>德語</dt><dd>{student.german_level}</dd></div><div><dt>年度預算</dt><dd>${student.budget_usd_per_year.toLocaleString()}</dd></div></dl>
    </section>

    <section className="review-section"><div className="section-intro"><p className="data-kicker">條件對照</p><h2>這些是可直接由目前資料檢查的項目。</h2><p>課程群組的學分分配有不可重複計算規則，必須由後端推薦邏輯完成，前端不自行判定。</p></div><div className="check-list"><CheckRow label="學位方向" detail={`需要 ${requirements.academic_degree.degree_type.replaceAll("_", " ")}`} passed={checks.degree} /><CheckRow label="總學分" detail={`推估 ${estimate} / 至少 ${requirements.coursework_credits.minimum_total} ${requirements.coursework_credits.unit}`} passed={checks.credits} /><CheckRow label="英文證明" detail={english ? `需要 ${english.minimum_level}；IELTS ${student.language_scores.ielts ?? "未提供"}、TOEFL ${student.language_scores.toefl ?? "未提供"}` : "課程資料未提供英文條件"} passed={checks.english} /><div className="check-row pending"><div><p>課程群組</p><span>需要以單一最佳群組分配每門課，待後端計算</span></div><strong>待判定</strong></div></div></section>

    <section className="course-section"><div><p className="section-label">課程與經驗</p><h2>前端完整保留原始資料，不替課程貼上未驗證的資格標籤。</h2></div><div className="course-columns"><article><h3>成績單課程 · {student.transcript_subjects.length} 門</h3><ul>{student.transcript_subjects.slice(0, 8).map((course) => <li key={course.name}><span>{course.name}</span><b>{course.credits} credits · {course.grade}</b></li>)}</ul><p>另有 {Math.max(student.transcript_subjects.length - 8, 0)} 門課程會由後端規則評估。</p></article><article><h3>經驗與興趣</h3><ul className="experience-list">{student.experiences.map((experience) => <li key={experience}>{experience}</li>)}</ul><h3 className="requirement-heading">課程群組要求</h3>{requirements.coursework_credits.groups.map((group) => <div className="requirement" key={group.id}><b>{group.minimum_credits} {requirements.coursework_credits.unit}</b><span>{group.topics.join(" · ")}</span></div>)}</article></div></section>

    <footer className="data-footer">資料來源：`data/schools/schools.json` 與 `data/transcripts/student_profile_S001.json` 至 `student_profile_S015.json`。`transcripts.json` 目前仍為空陣列。</footer>
  </main>;
}

function CheckRow({ label, detail, passed }: { label: string; detail: string; passed: boolean }) {
  return <div className={passed ? "check-row passed" : "check-row attention"}><div><p>{label}</p><span>{detail}</span></div><strong>{passed ? "已符合" : "需確認"}</strong></div>;
}
