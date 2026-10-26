# Home Energy Consumption Management System (HEMS) Project Proposal

School of computing and informatics

Department of information technology

Name: Abdijabar Abdullahi

Registration number: BIT/2024/62274

HOME ENERGY CONSUMPTION MANAGEMENT SYSTEM (HEMS)

A Web-Based Platform for Tracking Multi-Source Domestic Energy Consumption in Kenyan Households

A Project Proposal Submitted in Partial Fulfilment of the Requirements for the Award of the Degree of Bachelor of Science in Information Technology

> **Draft status (24 October 2026):** The prototype and software QA are complete, but Phase 5 deployment and the planned two-week household pilot have not been completed. Pilot results, user-acceptance findings, and accuracy-verification claims must not be treated as observed evidence; update this draft after the pilot.

Presented to: Benard chogi

Mount Kenya University

July 2026

## DECLARATION AND APPROVAL

### Student's Declaration

I declare that this project report is my own original work and has not been submitted for the award of any degree or diploma in any other institution of higher learning. All sources of information used have been duly acknowledged through referencing.

Signature: ____________________________          Date: ____________________

Name: Abdijabar Abdullahi hussein                              Registration No.: BIT/2024/62274

### Supervisor's Approval

This project report has been submitted for examination with my approval as the appointed university supervisor.

Signature: ____________________________          Date: ____________________

Name:

<br>

## ACKNOWLEDGEMENT

I wish to extend my sincere gratitude to my supervisor,Mr. Benard Chogi,  for the valuable guidance and constructive feedback provided throughout the development of this project. I also thank the households that participated in the requirements-gathering interviews, and my family and classmates for their continued encouragement and support during the course of this work.

## ABSTRACT

Domestic energy consumption in most Kenyan households is spread across four largely disconnected sources: grid electricity supplied by the Kenya Power and Lighting Company (KPLC), Liquefied Petroleum Gas (LPG) used for cooking, solar photovoltaic backup systems, and kerosene used as a secondary fuel. Because each source is tracked, if at all, through a different mechanism — prepaid tokens, opaque steel cylinders, basic charge controllers, and paper receipts — households have no single view of their overall energy footprint or monthly expenditure.

This project presents the design and development of the Home Energy Consumption Management System (HEMS), a web-based application that allows household members to manually record their electricity, LPG, solar, and kerosene usage through simple data-entry forms. The system converts these heterogeneous inputs into a common energy unit (kilowatt-hours) using standard thermodynamic conversion constants, computes running costs in Kenya Shillings, and presents the results through consolidated dashboards and trend charts. The application is built using the Python Flask framework, a MySQL relational database, and a Bootstrap-based responsive frontend, and was developed using an Agile iterative prototyping approach informed by structured interviews and field observations of target households. The resulting prototype gives families a practical, low-cost way to see where their energy budget is going and to make informed decisions about shifting consumption between fuel sources.

<br>

## TABLE OF CONTENTS

DECLARATION AND APPROVAL .................................................... ii

ACKNOWLEDGEMENT ................................................................ iii

ABSTRACT .............................................................................. iv

## CHAPTER ONE: INTRODUCTION ................................................ 1

## CHAPTER TWO: LITERATURE REVIEW ........................................ 6

## CHAPTER THREE: RESEARCH METHODOLOGY ............................ 11

## CHAPTER FOUR: SYSTEM ANALYSIS ........................................... 14

## CHAPTER FIVE: SYSTEM DESIGN & IMPLEMENTATION ................ 30

REFERENCES ........................................................................... 41

APPENDICES ............................................................................ 42

<br>

## CHAPTER ONE: INTRODUCTION

### 1.0 Background of the Study

In contemporary developing economies, and specifically within the urban and peri-urban socio-economic landscape of Kenya, domestic energy procurement and utilisation are heterogeneous, fragmented, and drawn from multiple sources. Unlike households in highly industrialised nations, where residential properties typically rely on a single, unified electrical smart grid for all domestic utility operations (including space heating, water heating, refrigeration, and cooking), a typical middle-income Kenyan household splits its daily utility operations among several independent, decentralised energy sources.

Grid electricity supplied by the Kenya Power and Lighting Company (KPLC) is treated as a premium but inherently unstable resource, and its use is therefore heavily restricted by household managers. Grid electricity is primarily reserved for low-load baseline operations, specifically lighting, low-to-medium draw refrigeration, and consumer electronics such as televisions, sound bars, internet routers, and mobile charging ports.

Heavy thermal cooking tasks are intentionally kept off the grid because of the historically high cost per kilowatt-hour of electricity and the risk of sudden outages. Cooking instead relies almost exclusively on pressurised Liquefied Petroleum Gas (LPG), distributed in standard 6 kg and 13 kg steel cylinders. To guard against frequent grid outages, many middle-income families also install small-scale solar photovoltaic backup systems that operate as isolated DC loops or low-capacity inverted AC circuits for critical loads. Kerosene remains a secondary backup fuel for basic water heating or manual lighting in some peri-urban homes.

Figure 1.1: Typical Kenyan household energy setup — four independent energy sources feeding separate categories of load

| Energy Source | Typical Use | How It Is Normally Tracked |
| --- | --- | --- |
| KPLC Grid Power | Lighting, TV, refrigeration, routers, charging | Prepaid token balance / monthly bill |
| LPG Cylinders | Heavy thermal cooking | Not tracked — discovered empty mid-use |
| Solar Backup | Emergency loop, critical loads during outages | Basic charge controller, no history stored |
| Kerosene | Emergency water heating, manual lighting | Loose cash receipts |

Despite the regular daily use of these four energy types, most domestic consumers keep this data in completely separate information silos, with no intersection between them. Grid consumption is invisible until a bill arrives or a low-credit alert sounds below 2.00 kWh. LPG tracking is entirely reactive because the steel cylinders give no visual indication of the fluid mass remaining, so households typically discover a depleted cylinder mid-meal. Solar generation statistics sit inside cheap charge controllers with no historical storage, and kerosene purchases are recorded, if at all, on receipts that are quickly misplaced.

The Home Energy Consumption Management System (HEMS) is proposed to close this gap. It provides a centralised web portal where household members can manually log appliance duty cycles, LPG cylinder weight changes, solar generation estimates, and kerosene volumes. The system converts these inputs into unified diagnostic data, generating real-time cost-benefit summaries that help Kenyan families identify hidden waste, plan their energy budgets, and make informed decisions about their household power mix.

### 1.1 Problem Statement

Kenya's domestic energy sector lacks integrated household-level data tracking tools. While industrial facilities rely on large-scale Supervisory Control and Data Acquisition (SCADA) systems, ordinary households manage a mix of four fuel types using guesswork, handwritten notes, and reactive spending habits.

#### 1.1.1 The Ideal Situation

An optimised household energy budget depends on full visibility of all domestic energy inputs. Ideally, a homeowner should have a single dashboard showing aggregated energy values, a real-time cost breakdown per fuel source, historical weekly and monthly consumption trends, and a way to identify high-drain appliances.

#### 1.1.2 The Existing Reality

Most Kenyan households operate with fragmented utility data spread across KPLC token notifications, cash fuel receipts, and unmonitored solar equipment, leaving no integrated view of total energy footprint or household expenditure.

#### 1.1.3 The Core Bottlenecks

No unified dashboard capable of combining different fuel measurements (kWh, kg, litres) into a single analytical view.

No analytical tools for comparing cost efficiency between grid electricity and alternative fuels.

No ability to log daily resource variations, which lets energy waste go unnoticed until bills arrive.

No context-aware recommendations to help users shift consumption toward cheaper alternatives.

#### 1.1.4 The Socio-Economic Impact

Without a diagnostic tool, families continue to overspend on expensive or inefficient energy sources without realising it. Unmonitored habits can quietly leak thousands of shillings a month from the household budget and delay the transition to cleaner, more sustainable energy options.

#### 1.1.5 The Solution Link

HEMS addresses these tracking issues as an accessible data-compilation engine: it turns manual logs into standardised consumption values, produces visual trend charts, and generates clear cost-saving insights to help families balance their domestic budgets.

### 1.2 Objectives of the Project

#### 1.2.1 General Objective

To design, develop, and implement a web-based Home Energy Consumption Management System that aggregates, monitors, and analyses multi-source domestic energy utilisation (electricity, LPG, solar, and kerosene) within a single Kenyan household context.

#### 1.2.2 Specific Objectives

| # | Specific Objective | Target |
| --- | --- | --- |
| 1 | Analyse current domestic energy tracking habits and compile system requirements from target households. | End of Week 2 |
| 2 | Design the system architecture, application interfaces, and relational database schema using UML notation. | End of Week 6 |
| 3 | Develop the multi-source tracking web application using Python Flask and a MySQL database. | End of Week 14 |
| 4 | Test system calculation logic, form inputs, and visual rendering responsiveness across devices. | End of Week 23 |
| 5 | Deploy the completed prototype in an experimental household environment to verify calculation accuracy. | End of Week 34 |

### 1.3 Scope of the Project

Defining clear boundaries for this project ensures development effort is focused on delivering a robust, working prototype without succumbing to feature creep.

#### Functional Scope

Dedicated manual data-entry modules for electricity (appliance wattage and runtime hours), LPG (cylinder mass-drop readings in kilograms), solar (estimated generation yield), and kerosene (volumetric consumption in litres). The system automatically computes total energy in kWh and cost in KES, and generates trend charts and rule-based efficiency tips.

#### Technical Scope

Frontend: HTML5, CSS3, and JavaScript with the Bootstrap 5 framework. Backend: Python 3.x on the Flask micro-framework, with MySQL for persistent storage. Charting: Chart.js on the client side.

#### Target Demographics

Homeowners as primary administrators with full data privileges, and other family members with view-only dashboard access.

#### Exclusions

This prototype excludes automated IoT sensor integrations, smart-plug hardware, direct API connections to commercial utility billing systems (e.g. KPLC), and native mobile applications for iOS or Android.

### 1.4 Justification of the Project

Conventional energy research tends to treat grid electricity in isolation from other domestic fuels, overlooking the mixed-utility patterns common in developing economies. This project addresses that gap through:

Operational Efficiency — replacing scattered receipts and token records with a single digital dashboard.

Financial Oversight — surfacing hidden energy leaks so households can adjust habits and protect their budget.

Strategic Resource Adjustments — comparative analytics showing exactly when to shift tasks toward cheaper energy sources.

### 1.5 Potential Project Risks and Mitigation Matrix

Because HEMS depends on manual data entry, it carries predictable technical and behavioural risks. Table 1.2 summarises these risks and the mitigations built into the system design.

| Risk ID | Risk Description | Probability | Severity | Mitigation Strategy |
| --- | --- | --- | --- | --- |
| R01 | Inconsistent data entry — users forget to log usage due to fatigue. | Medium | Medium | Simplified single-field forms optimised for quick updates. |
| R02 | Data integrity errors from invalid characters or incorrect figures. | Medium | Low | Strict HTML5 number inputs plus backend regex validation. |
| R03 | Reduced platform access due to local internet outages. | Medium | Medium | Local browser caching to preserve dashboard stability. |

### 1.6 Project Budget — Estimated Investment

Table 1.3 details the projected capital investment required to execute this project, from requirements gathering to final packaging. All figures are in Kenya Shillings (KES).

| Expenditure Category | Itemised Description | Projected Cost (KES) |
| --- | --- | --- |
| Production Infrastructure | Web cloud hosting setup and domain registration (12 months) | 5,000 |
| Research & Connectivity | Telecommunications bandwidth for development and testing | 2,000 |
| Documentation Processing | Report compilation, printing, and hardcover binding | 3,000 |
| Field Verification Tasks | Domestic site travel expenses for system prototyping | 2,000 |
| Contingency Reserves | Emergency allocation for system adjustments | 3,000 |

TOTAL INITIAL INVESTMENT: KES 15,000

### 1.7 Project Schedule

The development lifecycle for the HEMS prototype is scheduled across a 34.5-week timeline, distributed sequentially across five milestones as shown in Table 1.4.

| Project Phase Milestone | Duration (Weeks) | Cumulative Week |
| --- | --- | --- |
| 1. Requirements Analysis | 2.5 | Week 2.5 |
| 2. System Architecture Design | 4.0 | Week 6.5 |
| 3. Application Engineering | 7.5 | Week 14 |
| 4. Quality Assurance Testing | 9.5 | Week 23.5 |
| 5. Final Deployment & Packaging | 11.0 | Week 34.5 |

Total Timeline Allocation: 34.5 Weeks

### 1.8 Significance of the Study

This project is significant to several groups of stakeholders. For individual households, HEMS offers a practical, low-cost way to understand where money is going each month across four different energy sources, something no existing tool in the Kenyan market currently provides at this price point. For the wider community, a tool that nudges households toward cheaper, more efficient fuel choices contributes indirectly to reduced pressure on the national grid during peak hours and to more informed household-level decisions about renewable energy adoption.

For the academic community, this project contributes a documented case study of how Home Energy Management System theory — largely developed for automated, single-grid contexts in industrialised countries — can be adapted to fit the fragmented, multi-source reality of a developing economy. This adaptation itself is a contribution, since most HEMS literature assumes infrastructure conditions that do not hold in much of Sub-Saharan Africa.

Finally, for future developers and researchers, the system's modular design and open conversion methodology (Section 2.4) provide a foundation that can be extended with automated sensor integration, mobile applications, or utility API connections once such infrastructure becomes more widely accessible in Kenya.

### 1.9 Assumptions and Limitations of the Study

This project makes several working assumptions that shape its design. First, it assumes that household members are willing and able to perform manual data entry on a regular basis, since the prototype does not integrate automated sensors. Second, it assumes that the standard thermodynamic conversion constants used for LPG and kerosene (Section 2.4) are reasonably representative across cylinder types and fuel grades sold in the Kenyan market, even though minor variations exist between suppliers. Third, it assumes that local energy prices, while entered as fixed average values in the current prototype, are broadly stable enough over a monitoring period of a few months to produce meaningful cost comparisons.

The study is limited in scope by its reliance on manual logging rather than automated metering, which means the accuracy of its output is bound by the consistency of user input. It is further limited by its exclusion of mobile-native applications and any live connection to KPLC's billing systems, both of which were placed outside scope in Section 1.3 to keep the prototype achievable within the available timeframe and budget. These limitations are revisited in Chapter Six alongside recommendations for future extensions.

### 1.10 Definition of Key Terms

| Term | Definition |
| --- | --- |
| HEMS | Home Energy Management System — a platform used to monitor and manage domestic energy use. |
| kWh (Kilowatt-hour) | A standard unit of energy equal to one kilowatt of power sustained for one hour; used here as the common comparison unit across all fuel types. |
| LPG | Liquefied Petroleum Gas — a pressurised gas fuel used in Kenyan households mainly for cooking, sold in steel cylinders. |
| Prepaid Token | A numeric code purchased from KPLC that credits a household's electricity meter with a fixed number of kWh units. |
| Multi-Source Aggregation | The process of combining measurements from different fuel types into a single, standardised analytical view. |
| Duty Cycle | The pattern of on/off operation of an appliance over a given period, used here to estimate electricity consumption from wattage and runtime. |

### 1.11 Overview of Comparative Household Energy Costs

To motivate the need for a common comparison unit, Table 1.5 illustrates how differently the four energy sources are priced per unit and per kWh-equivalent in the Kenyan retail market, using the prototype's illustrative starting prices (Appendix C). Because each source is sold in a different physical unit — kWh, kilograms, or litres — households have no easy way to compare them side by side without first converting each into a common measure, which is precisely the function HEMS is designed to perform automatically.

| Energy Source | Retail Unit | Illustrative Retail Price | Approx. Cost per kWh-Equivalent |
| --- | --- | --- | --- |
| Grid Electricity | kWh | KES 28.00 per kWh | KES 28.00 |
| LPG | kg (13 kg cylinder) | KES 250.00 per kg (~KES 3,250 per cylinder) | KES 19.53 |
| Kerosene | Litre | KES 160.00 per litre | KES 15.46 |
| Solar (after initial setup) | kWh generated | No recurring per-unit cost | Effectively KES 0.00 per kWh |

The LPG starting value is an approximate household retail baseline derived from KES 3,250 per 13 kg refill. Actual prices vary by cylinder size, brand, and location; the dashboard lets each household configure its prices and their effective date. A tariff is a start-dated version: each log is costed using the latest tariff effective on or before its log date, and a new tariff date must be later than the existing start date. The comparison shows the effective date of the active price set and does not represent a live market feed.

This comparison illustrates a pattern that is often invisible to households using separate tracking mechanisms: LPG is, on a like-for-like energy basis, considerably cheaper than grid electricity for equivalent thermal output, which supports the kind of system advisory message described in Section 5.1 and reinforces the justification for the project set out in Section 1.4.

### 1.12 Organisation of the Report

The remainder of this report is organised into four further chapters. Chapter Two reviews relevant theory and existing systems, situating HEMS within both international HEMS research and the specific Kenyan context. Chapter Three describes the research methodology, including the development lifecycle, requirement-gathering methods, and feasibility assessment. Chapter Four presents the system analysis, covering data flow diagrams, functional and non-functional requirements, and the entity-relationship model. Chapter Five presents the detailed system design and implementation, including the user interface, database design phases, backend implementation, security design, and deployment architecture, closing with a summary of testing outcomes and overall conclusions drawn from the project.

### 1.13 Stakeholder Analysis

Table 1.6 identifies the main stakeholders affected by or involved in this project, along with their respective interests and level of expected involvement.

| Stakeholder | Interest in the Project | Level of Involvement |
| --- | --- | --- |
| Homeowner / Primary User | Wants a clear, low-cost way to track and reduce household energy spending. | High — daily data entry and dashboard use |
| Family Members | Want visibility into household costs without needing to manage data entry themselves. | Low — view-only dashboard access |
| Project Supervisor | Wants a well-analysed, correctly implemented, and clearly documented academic deliverable. | Medium — periodic review and approval |
| Future Developers | May extend the system with sensors, mobile apps, or utility integrations. | None during this phase — relevant to Section 5.10 recommendations |
| KPLC / LPG Retailers | Indirectly affected if households shift consumption patterns based on system insights. | None — external, not directly consulted |

#### 1.13.1 Detailed Cost-Benefit Rationale

To further justify the investment described in Section 1.6, it is useful to weigh the modest one-time development cost of KES 15,000 against the potential household-level savings the system is designed to surface. If behavioural feedback theory (Section 2.1.2) holds even at the conservative end of the 5% reduction range reported by Darby (2006), a household spending the KES 4,000 per month illustrated in the worked example of Appendix D would save roughly KES 200 per month, or KES 2,400 per year, purely from improved visibility — without changing suppliers or purchasing any new hardware. Scaled across even a modest number of households adopting the same approach, this suggests a favourable cost-benefit position for the underlying concept, independent of the specific KES 15,000 development budget, which is a one-time academic project cost rather than a recurring cost borne by each household.

### 1.14 Chapter Summary

This chapter has introduced the fragmented, multi-source nature of domestic energy consumption in Kenya, defined the problem this creates for household budgeting, and set out the general and specific objectives, scope, justification, risks, budget, and schedule governing the HEMS project. It has also clarified the assumptions and limitations under which the project operates and identified the stakeholders who stand to benefit from its outcomes.

A recurring theme throughout this chapter is that the core barrier to better household energy decisions in Kenya is not a lack of data per se — households already receive token alerts, feel a cylinder's weight, and glance at a charge controller — but a lack of any mechanism to bring these separate signals into one place where they can be compared on equal terms. Every objective, scope decision, and risk mitigation described in this chapter follows directly from that single observation. The next chapter reviews the theoretical and system-level literature that informs the specific design decisions taken in Chapters Four and Five.

<br>

## CHAPTER TWO: LITERATURE REVIEW

### 2.0 Introduction

This chapter reviews foundational research, established theory, and existing commercial systems relevant to Home Energy Management Systems (HEMS). It considers international and local Kenyan systems in order to position the technical framework of this project and to identify the specific gaps it is designed to close.

### 2.1 Theoretical Framework

#### 2.1.1 The Home Energy Management System (HEMS) Model

The HEMS framework is an architectural standard for optimising how power is consumed, stored, and distributed within domestic properties. Traditional HEMS research focuses heavily on automated smart grids — connected appliances and scheduling algorithms that balance demand during peak periods. This project adapts the HEMS model to a developing-region context by shifting emphasis from automated hardware control to data visibility across a mix of energy sources, since automated grid balancing has limited relevance where most Kenyan households are not even on a fully automated single-source grid.

#### 2.1.2 Behavioural Energy Feedback Theory

Energy Feedback Theory holds that giving people access to real-time consumption data prompts conscious changes in behaviour. Research led by Sarah Darby at the University of Oxford found that clear, persistent feedback on consumption can help households cut their overall energy use by roughly 5 to 15 percent, largely because visible feedback prompts users to notice waste, fix faulty equipment, and adjust daily routines. This behavioural mechanism underpins the value proposition of HEMS: visibility itself, even without automation, is expected to change habits.

Figure 2.1: Behavioural feedback loop — from data visibility to measurable consumption reduction

| Stage | Description |
| --- | --- |
| Centralised Data Visibility | Household usage across all fuel sources is logged in one platform. |
| Behavioural Awareness | Users notice idle devices, wasteful habits, and faulty equipment. |
| Measured Reduction | Households typically achieve a 5%–15% reduction in overall consumption. |

#### 2.1.3 Heterogeneous Multi-Source Aggregation

Conventional monitoring platforms are usually designed for a single-source utility connection, which does not reflect the mixed-fuel reality of developing economies. Multi-source aggregation instead combines diverse fuel types — grid electricity, pressurised gas, and alternative or biomass sources — into one analytics platform, giving households a complete picture of their spending and consumption habits.

### 2.2 Review of International System Architectures

#### 2.2.1 The Sense Home Energy Monitor

The Sense Home Energy Monitor is a premium hardware device installed directly in a property's main distribution panel. It samples current at very high frequency and uses machine learning to identify individual appliance signatures from a single measurement point. Despite its technical sophistication, its retail price above KES 40,000 and its requirement for professional electrical installation make it impractical for most Kenyan households.

#### 2.2.2 The Legacy Google PowerMeter Initiative

Google PowerMeter was an early cloud dashboard for real-time smart-meter data. It was eventually discontinued because it depended on utility companies opening access to their telemetry infrastructure. This failure illustrates the risk of building a system around corporate utility APIs, and supports HEMS's choice of an independent, user-driven manual logging model.

#### 2.2.3 Decentralised Smart-Plug Matrices

Consumer ecosystems such as TP-Link Kasa or Sonoff measure consumption through individual inline smart relays. Covering an entire house this way requires purchasing many separate units, which creates a real cost barrier, and these plugs cannot track non-electrical resources such as LPG cylinders or liquid fuels.

### 2.3 The Contemporary Kenyan Context

#### 2.3.1 KPLC Prepayment Metering

KPLC's prepaid infrastructure uses split Customer Interface Units that provide basic feedback through low-credit audio alerts and numeric kWh balances. These meters have no analytical dashboard to show which appliances are driving consumption, leaving households unable to diagnose the causes of rapid token depletion.

#### 2.3.2 Isolated Multi-Source Energy Studies

Local academic research tends to treat grid electricity, cooking-fuel programmes, and solar microgrids as separate subjects. This leaves a practical gap for a single tool that brings these everyday resources together, helping households make cost-effective decisions based on current local prices.

### 2.4 Standard Metric Conversion Formulas

To produce reliable comparisons, HEMS converts every fuel measurement into a common thermal-equivalent unit, kilowatt-hours (kWh), using standard conversion constants:

| Energy Source | Base Unit | Conversion to kWh |
| --- | --- | --- |
| Grid Electricity | kWh | 1.00 kWh = 1.00 kWh (base unit) |
| Liquefied Petroleum Gas (LPG) | kg | 1.00 kg ≈ 12.80 kWh |
| Domestic Kerosene | Litres | 1.00 L ≈ 10.35 kWh |

Total Domestic Energy Usage (kWh) = Electricity (kWh) + [LPG (kg) × 12.80] + [Kerosene (L) × 10.35]

### 2.5 Additional Theoretical Perspectives

#### 2.5.1 The Technology Acceptance Model (TAM)

The Technology Acceptance Model, originally proposed by Fred Davis, argues that a user's intention to adopt a new system is shaped primarily by two factors: perceived usefulness and perceived ease of use. Applied to HEMS, this model suggests that adoption by ordinary household members — who are not necessarily technically trained — will depend less on the sophistication of the underlying conversion engine and more on whether the data-entry forms feel quick and worthwhile to use. This is the theoretical basis for the simplified, single-field form design described in Section 5.2 and for the mitigation strategy against inconsistent data entry described in Table 1.2.

#### 2.5.2 Diffusion of Innovation Theory

Everett Rogers' Diffusion of Innovation theory classifies adopters of a new technology into innovators, early adopters, early majority, late majority, and laggards, and argues that an innovation spreads faster when it is compatible with existing routines, is not overly complex, and produces observable results quickly. HEMS is designed with this in mind: rather than requiring households to change their existing fuel-purchasing behaviour, it simply asks them to record data about routines they already follow, and produces a visible dashboard result almost immediately after the first few entries, which is expected to support faster voluntary adoption than a system requiring new hardware or a change in supplier.

#### 2.5.3 Resource-Based Household Budgeting Theory

Household budgeting research generally treats energy as a single undifferentiated expense line, which obscures the fact that, in mixed-fuel contexts such as Kenya, different energy sources compete for the same limited household budget under very different pricing structures. Treating electricity, LPG, solar, and kerosene as a single interchangeable resource pool, converted into a common unit as described in Section 2.4, allows a household budgeting decision — for example, whether to cook with gas or an electric appliance on a given day — to be made on a genuine cost basis rather than on habit alone.

### 2.6 Comparative Analysis of Reviewed Systems

Table 2.2 consolidates the systems reviewed in Sections 2.2 and 2.3 against the core criteria relevant to a Kenyan household context, making the positioning of HEMS relative to existing alternatives explicit.

| System | Multi-Fuel Support | Hardware Required | Approx. Cost | Suitable for Mass Kenyan Adoption? |
| --- | --- | --- | --- | --- |
| Sense Home Energy Monitor | No (electricity only) | Panel-level sensor + professional install | > KES 40,000 | No — cost and install barrier |
| Google PowerMeter (discontinued) | No (electricity only) | Smart meter + utility API | N/A (discontinued) | No — depended on utility cooperation |
| TP-Link Kasa / Sonoff smart plugs | No (electricity only) | One smart plug per appliance | ~KES 2,000–4,000 per plug | Partially — expensive to scale |
| KPLC Prepaid CIU | No (electricity only) | Built into meter | Included in tariff | Yes, but no analytics |
| HEMS (proposed) | Yes — electricity, LPG, solar, kerosene | None — manual web entry | Software only | Yes — low cost, no install barrier |

### 2.7 Local Kenyan Academic Studies on Household Energy Use

Several local studies have examined household cooking-fuel transitions and electrification patterns in Kenya, generally within energy-policy or environmental-studies departments rather than computing departments. These studies consistently report that Kenyan households use a mix of fuels rather than switching entirely from one source to another as income rises — a pattern sometimes called fuel stacking. This behaviour is directly relevant to HEMS, since it confirms that a monitoring tool must handle several concurrent fuel types rather than assuming a single dominant source, reinforcing the multi-source aggregation design chosen in Section 2.1.3.

However, these prior studies are almost entirely survey-based and descriptive; none of them propose or evaluate a software artefact that households could use directly to track their own consumption. This is the specific gap that the present project, situated within a computing rather than a policy-research discipline, is designed to fill.

### 2.8 Summary of Knowledge Gaps Identified

The reviewed solutions and studies share several limitations: high acquisition cost (in excess of KES 40,000 for hardware-based systems), an exclusive focus on grid electricity that ignores secondary fuels, high installation complexity requiring professional electrical work, a general absence of unified dashboards suited to the mixed-utility patterns typical of Kenyan homes, and — in the case of local academic research — a lack of any practical software tool arising from otherwise sound survey findings on fuel-stacking behaviour. HEMS is positioned to directly address each of these gaps.

### 2.9 Related Kenyan Digital Energy Payment Platforms

Beyond the monitoring-focused systems reviewed in Section 2.2, it is useful to consider Kenyan platforms built around energy payment rather than energy tracking, since these shape the environment HEMS operates within. M-KOPA Solar, for example, provides pay-as-you-go solar home systems financed through daily mobile-money instalments, tracked entirely through the vendor's own proprietary app tied to a specific hardware kit. Similarly, KPLC's own mobile app allows customers to buy prepaid electricity tokens and view a basic purchase history, but, as noted in Section 2.3.1, this history is limited to electricity and does not extend to LPG, solar, or kerosene.

These platforms demonstrate that Kenyan consumers are already comfortable with mobile-based energy interactions, which supports the operational feasibility of a web-based tool such as HEMS (Section 3.5.3). However, none of them attempt to unify tracking across more than one energy source, which is the specific niche this project occupies.

### 2.10 Dashboard and Data Visualisation Design Principles

Because HEMS is fundamentally a data-visibility tool, its effectiveness depends heavily on how clearly its dashboard communicates information, not merely on the accuracy of its underlying calculations. Established data visualisation guidance — most notably the principles popularised by Edward Tufte and later adapted for web dashboards — emphasises minimising unnecessary decoration, using consistent colour coding across related charts, and preferring simple line and bar charts over complex visual forms for time-series household data. These principles directly informed the layout decisions summarised in Table 5.1, particularly the choice to represent the multi-source expense profile as a straightforward percentage breakdown rather than a more elaborate chart type.

A second relevant principle is progressive disclosure: showing a simple headline number (total monthly cost) prominently, while allowing more detailed breakdowns to be explored only if the user chooses to look further. This avoids overwhelming non-technical household members with data while still giving power users access to the full detail they may want.

### 2.11 Synthesis: Positioning HEMS Against Reviewed Literature

Table 2.3 draws together the theoretical and system-level review presented in this chapter into a single synthesis, showing how each identified gap or principle directly shapes a specific design decision made later in this report.

| Literature Insight | Source | Resulting HEMS Design Decision |
| --- | --- | --- |
| Feedback reduces consumption by 5–15% | Darby (2006), Section 2.1.2 | Consolidated dashboard with weekly trend chart (Section 5.1) |
| Ease of use drives adoption more than sophistication | TAM, Section 2.5.1 | Single-field, minimal-friction data-entry forms (Section 5.2) |
| Innovations spread faster when compatible with existing routines | Diffusion of Innovation, Section 2.5.2 | No hardware change required; logging fits existing fuel-purchase habits |
| Hardware-based monitors are too costly for mass adoption | Section 2.2.1, 2.2.3 | Software-only, manual-entry architecture (Section 1.3) |
| Households fuel-stack rather than use one source | Section 2.7 | Simultaneous tracking of four fuel types via unified conversion (Section 2.4) |
| Simple, consistent visuals aid comprehension | Section 2.10 | Minimal, colour-consistent dashboard layout (Table 5.1) |

### 2.12 Summary of Reviewed Literature by Source

Table 2.4 consolidates every major source discussed in this chapter alongside its specific contribution to the present project, providing a single reference point before moving into the methodology described in Chapter Three.

| Author / Source | Core Contribution | Relevance to HEMS |
| --- | --- | --- |
| Darby (2006) | Feedback on consumption can reduce household energy use by 5–15%. | Justifies the dashboard-centred design approach (Section 5.1). |
| Davis (TAM) | Perceived usefulness and ease of use drive technology adoption. | Informs the simplified, low-friction form design (Section 5.2). |
| Rogers (Diffusion of Innovation) | Compatibility with existing routines speeds adoption of new tools. | Supports manual logging over hardware replacement (Section 1.3). |
| Sense Labs (2023) | Hardware-based monitoring is accurate but expensive and installation-heavy. | Confirms the cost gap HEMS is designed to close (Section 2.2.1). |
| Google (2011) | Utility-dependent platforms are vulnerable to being discontinued. | Justifies an independent, manually-entered data model (Section 2.2.2). |
| KPLC (2024) | Prepaid metering gives balance information but no appliance-level analytics. | Defines the specific gap in electricity-only feedback (Section 2.3.1). |

This synthesis confirms that no single reviewed source, whether theoretical or system-based, addresses the combination of low cost, multi-fuel coverage, and behavioural feedback that HEMS is designed to provide, reinforcing the specific contribution of this project set out in Section 2.8.

#### 2.12.1 Extended Theoretical Positioning

It is worth noting explicitly that the three theoretical lenses applied in this chapter — behavioural feedback theory (Section 2.1.2), the Technology Acceptance Model (Section 2.5.1), and Diffusion of Innovation theory (Section 2.5.2) — address three distinct concerns that together cover the full adoption pathway a household must travel. Behavioural feedback theory explains why visibility should change consumption once a household is already using the system; TAM explains what determines whether a household starts using the system in the first place; and Diffusion of Innovation explains how quickly the system might spread beyond an initial pilot group of households to a wider community. No single theory on its own would have been sufficient to justify both the technical design and the expected real-world impact of HEMS, which is why all three are retained and cross-referenced throughout the design chapters that follow.

### 2.13 Chapter Summary

This chapter has reviewed the theoretical foundations relevant to HEMS, including the general HEMS model, behavioural feedback theory, multi-source aggregation principles, the Technology Acceptance Model, and Diffusion of Innovation theory. It has also reviewed international hardware-based monitoring systems, the Kenyan prepaid metering context, related digital energy-payment platforms, and dashboard design principles, before synthesising all of these insights against the specific design decisions made elsewhere in this report. The consistent finding across every strand of this review is that existing tools address either cost, multi-fuel coverage, or behavioural feedback, but never all three simultaneously — the specific space HEMS occupies. The next chapter presents the research methodology used to translate this literature-informed positioning into a working prototype.

<br>

## CHAPTER THREE: RESEARCH METHODOLOGY

### 3.0 Introduction

This chapter presents the methodology used to build the software platform: the development lifecycle model adopted, the methods used to collect requirements, and the functional basis for the resulting system.

### 3.1 Development Model

The system was engineered using an Agile-driven iterative prototyping lifecycle. This model runs development across discrete sprints, allowing the platform to be tested and refined continuously based on feedback.

| Sprint | Focus Area |
| --- | --- |
| Sprint 1 | Core authentication and user management setup |
| Sprint 2 | Multi-source data logging module integration |
| Sprint 3 | Analytical processing and dashboard design |
| Sprint 4 | Reporting systems and automated logic engine |

### 3.2 Requirement-Gathering Methods

To ensure the application solves real tracking problems faced by local consumers, requirements were gathered directly from target users through three complementary methods:

Structured Interviews — conducted with target households to document utility purchase habits, pain points, and expectations (documented internally during requirements gathering).

Direct Field Observation — on-site review of household electricity setups, gas refill routines, and backup fuel storage.

Document Review — analysis of past utility receipts, prepayment tokens, and fuel bills to map core data fields and pricing structures.

### 3.3 Limitations of the Current Baseline Setup

The baseline approach used by most families today is entirely manual and disjointed. Grid usage is visible only when buying tokens, LPG consumption goes unmonitored until a cylinder runs out, and liquid fuels are bought on demand with no lasting record. This lack of centralised tracking makes it difficult for families to analyse monthly spending or identify opportunities to save.

### 3.4 Benefits of the Proposed System

The proposed web application replaces these disjointed workflows with a centralised data platform. Users record routine energy inputs through simple forms, and the application processes these values into consolidated costs and visual trends, giving households clear insight to manage spending and build more efficient energy habits.

### 3.5 Feasibility Study

Before committing to full development, the project was assessed against four standard feasibility dimensions: technical, economic, operational, and legal feasibility. This assessment confirmed that the project was achievable within the available time, budget, and skill set.

#### 3.5.1 Technical Feasibility

The proposed technology stack — Flask, MySQL, Bootstrap, and Chart.js — is open-source, well documented, and runs on modest hardware, requiring no specialised infrastructure beyond a standard laptop and a low-cost cloud hosting plan. All required skills (Python web development, relational database design, and basic frontend scripting) fall within the existing coursework covered in the degree programme, making the project technically feasible without dependence on hardware procurement or specialised electronics knowledge.

#### 3.5.2 Economic Feasibility

As shown in the budget in Table 1.3, the total projected cost of the project is KES 15,000, covering hosting, connectivity, documentation, and field verification. This is a modest sum relative to the value delivered, particularly when compared against the KES 40,000-plus cost of hardware alternatives reviewed in Section 2.2.1. Because the finished system requires no special hardware to operate, the ongoing running cost for an end household is limited to standard internet access, which most target households already have.

#### 3.5.3 Operational Feasibility

The system was deliberately designed around simple, familiar web forms rather than unfamiliar interaction patterns, which reduces the training burden on end users. The requirement-gathering interviews described in Section 3.2 confirmed that target household members were comfortable with basic web and mobile browser interactions, supporting the assumption that the system can be operated without extensive user training once deployed.

#### 3.5.4 Legal Feasibility

The system stores only data that users voluntarily enter about their own household's energy use; it does not collect or process third-party personal data, and it does not connect to any external utility or government database. Passwords are stored using industry-standard hashing rather than in plain text (Section 4.2.2, NFR1), which aligns with basic data-protection expectations under Kenya's Data Protection Act, 2019, for handling any personally identifiable account information.

### 3.6 Justification of Development Tools

Table 3.2 summarises the reasoning behind each major technology choice made for this project.

| Tool / Technology | Reason for Selection |
| --- | --- |
| Python / Flask | Lightweight micro-framework with a low learning curve, well suited to a single-developer academic project, and with strong community documentation. |
| MySQL | Mature, widely supported relational database engine with strong support for the structured, tabular energy-log data used in this system. |
| Bootstrap 5 | Provides ready-made responsive UI components, reducing frontend development time while still allowing custom styling. |
| Chart.js | A lightweight, well-documented charting library that integrates directly with data returned from Flask without requiring a heavier data-visualisation stack. |
| Werkzeug security (pbkdf2:sha256) | Built-in, peer-reviewed password hashing utility bundled with Flask, avoiding the risks of a custom-built hashing routine. |

### 3.7 Testing Strategy

Testing was planned as a continuous activity running alongside each development sprint described in Table 3.1, rather than as a single activity performed only at the end of development. Table 3.3 outlines the testing levels applied and their specific purpose within this project.

| Testing Level | Purpose | Example in HEMS |
| --- | --- | --- |
| Unit Testing | Verify that individual calculation functions return correct values. | Confirming the LPG-to-kWh conversion function returns 12.80 kWh for an input of 1 kg. |
| Integration Testing | Verify that modules work correctly together. | Confirming that a saved appliance log is correctly reflected in the dashboard's electricity total. |
| System Testing | Verify the complete application against the functional requirements in Section 4.2.1. | Walking through registration, login, data entry, and dashboard viewing end to end. |
| User Acceptance Testing (UAT) | Verify the system meets the needs of real target households. | Asking pilot households to log a week of real data and comment on ease of use. |

### 3.8 Target Population and Sampling

The target population for the requirement-gathering phase consisted of middle-income households in urban and peri-urban Nairobi that use at least two of the four energy sources described in Section 1.0. A purposive sampling approach was used rather than random sampling, since the study specifically required households already managing a mixed-fuel setup rather than a representative cross-section of the general population. Five households were selected for the structured interviews described in Section 3.2. Three households are proposed as the pilot cohort; the pilot has not yet been conducted.

This sample size is consistent with the qualitative, requirements-focused nature of the study: the goal was to surface recurring pain points and data-entry expectations in sufficient depth, rather than to produce statistically generalisable findings, which would have required a substantially larger and more randomly selected sample.

### 3.9 Data Collection Instruments

Three instruments were used to collect requirements data, corresponding to the three methods introduced in Section 3.2. The interview guide (Appendix A of the requirements documentation) consisted of seven open-ended questions covering current tracking habits, pain points, and willingness to adopt a digital tool. A structured observation checklist was used during field visits to record the physical setup of each household's meter, cylinder storage area, and solar equipment. Finally, a document collection form was used to log the type, date range, and completeness of any receipts or token records a household was willing to share.

| Instrument | Data Captured | Administered By |
| --- | --- | --- |
| Interview Guide | Qualitative responses on habits, pain points, and expectations | Researcher, in person |
| Observation Checklist | Meter type, cylinder size, solar equipment present | Researcher, on-site |
| Document Collection Form | Receipt/token date ranges and completeness | Household member, self-reported |

### 3.10 Data Analysis Procedure

Interview responses were analysed qualitatively by grouping recurring statements into themes — such as "cylinder runs out unexpectedly" or "no way to compare gas versus electricity cost" — which directly informed the core bottlenecks listed in Section 1.1.3. Observation data was tabulated to confirm which of the four energy sources were actually present in each household, ensuring the system's functional scope (Section 1.3) matched real conditions rather than an assumed configuration. Document samples were used only to confirm plausible price ranges for the conversion constants in Section 2.4, and were not used to draw any statistical conclusions given the small and non-random sample.

### 3.11 Ethical Considerations

Because this study involves information about household energy use and spending, safeguards are required for any data collection. Participation in interviews and any future pilot must be voluntary, with the purpose explained before participants agree to take part. Personally identifying financial information, such as full receipts or account numbers, should not be included in the final report; use only aggregated or anonymised figures. No pilot data has been collected because the planned deployment has not yet taken place.

### 3.12 Development Environment and Tools

Table 3.4 lists the specific software versions and supporting tools used during development, to support reproducibility of the prototype described in this report.

| Category | Tool / Version |
| --- | --- |
| Programming Language | Python 3.11 |
| Web Framework | Flask 3.x |
| Database Engine | MySQL 8.0 |
| Frontend Framework | Bootstrap 5.3 |
| Charting Library | Chart.js 4.x |
| Version Control | Git, hosted on a private repository |
| Code Editor | Visual Studio Code |

### 3.13 Change Management Approach

Because the Agile model described in Section 3.1 assumes that requirements may shift slightly as feedback is received, a lightweight change-management approach was adopted rather than a formal change-control board, which would be disproportionate for a project of this scale. Any proposed change to scope, arising either from supervisor feedback or from pilot household input during Sprint 4, was logged with a short description, a rationale, and an assessment of its impact on the schedule in Table 1.4 before being accepted into the next sprint. This kept the project responsive to real feedback while still protecting the fixed 34.5-week timeline from uncontrolled scope growth.

### 3.14 Sprint Deliverables in Detail

Table 3.5 expands on the four sprints introduced in Table 3.1, specifying the concrete deliverable produced at the end of each sprint and the criterion used to confirm that the sprint was complete.

| Sprint | Concrete Deliverable | Completion Criterion |
| --- | --- | --- |
| Sprint 1 | Working registration, login, and logout routes with hashed passwords. | A test user can register, log out, and log back in successfully. |
| Sprint 2 | Functional appliance, LPG, kerosene, and solar logging forms. | A reading submitted through each form appears correctly in its database table. |
| Sprint 3 | Dashboard route returning correct aggregated totals and a rendered trend chart. | Manually computed totals match the values shown on the dashboard. |
| Sprint 4 | Rule-based advisory message and finalised reporting views. | The advisory message correctly reflects the cheaper fuel source for a given test dataset. |

### 3.15 Risk Management Approach During Development

Beyond the project-level risks identified in Table 1.2, day-to-day development risk was managed by keeping each sprint deliverable in Table 3.5 small enough to test independently before moving to the next. This meant that a defect in, for example, the LPG conversion logic implemented in Sprint 2 could be caught and corrected before the dashboard aggregation logic in Sprint 3 was built on top of it, reducing the chance of compounding errors late in development. Version control commits were made at the end of each completed feature, giving a clear rollback point if a later change introduced a regression.

### 3.16 Chapter Summary

This chapter has set out the Agile iterative prototyping model adopted for this project, the three requirement-gathering methods used, the limitations of the current manual baseline, the feasibility assessment across four dimensions, the justification for each development tool selected, and the multi-level testing strategy applied throughout. It has further detailed the target population and sampling approach, the specific data collection instruments used, the ethical safeguards applied, and the development environment and change-management practices that supported the project.

Taken together, this methodology was chosen specifically because it matches the scale and constraints of a single-developer academic project: it avoids the overhead of a large-team process framework while still giving structured checkpoints — at the end of each sprint in Table 3.5 — where the emerging system could be verified against the objectives set out in Section 1.2 before further work was committed. The next chapter builds on this methodology to present the detailed system analysis.

#### 3.17.1 Validity and Reliability Considerations

Given the purposive requirements-gathering sample described in Section 3.8, validity and reliability should be considered within the limits of a small qualitative study. Requirements can be cross-checked across interviews, direct observation, and document review as described in Section 3.2. The planned pilot has not yet occurred, so no claims about pilot reliability or household acceptance can be made at this stage.

### 3.18 Chapter Summary

Table 3.6 consolidates the key methodological decisions made in this chapter alongside the specific reason each was chosen over an available alternative, closing the chapter with a single point of reference.

| Decision | Alternative Considered | Reason Chosen |
| --- | --- | --- |
| Agile iterative prototyping | Waterfall model | Allows requirements to be refined as pilot feedback arrives, suited to a single-developer timeline. |
| Purposive sampling of 5 households | Random sampling of a large population | Requirements needed depth from mixed-fuel households specifically, not general representativeness. |
| Planned manual pilot deployment (3 households) | Simulated / synthetic test data only | A future pilot can assess conversion results against genuine household usage patterns; it has not yet taken place. |
| Direct SQL via flask_mysqldb | Full ORM (e.g. SQLAlchemy) | Keeps the codebase lightweight and easier to reason about for a project of this scope. |

<br>

## CHAPTER FOUR: SYSTEM ANALYSIS

### 4.0 Introduction

This chapter defines the functional structure of the application using Data Flow Diagrams (DFDs), explicit system requirements, and a logical Entity-Relationship Diagram (ERD).

### 4.1 Data Flow Overview

#### 4.1.1 Context-Level (Level 0) Description

At the highest level, the system has one external entity — the household member — who submits data (appliance logs, fuel readings) to the HEMS application and receives visual dashboards in return. The application reads from and writes to a relational data store that holds all persisted records.

#### 4.1.2 Level 1 Process Breakdown

The main system decomposes into four core processes, summarised in Table 4.1.

| Process | Trigger | Data Store Written / Read |
| --- | --- | --- |
| 1.0 Manage Appliances | Household member adds/edits an appliance | Writes to D1: Appliances |
| 2.0 Log Fuel Mass / Volume | Household member records LPG, kerosene, or solar reading | Writes to D2: Gas Logs, D3: Kerosene, D4: Solar Logs |
| 3.0 Run Conversion Engine | Triggered on dashboard request | Reads D1–D4 |
| 4.0 Compile Dashboard | Household member requests dashboard view | Reads D1, D2, D3, D4 |

### 4.2 System Requirements Specification

#### 4.2.1 Functional Requirements

| ID | Requirement | Description |
| --- | --- | --- |
| FR1 | Authentication | Secure user registration, credential encryption, and profile access control. |
| FR2 | Appliance Management | Add, modify, and delete appliance profiles along with wattage ratings and runtime hours. |
| FR3 | Fuel Tracking | Dedicated input fields for volumetric fuel quantities and cylinder weight drops. |
| FR4 | Engine Calculations | Automated conversion of raw inputs into standardised energy units (kWh) and cost estimates (KES). |
| FR5 | Visual Analytics | Dynamic generation of charts and reports covering selected timeframes. |

#### 4.2.2 Non-Functional Requirements

| ID | Requirement | Description |
| --- | --- | --- |
| NFR1 | Security | Password protection using secure hashing algorithms (e.g. pbkdf2:sha256). |
| NFR2 | Responsiveness | Fluid interface layout across mobile screens and desktop monitors. |
| NFR3 | Maintainability | Modular backend organisation for simple updates and troubleshooting. |

### 4.3 Entity-Relationship Overview

The relational schema links each user to one set of appliance profiles and to four categories of daily consumption logs. A single user record can have many appliances and many readings in each of the electricity, gas, kerosene, and solar log tables, forming four one-to-many relationships radiating from the USERS entity.

| Entity | Key Attributes | Relationship to USERS |
| --- | --- | --- |
| USERS | id (PK), username, password_hash | Parent entity |
| APPLIANCES | id (PK), user_id (FK), name, wattage, hours | One user → many appliances |
| ELEC_READINGS | id (PK), user_id (FK), log_date, kwh_value | One user → many electricity readings |
| GAS_READINGS | id (PK), user_id (FK), log_date, kg_consumed | One user → many gas readings |
| KEROSENE_LOGS | id (PK), user_id (FK), log_date, liters_used | One user → many kerosene logs |
| SOLAR_LOGS | id (PK), user_id (FK), log_date, kwh_yield | One user → many solar logs |

### 4.4 Use Case Analysis

Table 4.2 lists the primary use cases supported by HEMS and the actors associated with each, forming the basis for the use case diagram referenced in the system design phase.

| Use Case | Primary Actor | Description |
| --- | --- | --- |
| Register Account | Homeowner | Create a new user account protected by a hashed password. |
| Log In / Log Out | Homeowner, Family Member | Authenticate to access the dashboard and end an active session. |
| Manage Appliances | Homeowner | Add, edit, or remove appliance profiles with wattage and runtime data. |
| Log Fuel Reading | Homeowner | Record LPG, kerosene, or solar readings for a given date. |
| View Dashboard | Homeowner, Family Member | View aggregated energy and cost figures and trend charts. |
| View Advisory Tip | Homeowner, Family Member | Receive a rule-based recommendation on cost-efficient fuel choices. |

#### 4.4.1 Use Case Narrative — Log Fuel Reading

This narrative describes the primary use case flow in detail, since it represents the core recurring interaction on which the rest of the system's analytics depend.

| Step | Actor Action | System Response |
| --- | --- | --- |
| 1 | Household member selects the fuel type to log (LPG, kerosene, or solar). | System displays the corresponding data-entry form. |
| 2 | Household member enters the reading value and date. | System validates the input type and range on the client side. |
| 3 | Household member submits the form. | System writes a new record to the relevant table (GAS_READINGS, KEROSENE_LOGS, or SOLAR_LOGS). |
| 4 | — | System redirects to a confirmation view and updates the dashboard totals on next visit. |

### 4.5 Sequence of Operations — Dashboard Compilation

When a household member requests the dashboard, the system performs a fixed sequence of operations rather than an ad-hoc query. First, the application authenticates the session and retrieves the associated user_id. Second, it queries the APPLIANCES table and computes total electricity in kWh from the sum of wattage multiplied by runtime hours, divided by 1000, across all appliance records. Third, it queries GAS_READINGS and KEROSENE_LOGS to obtain total kilograms of LPG and litres of kerosene consumed. Fourth, it applies the conversion constants defined in Section 2.4 to translate LPG and kerosene into kWh-equivalent values. Fifth, it multiplies each energy category by its respective per-unit price (Appendix C) to compute a cost breakdown in KES. Finally, it passes the aggregated values to the dashboard template, which renders the summary cards and trend chart described in Section 5.1.

This fixed sequence ensures that every dashboard view reflects the same calculation logic regardless of how many fuel types a given household actively uses, and that a household with no kerosene or solar records simply receives a zero value for that category rather than an error.

### 4.6 Class-Level View of Core Entities

Table 4.3 presents a simplified class-level view of the core backend entities, showing the key attributes and behaviours associated with each, as a bridge between the relational ERD in Section 4.3 and the implementation in Chapter Five.

| Class | Key Attributes | Key Behaviours |
| --- | --- | --- |
| User | id, username, password_hash | register(), authenticate(), start_session() |
| Appliance | id, user_id, name, wattage, hours | add(), edit(), delete(), compute_kwh() |
| FuelReading | id, user_id, log_date, value, fuel_type | add(), convert_to_kwh(), convert_to_cost() |
| DashboardCompiler | user_id | aggregate_totals(), generate_advisory(), render_view() |

### 4.7 Activity Flow — New Reading Lifecycle

Table 4.4 traces the full lifecycle of a single fuel reading from the moment a household member decides to log it to the moment it contributes to a dashboard figure, making explicit the states a reading passes through inside the system.

| State | Trigger | Next State |
| --- | --- | --- |
| Draft (in form) | User opens a fuel logging form | Submitted, once the form passes client-side validation |
| Submitted | Form POST request received by Flask route | Validated, once server-side type and range checks pass |
| Validated | Backend confirms numeric ranges and required fields | Persisted, once the INSERT statement commits |
| Persisted | Record written to the relevant readings table | Aggregated, on the next dashboard request |
| Aggregated | Dashboard route sums and converts the record | Displayed, as part of the rendered summary view |

### 4.8 Data Dictionary

Table 4.5 provides a complete data dictionary for the core tables introduced in the ERD (Section 4.3), specifying data types and constraints used at the physical database level.

| Table | Field | Data Type | Constraint |
| --- | --- | --- | --- |
| users | id | INT | Primary Key, Auto Increment |
| users | username | VARCHAR(80) | Unique, Not Null |
| users | password_hash | VARCHAR(255) | Not Null |
| appliances | wattage | DECIMAL(10,2) | Not Null, > 0 |
| appliances | hours | DECIMAL(5,2) | Not Null, 0–24 |
| gas_readings | kg_consumed | DECIMAL(10,2) | Not Null, ≥ 0 |
| kerosene_logs | liters_used | DECIMAL(10,2) | Not Null, ≥ 0 |
| solar_logs | kwh_yield | DECIMAL(10,2) | Not Null, ≥ 0 |

### 4.9 Input Validation Rules

Table 4.6 sets out the specific validation rules enforced for each data-entry field, directly implementing the risk mitigation for R02 described in Table 1.2 and the NFR1 security requirement in Section 4.2.2.

| Field | Validation Rule | Failure Behaviour |
| --- | --- | --- |
| Username | Must be unique, 3–80 characters | Registration rejected with an on-screen error |
| Password | Minimum 6 characters before hashing | Registration form re-displayed with a warning |
| Wattage | Positive decimal number only | Form blocks submission via HTML5 number constraint |
| Runtime Hours | Decimal between 0 and 24 | Form blocks submission via HTML5 min/max constraint |
| Fuel Quantity (kg / litres) | Non-negative decimal number | Server-side check rejects negative values before insert |

### 4.10 Elaboration of Non-Functional Requirements

Section 4.2.2 introduced three non-functional requirements at a summary level. Table 4.7 elaborates each with a specific, testable acceptance criterion, since a non-functional requirement that cannot be verified provides little practical guidance during system testing (Section 3.7).

| ID | Acceptance Criterion |
| --- | --- |
| NFR1 (Security) | All stored passwords must be hashed with pbkdf2:sha256; no password may appear in plain text in any log, database column, or error message. |
| NFR2 (Responsiveness) | All primary pages must render correctly, without horizontal scrolling or overlapping elements, on screen widths from 360px (typical smartphone) to 1920px (typical desktop). |
| NFR3 (Maintainability) | Each Flask route must be documented with a short comment describing its purpose, and business logic (conversion formulas) must be isolated from routing logic to support future modification without rewriting unrelated code. |

### 4.11 System Constraints

Several constraints bound the system analysis presented in this chapter. The system assumes a single primary administrator account per household, consistent with the target demographics defined in Section 1.3, and does not currently support multiple administrator accounts contributing data to the same household record. It also assumes a stable, if intermittent, internet connection for data submission, mitigated by the local caching strategy in Table 1.2 (R03), and it assumes that all monetary values are recorded and displayed in Kenya Shillings only, with no multi-currency support built into the schema described in Section 4.3.

### 4.12 Chapter Summary

This chapter has presented the functional structure of HEMS through data flow diagrams, a full functional and non-functional requirements specification, an entity-relationship model, a use case analysis with a detailed narrative and sequence of operations, a class-level view of core entities, an activity lifecycle for a fuel reading, a complete data dictionary, and a set of input validation rules. Together, these artefacts provide the analytical foundation for the detailed design and implementation presented in Chapter Five.

### 4.13 Traceability Between Requirements and Design Artefacts

Table 4.8 provides a traceability matrix linking each functional requirement defined in Section 4.2.1 to the specific analysis artefact in this chapter that models it, and forward to the implementation section in Chapter Five where it is realised, giving a single point of reference for verifying that no requirement was analysed without being carried through to implementation.

| Requirement | Analysis Artefact | Implementation Reference |
| --- | --- | --- |
| FR1 (Authentication) | Use case: Register / Log In (Table 4.2) | Section 5.4 — /register, /login routes |
| FR2 (Appliance Management) | Class-level view: Appliance (Table 4.3) | Section 5.4, Appendix B — /appliances route |
| FR3 (Fuel Tracking) | Use case narrative: Log Fuel Reading (Section 4.4.1) | Section 5.4 — fuel-specific logging routes |
| FR4 (Engine Calculations) | Sequence of operations (Section 4.5) | Section 5.4 — /dashboard aggregation logic |
| FR5 (Visual Analytics) | Class-level view: DashboardCompiler (Table 4.3) | Section 5.1 — chart rendering |

<br>

## CHAPTER FIVE: SYSTEM DESIGN & IMPLEMENTATION

### 5.0 Introduction

This chapter presents the detailed design of the system's user interface, input validation model, database architecture, and backend implementation.

### 5.1 User Interface Design

The primary dashboard uses a modular layout. Aggregate summary values sit at the top of the screen, with multi-source comparison charts arranged directly below to highlight cost breakdowns, and a short rule-based advisory message at the bottom of the page.

| Dashboard Section | Contents |
| --- | --- |
| Operational Snapshot | Aggregated load consumption (kWh) and estimated cost (KES) for the running month. |
| Multi-Source Expense Profile | Percentage cost share for grid, LPG, and alternative sources. |
| Historical Consumption Trend | Weekly kWh trend line for the current month. |
| System Advisory | Rule-based tip, e.g. recommending LPG over grid for thermal cooking when cheaper. |

### 5.2 Input Design

Data-capture forms use native client-side type checking to prevent malformed values from reaching the database layer.

| Field | Example Value | Input Constraint |
| --- | --- | --- |
| Appliance Name | Living Room Refrigerator | Free text, required |
| Power Consumption (W) | 250 | Numeric, positive, required |
| Daily Runtime (hrs) | 12.5 | Numeric, 0–24, required |

### 5.3 Database Design Phases

The database was created through four standard design phases:

Requirements Analysis — mapping essential data fields for authentication, appliance configuration, and transaction logs across all four energy sources.

Conceptual Design — defining platform-independent entities such as User, Appliance, and EnergyReading, and the relationships between them.

Logical Design — translating the conceptual model into relational tables with primary and foreign keys.

Physical Design — implementing the schema in MySQL, setting field types (e.g. DECIMAL(10,2) for monetary and energy values), and adding indexes on date fields for query performance.

### 5.4 Backend Implementation

The Flask backend implements four route groups: authentication (registration, login, logout), appliance management, fuel logging, and dashboard compilation. The dashboard route aggregates electricity from logged appliance duty cycles, sums LPG and kerosene readings, applies the conversion constants from Section 2.4, and multiplies each converted value by its local per-unit price to compute total cost. Full source code is provided in Appendix B.

### 5.5 Security Design

Beyond password hashing (NFR1, Section 4.2.2), the system applies several additional safeguards appropriate to a web application handling household financial data. Session state is managed server-side using Flask's signed session cookies, protected by a secret key, so that session data cannot be tampered with by the client. All database queries use parameterised statements rather than string concatenation, which prevents SQL injection through the data-entry forms. Form inputs are constrained both on the client side, using native HTML5 input types, and on the server side, using explicit type casting and range checks before any value is written to the database, addressing risk R02 in Table 1.2.

Access control is enforced at the route level: any request to a protected route such as /dashboard first checks for an active session and redirects unauthenticated requests back to the login page. Family members with view-only access are restricted at the template level from seeing the data-entry and appliance-management forms, so that only the primary homeowner account can modify household records.

### 5.6 Deployment Architecture

The prototype is deployed using a straightforward three-tier architecture suited to a small-scale academic deployment. The presentation tier consists of server-rendered HTML templates styled with Bootstrap and enhanced with Chart.js, served directly by Flask. The application tier is the Flask process itself, handling routing, validation, and the conversion calculations described in Section 4.5. The data tier is a MySQL instance, which may run on the same host as the application during testing but is designed to be moved to a separate managed database service without code changes, since all database access is abstracted through the flask_mysqldb connection object.

Figure 5.1: Three-tier deployment architecture — presentation, application, and data tiers

| Tier | Technology | Responsibility |
| --- | --- | --- |
| Presentation | HTML5, Bootstrap 5, Chart.js | Renders forms and dashboards in the household member's browser. |
| Application | Python 3.x, Flask | Handles routing, session management, validation, and conversion logic. |
| Data | MySQL | Persists user, appliance, and fuel-reading records. |

### 5.7 Sample Test Cases

Table 5.4 presents a representative sample of test cases executed during system testing, linked to the functional requirements in Section 4.2.1 and the testing strategy in Section 3.7.

| Test ID | Requirement | Test Description | Expected Result | Status |
| --- | --- | --- | --- | --- |
| TC01 | FR1 | Register with a username that already exists. | System rejects duplicate username with an error message. | Passed |
| TC02 | FR1 | Log in with an incorrect password. | System denies access and displays an invalid-credentials message. | Passed |
| TC03 | FR2 | Add an appliance with a negative wattage value. | System rejects the input before it reaches the database. | Passed |
| TC04 | FR3 | Log an LPG reading of 3 kg. | System converts and stores the reading as 38.40 kWh-equivalent. | Passed |
| TC05 | FR4 | View dashboard with no kerosene records. | System displays a kerosene total of 0.00 without error. | Passed |
| TC06 | FR5 | Request the historical trend chart for a household with four weeks of data. | System renders a four-point weekly trend line. | Passed |

### 5.8 Summary of Testing Results

Software verification was carried out through automated unit and integration tests, application workflow checks, and browser checks against the functional requirements. The test suite currently contains 56 passing automated tests. Household user-acceptance testing has not yet taken place; it is planned for Phase 5 after deployment.

| Testing Level | Test Cases Executed | Passed | Failed / Reworked |
| --- | --- | --- | --- |
| Automated unit and integration tests | 56 | 56 | 0 |
| MySQL and browser workflow checks | Completed; see the QA evidence in `ROADMAP.md` | Passed for the exercised workflows | No household pilot |
| User Acceptance Testing | Not yet conducted | Pending deployment and two-week pilot | No user findings available |

### 5.9 Discussion of Findings

The automated tests and recorded application workflow checks provide evidence for the software's conversion, validation, access-control, and dashboard behaviour. No household user-acceptance or pilot feedback is available because deployment and the planned two-week pilot remain outstanding. The usability and real-household accuracy of the system must therefore be assessed during that pilot rather than inferred from software tests.

Table 5.6 maps each specific objective defined in Section 1.2.2 against the evidence of its achievement within this project.

| Objective | Evidence of Achievement |
| --- | --- |
| 1. Analyse tracking habits and compile requirements | Completed through structured interviews, field observation, and document review (Section 3.2). |
| 2. Design architecture, interfaces, and schema | Completed through DFDs, ERD, and use case analysis (Chapter Four). |
| 3. Develop the tracking web application | Completed using Flask and MySQL, with core routes implemented and verified (Section 5.4; Appendix B). |
| 4. Test calculation logic, inputs, and responsiveness | Completed across four testing levels with results summarised in Table 5.5. |
| 5. Deploy the prototype for accuracy verification | Pending: deployment and a two-week pilot with three households remain Phase 5 work. |

#### 5.9.1 Detailed Screen-by-Screen Wireframe Descriptions

Table 5.7 describes the primary screens implemented in the prototype in more detail than the summary dashboard layout in Table 5.1, providing a screen-by-screen reference for the frontend implementation.

| Screen | Key Elements | Primary Action |
| --- | --- | --- |
| Login | Username field, password field, Register link, flash error area | Submit credentials to start a session |
| Register | Username field, password field, Confirm button | Create a new hashed-password account |
| Appliance List | Table of existing appliances, Add New button, Edit/Delete icons per row | Manage appliance profiles |
| Fuel Logging Form | Fuel-type selector, value field, date picker, Commit Log button | Record a new fuel reading |
| Dashboard | Snapshot cards, expense-profile bars, trend chart, advisory banner | Review consolidated energy and cost data |

#### 5.9.2 API and Route Reference

Table 5.8 provides a consolidated reference of every route exposed by the Flask backend, expanding on the summary already provided in Appendix B, and cross-referencing each route to the functional requirement it fulfils.

| Route | Method | Linked Requirement | Notes |
| --- | --- | --- | --- |
| / | GET | FR1 | Entry point; redirects based on session state. |
| /register | GET, POST | FR1 | Creates account; enforces unique username at the database level. |
| /login | POST | FR1 | Verifies password hash and starts a signed session. |
| /appliances | GET, POST | FR2 | Lists and creates appliance records for the logged-in user. |
| /fuel/lpg, /fuel/kerosene, /fuel/solar | GET, POST | FR3 | Fuel-specific logging endpoints sharing a common validation routine. |
| /dashboard | GET | FR4, FR5 | Aggregates, converts, and renders consolidated totals and charts. |
| /logout | GET | FR1 | Clears the active session and returns to the login screen. |

### 5.10 Conclusion and Recommendations

This project set out to address the absence of an integrated household-level energy tracking tool suited to the mixed-fuel reality of Kenyan homes. The HEMS prototype provides manual logging and consolidates four energy sources into kWh and KES views. Software QA results in Section 5.8 support the tested application behaviour, but real-household accuracy and usability remain unverified until the planned Phase 5 deployment and pilot are completed.

Looking ahead, several extensions would strengthen the system further: integrating low-cost IoT sensors to automate electricity logging, developing a companion mobile application to reduce data-entry friction, exploring a data-sharing arrangement with KPLC once suitable API access becomes available, extending the rule-based advisory engine into a more adaptive recommendation system, and conducting a larger-scale pilot to validate the cost-saving impact with stronger statistical evidence.

### 5.12 Future-Proofing and Extensibility Design

Although the current prototype is complete and functional as designed, the system architecture has been intentionally structured to support future extensions without requiring a complete rewrite. Three extension pathways are particularly important to flag here, each of which has been anticipated in the design choices made.

First, if automated IoT sensors become practical to deploy (e.g. smart plugs for electricity, weight sensors on LPG cylinders, or simple temperature loggers for kerosene), the current manual data-entry endpoints can be left untouched while new automated-input routes are added in parallel. The database schema already accepts timestamp information, which would be set automatically by sensors rather than by user input. The conversion and calculation logic in the dashboard route is completely independent of whether a given reading came from manual entry or an automated sensor, so adding sensor support requires only that the new sensor-input routes write to the same tables. A hypothetical route like @app.route('/sensor/appliance-log', methods=['POST']) could accept JSON payloads from smart plugs and insert them into the ELEC_READINGS table with no changes needed to the dashboard calculation engine.

Second, if a partnership with KPLC becomes feasible in future, the system could import prepaid-meter transaction history via an API endpoint rather than requiring users to enter electricity consumption manually. This would replace the current appliance-wattage-based estimate with actual consumption data, increasing accuracy. A scheduled import job could run nightly, calling KPLC's hypothetical API at /api/v1/consumption?meter_id={id}, parsing the JSON response, and writing each transaction to a dedicated table like KPLC_TRANSACTIONS, which would then be queried instead of APPLIANCES when computing electricity consumption. The front-end and dashboard calculation logic would not need to change; only the source of the electricity-consumption data would shift.

Third, the current rule-based advisory messages (Section 5.1) could in future be replaced or augmented with machine-learning-based recommendations that learn from a household's historical patterns and seasonal variations. For example, a system might notice that a household consistently shifts to LPG cooking on Tuesdays, or that solar generation drops during the rainy season. Rather than a static comparison of per-kWh prices, it could predict cost savings from specific behaviour changes. The structure of the recommendations output is already decoupled from the calculation logic — it is generated in a separate function called generate_advisory() within the dashboard route — so this change could be made by replacing that one function without rewriting the rest of the application.

Each of these extension pathways is made possible by the clear separation of concerns in the application architecture, the use of standard data formats (relational tables, standard thermodynamic constants), and the modular organisation of the Flask routes and template system. This design was deliberate, informed by the principle that an academic prototype is more valuable to future researchers and developers if it is extensible rather than monolithic. The code is written to be readable, with clear variable names and function signatures that telegraph their purposes, which further reduces the cognitive burden on someone extending the system in future.

### 5.13 Comparative Advantages of the HEMS Approach

To close Chapter Five with a final perspective, it is useful to summarise what HEMS offers that distinguishes it from the review of existing systems in Section 2.2. Table 5.5 presents this comparison in structured form.

| Comparison Dimension | Sense / Hardware Approach | HEMS Approach |
| --- | --- | --- |
| Capital cost to household | KES 40,000+ hardware + installation | Software only, no hardware cost |
| Technical skill required to install | Professional electrician needed | None — web browser sufficient |
| Fuel types tracked | Electricity only | Electricity, LPG, kerosene, solar |
| Onset time (weeks to first dashboard view) | 2–4 weeks (installation queue) | 1–2 days (account setup + first log) |
| Scalability to other households | Requires physical install per home | Unlimited — software scales with users |
| Dependence on external services | May depend on vendor APIs / cloud | Independent — uses only own server |
| Cost to deploy to 100 households | KES 4,000,000+ (hardware + labour) | KES 10,000–30,000 (hosting + support) |

This comparison underscores why HEMS, despite lacking the technical sophistication of hardware-based alternatives, is better positioned for rapid, low-cost adoption across a large number of households in a developing-economy context. It trades some technical elegance for practical deployability, and this trade is appropriate given the target context.

### 5.11 Chapter Summary

### 5.11 Chapter Summary

This chapter has presented the design and implementation of the HEMS prototype: the dashboard and input interface, database design, backend routes, security safeguards, deployment architecture, and software QA results. It has mapped the project objectives to current evidence and identified deployment, household pilot testing, and accuracy verification as outstanding work.

Read together with the preceding chapters, this report describes the problem, literature, methodology, analysis, and implemented prototype. The software has been verified against the automated test suite, while the planned deployment and household pilot remain necessary to complete the full development lifecycle.

<br>

## REFERENCES

Darby, S. (2006). The effectiveness of feedback on energy consumption: A review for DEFRA of the literature on metering, billing and direct displays. Environmental Change Institute, University of Oxford, 26(2), 585–608.

Kenya Power and Lighting Company (KPLC). (2024). Prepaid metering and tariff guide. Nairobi: KPLC.

Mount Kenya University. (2024). Guidelines for computing projects development approaches. Directorate of Computing and Informatics.

Sense Labs Inc. (2023). Sense Home Energy Monitor — product and technical documentation. Retrieved from https://sense.com

Google Inc. (2011). Google PowerMeter: Retrospective on a discontinued smart-energy initiative.

Grinnell, R. M., & Unrau, Y. A. (2018). Social work research and evaluation: Foundations of evidence-based practice (11th ed.). Oxford University Press.

<br>

## APPENDICES

### Appendix A: Sample Data-Entry Form Layouts

Table A.1 summarises the fields used on the four primary data-entry forms referenced in Sections 1.3 and 5.2.

| Form | Fields Captured | Unit |
| --- | --- | --- |
| Appliance Log | Appliance name, wattage, daily runtime hours | W, hrs |
| LPG Reading | Cylinder weight before/after, log date | kg |
| Solar Reading | Estimated generation yield, log date | kWh |
| Kerosene Log | Volume purchased/used, log date | Litres |

### Appendix B: Backend Route Summary (app.py)

Table B.1 summarises the Flask routes implemented in the prototype's backend. Full inline source code is available in the project code repository submitted alongside this report.

| Route | Method | Purpose |
| --- | --- | --- |
| / | GET | Redirects logged-in users to the dashboard, otherwise shows login page. |
| /register | GET, POST | Creates a new user account with a securely hashed password. |
| /login | POST | Authenticates a user and starts a session. |
| /dashboard | GET | Aggregates electricity, LPG, and kerosene logs, applies conversion formulas, and renders the summary view. |
| /logout | GET | Clears the active session. |

### Appendix C: Standard Conversion Constants Used

| Fuel | Constant | Value |
| --- | --- | --- |
| LPG | kWh per kg | 12.80 |
| Kerosene | kWh per litre | 10.35 |
| Electricity tariff (average) | KES per kWh | 28.00 |
| LPG starting price (illustrative) | KES per kg | 250.00 |
| Kerosene price (average) | KES per litre | 160.00 |
