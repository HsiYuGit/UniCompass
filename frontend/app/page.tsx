"use client";

import { useMemo, useState } from "react";
import { ectsEstimate, getEligibility, programmes, studentProfiles } from "../src/services/fixture-data";
import "./data.css";

const initialProgramme = programmes[0];

export default function Home() {
  const [studentId, setStudentId] = useState(studentProfiles[0].student_id);
  const [programmeId, setProgrammeId] = useState(initialProgramme.id);
  const [query, setQuery] = useState("");
  const [visibleCount, setVisibleCount] = useState(12);
  const student = studentProfiles.find((item) => item.student_id === studentId) ?? studentProfiles[0];
  const programme = programmes.find((item) => item.id === programmeId) ?? initialProgramme;
  const checks = getEligibility(student, programme);
  const estimate = ectsEstimate(student);
  const english = programme.entrance_requirements.language_requirements.find((item) => item.language === "english");
  const filteredProgrammes = useMemo(() => programmes.filter((item) => `${item.school.name} ${item.program.name}`.toLowerCase().includes(query.trim().toLowerCase())), [query]);
  const visibleProgrammes = filteredProgrammes.slice(0, visibleCount);

  function chooseProgramme(id: string) {
    setProgrammeId(id);
    document.getElementById("review")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return <main className="data-shell">
    <header className="data-header"><a className="data-brand" href="#top"><span aria-hidden="true">U</span>UniCompass</a><p>{programmes.length} 個德國碩士學程 · {studentProfiles.length} 個申請者檔案</p></header>
    <section className="data-hero" id="top"><div><p className="data-kicker">從資料開始選校</p><h1>先看你的條件，再找值得深入研究的學程。</h1><p>這裡呈現 data 資料夾已提供的事實與前檢。課程分組、最終資格與推薦排序仍由後端 agent 產生。</p></div><label className="profile-picker" htmlFor="student">選擇申請者<select id="student" value={studentId} onChange={(event) => setStudentId(event.target.value)}>{studentProfiles.map((item) => <option key={item.student_id} value={item.student_id}>{item.student_id} · {item.name}</option>)}</select></label></section>

    <section className="profile-strip" aria-label="申請者摘要"><div><p className="section-label">目前申請者</p><h2>{student.name}</h2><span>{student.student_id} · GPA {student.gpa}/{student.gpa_scale} · 推估 {estimate} ECTS · 德語 {student.german_level}</span></div><div className="interest-list">{student.interests.map((interest) => <span key={interest}>{interest}</span>)}</div></section>

    <section className="catalog" aria-labelledby="catalog-title"><div className="catalog-head"><div><p className="data-kicker">探索學程</p><h2 id="catalog-title">從 {programmes.length} 個學程中開始。</h2></div><label className="search-field" htmlFor="programme-search">搜尋學校或科系<input id="programme-search" value={query} onChange={(event) => { setQuery(event.target.value); setVisibleCount(12); }} placeholder="例如：data、architecture、Aarberg" /></label></div><p className="result-count">{filteredProgrammes.length} 個符合搜尋的學程</p><div className="programme-grid">{visibleProgrammes.map((item) => <button className={item.id === programme.id ? "programme-card selected" : "programme-card"} type="button" key={item.id} onClick={() => chooseProgramme(item.id)}><span>{item.program.degree_level}</span><strong>{item.program.name}</strong><small>{item.school.name}</small><em>至少 {item.entrance_requirements.coursework_credits.minimum_total} {item.entrance_requirements.coursework_credits.unit}</em></button>)}</div>{visibleProgrammes.length < filteredProgrammes.length && <button className="load-more" type="button" onClick={() => setVisibleCount((count) => count + 12)}>顯示更多學程</button>}</section>

    <section className="review-section" id="review"><div className="section-intro"><p className="data-kicker">條件對照</p><h2>{programme.program.name}</h2><p>{programme.school.name}。目前結果是前端可直接從資料得出的初步對照，不是錄取預測。</p></div><div className="check-list"><CheckRow label="學位方向" detail={`需要 ${programme.entrance_requirements.academic_degree.degree_type.replaceAll("_", " ")}`} passed={checks.degree} /><CheckRow label="總學分" detail={`推估 ${estimate} / 至少 ${programme.entrance_requirements.coursework_credits.minimum_total} ${programme.entrance_requirements.coursework_credits.unit}`} passed={checks.credits} /><CheckRow label="英文證明" detail={english ? `需要 ${english.minimum_level ?? "指定證明"}；IELTS ${student.language_scores.ielts ?? "未提供"}、TOEFL ${student.language_scores.toefl ?? "未提供"}` : "課程資料未提供英文門檻"} passed={checks.english} /><div className="check-row pending"><div><p>課程群組</p><span>每門課只能指派一個最符合的群組，交由後端 agent 計算。</span></div><strong>待後端</strong></div></div></section>

    <section className="requirements"><div><p className="section-label">資料完整度</p><h2>後端完成分類後，這裡會顯示真正的資格與推薦理由。</h2></div><div className="requirement-columns"><article><h3>課程群組門檻</h3>{programme.entrance_requirements.coursework_credits.groups.map((group) => <div className="requirement" key={group.id}><b>{group.minimum_credits} {programme.entrance_requirements.coursework_credits.unit}</b><span>{group.topics.join(" · ")}</span></div>)}</article><article><h3>申請者資料</h3><p>{student.transcript_subjects.length} 門成績單課程、{student.experiences.length} 項經驗、年度預算 ${student.budget_usd_per_year.toLocaleString()}。</p><ul>{student.experiences.map((experience) => <li key={experience}>{experience}</li>)}</ul><p className="quality-note">學程來源驗證狀態：{programme.verificationStatus}</p></article></div></section>
    <footer className="data-footer">資料來源：`data/schools/*.json` 與 `data/transcripts/*_experience.json`。</footer>
  </main>;
}

function CheckRow({ label, detail, passed }: { label: string; detail: string; passed: boolean }) {
  return <div className={passed ? "check-row passed" : "check-row attention"}><div><p>{label}</p><span>{detail}</span></div><strong>{passed ? "已符合" : "需確認"}</strong></div>;
}
