# 2nd-Project-HealthCare-
Process-efficiency analytics for the HHS Unaccompanied Alien Children Program transforming custody counts into transition, backlog, and discharge-effectiveness metrics with the help of  a Streamlit dashboard.
#Student:
*Name:G.Bhavik Joushva
*Year:1st year
*Project:2nd

1.Project Overview:
The HHS Unaccompanied Alien Children (UAC) Program cares for children who cross the U.S. border without a parent or guardian, moving them through a three-stage pipeline:
.**Apprehension and CBP Custody → Transfer to HHS Care → Medical Screening and Case Management → Discharge to a Vetted Sponsor**
Public reporting on this program tracks *how many* children are in custody at any given time, but not *how efficiently* they move through the system. This project closes that gap by rebuilding the dataset around five process-efficiency KPIs, identifying bottlenecks and backlog periods, and delivering the analysis through a live interactive dashboard, a full research paper, and an executive summary for policy stakeholders.


2.Key Finding
The HHS care population fell **78.4%** — from a peak of **11,516 children** (Dec 2023) to **2,484 children** (Dec 2025). But this decline is driven almost entirely by an **88.9% collapse in new apprehensions**, not by faster discharge processing. In fact, Discharge Effectiveness (share of caseload placed with a sponsor daily) *weakened* over the same period — from 3.3% (2023) to 0.9% (2025). A shrinking caseload should not be mistaken for an improving process.

3.Objectives
Primary:
- Measure the efficiency of CBP → HHS transitions
- Evaluate discharge and sponsor-placement outcomes
- Identify delays and process bottlenecks
Secondary:
- Support faster reunification
- Improve case-management workflows
- Inform policy-level process reforms

3.Dataset:
.720 rows of daily pipeline observation data.

.3-stage system flow (CBP Custody → HHS Care → Sponsor Discharge).

.3 calendar years of comprehensive trend tracking.

.1,095 days of chronological program timeline history (covering January 2023 – December 2025).

4.Features
.Care Pipeline Flow Visualization (Caseload stock vs. daily flow tracking).
.Transfer & Discharge Efficiency Panels (Rolling-average KPI trend metrics).
.Bottleneck & Backlog Detection Alerts (Configurable caseload accumulation signals).
.Temporal & Stability Analytics (Weekday vs. weekend patterns and month-over-month stability scores).
.Policy Stakeholder Deliverables (Automated generation prompts for executive summaries and full research papers).
.Advanced Pipeline EDA (Inflow/outflow imbalance matrix and case velocity mapping).

5.KPIs Tracked
*KPI,Formula,What It Measures.
| Transfer Efficiency Ratio | Transferred ÷ CBP Custody | Speed of CBP → HHS clearance |
| Discharge Effectiveness Index | Discharged ÷ HHS Care | Share of caseload placed with sponsors daily |
| Pipeline Throughput Rate | (Transferred + Discharged) ÷ (Apprehended + Transferred) | Overall system exit velocity |
| Backlog Accumulation Signal | Day-over-day change in HHS Care population | Whether caseload is growing or shrinking |
| Outcome Stability Score | Rolling std. dev. of Discharge Effectiveness | Consistency of placement outcomes |
