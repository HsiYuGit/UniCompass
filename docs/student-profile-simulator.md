# Student profile simulator

The frontend currently uses the 15 fixture profiles in
`data/transcripts/*_experience.json` as a stand-in for the future applicant
input flow.

When a profile is selected, the interface displays the supplied academic
record, language scores, relevant experience, interests, country preference,
budget, and a six-course transcript preview. This lets reviewers understand
which inputs the recommendation pipeline is using before they assess a
programme match.

The preview is read-only by design. It must not suggest that a student has
personally entered or submitted the fixture data. A future form may replace
this selector while preserving the same profile data shape.
