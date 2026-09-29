# Software Engineering Lab

**Course:** Software Engineering
**Student:** Kruthiknandan R
**SRN:** PES1UG24CS239

This repository contains the documents and deliverables for the Software Engineering lab sessions. Each lab is in its own folder.

## Table of Contents

- [Repository Structure](#repository-structure)
- [Lab 1: Requirements and Use Case Modelling](#lab-1-requirements-and-use-case-modelling)
- [Lab 2: Agile Backlog and Sprint Simulation in Jira](#lab-2-agile-backlog-and-sprint-simulation-in-jira)
- [Lab 3: Architecture Selection and UML Component Diagram](#lab-3-architecture-selection-and-uml-component-diagram)
- [Viewing the Files](#viewing-the-files)
- [Author](#author)

## Repository Structure

```
SE_PES1UG24CS239/
├── Lab_1/
│   ├── Requirements_table.docx
│   ├── Use_case diagram.pdf
│   └── Usecase_flow.docx
├── Lab_2/
│   └── Lab2_Agile_Jira_Report_PES1UG24CS239.pdf
├── Lab_3/
│   ├── Lab3_Justification.pdf
│   └── UML_component Diagram.pdf
└── README.md
```

## Lab 1: Requirements and Use Case Modelling

Requirements analysis and use case modelling for a conference paper management system. The stakeholders are the Conference Author, Peer Reviewer, Track Chair and Attendee.

| File | Description |
| ---- | ----------- |
| `Requirements_table.docx` | Functional and non-functional requirements, each with ID, type, priority, acceptance criteria and rationale. Covers anonymous (double-blind) paper review, paper submission, reviewer assignment, multi-track schedule generation, live audience Q&A, and performance and security needs. |
| `Use_case diagram.pdf` | UML use case diagram showing the actors and their interactions with the system. |
| `Usecase_flow.docx` | Detailed use case scenario for **Generate Multi-Track Schedule** (primary actor: Track Chair). Includes preconditions, postconditions, the main success scenario, the alternate flow for scheduling conflicts, and the `«include»` relationship with *Resolve Scheduling Conflicts*. |

## Lab 2: Agile Backlog and Sprint Simulation in Jira

Agile planning for the **Airport Lost Luggage Claim & Tracking Portal**, simulated in Jira (space: `SE_LAB_2`).

| File | Description |
| ---- | ----------- |
| `Lab2_Agile_Jira_Report_PES1UG24CS239.pdf` | Report with Jira screenshots and analysis. |

The report covers:

- **Backlog:** 5 top-level Epics with child user stories.
- **Estimation:** Story points on the Fibonacci scale (2, 3, 5, 8).
- **Sprint board:** Active sprint view with To Do, In Progress and Done columns.
- **Sprints:** Sprint 1 (9 stories) and Sprint 2 (6 stories), both completed.
- **Burndown charts:** One chart for each sprint.
- **Scope changes log:** Record of re-estimations and sprint scope changes.
- **Reflection:** Estimation accuracy, backlog prioritisation, plan vs. actual, and what the burndown charts show about capacity.

## Lab 3: Architecture Selection and UML Component Diagram

Architectural design for a **Virtual Technical Conference Platform**.

| File | Description |
| ---- | ----------- |
| `Lab3_Justification.pdf` | Justification for choosing a **Microservices Architecture**. It covers independent scaling for unpredictable load (for example, live streaming during keynotes), independent deployment and technology diversity, security isolation (for example, an isolated Payment Service), and performance benefits. |
| `UML_component Diagram.pdf` | UML component diagram of the platform's services, such as Live Streaming, Registration, Payment, and Chat & Q&A. |

## Viewing the Files

1. Clone the repository:
```bash
   git clone https://github.com/KN15-git/SE_PES1UG24CS239.git
```
2. Open the folder for the lab you want.
3. Open `.docx` files in Microsoft Word, Google Docs or LibreOffice, and `.pdf` files in any PDF reader.

## Author

**Kruthiknandan R**
SRN: PES1UG24CS239
