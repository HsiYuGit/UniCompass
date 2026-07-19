"""Data contracts and orchestration for the school recommendation agent.

Pipeline:
    Step 1 (LLM):  classify_courses      - assign transcript subjects to a school's credit groups
    Step 2 (code): aggregate_eligibility - sum credits per group, compare against thresholds
    Step 3 (LLM):  match_and_rank        - rank eligible candidates against student preferences
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable, Literal

# ---------------------------------------------------------------------------
# Block 1 input: precomputed elsewhere (grades/credits function), not by an LLM
# ---------------------------------------------------------------------------


@dataclass
class LanguageCheck:
    german_level: str | None
    english_ielts: float | None
    english_toefl: float | None
    gre_verbal: int | None = None
    gre_quant: int | None = None
    gre_writing: float | None = None


@dataclass
class GradesCredits:
    gpa_normalized_4: float
    is_graduated: bool
    graduation_credits_completed: int
    language_check: LanguageCheck


@dataclass
class TranscriptSubject:
    name: str
    credits: float


@dataclass
class StudentPreferences:
    target_degree: str
    experiences: list[str]
    interests: list[str]
    preferred_countries: list[str]
    budget_usd_per_year: float | None = None


# ---------------------------------------------------------------------------
# School-side requirement shapes (subset of data/schools/schools.json)
# ---------------------------------------------------------------------------


@dataclass
class CreditGroup:
    id: str
    minimum_credits: int
    topics: list[str]


@dataclass
class CourseworkCredits:
    minimum_total: int
    groups: list[CreditGroup]


@dataclass
class LanguageRequirement:
    language: str
    required: bool
    minimum_level: str | None
    accepted_proofs: list[dict]


@dataclass
class SchoolRequirements:
    school: str
    program: str
    degree_level: str
    coursework_credits: CourseworkCredits
    language_requirements: list[LanguageRequirement]
    unmodeled_requirements: list[str]
    verification_status: str


# Signature every LLM backend (Anthropic/OpenAI/local) must satisfy:
# (system_prompt, payload) -> parsed JSON response as a dict.
LLMCall = Callable[[str, dict], dict]


# ---------------------------------------------------------------------------
# Step 1 (LLM): course -> credit-group classification
# ---------------------------------------------------------------------------

COURSE_CLASSIFIER_SYSTEM_PROMPT = """\
你是一個大學課程分類器。你的任務是把學生的修課紀錄，依照目標科系公告的
「學分群組」定義，將每一門課分配到最匹配的一組。

規則：
1. 每門課只能分配到一個群組，不可拆分或重複計入多組。
2. 若某門課的內容與所有群組都無明顯關聯，標記為 "unclassified"，並簡短說明原因。
3. 只能使用輸入中提供的 group id，不可自創或更改群組名稱。
4. 不要計算學分加總或判斷是否達到門檻——那不是你的任務，只需完成分類。
5. 輸出必須是合法 JSON，符合下方輸出格式，不要加入其他文字。

請根據課程名稱與學術常識判斷最佳分類，而非單純關鍵字比對。
"""


@dataclass
class CourseClassification:
    course: str
    credits: float
    group_id: str  # one of the school's group ids, or "unclassified"
    confidence: Literal["high", "medium", "low"] | None = None
    reason: str | None = None  # required when group_id == "unclassified"


def classify_courses(
    llm_call: LLMCall,
    subjects: list[TranscriptSubject],
    groups: list[CreditGroup],
) -> list[CourseClassification]:
    """Step 1: ask the LLM to assign each subject to one of the school's credit groups."""
    payload = {
        "transcript_subjects": [{"name": s.name, "credits": s.credits} for s in subjects],
        "groups": [{"id": g.id, "topics": g.topics} for g in groups],
    }
    result = llm_call(COURSE_CLASSIFIER_SYSTEM_PROMPT, payload)
    return [CourseClassification(**c) for c in result["classifications"]]


# ---------------------------------------------------------------------------
# Step 2 (code, deterministic): credit aggregation + threshold comparison
# ---------------------------------------------------------------------------

# Borderline tolerance: how far below a threshold still counts as "borderline"
# rather than "fail". Needs team sign-off before tuning.
BORDERLINE_RATIO = 0.9

_CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


@dataclass
class GroupEligibility:
    id: str
    required: int
    matched: float
    status: Literal["ok", "below_threshold"]


@dataclass
class HardEligibility:
    credit_groups: list[GroupEligibility]
    credit_total: GroupEligibility
    language_status: Literal["pass", "fail"]
    overall: Literal["pass", "borderline", "fail"]


def _cefr_meets(level: str, minimum: str | None) -> bool:
    if minimum is None:
        return True
    return _CEFR_ORDER.index(level) >= _CEFR_ORDER.index(minimum)


def compare_language(
    check: LanguageCheck, requirements: list[LanguageRequirement]
) -> Literal["pass", "fail"]:
    for req in requirements:
        if not req.required:
            continue
        if req.language == "english":
            proofs = req.accepted_proofs
            ielts_ok = check.english_ielts is not None and any(
                p["proof_type"] == "ielts" and check.english_ielts >= float(p["minimum_result"])
                for p in proofs
            )
            toefl_ok = check.english_toefl is not None and any(
                p["proof_type"] == "toefl_ibt" and check.english_toefl >= float(p["minimum_result"])
                for p in proofs
            )
            if not (ielts_ok or toefl_ok):
                return "fail"
        elif req.language == "german":
            if check.german_level is None or not _cefr_meets(check.german_level, req.minimum_level):
                return "fail"
    return "pass"


def aggregate_eligibility(
    classifications: list[CourseClassification],
    school: SchoolRequirements,
    grades: GradesCredits,
) -> HardEligibility:
    """Step 2: sum classified credits per group and compare against the school's thresholds."""
    credit_groups = []
    for group in school.coursework_credits.groups:
        matched = sum(c.credits for c in classifications if c.group_id == group.id)
        status = "ok" if matched >= group.minimum_credits else "below_threshold"
        credit_groups.append(GroupEligibility(group.id, group.minimum_credits, matched, status))

    total_matched = sum(c.credits for c in classifications if c.group_id != "unclassified")
    total_required = school.coursework_credits.minimum_total
    credit_total = GroupEligibility(
        "total",
        total_required,
        total_matched,
        "ok" if total_matched >= total_required else "below_threshold",
    )

    language_status = compare_language(grades.language_check, school.language_requirements)

    if not grades.is_graduated or language_status == "fail":
        overall = "fail"
    elif credit_total.status == "ok" and all(g.status == "ok" for g in credit_groups):
        overall = "pass"
    elif total_matched >= total_required * BORDERLINE_RATIO:
        overall = "borderline"
    else:
        overall = "fail"

    return HardEligibility(credit_groups, credit_total, language_status, overall)


# ---------------------------------------------------------------------------
# Step 3 (LLM): interest/experience fit + final ranking
# ---------------------------------------------------------------------------

MATCH_AND_RANK_SYSTEM_PROMPT = """\
你是德國留學選校顧問 agent。你會收到一位學生的背景資訊，以及一份已完成
資格檢查的候選校系清單。你的任務是根據學生的興趣、經歷、目標國家與預算，
評估每個候選校系的適配程度，並產出排序後的推薦清單。

規則：
1. hard_eligibility.overall 為 "fail" 的校系，不放入推薦清單，改放入
   not_recommended 並簡述原因；不要重新判斷或質疑 hard_eligibility 裡的
   數字本身，那已經是既定事實。
2. 依興趣/經歷/目標國家/預算與 program 的契合程度，把 pass 或 borderline
   的校系分為三級：
   - Safety：資格穩（overall=pass）且契合度高
   - Match：資格與契合度中等
   - Reach：資格邊緣（overall=borderline）或契合度較低但仍值得一試
3. 每筆推薦必須附具體理由，並引用 hard_eligibility 中的實際數字或狀態，
   禁止空泛描述。
4. 若 data_quality.verification_status 為 "unverified"，理由中必須註明
   「資料尚待查證」。
5. 只能推薦輸入清單中存在的校系，不可捏造學校或科系名稱。
6. 輸出必須是合法 JSON，符合下方輸出格式，不要加入其他文字。
"""


@dataclass
class CandidateForRanking:
    school: str
    program: str
    hard_eligibility: HardEligibility
    unmodeled_requirements: list[str]
    verification_status: str


@dataclass
class Recommendation:
    school: str
    program: str
    tier: Literal["safety", "match", "reach"]
    eligibility_summary: str
    fit_reasoning: str
    caveats: list[str] = field(default_factory=list)


@dataclass
class NotRecommended:
    school: str
    program: str
    reason: str


@dataclass
class RecommendationResult:
    recommendations: list[Recommendation]
    not_recommended: list[NotRecommended]


def match_and_rank(
    llm_call: LLMCall,
    preferences: StudentPreferences,
    candidates: list[CandidateForRanking],
) -> RecommendationResult:
    """Step 3: rank hard-eligible candidates against the student's soft preferences."""
    payload = {
        "student_preferences": {
            "target_degree": preferences.target_degree,
            "experiences": preferences.experiences,
            "interests": preferences.interests,
            "preferred_countries": preferences.preferred_countries,
            "budget_usd_per_year": preferences.budget_usd_per_year,
        },
        "candidates": [
            {
                "school": c.school,
                "program": c.program,
                "hard_eligibility": {
                    "credit_groups": [g.__dict__ for g in c.hard_eligibility.credit_groups],
                    "credit_total": c.hard_eligibility.credit_total.__dict__,
                    "language_status": c.hard_eligibility.language_status,
                    "overall": c.hard_eligibility.overall,
                },
                "unmodeled_requirements": c.unmodeled_requirements,
                "data_quality": {"verification_status": c.verification_status},
            }
            for c in candidates
        ],
    }
    result = llm_call(MATCH_AND_RANK_SYSTEM_PROMPT, payload)
    return RecommendationResult(
        recommendations=[Recommendation(**r) for r in result["recommendations"]],
        not_recommended=[NotRecommended(**r) for r in result["not_recommended"]],
    )


# ---------------------------------------------------------------------------
# LLMCall implementation backed by OpenAI's Codex models
# ---------------------------------------------------------------------------


def make_openai_llm_call(model: str | None = None) -> LLMCall:
    """Builds an LLMCall backed by the OpenAI Responses API.

    Reads the API key from the OPENAI_API_KEY environment variable (the
    OpenAI SDK's default lookup). Pass `model` explicitly or set OPENAI_MODEL
    to pick which codex/gpt model to use; defaults to "gpt-5.3-codex".
    Requires an `openai` package version new enough to expose
    `client.responses.create` - Codex models are served through the
    Responses API, not the legacy Chat Completions API.
    """
    from openai import OpenAI  # imported lazily so the module loads without the dependency installed

    client = OpenAI()
    resolved_model = model or os.environ.get("OPENAI_MODEL", "gpt-5.3-codex")

    def llm_call(system_prompt: str, payload: dict) -> dict:
        response = client.responses.create(
            model=resolved_model,
            instructions=system_prompt,
            input=json.dumps(payload, ensure_ascii=False),
            text={"format": {"type": "json_object"}},
        )
        content = response.output_text
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"OpenAI response was not valid JSON: {content!r}") from exc

    return llm_call


# ---------------------------------------------------------------------------
# Orchestration: the full three-step pipeline
# ---------------------------------------------------------------------------


def run_recommend_agent(
    llm_call: LLMCall,
    grades: GradesCredits,
    subjects: list[TranscriptSubject],
    preferences: StudentPreferences,
    schools: list[SchoolRequirements],
) -> RecommendationResult:
    """Runs the full pipeline: classify -> aggregate -> rank, across every candidate school."""
    candidates = []
    for school in schools:
        classifications = classify_courses(llm_call, subjects, school.coursework_credits.groups)
        eligibility = aggregate_eligibility(classifications, school, grades)
        candidates.append(
            CandidateForRanking(
                school=school.school,
                program=school.program,
                hard_eligibility=eligibility,
                unmodeled_requirements=school.unmodeled_requirements,
                verification_status=school.verification_status,
            )
        )
    return match_and_rank(llm_call, preferences, candidates)


# ---------------------------------------------------------------------------
# OpenAI Agents SDK implementations for production recommendation requests
# ---------------------------------------------------------------------------


class AgentsSdkUnavailableError(RuntimeError):
    """Raised when the backend was deployed without the OpenAI Agents SDK."""


@dataclass
class CourseClassificationOutput:
    classifications: list[CourseClassification]


def _agents_sdk_types():
    """Import lazily so deterministic tests do not require an API dependency."""
    try:
        from agents import Agent, Runner
    except ModuleNotFoundError as exc:
        raise AgentsSdkUnavailableError(
            "OpenAI Agents SDK is not installed. Run `pip install -r backend/requirements.txt`."
        ) from exc
    return Agent, Runner


def _resolved_openai_model(model: str | None) -> str:
    return model or os.environ.get("OPENAI_MODEL", "gpt-5.3-codex")


def _run_structured_agent(
    *,
    name: str,
    instructions: str,
    output_type: type,
    payload: dict,
    model: str | None,
):
    """Run one non-tool Agent SDK turn and return its schema-validated output."""
    Agent, Runner = _agents_sdk_types()
    agent = Agent(
        name=name,
        instructions=instructions,
        model=_resolved_openai_model(model),
        output_type=output_type,
    )
    result = Runner.run_sync(
        agent,
        json.dumps(payload, ensure_ascii=False),
        max_turns=1,
    )
    return result.final_output


def _validate_classifications(
    classifications: list[CourseClassification],
    subjects: list[TranscriptSubject],
    groups: list[CreditGroup],
) -> list[CourseClassification]:
    """Reject a model output that changes the transcript or reuses a course."""
    expected_credits = {subject.name: subject.credits for subject in subjects}
    if len(expected_credits) != len(subjects):
        raise ValueError("Transcript subject names must be unique for course allocation.")

    received_courses = [classification.course for classification in classifications]
    if len(received_courses) != len(set(received_courses)):
        raise ValueError("Agent returned more than one allocation for a course.")
    if set(received_courses) != set(expected_credits):
        raise ValueError("Agent must return exactly one allocation for every transcript course.")

    valid_groups = {group.id for group in groups} | {"unclassified"}
    for classification in classifications:
        if classification.group_id not in valid_groups:
            raise ValueError(f"Agent returned an unknown credit group: {classification.group_id}")
        if classification.credits != expected_credits[classification.course]:
            raise ValueError(f"Agent changed the credits for course: {classification.course}")
        if classification.group_id == "unclassified" and not classification.reason:
            raise ValueError("Unclassified courses require a reason.")
    return classifications


def classify_courses_with_openai_agents(
    subjects: list[TranscriptSubject],
    groups: list[CreditGroup],
    *,
    model: str | None = None,
) -> list[CourseClassification]:
    """Use Agent SDK structured output for course-to-group allocation."""
    payload = {
        "transcript_subjects": [{"name": s.name, "credits": s.credits} for s in subjects],
        "groups": [{"id": g.id, "topics": g.topics} for g in groups],
    }
    output = _run_structured_agent(
        name="Course credit classifier",
        instructions=COURSE_CLASSIFIER_SYSTEM_PROMPT,
        output_type=CourseClassificationOutput,
        payload=payload,
        model=model,
    )
    if not isinstance(output, CourseClassificationOutput):
        raise ValueError("Course classifier returned an unexpected structured output.")
    return _validate_classifications(output.classifications, subjects, groups)


def match_and_rank_with_openai_agents(
    preferences: StudentPreferences,
    candidates: list[CandidateForRanking],
    *,
    model: str | None = None,
) -> RecommendationResult:
    """Use Agent SDK structured output for final preference-based ranking."""
    payload = {
        "student_preferences": preferences.__dict__,
        "candidates": [
            {
                "school": c.school,
                "program": c.program,
                "hard_eligibility": {
                    "credit_groups": [g.__dict__ for g in c.hard_eligibility.credit_groups],
                    "credit_total": c.hard_eligibility.credit_total.__dict__,
                    "language_status": c.hard_eligibility.language_status,
                    "overall": c.hard_eligibility.overall,
                },
                "unmodeled_requirements": c.unmodeled_requirements,
                "data_quality": {"verification_status": c.verification_status},
            }
            for c in candidates
        ],
    }
    output = _run_structured_agent(
        name="Programme recommendation ranker",
        instructions=MATCH_AND_RANK_SYSTEM_PROMPT,
        output_type=RecommendationResult,
        payload=payload,
        model=model,
    )
    if not isinstance(output, RecommendationResult):
        raise ValueError("Recommendation ranker returned an unexpected structured output.")

    known_candidates = {(candidate.school, candidate.program): candidate for candidate in candidates}
    seen_recommendations: set[tuple[str, str]] = set()
    for recommendation in output.recommendations:
        key = (recommendation.school, recommendation.program)
        candidate = known_candidates.get(key)
        if candidate is None or key in seen_recommendations:
            raise ValueError("Recommendation ranker returned an unknown or duplicate programme.")
        if candidate.hard_eligibility.overall == "fail":
            raise ValueError("Recommendation ranker cannot recommend a hard-ineligible programme.")
        seen_recommendations.add(key)
    return output


def run_recommend_agent_with_openai_agents(
    grades: GradesCredits,
    subjects: list[TranscriptSubject],
    preferences: StudentPreferences,
    schools: list[SchoolRequirements],
    *,
    model: str | None = None,
) -> RecommendationResult:
    """Run the three-stage pipeline with Agent SDK for both model stages."""
    candidates = []
    for school in schools:
        classifications = classify_courses_with_openai_agents(
            subjects, school.coursework_credits.groups, model=model
        )
        eligibility = aggregate_eligibility(classifications, school, grades)
        candidates.append(
            CandidateForRanking(
                school=school.school,
                program=school.program,
                hard_eligibility=eligibility,
                unmodeled_requirements=school.unmodeled_requirements,
                verification_status=school.verification_status,
            )
        )
    return match_and_rank_with_openai_agents(preferences, candidates, model=model)
