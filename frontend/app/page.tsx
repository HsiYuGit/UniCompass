"use client";

import { useMemo, useState } from "react";
import { ectsEstimate, getEligibility, programmes, studentProfiles } from "../src/services/fixture-data";
import { buildRecommendationPreview, createProgrammePrecheck, type RecommendationCandidate } from "../src/services/recommendation-adapter";
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
  const selectedPrecheck = createProgrammePrecheck(student, programme);
  const estimate = ectsEstimate(student);
  const english = programme.entrance_requirements.language_requirements.find((item) => item.language === "english");
  const recommendationPreview = buildRecommendationPreview(student, programmes);
  const filteredProgrammes = useMemo(
    () => programmes.filter((item) => `${item.school.name} ${item.program.name}`.toLowerCase().includes(query.trim().toLowerCase())),
    [query],
  );
  const visibleProgrammes = filteredProgrammes.slice(0, visibleCount);

  function chooseProgramme(id: string) {
    setProgrammeId(id);
    document.getElementById("programme-review")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <main className="data-shell">
      <header className="data-header">
        <a className="data-brand" href="#top"><span aria-hidden="true">U</span>UniCompass</a>
        <p>以可追溯資料準備你的研究所申請候選清單</p>
        <a className="header-link" href="#recommendations">查看推薦準備狀態</a>
      </header>

      <section className="data-hero" id="top">
        <div>
          <p className="data-kicker">申請方向工作台</p>
          <h1>先釐清資格，再比較真正適合你的學程。</h1>
          <p>UniCompass 先公開目前可驗證的條件，接著再將符合基本門檻的候選項目交由推薦引擎進行課程歸類、資格判定與偏好排序。</p>
        </div>
        <label className="profile-picker" htmlFor="student">
          選擇申請者資料
          <select id="student" value={studentId} onChange={(event) => setStudentId(event.target.value)}>
            {studentProfiles.map((item) => <option key={item.student_id} value={item.student_id}>{item.student_id}，{item.name}</option>)}
          </select>
          <span>切換資料會重新計算此頁的透明預檢。</span>
        </label>
      </section>

      <section className="profile-strip" aria-label="目前申請者摘要">
        <div>
          <p className="section-label">目前申請者</p>
          <h2>{student.name}</h2>
          <span>{student.student_id} · GPA {student.gpa}/{student.gpa_scale} · 估算 {estimate} ECTS · 德語 {student.german_level}</span>
        </div>
        <div className="interest-list" aria-label="興趣">{student.interests.map((interest) => <span key={interest}>{interest}</span>)}</div>
      </section>

      <section className="recommendation-section" id="recommendations" aria-labelledby="recommendations-title">
        <div className="section-intro">
          <p className="data-kicker">推薦準備狀態</p>
          <h2 id="recommendations-title">哪些選項已可送入推薦引擎？</h2>
          <p>這不是最終排名。後端仍須把課程歸入各校要求的學分群組，並依興趣、經驗與地區偏好產生安全、合適與挑戰級距。</p>
        </div>
        <div className="recommendation-summary" aria-label="推薦預檢摘要">
          <div><span>可送入引擎</span><strong>{recommendationPreview.readyForAgent.length}</strong><p>基本資料均已通過</p></div>
          <div><span>需要先處理</span><strong>{recommendationPreview.needsPrerequisite.length}</strong><p>至少一項可驗證條件未通過</p></div>
          <div><span>學程資料</span><strong>{programmes.length}</strong><p>下一步仍會檢查課程分類</p></div>
        </div>
        <div className="agent-flow" aria-label="後端推薦流程">
          <div><span>01</span><p>課程歸類</p><small>將成績單科目對應至學程的學分群組。</small></div>
          <div><span>02</span><p>資格判定</p><small>以程式彙總學分、語言與畢業條件。</small></div>
          <div><span>03</span><p>適配排序</p><small>依興趣、經驗、預算與地區偏好排序。</small></div>
        </div>
        <div className="candidate-list" aria-live="polite">
          <div className="candidate-list-head"><div><p className="section-label">候選佇列</p><h3>可交由推薦引擎進一步判定</h3></div><span>{recommendationPreview.readyForAgent.length} 個候選項目</span></div>
          {recommendationPreview.readyForAgent.length > 0 ? recommendationPreview.readyForAgent.map((candidate) => <CandidateRow key={candidate.programme.id} candidate={candidate} onChoose={chooseProgramme} />) : <p className="empty-queue">目前沒有符合所有可驗證基本條件的學程。請在下方清單檢視缺少的條件。</p>}
        </div>
        <details className="prerequisite-details">
          <summary>查看 {recommendationPreview.needsPrerequisite.length} 個尚未進入候選佇列的學程</summary>
          <div className="blocked-list">{recommendationPreview.needsPrerequisite.map((candidate) => <button type="button" key={candidate.programme.id} onClick={() => chooseProgramme(candidate.programme.id)}><span>{candidate.programme.program.name}</span><small>{candidate.programme.school.name} · {candidate.blockers.join("、")}</small></button>)}</div>
        </details>
      </section>

      <section className="catalog" aria-labelledby="catalog-title">
        <div className="catalog-head"><div><p className="data-kicker">完整學程資料庫</p><h2 id="catalog-title">先探索，再檢視每一項要求。</h2></div><label className="search-field" htmlFor="programme-search">搜尋學校或學程<input id="programme-search" value={query} onChange={(event) => { setQuery(event.target.value); setVisibleCount(12); }} placeholder="例如：data、architecture、Aarberg" /></label></div>
        <p className="result-count">找到 {filteredProgrammes.length} 個學程</p>
        <div className="programme-grid">{visibleProgrammes.map((item) => <button className={item.id === programme.id ? "programme-card selected" : "programme-card"} type="button" key={item.id} onClick={() => chooseProgramme(item.id)}><span>{item.program.degree_level}</span><strong>{item.program.name}</strong><small>{item.school.name}</small><em>最低 {item.entrance_requirements.coursework_credits.minimum_total} {item.entrance_requirements.coursework_credits.unit}</em></button>)}</div>
        {visibleProgrammes.length < filteredProgrammes.length && <button className="load-more" type="button" onClick={() => setVisibleCount((count) => count + 12)}>顯示更多學程</button>}
      </section>

      <section className="review-section" id="programme-review">
        <div className="section-intro"><p className="data-kicker">學程預檢</p><h2>{programme.program.name}</h2><p>{programme.school.name}。此區只呈現可從目前資料確認的結果，並不取代後端的課程歸類與最終推薦理由。</p></div>
        <div className="check-list">
          <CheckRow label="學位與目標學程" detail={`需要 ${programme.entrance_requirements.academic_degree.degree_type.replaceAll("_", " ")}`} passed={checks.degree} />
          <CheckRow label="已知總學分" detail={`估算 ${estimate} / 最低 ${programme.entrance_requirements.coursework_credits.minimum_total} ${programme.entrance_requirements.coursework_credits.unit}`} passed={checks.credits} />
          <CheckRow label="英語條件" detail={english ? `最低 ${english.minimum_level ?? "依校方規定"}，IELTS ${student.language_scores.ielts ?? "未提供"}，TOEFL ${student.language_scores.toefl ?? "未提供"}` : "目前資料未列出英語門檻"} passed={checks.english} />
          <div className="check-row pending"><div><p>課程群組歸類</p><span>後端推薦引擎需要將每一門課對應至此學程的學分群組，才能判定是否符合細項要求。</span></div><strong>{selectedPrecheck.needsCourseAllocationReview ? "待後端判定" : "完成"}</strong></div>
        </div>
      </section>

      <section className="requirements"><div><p className="section-label">申請依據</p><h2>把還不確定的地方保留為待確認，而不是把它猜成資格。</h2></div><div className="requirement-columns"><article><h3>課程與學分群組</h3>{programme.entrance_requirements.coursework_credits.groups.map((group) => <div className="requirement" key={group.id}><b>{group.minimum_credits} {programme.entrance_requirements.coursework_credits.unit}</b><span>{group.topics.join(" · ")}</span></div>)}</article><article><h3>申請者資料</h3><p>{student.transcript_subjects.length} 門成績單科目，{student.experiences.length} 項經驗，年度預算 USD {student.budget_usd_per_year.toLocaleString()}。</p><ul>{student.experiences.map((experience) => <li key={experience}>{experience}</li>)}</ul><p className="quality-note">學程驗證狀態：{programme.verificationStatus}</p></article></div></section>
      <footer className="data-footer">資料來源：data/schools/*.json 與 data/transcripts/*_experience.json。最終推薦結果需要由後端推薦引擎產生。</footer>
    </main>
  );
}

function CandidateRow({ candidate, onChoose }: { candidate: RecommendationCandidate; onChoose: (id: string) => void }) {
  return <button className="candidate-row" type="button" onClick={() => onChoose(candidate.programme.id)}><span className="candidate-mark" aria-hidden="true">✓</span><span className="candidate-title"><strong>{candidate.programme.program.name}</strong><small>{candidate.programme.school.name}</small></span><span className="candidate-checks"><span>學位</span><span>學分</span><span>英語</span></span><span className="candidate-status">待課程歸類</span></button>;
}

function CheckRow({ label, detail, passed }: { label: string; detail: string; passed: boolean }) {
  return <div className={passed ? "check-row passed" : "check-row attention"}><div><p>{label}</p><span>{detail}</span></div><strong>{passed ? "目前符合" : "需要補強"}</strong></div>;
}