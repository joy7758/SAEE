# Venue Selection and Fee Gate

Snapshot date: 2026-07-17

## Decision

```text
TARGET_JOURNAL=Autonomous Agents and Multi-Agent Systems
TARGET_PUBLISHER=Springer Nature
ARTICLE_TYPE=Viewpoint
PUBLISHING_MODEL=HYBRID
SELECTED_ROUTE=SUBSCRIPTION
AUTHOR_SIDE_APC=0
MANDATORY_APC_ALLOWED=false
PAID_OPEN_ACCESS_SELECTED=false
```

The primary target is *Autonomous Agents and Multi-Agent Systems* (JAAMAS),
using its subscription publishing route. The journal's official publishing page
states that no article processing charge applies to the subscription route. Its
official article taxonomy defines a Viewpoint as an article intended to spark
interest and activity in timely new areas or ideas rather than report original
research or survey an area. That description matches this manuscript's category-
definition and research-agenda contribution.

Official sources:

1. Aims and scope: <https://link.springer.com/journal/10458/aims-and-scope>
2. Publishing routes and fees: <https://link.springer.com/journal/10458/how-to-publish-with-us>
3. Submission guidelines: <https://link.springer.com/journal/10458/submission-guidelines>

## Fit Assessment

| Criterion | Assessment | Basis |
| --- | --- | --- |
| Autonomous-agent and multi-agent scope | Strong | The scope explicitly covers trust, reputation, commitments, norms, verification, and multi-agent systems. |
| Category-definition article | Strong | The Viewpoint type is meant to stimulate new areas and timely ideas. |
| Research-agenda contribution | Strong | The manuscript frames falsifiable questions rather than claiming a finished system. |
| Free author-side route | Pass | Subscription publishing is available with no article processing charge. |
| Evidence burden | Manageable | A rigorous synthesis and a 1-2 page information sheet are required; original experiments are not the defining requirement for a Viewpoint. |
| Main risk | Material | Editors may judge the category too broad or insufficiently distinguished from trust, accountability, observability, and assurance literature. |

## Required Journal Controls

The draft package follows the following official requirements:

- 150-250 word abstract.
- 4-6 keywords.
- Numbered citations in square brackets.
- A 1-2 page information sheet answering the six Viewpoint questions.
- Editable source at submission.
- Statements and Declarations, including competing interests.
- Disclosure of generative large-language-model assistance where required.

No submission or payment selection is authorized by this document.

Before submission, the human author must recheck that no funder or institution
requires immediate open access, because the journal states that such a mandate
may make the subscription route unsuitable. Optional services and any portal-
specific charges must also be declined or re-evaluated; the present decision is
based specifically on the official statement that no article processing charge
applies to subscription publication.

## Backup Venues

| Rank | Journal | Potential article fit | Free route | Why not first |
| --- | --- | --- | --- | --- |
| 2 | *AI & Society* | Position or viewpoint on social and organizational implications | Subscription route with no article processing charge | Less direct technical multi-agent-systems audience. |
| 3 | *AI and Ethics* | Conceptual work on responsibility and governance | Subscription route with no article processing charge | Stronger ethics and policy emphasis than infrastructure and multi-agent-systems emphasis. |

Official fee pages:

- *AI & Society*: <https://link.springer.com/journal/146/how-to-publish-with-us>
- *AI and Ethics*: <https://link.springer.com/journal/43681/how-to-publish-with-us>

## Exclusion Rule

Any journal or route requiring an unavoidable article processing charge is out
of scope. A journal is not retained merely because waivers may exist. The route
must allow an author-side free publication path under ordinary subscription or
traditional publishing terms.

```text
FREE_TRADITIONAL_ROUTE_REQUIRED=true
FULLY_OPEN_ACCESS_MANDATORY_APC_JOURNALS_EXCLUDED=true
WAIVER_DEPENDENCY_ACCEPTED=false
SUBMISSION_AUTHORIZED=false
```
