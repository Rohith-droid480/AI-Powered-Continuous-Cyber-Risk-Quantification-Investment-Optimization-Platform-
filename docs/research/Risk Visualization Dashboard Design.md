# **Executive Visualization of Probabilistic Financial Risk: Architecture, Cognitive Ergonomics, and Front-End Implementation**

Communicating probabilistic risk to executive leadership and corporate boards requires bridging mathematical rigor and cognitive accessibility. Traditional governance workflows have historically depended on qualitative risk matrices that assign ordinal rankings, such as red, amber, and green indicators. These matrices introduce severe systemic errors, including range compression, subjective scoring inflation, and an inability to account for portfolio aggregation.  
Modern quantitative risk frameworks, such as the Factor Analysis of Information Risk (FAIR) standard and actuarial catastrophe modeling, calculate exposure as continuous financial distributions generated via Monte Carlo simulations1. Translating metrics such as Value at Risk (![][image1]), Expected Shortfall (![][image2]), and annualized loss exceedance into intuitive graphical interfaces demands a grounded understanding of human visual cognition, front-end rendering engines, and empirical uncertainty communication3.

## **Front-End Visualization Framework Evaluation: Recharts and D3.js**

Developing interactive executive dashboards requires selecting a rendering architecture that balances implementation velocity against graphical expressiveness. In the modern TypeScript and React ecosystem, this choice centers on high-level declarative component abstractions versus low-level visualization toolboxes.

\+-------------------------------------------------------------------------+  
|                  React Application State & User Controls                |  
\+-------------------------------------------------------------------------+  
                                     |  
                                     v  
\+-------------------------------------------------------------------------+  
|         Headless Statistical & Transformation Pipeline (d3-array)       |  
|    \- Computes Monte Carlo binning via Freedman-Diaconis                 |  
|    \- Derives Complementary Cumulative Distribution Function (CCDF)      |  
|    \- Extracts percentiles: 50th (Median), 90th, 95th (VaR), 99th        |  
\+-------------------------------------------------------------------------+  
                                     |  
                                     v  
\+-------------------------------------------------------------------------+  
|           Declarative Rendering Plane (Recharts v3.10.1 SVG)            |  
|    \- AreaChart: Exceedance probability surface with gradient fill       |  
|    \- ComposedChart: Discrete frequency histogram with PDF spline        |  
|    \- ReferenceLine: Interactive anchors for Risk Tolerance and VaR      |  
|    \- ResponsiveContainer & Custom Tooltip: Frequency-framed callouts    |  
\+-------------------------------------------------------------------------+

### **Recharts Declarative Architecture**

Recharts is a declarative charting library specifically optimized for React, wrapping native Scalable Vector Graphics (SVG) elements with decoupled state management5. The platform eliminates direct Document Object Model (DOM) mutation by letting React manage component lifecycles and virtual DOM diffing5.

| Framework Dimension | Technical Specification |
| :---- | :---- |
| **Current Release** | v3.10.1 (with experimental canary tracks testing integrated theming engines)5 |
| **Core Distribution Components** | AreaChart, BarChart, LineChart, ComposedChart, ScatterChart \[cite: 5, 8\] |
| **Layout & Coordination Modules** | ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend \[cite: 6, 8\] |
| **Statistical Annotation Primitives** | ReferenceLine, ReferenceArea, ReferenceDot, ErrorBar \[cite: 6\] |
| **Architectural Strengths** | Rapid prototyping, built-in responsive scaling, native accessibility controls, seamless React JSX binding5 |
| **Architectural Limitations** | Requires pre-binned upstream data; lacks built-in kernel density or cumulative probability mathematical routines6 |

In Recharts v3.10.1, displaying continuous Probability Density Functions (PDF) or Cumulative Distribution Functions (CDF) relies primarily on AreaChart and ComposedChart5. The ComposedChart permits simultaneous rendering of discrete histogram bars alongside continuous probability spline overlays on shared horizontal and vertical coordinates5. Statistical thresholds—such as median financial impact, 95th percentile Value at Risk, or board-approved loss tolerance limits—are rendered declaratively using \<ReferenceLine /\> and \<ReferenceArea /\> elements6.  
With the architectural overhaul in version 3.0, internal state management was decoupled, tick generation was unified, and default accessibility properties were embedded natively6. However, Recharts functions exclusively as a rendering layer. It cannot calculate kernel densities, empirical cumulative distributions, or bin widths internally, requiring all statistical data transformations to occur upstream before passing props to components6.

### **D3.js Visual Compilation Primitives**

D3.js operates as a foundational, low-level data visualization library rather than a pre-packaged charting solution9. It provides a modular suite of approximately thirty independent packages designed to bind arbitrary data structures directly to web graphics standards, including SVG, HTML Canvas, and WebGL9.

| Framework Dimension | Technical Specification |
| :---- | :---- |
| **Current Release** | v7.9.0 \[cite: 11, 12\] |
| **Data Transformation Modules** | d3-scale (continuous, logarithmic, quantile), d3-array (binning, percentiles, deviations)13 |
| **Shape & Geometry Modules** | d3-shape (curves, areas, ribbons, radial links), d3-contour (density estimations)13 |
| **Behavioral & Interactive Modules** | d3-brush (dynamic coordinate slicing), d3-zoom (panning/zooming), d3-drag \[cite: 10, 14\] |
| **Architectural Strengths** | Unbounded geometric flexibility, arbitrary spline calculations, full control over SVG path generation9 |
| **Architectural Limitations** | High development overhead; imperative DOM manipulation directly conflicts with React virtual DOM reconciliation9 |

The graphical capability of D3 makes it suitable for complex uncertainty encodings, such as animated Hypothetical Outcome Plots, quantile dot arrays, and dynamic ridge distributions4. Modules such as d3-array provide built-in implementations of the Freedman–Diaconis, Scott, and Sturges binning formulations to partition continuous Monte Carlo distributions into optimal discrete intervals14.  
When integrating D3 into modern React environments, engineers avoid imperative DOM methods like d3-selection and d3-transition, which bypass React's render lifecycle9. The established paradigm treats D3 as a headless mathematical engine: functions from d3-scale and d3-shape compute geometric paths and screen coordinates, which are then passed into declarative React SVG JSX elements15. While this hybrid approach yields visual flexibility, building axes, responsive frames, tooltips, and legends from scratch requires significant development time9.

## **Commercial Cyber Risk Quantification Visual Paradigms**

Commercial Cyber Risk Quantification (CRQ) platforms have operationalized statistical risk visualization for executive teams, enterprise risk managers, and board audit committees2. Examining established commercial platforms highlights how abstract Monte Carlo outputs are structured for executive decision-making.

| Platform | Modeling Foundation | Primary Executive Visual Metaphors | Target Executive Decisions |
| :---- | :---- | :---- | :---- |
| **Safe Security (RiskLens)** \[cite: 1, 17, 18\] | Open FAIR Standard with automated attack-surface telemetry17 | Annualized Loss Exposure ranges (P10, P50, P90); continuous Loss Exceedance Curves; prioritized threat scenario tables1 | Cyber insurance limit validation, capital buffer sizing, control investment ROI prioritization16 |
| **Kovrr** \[cite: 2, 21\] | Proprietary cyber catastrophe engine informed by global incident databases2 | Loss Exceedance Curves with discrete return-period markers (1:100, 1:250 year); financial loss breakdown by category2 | Solvency testing, enterprise risk appetite benchmarking, reinsurance and risk transfer structuring2 |
| **Balbix** \[cite: 23, 24\] | Continuous AI-driven vulnerability and exposure mapping24 | Aggregated monetary risk scores; interactive multi-dimensional bubble heat maps; remediation velocity trendlines23 | Operational fix prioritization, C-suite exposure tracking, business unit risk accountability23 |
| **Axio (Axio360)** \[cite: 27, 28\] | The Axio Method integrating Cyentia empirical likelihood telemetry27 | Min-Likely-Max financial impact spectrums; four-quadrant decision matrices; boardroom-ready impact reports27 | Balance of mitigation versus insurance transfer; justification of security budgets; D\&O liability defensibility27 |

### **Safe Security and the RiskLens FAIR Legacy**

Safe Security acquired RiskLens in 2023, unifying the Open FAIR standard with automated enterprise telemetry ingestion17. The platform structures executive risk communication entirely around financial values rather than qualitative labels1. The core interface presents risk through Annualized Loss Exposure (ALE) distributions1.  
Rather than reporting a single expected loss figure, the platform visualizes outcomes through continuous percentile intervals, highlighting the 10th percentile (optimistic outcome), 50th percentile (median outcome), and 90th percentile (tail exposure)1. Safe Security integrates interactive Loss Exceedance Curves that illustrate the probability of cumulative enterprise losses exceeding specified dollar amounts within a twelve-month window1. Discrete cyber loss events, such as ransomware exfiltration or cloud infrastructure outages, are ranked in monetary order, allowing corporate boards to assess the financial impact of specific security investments1.

### **Kovrr Enterprise Exposure Analytics**

Kovrr structures its visualization architecture around catastrophe modeling principles adapted from property and casualty insurance analytics2. The platform translates threat telemetry and company asset profiles into two financial metrics: Average Annualized Loss (AAL) and return-period thresholds2.  
Kovrr uses the Loss Exceedance Curve to demonstrate solvency impacts at 1-in-100-year and 1-in-250-year return periods, which represent the 99th and 99.6th percentiles of maximum probable loss2. To make these metrics actionable for non-technical leadership, Kovrr decomposes aggregate financial projections into four practical business categories: primary response costs, business interruption expenses, legal and regulatory liabilities, and secondary stakeholder damages2. This categorization shows executives how insurance policies respond across different loss scenarios2.

### **Balbix Posture Dollarization**

Balbix links operational telemetry to executive communication by assigning real-time dollar valuations to technical attack surfaces23. The platform processes internal vulnerability scans, identity misconfigurations, and external threat intelligence through an AI engine that continuously computes breach likelihood and business impact24.  
Rather than relying on static 5x5 grids, Balbix visualizes risks through dynamic bubble heat maps where spatial position reflects exploit probability and operational severity, while bubble volume denotes quantified monetary risk25. The interface supports drill-down navigation: executive leadership can view total enterprise financial exposure over time, then filter by operating subsidiary, physical geography, or specific application infrastructure to see which issues drive the highest risk16.

### **Axio360 Decision Engineering**

Axio360 focuses on defensible decision-making under uncertainty, incorporating empirical incident probabilities developed in partnership with the Cyentia Institute27. The platform uses horizontal range indicators that present financial exposure across a continuous scale from minimum probable loss to maximum catastrophic impact27.  
Axio organizes risk scenarios using a four-quadrant decision matrix that balances financial consequence against occurrence likelihood, directing management toward avoidance, control improvement, acceptance, or risk transfer through insurance policies27. The platform's scenario modeling allows leadership to simulate control investments and evaluate the resulting reduction in financial tail risk, providing documentation for regulatory compliance and board-level risk governance27.

## **Cognitive and Empirical Foundations for Communicating Statistical Uncertainty**

Visualizing statistical uncertainty for non-expert audiences presents distinct psychological challenges. Decades of behavioral research show that decision-makers misinterpret probabilistic graphics when interfaces rely on standard academic conventions3.

| Cognitive Bias / Failure Mode | Empirical Manifestation in Traditional Visualizations | Evidence-Based Visual Remedy | Supporting Empirical Research |
| :---- | :---- | :---- | :---- |
| **Within-the-Bar Bias** | Viewers assume data points falling inside a graphic bar are disproportionately more probable than points immediately outside it4. | Display continuous gradient surfaces, violin profiles, or explicit quantile density steps4. | Hullman et al. (2015)4; Padilla et al. (2020)32 |
| **Deterministic Construal** | Users treat point estimates or mean indicators as certain predictions, discounting ranges3. | Eliminate standalone point marks; emphasize distribution intervals and range spans3. | Spiegelhalter et al. (2011)3; van der Bles et al. (2019)34 |
| **Probability-Magnitude Conflation** | Non-technical executives confuse event occurrence likelihood with the financial severity of the event3. | Map independent visual dimensions: express likelihood via frequency frames and severity in currency units3. | Spiegelhalter et al. (2011)3; Gigerenzer & Hoffrage (1995)36 |
| **Bivariate Misinterpretation** | When comparing overlapping error bars, viewers severely underestimate the probability of one variable exceeding another4. | Deploy Hypothetical Outcome Plots or quantile dot plots to support visual counting4. | Hullman et al. (2015)4; Kale et al. (2018)38 |
| **False Imprecision Skepticism** | Audiences distrust models displaying broad uncertainty unless accompanied by context34. | Separate direct statistical variance from indirect model quality tags34. | van der Bles et al. (2019)34 |

### **Natural Frequencies and Visual Discretization**

The work of David Spiegelhalter demonstrates that human cognition struggles to interpret single-event probabilities expressed as percentages, decimals, or abstract odds3. Non-technical decision-makers routinely miscalibrate risk when presented with statements such as "a 2% annual probability of breach"3.  
Risk comprehension improves when probabilities are translated into natural frequencies, such as "2 out of 100 operating years" or "a 1-in-50-year event"3. Natural frequencies allow the mind to construct concrete mental models of discrete occurrences rather than struggling with continuous mathematical abstractions3.  
Jessica Hullman, Paul Resnick, and Eytan Adar built upon these cognitive principles by investigating alternatives to traditional error bars and violin plots4. Their experiments revealed that static interval bars fail when non-experts compare probabilistic variables4. When presented with two 95% confidence intervals with overlapping boundaries, more than half of study participants estimated the probability of one variable exceeding the other at roughly 0.20 to 0.25, when the true mathematical probability was approximately 0.754. Furthermore, viewers consistently exhibited within-the-bar bias, viewing the visual boundary of a bar as a hard threshold rather than a continuous probability density4.

Conventional Visual Interval (Prone to Within-the-Bar Bias)  
Value Range: ├───\[==== Central 50% \====\]───┤ (Viewers misinterpret edges as cliffs)

Discretized Quantile Array (Supports Intuitive Visual Counting)  
Frequency:   \[ \* \* \* \* \* \* \* \* o o \] (Directly conveys: 8 out of 10 runs exceed limit)

To resolve these cognitive limitations, Hullman et al. introduced **Hypothetical Outcome Plots (HOPs)**4. Rather than summarizing a distribution through static spatial dimensions, HOPs animate individual simulation runs in rapid sequence, presenting each draw as a discrete visual frame4. Viewers evaluate probabilities through intuitive visual sampling and mental counting rather than complex spatial decoding4.  
In dashboard environments where continuous animation may distract users, these same cognitive benefits can be captured using static **quantile discretization**4. By binning continuous distributions into discrete visual markers—such as quantile dot plots or stepped histograms where each graphical segment represents a 1% or 5% probability slice—executives can quickly evaluate likelihoods through visual counting4.

### **Direct Versus Indirect Uncertainty Framing**

Anne Marthe van der Bles, David Spiegelhalter, and their research collaborators established a framework separating uncertainty into two distinct categories: direct and indirect uncertainty34. Direct uncertainty refers to the quantifiable statistical variance of the underlying system, expressed through parameters like standard deviations, confidence intervals, or probability distributions34. Indirect uncertainty refers to the epistemic quality of the underlying evidence, reflecting data gaps, methodological assumptions, and model limitations34.  
Their empirical testing demonstrated that explicitly communicating direct uncertainty through quantitative ranges does not erode user trust or impair executive decision quality34. However, if direct uncertainty is presented without qualitative context, decision-makers often dismiss the model as uninformative34.  
Executive interfaces should therefore implement a dual visual hierarchy: primary visual axes display direct quantitative ranges, while secondary badges or status indicators convey data quality, model maturity, and assessment confidence34.

## **Mechanics and Strategic Function of the Loss Exceedance Curve**

The Loss Exceedance Curve (LEC) is the standard visual representation across insurance underwriting, catastrophe modeling, and enterprise risk quantification2. Built upon open standards developed by The Open Group and the FAIR Institute, the LEC provides an actionable summary of complex Monte Carlo simulations2.

Probability P(L \>= x)  
  100% |-------------\\  
       |               \\  
   50% |                \\   \<-- Median Annualized Loss  
       |                 \\  
       |                  \\      Board Risk Tolerance  
       |                   \\              |  
   10% |                    \\-------------+-------- \<-- 90th Percentile (VaR)  
       |                     \\            |  
    0% \+----------------------\\-----------+------------  
       $0                    $5M         $10M      Loss Exceedance Threshold (x)

### **Mathematical Formulation**

Mathematically, the Loss Exceedance Curve plots the **Complementary Cumulative Distribution Function (CCDF)** of an aggregated loss variable43. Let ![][image3] denote a continuous non-negative random variable representing potential financial loss over an annual horizon, characterized by the probability density function ![][image4] and cumulative distribution function ![][image5]1. The exceedance probability ![][image6] is defined as:  
![][image7]  
The visual mapping follows strict coordinate conventions:

* The horizontal axis (![][image3]) represents loss magnitude, expressed in financial currency units (such as thousands or millions of dollars)43.  
* The vertical axis (![][image8]) represents the annual probability (from 0.0 to 1.0, or 0% to 100%) that cumulative losses will meet or exceed that specific dollar value43.

### **Strategic Significance for Executive Governance**

The Loss Exceedance Curve is widely used in executive boardrooms because it overcomes the structural limitations of point estimates and traditional averages2.

| Strategic Analytical Task | Classical Single-Point Reporting | Loss Exceedance Curve Analysis |
| :---- | :---- | :---- |
| **Tail Risk Visibility** | Averages conceal low-probability, high-impact events within aggregated figures2. | Directly exposes the shape, skew, and extent of catastrophic tail exposures2. |
| **Risk Appetite Integration** | Cannot show whether extreme scenarios breach enterprise risk appetite20. | Allows risk appetite boundaries to be plotted directly over the probability curve20. |
| **Capital Allocation Sizing** | Leaves executives uncertain about appropriate contingency capital reserves2. | Directly illustrates Value at Risk (![][image9]) to guide capital reserve sizing2. |
| **Insurance Coverage Validation** | Policy limits are chosen using arbitrary guesses or basic compliance rules1. | Benchmarks policy limits and deductibles against empirical exceedance probabilities2. |
| **Mitigation ROI Demonstration** | Static metrics struggle to show the value of risk reduction investments20. | Pre- and post-mitigation curves can be overlaid, visualizing total exposure reduction20. |

By reading horizontally from a target probability (e.g., 5%, corresponding to a 1-in-20-year event), leadership can extract the Value at Risk (![][image9])2. Conversely, by identifying a specific loss threshold (such as a $10,000,000 cash reserve limit), executives can determine the exact probability that cyber incidents will exceed enterprise liquidity reserves2.  
Overlaying the organization's approved risk appetite curve creates an immediate visual benchmark: any portion of the curve extending beyond tolerance thresholds highlights exposures that require capital allocation, risk transfer, or technical remediation20.

## **Source Verification Matrix**

Every commercial tool, front-end library, peer-reviewed study, and industry standard has been independently confirmed via active endpoints.

| Source Name & Organization | Direct URL | Status | Actual Content Summary | Specific Dashboard Design Takeaway |
| :---- | :---- | :---- | :---- | :---- |
| **Recharts Documentation** Recharts Open Source Team5 | https://recharts.github.io/ | **VERIFIED** | Active documentation for stable release v3.10.1. Details component APIs including AreaChart, BarChart, ComposedChart, LineChart, ResponsiveContainer, Tooltip, and ReferenceLine. | Implement responsive probabilistic charts natively in React; utilize ComposedChart for distribution overlays and ReferenceLine for threshold markings. |
| **D3.js Visualization Engine** Observable / Mike Bostock9 | https://d3js.org/ | **VERIFIED** | Active documentation for stable release v7.9.0. Details low-level visualization modules including d3-scale, d3-array, d3-shape, and d3-axis. | Restrict D3 to headless data-processing pipelines (calculating bin thresholds, percentiles, and path strings) while allowing React to render SVG elements. |
| **Safe Security (RiskLens)** Safe Security Inc.1 | https://safe.security/resources/insights/what-is-cyber-risk-quantification/ | **VERIFIED** | Active product overview following the acquisition of RiskLens. Details FAIR-based Monte Carlo simulations, breach financial calculations, and 90-day exposure trends. | Express all visual outputs in monetary currency; present distributions via 10th, 50th, and 90th percentile ranges rather than qualitative risk scores. |
| **Kovrr Platform** Kovrr Financial Technologies2 | https://www.kovrr.com/cyber-risk-quantification | **VERIFIED** | Active enterprise CRQ platform documentation. Details modeling of cyber events, Average Annualized Loss (AAL), return periods (1:100, 1:250), and damage categorizations. | Pair the Loss Exceedance Curve with discrete return-period markers, breaking down tail losses across operational, legal, and response costs. |
| **Balbix Platform** Balbix Inc.23 | https://securityboulevard.com/2022/11/balbixs-role-based-dashboards-reduce-risk-at-high-velocity/ | **VERIFIED** | Active exposure management platform overview. Documents automated inventory discovery, monetary breach risk mapping, multi-attribute heat maps, and drill-downs. | Provide an executive-level monetary summary, supported by drill-down views that link risk values directly to specific business units and threat scenarios. |
| **Axio360 Platform** Axio Global Inc.27 | https://axio.com/crq/ | **VERIFIED** | Active cyber risk quantification platform documentation. Details the Axio Method, Cyentia empirical likelihood models, min-to-max exposure spans, and D\&O liability reporting. | Use horizontal impact ranges to communicate minimum, most likely, and maximum financial losses for top risk scenarios. |
| **Spiegelhalter et al. (2011)** *Science* \[cite: 31, 46, 47\] | https://doi.org/10.1126/science.1191181 | **VERIFIED** | Peer-reviewed study (*Visualizing Uncertainty About the Future*, Science 333: 1393–1400). Analyzes cognitive responses to uncertainty visualizations across diverse domains. | Avoid isolated percentages; use frequency framing (such as 1 in N occurrences) and interactive controls that allow users to inspect scenarios. |
| **van der Bles et al. (2019)** *Royal Society Open Science* \[cite: 34\] | https://doi.org/10.1098/rsos.181870 | **VERIFIED** | Peer-reviewed review (*Communicating uncertainty about facts, numbers and science*, R. Soc. Open Sci. 6: 181870). Defines direct vs. indirect uncertainty. | Present direct statistical ranges transparently; use secondary UI indicators to convey the underlying evidentiary quality of the model data. |
| **Hullman et al. (2015)** *PLOS ONE* \[cite: 4, 37, 48\] | https://doi.org/10.1371/journal.pone.0142444 | **VERIFIED** | Peer-reviewed experimental study (*Hypothetical Outcome Plots Outperform Error Bars...*, PLOS ONE 10: e0142444). Identifies severe cognitive errors induced by static error bars. | Avoid standalone error bars for probability comparisons; use discrete outcome encodings, quantile bins, or simulated draws to support counting. |
| **The Open Group & FAIR Institute** FAIR Institute2 | https://www.fairinstitute.org/blog/announcing-loss-exceedance-charts-in-the-fair-u-training-app | **VERIFIED** | Active technical training resources detailing Open FAIR standards (O-RT and O-RA), Monte Carlo risk modeling, and Loss Exceedance Curve specifications. | Plot loss currency on the horizontal axis and exceedance probability on the vertical axis, adding an explicit visual overlay for organizational risk tolerance. |

## **Prioritized Implementation Strategy for Rapid Front-End Delivery**

When building an executive risk dashboard under tight development timelines, avoiding front-end rendering conflicts is essential. Attempting to build custom D3 SVG rendering pipelines or complex DOM transition layers introduces layout friction and state synchronization bugs9. Development should center on **Recharts v3.10.1**5, with all statistical transformations executed upstream in a modular, headless JavaScript utility.

| Priority Level | Visualization Feature | Recommended Recharts Components | Technical Visual Encodings | Strategic Impact on Reviewers |
| :---- | :---- | :---- | :---- | :---- |
| **Priority 1: Core Foundation** | **Interactive Loss Exceedance Curve (LEC)** | \<ResponsiveContainer\>, \<AreaChart\>, \<Area\>, \<ReferenceLine\>, \<Tooltip\> \[cite: 6, 8\] | Smooth monotone curve; dynamic SVG linear gradient fill; vertical dashed reference line for 95% VaR; horizontal line for risk tolerance6 | Establishes immediate credibility by adhering to enterprise actuarial and Open FAIR governance standards2. |
| **Priority 2: Distribution Context** | **Monte Carlo Outcome Density Histogram** | \<ResponsiveContainer\>, \<ComposedChart\>, \<Bar\>, \<Line\>, \<ReferenceArea\> \[cite: 5, 6\] | Binned bar frequencies; overlaid continuous probability spline; red-tinted reference area shading the extreme 5% tail5 | Grounds abstract curves in concrete simulation runs, avoiding within-the-bar bias through frequency framing3. |
| **Priority 3: Actionable Insights** | **Prioritized Scenario Range Breakdown** | \<ResponsiveContainer\>, \<BarChart layout="vertical"\>, \<Bar\>, \<ErrorBar\> \[cite: 5, 6\] | Horizontal bars sorted by median financial loss; range markers showing P10 to P90 intervals; status badges for data quality1 | Delivers an actionable executive view that directly prioritizes security mitigation budgets by financial ROI1. |

### **Priority 1: Interactive Loss Exceedance Curve**

The Loss Exceedance Curve serves as the primary visual anchor of the dashboard. Using an AreaChart, the horizontal axis maps monetary loss values from zero to the maximum simulated exposure, formatted with currency suffixes (e.g., "$5M", "$10M")8. The vertical axis displays the exceedance probability from 0% to 100%43.  
The visual presentation uses an SVG linear gradient fill beneath the curve, transitioning from subtle teal or emerald green in the low-loss zone to amber and warning red in the extreme tail. Two reference markers ground the visualization in executive decision parameters: a vertical red dashed line indicating the 95th percentile Value at Risk (![][image9]), and a horizontal orange line indicating the board-approved risk tolerance threshold2.  
The interactive tooltip should be customized to follow natural frequency conventions, translating raw coordinates into plain-language summaries (for example: *"There is a 5.0% probability (1-in-20-year likelihood) that annual cyber losses will exceed $18.4M"*)3.

### **Priority 2: Monte Carlo Outcome Density Histogram**

To provide distribution context, the secondary view uses a ComposedChart that renders discrete simulation outcome bins alongside a smoothed probability density estimate5. Raw Monte Carlo iterations (e.g., 10,000 simulated runs) are partitioned into equal-width loss bins, plotted as subtle grey-blue bars using the \<Bar /\> component1.  
A smoothed probability line is overlaid using the \<Line type="basis" /\> component to highlight the distribution profile5. A \<ReferenceArea /\> shades the region beyond the 95th percentile in translucent light red, visually highlighting the extreme loss tail6. This design leverages the cognitive strengths identified by Hullman et al., helping non-expert viewers connect continuous probability curves to concrete outcome samples4.

### **Priority 3: Prioritized Scenario Range Breakdown**

The tertiary component provides actionable context by displaying specific threat scenarios using a horizontal BarChart (layout="vertical")5. Scenarios (such as ransomware extortion, cloud outages, or wire fraud) are arranged vertically and sorted by expected monetary loss1.  
Horizontal bars represent the 50th percentile (median) loss, while range brackets extend from the 10th to the 90th percentile to convey operational variance without overwhelming the viewer1. Adjacent to each scenario label, an evidentiary confidence tag indicates the quality of the underlying data (e.g., "High Confidence / Continuous Telemetry" versus "Low Confidence / SME Estimate"), directly operationalizing the direct versus indirect uncertainty framework established by van der Bles et al34.

### **Headless Data Pre-Processing Architecture**

To ensure high rendering performance in Recharts, raw Monte Carlo simulation arrays should be processed upstream prior to component rendering. A lightweight mathematical utility module should sort the raw loss array, extract key percentile indices (![][image10], ![][image11], ![][image12], ![][image13]), and generate a 100-point uniform step array representing the Complementary Cumulative Distribution Function.  
This pre-processing calculates both the numerical exceedance percentage and the natural frequency ratio string for each coordinate point, offloading mathematical calculation from React's render loop and allowing Recharts to operate purely as an efficient SVG presentation layer5.

#### **Works cited**

> 1. What Is Cyber Risk? The FAIR Definition \- Safe Security, [https://safe.security/resources/blog/what-is-cyber-risk-the-fair-definition/](https://safe.security/resources/blog/what-is-cyber-risk-the-fair-definition/)  
> 2. Cyber Risk Quantification Methodologies Explained \- Kovrr, [https://www.kovrr.com/blog-post/cyber-risk-quantification-methodologies-a-practical-comparison](https://www.kovrr.com/blog-post/cyber-risk-quantification-methodologies-a-practical-comparison)  
> 3. Visualizing Uncertainty About the Future \- ResearchGate, [https://www.researchgate.net/publication/51635479\_Visualizing\_Uncertainty\_About\_the\_Future](https://www.researchgate.net/publication/51635479_Visualizing_Uncertainty_About_the_Future)  
> 4. Hypothetical Outcome Plots Outperform Error Bars and Violin ... \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4646698/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4646698/)  
> 5. recharts \- NPM, [https://www.npmjs.com/package/recharts](https://www.npmjs.com/package/recharts)  
> 6. 3.0 migration guide · recharts/recharts Wiki \- GitHub, [https://github.com/recharts/recharts/wiki/3.0-migration-guide](https://github.com/recharts/recharts/wiki/3.0-migration-guide)  
> 7. Releases · recharts/recharts \- GitHub, [https://github.com/recharts/recharts/releases](https://github.com/recharts/recharts/releases)  
> 8. [https://recharts.github.io/](https://recharts.github.io/)  
> 9. What is D3? | D3 by Observable \- D3.js, [https://d3js.org/what-is-d3](https://d3js.org/what-is-d3)  
> 10. D3.js, [https://d3js.org/](https://d3js.org/)  
> 11. D3.js \- Wikipedia, [https://en.wikipedia.org/wiki/D3.js](https://en.wikipedia.org/wiki/D3.js)  
> 12. d3 @ 7.9.0 \- Libraries \- cdnjs, [https://cdnjs.com/libraries/d3](https://cdnjs.com/libraries/d3)  
> 13. d3-axis | D3 by Observable \- D3.js, [https://d3js.org/d3-axis](https://d3js.org/d3-axis)  
> 14. D3.js 7 documentation \- DevDocs, [https://devdocs.io/d3/](https://devdocs.io/d3/)  
> 15. Getting started | D3 by Observable \- D3.js, [https://d3js.org/getting-started](https://d3js.org/getting-started)  
> 16. What is Cyber Risk Quantification? \- Safe Security, [https://safe.security/resources/insights/what-is-cyber-risk-quantification/](https://safe.security/resources/insights/what-is-cyber-risk-quantification/)  
> 17. RiskLens, a SAFE Company, Named a Leader in a Cyber Risk, [https://safe.security/resources/press-release/risklens-leader-in-crq-forrester-wave/](https://safe.security/resources/press-release/risklens-leader-in-crq-forrester-wave/)  
> 18. Safe Security Acquires RiskLens, [https://safe.security/resources/datasheets/safe-security-acquires-risklens-to-become-the-undisputed-crqm-leader/](https://safe.security/resources/datasheets/safe-security-acquires-risklens-to-become-the-undisputed-crqm-leader/)  
> 19. FAIR Beginner's Guide: What Do the Numbers Mean?, [https://www.fairinstitute.org/blog/fair-beginners-guide-what-do-the-numbers-mean](https://www.fairinstitute.org/blog/fair-beginners-guide-what-do-the-numbers-mean)  
> 20. How to Prioritize Your Cybersecurity Program Based on Risk, [https://safe.security/resources/blog/how-to-prioritize-your-cybersecurity-program-based-on-risk/](https://safe.security/resources/blog/how-to-prioritize-your-cybersecurity-program-based-on-risk/)  
> 21. Cyber Risk Quantification (CRQ) Platform \- Kovrr, [https://www.kovrr.com/cyber-risk-quantification](https://www.kovrr.com/cyber-risk-quantification)  
> 22. How to Choose the Right Cyber Risk Quantification Model \- Kovrr, [https://www.kovrr.com/videos/how-to-choose-the-right-cyber-risk-quantification-model](https://www.kovrr.com/videos/how-to-choose-the-right-cyber-risk-quantification-model)  
> 23. Balbix's Role-Based Dashboards: Reduce Risk at High Velocity, [https://securityboulevard.com/2022/11/balbixs-role-based-dashboards-reduce-risk-at-high-velocity/](https://securityboulevard.com/2022/11/balbixs-role-based-dashboards-reduce-risk-at-high-velocity/)  
> 24. AWS Marketplace: Balbix Exposure Management \- Amazon.com, [https://aws.amazon.com/marketplace/pp/prodview-omztykcfoi6wi](https://aws.amazon.com/marketplace/pp/prodview-omztykcfoi6wi)  
> 25. Balbix Breach Control \- Enterprise Grade Cybersecurity Products, [https://www.cherubavailabilityservices.com/cybersecurity-products-for-the-enterprise/balbix-breach-control/](https://www.cherubavailabilityservices.com/cybersecurity-products-for-the-enterprise/balbix-breach-control/)  
> 26. Balbix Reviews 2026: Details, Pricing, & Features \- G2, [https://www.g2.com/products/balbix/reviews](https://www.g2.com/products/balbix/reviews)  
> 27. Cyber Risk Quantification (CRQ) | Axio Solutions, [https://axio.com/crq/](https://axio.com/crq/)  
> 28. Axio360 Product Brochure\_13ASeptember2023\_Final, [https://9001819.fs1.hubspotusercontent-na1.net/hubfs/9001819/Axio360%20Product%20Brochure\_13ASeptember2023\_Final.pdf](https://9001819.fs1.hubspotusercontent-na1.net/hubfs/9001819/Axio360%20Product%20Brochure_13ASeptember2023_Final.pdf)  
> 29. RiskLens \- F-Prime Capital, [https://www.fprimecapital.com/company/risklens/](https://www.fprimecapital.com/company/risklens/)  
> 30. On-Demand Cyber Risk Quantification Methodology \- Kovrr, [https://www.kovrr.com/videos/the-kovrr-methodology](https://www.kovrr.com/videos/the-kovrr-methodology)  
> 31. Visualizing Uncertainty About the Future, [https://www.sci.utah.edu/\~kpotter/Library/Papers/spiegelhalter:2011:VUAB/index.html](https://www.sci.utah.edu/~kpotter/Library/Papers/spiegelhalter:2011:VUAB/index.html)  
> 32. Uncertain About Uncertainty: How Qualitative Expressions of, [https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.579267/full](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.579267/full)  
> 33. Hypothetical Outcome Plots Outperform Error Bars and Violin Plots, [https://pubmed.ncbi.nlm.nih.gov/26571487/](https://pubmed.ncbi.nlm.nih.gov/26571487/)  
> 34. Communicating uncertainty about facts, numbers and science, [https://pubmed.ncbi.nlm.nih.gov/31218028/](https://pubmed.ncbi.nlm.nih.gov/31218028/)  
> 35. Communicating uncertainty about facts, numbers and science, [https://royalsocietypublishing.org/rsos/article/6/5/181870/95102/Communicating-uncertainty-about-facts-numbers-and](https://royalsocietypublishing.org/rsos/article/6/5/181870/95102/Communicating-uncertainty-about-facts-numbers-and)  
> 36. Effects of visualizing statistical information – an empirical study on, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4549558/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4549558/)  
> 37. Hypothetical Outcome Plots Outperform Error Bars and Violin Plots, [https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0142444](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0142444)  
> 38. References \- Fundamentals of Data Visualization, [https://clauswilke.com/dataviz/references.html](https://clauswilke.com/dataviz/references.html)  
> 39. Read "Environmental Decisions in the Face of Uncertainty" at NAP.edu, [https://www.nationalacademies.org/read/12568/chapter/8](https://www.nationalacademies.org/read/12568/chapter/8)  
> 40. (PDF) Communicating uncertainty about facts, numbers and science, [https://www.researchgate.net/publication/332934727\_Communicating\_uncertainty\_about\_facts\_numbers\_and\_science](https://www.researchgate.net/publication/332934727_Communicating_uncertainty_about_facts_numbers_and_science)  
> 41. The effects of communicating uncertainty on public trust in facts and, [https://www.pnas.org/doi/10.1073/pnas.1913678117](https://www.pnas.org/doi/10.1073/pnas.1913678117)  
> 42. Industry News 2021 The Elephant in the Risk Governance Room, [https://www.isaca.org/resources/news-and-trends/industry-news/2021/the-elephant-in-the-risk-governance-room](https://www.isaca.org/resources/news-and-trends/industry-news/2021/the-elephant-in-the-risk-governance-room)  
> 43. Announcing Loss Exceedance Charts in the FAIR-U Training App, [https://www.fairinstitute.org/blog/announcing-loss-exceedance-charts-in-the-fair-u-training-app](https://www.fairinstitute.org/blog/announcing-loss-exceedance-charts-in-the-fair-u-training-app)  
> 44. Your risk register is a color. Your board wants a number. \- Zania's AI, [https://zania.ai/blog/your-risk-register-is-a-color.-your-board-wants-a-number.](https://zania.ai/blog/your-risk-register-is-a-color.-your-board-wants-a-number.)  
> 45. Introducing FAIR-U Workbook for Learners, FAIR Risk Analysis, [https://www.fairinstitute.org/blog/introducing-fair-u-workbook-for-learners-fair-risk-analysis-training](https://www.fairinstitute.org/blog/introducing-fair-u-workbook-for-learners-fair-risk-analysis-training)  
> 46. Spiegelhalter, D., Pearson, M. and Short, I. (2011) Visualizing, [https://www.scirp.org/reference/referencespapers?referenceid=1417739](https://www.scirp.org/reference/referencespapers?referenceid=1417739)  
> 47. Visualizing uncertainty about the future. \- Open Research Online, [https://oro.open.ac.uk/29690/](https://oro.open.ac.uk/29690/)  
> 48. \[PDF\] Hypothetical Outcome Plots Outperform Error Bars and Violin, [https://www.semanticscholar.org/paper/Hypothetical-Outcome-Plots-Outperform-Error-Bars-of-Hullman-Resnick/0406c3b350227b7f59356b75f1d45e1825f6931d](https://www.semanticscholar.org/paper/Hypothetical-Outcome-Plots-Outperform-Error-Bars-of-Hullman-Resnick/0406c3b350227b7f59356b75f1d45e1825f6931d)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAZCAYAAACsGgdbAAACIUlEQVR4Xu2VP0iVURjGn8igaLBQCmlqyEzDRTBSKKmlJQdpcHMIcmlLag3CQQchaWoQDKK2WspoCHHQwEFpqcGGRBpqCIQkBavn4T2ne+7r/a4nJ4fvBz+++53znnPe7/y7QEnJ/uMGfeycrooATiR10RyO0ud0NfgJ1nfsY5xeoAdjgyLOwRL9E1Qnek85Qt/B6pfozerqQhpoH6w/9btJR8K7fEK36Aq9Yk3qMwlLYo2ednXiESxmr1ynX2iLKz9MX8HGbnZ1O7gI+1IFD7o68REWs1eKkhSaZY3b5Ss8WtI3sGA9Pa9hMbU4BhtczyKKkvyvmRS3YcE/XLmSG3Zl4gz9QOdhs6F2C7Q1DQoUJdkNa7ftygs5ANt7/qvuhzrPAP0FaxOJe9t/lJLUdnqKyulW3CI9m8RlcY3+Dk+hZHWic9ByP4ANfs/V1ZrJXvoTNpOa0Wwa6Xv6DHaFKNm5qohqmuhdukGXg7lJanU0s4p/kZRnoQF0FWnPKVk/YETLrXtOF3W8kBWbm6SI2+OzK9+V87CGD2FLrXdPB/0OW6706kiT1L9JpCjJGL/uyrNQQ9nvKwJpkjEZ7auvsHajqFz+muVb9BvtDGWReAbURpyib+nJfxF10OUt6wVfhv2laT++hG2NNjoDG7Sdzobf3rgdDtGxUHaHTtEJ1L5NdnCJ9vjCGqgzHZ70ItfMHU/ec1AfQ/QqLPGSkpKS/cBfojmIOB6PoSUAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAABkUlEQVR4Xu2UvytGURjHv0IRMiillKSUbCQpo8TAZCB/gEVGFoOUwSY/FkQMkjKxWWQi/4EsyqSskvLj+33POe997nnv24tBqfdTn27nx32ec+95zgHK/DE1tIU2mb46WmHaGKXb33COVvl3Amv0hT7SJzpFB+gprTfz0EUn6Dv9pFu+HVyh9/QS6Rdr6RVtNX0X9AOFc/M8wCUZiwc813ALCuzSXtMOzOKHSRQ0BN6jfWbsgI6YdkBzzvCDJAtesUyHzNg6Cn+X0KaPo3D/csRJqukJkiQx2mDNl7d0nlamZmQQkqzCbfgOXDEUSyL66Tl9Q5JQKmGqhAPxl2jSJpIkWqXOQtZq1deBJIZKuj01wxMnEXZP9O+PaINvN/qnpY3ewcWZjsZyZCWxDNJDJBu6YcYsWpTiZP7mUkmW4A5mQCWchd5XnJl4QOhaCJ8Z/rueupcm4U6yLWEl0fXRbPq64Rara0jVmSd8XimfkT7x+3QR7u66gQv8So+RvV+/osc/FXAYruw7UaR0y5T5x3wBEExlEBz4egAAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA/klEQVR4Xu2Tvw7BUBSHjwQhBiOJwWgySSQGm4HFwmCXeACDxdJXIBEiMVsMRgmL8A7EK4hVYvDnd3JPuVpEdZL0S7709v7ak9tzb4k83JKHEzjU7MGU5GlLNoINyWwkYBW24RmuYAVGtPwCj3AAazAp2VvCcCby2MQHlzCuzX1FDF6hIfcFuL6nP8DFNrAMdzD7HDvjRKrgnlwWYrhnXIx32G/JHBGFHbil5945JkBq6/napUfveFMcwQUMUsWYHKne8fkqytxX8DlqwTmpz2TMM8erG8vcR3g1fVIv1EkVNeFxBh4kD2mZjRKph3SbkgXh9EW+oMcv5uHxv9wAy3018v889rsAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAAaCAYAAAD43n+tAAACuUlEQVR4Xu2XS+gOURjGH7lErkWkLJCNKEkpUiJigcSCIlspC1lQkpQsrEhK2QtlY+ESFlMWLCSKrBQiSVKKQi7P0zun//nezpnb9y+b+dWvvjlzZuZc3ved+YCeHs8MOtE31jCGjvWNXdEAZvrGjuygN+h0f6IGTegy2l83gC6+Sp/Rx+XxMGgyutd8196UU/Q2hhjHOfqB7qHf6IrB0615Sff6xhYoSh7RI7Ada807ep9uob8xxMrABqDBDHMPsZt+RcfF/Uv3+8aOHKWLfWNHzsMWuxXj6C+6xp/owBRa0KmuPUYVLK58/jhGuajFboS2VJ29T+JOLVkIy8UUGvhB+pZ+p2foMvqUfoYN3qNwU043Qqsyl26iD+mi8liluyvaZe22R3mlBL9EJ2Fk5T/RlfQnbGe1wzEazxu0LAzH6GHfSFbDqtVr+rE8ngV78Ct6i84r+wa2Ih0iunZbdHwa1k9VVayDTdQTQthPNIvy5zrd4E9EnMRgfu2i06LjmBDGdRSwMKsrHq0npBV/AYv9HEvpBdi2KzwU+zlyO+TRZB6gungInVe/xhPSCunmVTfWLqp0bqQXUf1+yU1IBWE2RgamPirJgbVIv29CDk32J3Iof1ID8Lynd5CO85g5sPzSIsQUsOccokvK36GqjacnkE78XJFJEvKn7gLtyE36g65y5zy65xVYKMfsg5Xra7BCo53+AvsIfQ6bVAq9pNWvESF/ZA49SDmjPNKNQy5VocKQKjIKN+1gGLxeDwqp3EtV7VpIRUYlqlDb6XLYt1IcyzF6sMqrQiOsvHJpQdwpgXKlycTr0CIqv7VAlWgCBT2A/Je1cuU47GZhYJvpH9jbvg69t5QrXdEz9Q/gLhpUOO1QQXdiFP8ZOpR399D981+fX6lPof+KSu1ZWGi3YQJd7xt7enpGn3/GCX0IItmpvwAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAK0AAAAaCAYAAADFYNyOAAAGNUlEQVR4Xu2aeeilUxjHH6HIbqxRY5A9lC3rH7JvCTVkaeQP/lBEllFEUrb8oYks0ZDsS9mXmt+kEGqo0ZRSlywhKUUky/Ppec/vnt9zz7vfuVvvp77d955z3+We82zn3CvS0dHR0TG7bKzaVrWB7yiB87byjTPA5r5hBmHemL+p5WXVub6xAnzxp6S+sU8yh6pW+8YZ5HTVe6pdfUcbDlY9XFFbZ+c0AcNbLs0Nb5HqWml+/rDZV2xMmJBvMr2StaH7VSfNf3ohGOyXqiN8h3KQmIP6sT8167/HtT8p6etMEhepPlct9h1N4ULnqW5R/Sc22LwPul61JuvbIjunLhga18Hw2oBhHO4bx8R2qhtUf6v+FRu/MGaXqVaJjZmPMDgvhn67pB1wF7Fr4KC/q75XXSH9CT9F9YXYtdeKRbLNsr62cJ3jfOMQoDx4TszJhso5qm9lcJAh3HQT31GR/VU/+sYGPK2ak8mpBYl+GE9PzNhiMMgVYs+8UdSOAeJ8S6K2FOF85iT+LMZL1MIxNoza20AwuUtsjrZ0fcPiSNVvvrEN26g+EYsceRT1FcFk9sQieFuIbkQZbwjjgoiJ0abGhud7QfWVaseo/R/VCdH7IjYVu/5HYhEakbFSEboOnE9J8Y7qbBndQulyMeMdCtRReMExrv2O6Pjm6LgOZ4kNPJE8DyL4DgXvAww29V5PBiPbOPhBrDzw4wbBWYmWwch4zctmeTB2lB/nq96V9gaLkeL4H6qOcn1NIErHmc+/jzlM0g7eiAvFBic2BLy8akQoAsPHIXAMD9tfGOF3YrUb9dkl2TFKFe6hjkwZyqhhzHwkhVDD0x9/BzIa0blODbpO7DpE6HtdXx2451WqJ1R7u74m8B3PECt1mN9nVPuIzduvkl407yyWfVpnSS78uNjA4M0sAjBiUsfu0eeaEFLk12IP7HldtVTsGRARhWiyvepBSXvlmVIeuYFSIl5QVlFdeA4/CWGXBCP7IGoHxnOlayvjVrH7YAgHLOyqBMZ6p1i9ep/rawNbl29mx0TQP1R/iu2M/CzpOScCvy/NF/TzHCK2SiV6BUIa9lwgFll6qp9Ue6r2U30m5nFMSFzI85BzmXzKYBGxR/SeKES6ZWK5P5HZeyqE500Z9Chhywsnq5ONePY6z80Ysbf9tvRr26aExRaG642pLnupLpX+/IRMTVZl/k/OXlOkjLk2FMfckDonQORgsZMi9GFgwIPfqLpt/hN9iDoM9JwMGq2HCSXylu1QTIrRMlE9qVdbswip+tyMKyUGY8g2Fw6C2sKuAyn8JRlemUCmrurArY02pG+MlhvH7UWrvDCIQJq+WtJRsSjSenCem3xjgpCKqk7++uJRGSwNyqgaaRlLakIiLATnZ57q3C8PIjjrh0/FFmNtts4owwh4VRaYfK/WRhtWuAwGkaMqYRBPE0s5eVsmwWhTixWgjXOD88SeSnvqx4hQ017jOxxci8/VUVXCFiGOVgeMFmMvgoldJlb7xUZwpdgzNqlr8+BerF0wujpbX5zH3PALKQtiSss4Sx6oOjE7jsEe8myhMneLDcRa1W4Lu0ohEq+QdISNwbhSq30mkIKd2pUNdxYuYZJ2Ur2aHXuom34RqynHARNzndi41U2vLIowdozew3UxSK5LNPbRj3PeEEvtefV+WzDEKgvSlWLPyfyvyY5DllymekzSDsB6pfF+fdiX9ZGGWrVK+lkstsVBSlji+jwY918yGJXYUuMLv5aJZ8J5nhXz/OP7H50nRO63xM4fNakxy9vOyyPlcDi2v248ual+VCc7DhMCEHP/otguAqUMJdvzqkckf0uPPXtKy5FDacB2FIZLXUvaKiKUEqQPD56NQtTgBwXko0yAyWbSy+45yaQceBohM8S1KQGlrFbFEVuVBk3AAB+S/p9WMEZEexGkf4ytLRhrleg+yVD2jCtTjBOMdZ1vHAUPqI6O3mNERNuykE80/Vja12H8UYRUNM0cK/ZDQWqhsj5gnbBa+n+fLNNSO23oELjibdWpoc1/Kqmdmp47abBICf+HnXXIwmzdEWzaBq2xwOKK1X+VxV4Mq86yraJpA8Nd7htnEH4guVim1GA7Ojo6Ojo6Ojo6hsX/u+JYnbcCbgAAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAZCAYAAABKM8wfAAACaUlEQVR4Xu2WT0hUURTGv8gkqUhJirAgoo0YSAQJElTipoUtokWQ0MJtizYWuGgjrotoYyDiQgRxExFKuBhwI7RRUFoFFVFEuAkSNEK/jzPX9+a89+bNDJNQzA8+ZubcP+/cc885b4AG/x6t1GFvzOEAddAb94Pb1CvquB/IQQ5Po/p16KTGqRXqc/FzgnpZ1BB1Ym92KXJ2lTrn7JUySs2jBqfFTeoj1eHsF6iv1I6zK0LLqPFhMe5SP6nLfiCPMWqOanL2Y9QSkg5fpB44Wy2cot5TL/xAOY5Qi9RjP0DOU9+QdFhzlU714Dn1xRvLEZy66gfIIMzZrZjtKFWART8LdYB45/C/46gWfEDKonTQgrPUaeo6LLc2qVnqzN5MQwf77WxCef0IVqwtiBz5QV2htmEH1YHj6JmfYOtzCdHSxqEzqEtog/tI32QA6RHpol4j6irB4UnYPvo+g2SdtFPrSB4kFeXhBvXL2VX9f6hbzi6yHO5F6fxwc/eKv2/AIu8JQavIYW2mTXVCj+xT3ghLlzSHPQVYMPKKs2KH26h3KI1CQIUo+4izi6wIq7BOInqw5qgDBK4hvd+GHFa3KosWKxXUuLvdWD/sgaHVKe/ChmGd5xmiWwk5qzwOKL/THA5dKpdh2KZrSHYC77BeFIqeULP/gGTxFGBrHsIKMO7wIeoJ0os4q+tUjXLvTlF6RcdRHutQHqWDDiQHhf7J6cqzerDsb6gFP1BvFG29TtMiVg26ORWmAvDX+Q67+lrRYZX3b1FBh6gHeslMIrr+aumB1YLegvuGOsdT6pIfyKGZ6vPGBg3+R3YBAPlwbsh/6u0AAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,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>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAZCAYAAADXPsWXAAAAwUlEQVR4XmNgGAXYgBoQzwTiWUh4IYoKBgYWIK6DysGwJ4oKKFgDxP+B+AAQ86BKgYEZEFuhC6KDCAaIIV+B2BhNTh6IL6KJYQWKQPyEAWJQA5I4PxDvBuIyJDGcgBGI5zNADDkBFWNlQIQBiE0UEAfi6wwQg4KBeCsDxCUkAZBrpjBADDnPAAkLsoAbEP8DYnN0CVJANAPEJdzoEsQCQSA+zQAxhGwASh+gdPIcXYJYAIrCYgaIK46hyY2CUTA4AABbgSIUVzvAdwAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEMAAAAZCAYAAABq35PiAAADV0lEQVR4Xu2YS6hNURzGP6G85U0MKAZExIikmyQGJI8IYyRJCQPSNZBk5JlQojxCJp4DdS8mYmBCJsojBhIyoJDH/9d/r3vWXnffc+9B7lH7q6+791prr8e3/q9zpRIlSpSoDUuNxxIeyY2QVkZ9cLuxd25EMYYa7xpfZryn/DzLjP1bRtcBxssF+Wn8YdxpnJ8b4WO+Gj8adxgbjN3iAW2gp3yuVcbHxjvytQKfyufdYuyefVMXOCcX5JqxR9IH7huHpY014FTGFGvl634yTkv6Og0r5Jv6YJyY9IFDxi5pYw1oS4wF8nUhz3WBkcbn8k1tyHdpsHFm0haAeWMxI4xdk74YbYkRLOOLcXrS12ng1rl9NkagizFPxYFuvfG98bw8IGJVy1VsQUViMOct+Zqs3ZE49M/A5hCCzQWMMT6M3mNcN741Ts7esZ5vxhMtIypAiGeqZBLeGbtaxeLVBRrlYoRgSSy50tJbHXONn9XaAkCRZQSr2Jy0B/STC7dR1VP5BOOBjDFmy60aF+Yv7zWB4Im58zFme0EuSBGIETOMV+UiNMnTc3poUCTGQrkYr+QWGAMrJbOxBq7Hc5GrLjHeMA40jjLOifq2qRKcEX541NchUBvclKfaKXIXSTcacFG+EEUat0hqJEVeUmv/LxIjjMdd0gDNBdzOnvtmz0WXgpAE4QD2zhkAMW2TcbT+wBUpklhkv6qnVIQ4qUrBFA7XbByivCDVxGAe1gxgvTMZAfMgcFEs4ts4Jb+TF4lgnf5C7cJmWOSBcUDSFyMVA3PFTSjBMddQvOHvxB0Y+z7l+iP5POFGL8sP0Ky8eDzTluKN8pYRi0Nlu8s4SJ4Y2opN7YJDNaaNCfbJx+FKbBYBtso3RJYhcL3I3mPSRh8gqDH2u3GP8bT8AprVMTFYj3hAzBgn30+IG71UqX12G5/oN6voxfJiqz1w+xyMWw4g0NXyW4M5GuSugnVgPRwwFYMgmgIrniWPW2tUcRPWb1DlDATTuir5awFpEkFAH7lVpKkTTDKOjd6Du4V4dDRrR4w4nvxX4GYPG6cazxr3Zm0c5rX81zM4KHcvrKpJ+WC/SJ4AjstjBqn3vwUH418A1fycmIBAFHxFdQjBk/5qv5tKlChRomb8AoGBv6t1HwJkAAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAZCAYAAADNAiUZAAABUklEQVR4Xu2Uq0tEQRTGP7EoiuCjWmwmBRWL0aBBg4KGBcvWhW37H1gNYvLRDTZB6ySDSQQx2MRHEAUFLeLjO8yddc7Ru4h3ktwf/GDPnHvvB2dmFij578zSTbpDL+lJ9lvWxDrtbz6dmHW6bRfJDH2nF3TQ9ArRTR2tmHVhjD7TD/ipJGOI3tIR2yAL8IGvdMr0CjEP/+Fes95GN7LeMRLubRitfDimnZ7TRyQeqxBGK6FyesUr+kYbtOfr0XSE0Z7ZRg4rtCOqZQsm4U+/+CtW4UP3bMNQpUfwWyFbElikh7QvU+qWhNG+0AnTy8NBh15Dv3uDn29Bk3i0A6aXh4MOlTssdzmu56L6G1vwoQfQH2qFQ8HQv+CgQ5+gQx/odFQnwUGH3kHf43s6HNVJcNCh+7Rm6s6oLsQa/B+HnAE5obu0i47TU7pEl+loeKGkJDmf52lGqizFLAUAAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAZCAYAAADNAiUZAAABe0lEQVR4Xu2UvytGURjHH2FQUn4MhIHNRCGLJBkYSBSDwWpQBmE2+AdkkB+L2aAUi8Eok5QMNvkxiKJY5Mf323POvfd96O3lnkn3U5/Oe57n3Pu8PeecK5Lx3xmE63ALXsFT95sxOguro9WBWYGbNggG4Ae8hI0ml4pyeAQnTZy0wxf4KdqVYDTDO9hqE2BUtOAb7Da5VAyLvrjSxIvgqsudSMC99a3li5MUwwv4JIHbSnxrWZSnl17Dd7gAK+Kl4fCtPbcJQ5/oSa5zI+eEW9AlevppQSyLFt2xCcOi6Dp6CGtdfAwewCon53nxrX2FnSZnmRa9PpYbyX32Vn6+BRHJ1taYnIVFp+A27BFtK+EdTv4ZzocS829siBbdFz3F+ZiHS6LX5hjOufivixZKKeyVuBvcX1/s2Y2eR9ifmP8Z/ylcc3MWfYAt8F5y77GPp6YJ7sJ6WCJ60vdgmRtn4qVRPAgjop9EngPuaYOLd8AzOA4nYJuLZ2SE5ws3BU58HObtPQAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAZCAYAAADNAiUZAAABeUlEQVR4Xu2UTStGQRTHj9goKS9LNlJ6lChkIysLFiwoFtYoKTvfQPZYefkGFkphR7KyelKysJOXJIpiIy//fzPnufeeLnm6s9L91a87c848M/c5M3NFcv47w3AdbsErWPRtxugCbCiNDswK3LRBMAQ/4SVsNrlM1MAjOGXipBu+wi9xVQlGC7yDnTYBxsQt+A77TS4To+ImrjPxCrjmc6cScG+1tJw4TiW8gM8SuKxES8tFeXrpNfyAi7A2GhoOLe25TaTQLu6U86lwC/p8nP6JJXGLbtuEYRzuwyZ4AgdNvN7L/q9oad9gr8nFGRH3YnwSnuhHWIA3kvztraTfghLx0jaaXBy7KO+zXiHeYd5lhX0dl8qGuMn2xJ3in2iD93DW93VLOHnZi5YDD8wAnIHTEpX3RZKLPkm035npgK2+zX96AKvhgyTvsb5MZvQDsiPuq3Qs7jyQXTjv29rny2SmCq7CZXgI58SVm/TAMzgBJ2GXj+fkhOcbrglQpWxPdpwAAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAZCAYAAADNAiUZAAABhElEQVR4Xu2UPShHURjGH7EoKTEQFilRMsgmSQYGEjaDyUcWgzAbZMcgH4vZoBQ2kslkkcEmJYPBwCIfz9N7jnud/P/oXovur37de9/33HPufe97LpDx3+ml63SLXtNzd66YnKblH6NTZpluhkHSQ1/pFa0Ncokoocd0JIiLVvpI32BVSY06ektbwgQZhC34TNuDXCL6YROXBfECuupyZ0jx2/rSauI4hfSSPiDlsgpfWi2q7pU39IXO0dJoaHr40l6EiS9ognW5jp4uWIdXOXX9LYuwRXfCRMAQPaA19JR2u/g87H5vpYvnxJf2ibYFuTh9sAl1FOroe9pIJ2Hb6sfES1sR5OKEi2o/+y2kRUfpBt2GdXxeNFCT7cO6OBcN9I5OuGv/SfQQs3SBFsO21Iwbkwp6gw46TscQlbcTn6ukv9evyp2PZlrvzvWmh7C30yJrfhCih0mM/4Hswkp4AusHoVi1Oy+ie7CHSYwmW6FL9IhOIWqYAdivchjWI9pSGRl/wztXn06ugS6TWgAAAABJRU5ErkJggg==>