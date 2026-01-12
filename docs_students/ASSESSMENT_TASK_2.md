# ASSESSMENT_TASK_2.md — Assessment Notification (VIP Pizza)

**Year:** 12

**Subject:** Software Engineering

**Task:** Task 2

**Task title:** Secure Software Architecture

**Date issued:** Monday, 8 December 2025

**Due date:** Friday, 20 March 2026

**Weighting:** 20%

**Total marks:** 50

---

## Outcomes

- SE-12-01 justifies methods used to plan, develop and engineer software solutions
- SE-12-02 applies structural elements to develop programming code
- SE-12-06 justifies the selection and use of tools and resources to design, develop, manage and evaluate software
- SE-12-09 applies methods to manage and document the development of a software project

---

## Context: Securing a Progressive Web App

Your client, **The Unsecure PWA Company**, has engaged you as a software engineering security specialist to provide expert advice on the security and privacy of their Progressive Web App (PWA).

The application is currently in the testing and debugging phase of the software development lifecycle, with intentional vulnerabilities introduced for assessment and remediation.

Your task is to identify critical security issues, recommend fixes to at least **3 critical vulnerabilities**, document your process, and present your solutions to the client.

The repository you will need to fork is at:

`https://github.com/Mr-Zamora/12SE_Task2`

---

## Components and Mark Allocation

### Component A: Security Report (35 marks)

**Purpose:**
Document the vulnerabilities you identify in the PWA, explain your testing methods, detail the fixes you applied, and provide recommendations for future security.

**Use these project docs to help you:**
- `docs_students/INSTRUCTIONS.md`
- `docs_students/TESTING.md`
- `docs_students/REPORT_TEMPLATE.md`
- `docs_students/SAMPLE/SAMPLE_REPORT_TEMPLATE.md`

#### Requirements

##### A1. Introduction (5 marks)
- Describe the PWA and the scope of your security assessment.
- Outline the testing methods used:
  - blackbox testing
  - greybox testing
  - whitebox testing

##### A2. Findings (15 marks)
- For each input-based vulnerability:
  - clearly articulate the mechanism of exploit
  - justify why the fix requires a combination of **Input Validation** and **Data Sanitisation**
- Describe how each vulnerability could be exploited and its potential impact on the PWA.
- Include evidence such as screenshots from testing tools (e.g. Google Lighthouse, Postman) and/or browser DevTools.

##### A3. Fixes (15 marks)
- Explain how you would resolve at least **3 critical vulnerabilities**.
- Justify why these critical vulnerabilities were chosen over others.
- Provide code snippets and justification that clearly distinguishes and demonstrates the use of both:
  - **Input Validation** (e.g. length/regex checks)
  - **Data Sanitisation** (e.g. character escaping/filtering using Python functions)

#### Deliverable
- Submit a professionally formatted document (PDF or Word) uploaded to Canvas.
- Include:
  - table of contents
  - headings and sub-headings
  - bibliography
  - tables where appropriate for clarity

---

### Component B: Paper Quiz (15 marks)

**Purpose:**
Assess your understanding of the security concepts and practices applied in this assessment.

**Requirements:**
- Complete a paper quiz in class on the submission due date.
- The quiz will include questions on:
  - identifying vulnerabilities and their impacts from `https://www.hacksplaining.com/lessons`
  - secure coding techniques (e.g. input validation, password hashing)

**Deliverable:**
- No separate submission is required.
- The quiz will be completed in class on:
  - Friday, 20 March, Period 1 (30 mins)

---

## Submission Guidelines

1. Submit a single document (Word or PDF) containing all required written tasks.
    - You may submit a completed version of `docs_students/REPORT_TEMPLATE.md` as your final report.
2. Any use of AI must be clearly and explicitly acknowledged and cited in the Bibliography.

---

## Use of AI

Please refer to the College **Use of AI Technology Policy**.

You may use AI for planning, idea development, and research. Your final submission should show how you have developed and refined these ideas.

---

## APA Referencing Requirements

All research and written components of this task must include APA 7th edition referencing.

Students are required to:
- acknowledge all sources used for information, images, data, quotes, and AI-assisted material
- include in-text citations whenever information is paraphrased or quoted
- provide a reference list on a separate page at the end of the task
- ensure references follow correct APA 7th edition format (author, year, title, source)
- reference AI-generated content, indicating the prompt and the AI tool used (e.g. ChatGPT, 2025)

Failure to correctly acknowledge sources may result in a loss of marks for academic integrity.

---

## Academic Integrity

All written work must be the student's original creation. Failure to cite sources, including AI-generated content, may be considered academic malpractice and may result in penalties per the school's academic integrity policy.

---

## Marking Criteria

Refer to the marking scaffold provided by your teacher:

- **Component A: Security Report (35 marks)**
  - A1. Introduction (5 marks)
  - A2. Findings (15 marks)
  - A3. Fixes (15 marks)
- **Component B: Paper Quiz (15 marks)**

---

## Project Guidance (VIP Pizza)

This section shows you where to find the key files in this repository.

### Starting point

1. Follow the setup steps in:
   - `docs_students/INSTRUCTIONS.md`
2. Use the testing steps and vulnerability list in:
   - `docs_students/TESTING.md`
3. Write your report using:
   - `docs_students/REPORT_TEMPLATE.md`
4. Use the example for evidence quality:
   - `docs_students/SAMPLE/SAMPLE_REPORT_TEMPLATE.md`

### Evidence expectations (for A2)

For each finding you include in your report:
 - write the endpoint/URL
 - write the exact input/payload you used
 - include screenshots (or copied output) showing the result
 - explain impact (what could happen in the real world)

### Fix expectations (for A3)

For at least **3 critical vulnerabilities**, explain how you would fix them with:
 - **Input Validation** (e.g. allowlist, length checks, type checks, regex)
 - **Data Sanitisation** (e.g. escaping output, filtering/encoding unsafe characters)

Your explanation must clearly distinguish validation vs sanitisation.
