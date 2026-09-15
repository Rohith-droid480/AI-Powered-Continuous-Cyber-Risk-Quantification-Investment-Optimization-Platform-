# **Technical Evaluation of Mathematical Optimization Frameworks and Formulations for Security Budget Allocation**

Enterprise cybersecurity resource allocation requires mapping complex control portfolios to constrained optimization models1. When an organization must select an optimal subset of defensive countermeasures to maximize cumulative risk reduction subject to a fixed fiscal ceiling, the decision space conforms fundamentally to the 0/1 Knapsack Problem (01-KP) and Mixed-Integer Linear Programming (MILP)1. Real-world operational environments rarely exhibit purely additive utility or independent actions; rather, security architectures are constrained by prerequisite technical dependencies, mutually exclusive solution candidates, and submodular diminishing marginal returns arising from overlapping defensive layers2.  
Selecting an appropriate mathematical modeling language and solver backend governs both algorithmic correctness and development velocity5. The following technical report provides verified documentation, rigorous mathematical formulations, implementation architectures, and a comparative evaluation of the Python optimization libraries PuLP and SciPy5.

## **Standard and Extended Knapsack Formulations for Security Portfolios**

### **Classical 0/1 Knapsack Formulation**

The standard 0/1 Knapsack Problem serves as the baseline discrete archetype for capital budgeting under a single resource constraint1. Formally established in combinatorial optimization literature by Martello and Toth, the model selects from ![][image1] discrete items to maximize total profit without exceeding knapsack capacity3:  
![][image2]  
![][image3]  
![][image4]  
In the security investment domain:

* The parameter ![][image5] denotes the quantified risk reduction metric or security utility delivered by control ![][image6]1.  
* The parameter ![][image7] represents the total financial cost (incorporating procurement, deployment, and operational maintenance) of control ![][image6]1.  
* The scalar ![][image8] denotes the total allocated security budget envelope1.  
* The decision variable ![][image9] indicates whether control ![][image6] is funded (![][image10]) or rejected (![][image11])3.

The continuous linear programming relaxation replaces the discrete domain with ![][image12]3. The linear relaxation is solvable in ![][image13] time by sorting controls according to non-increasing efficiency ratios ![][image14] and greedily filling the budget until reaching the split item3. Modern branch-and-cut solvers use this relaxation bound to prune branches during tree search8.

### **Modeling Prerequisite Dependencies**

Security controls frequently function within architectural hierarchies where advanced capabilities require foundational controls4. For example, automated threat containment requires endpoint agent deployment, and centralized log auditing requires a logging pipeline4.  
When control ![][image15] depends strictly on control ![][image16], the activation of ![][image15] is conditional on the activation of ![][image16]4. This condition is enforced via the linear inequality:  
![][image17]  
If control ![][image15] requires an entire set of prerequisites ![][image18], the relationship expands into a system of individual inequalities:  
![][image19]  
Conversely, if control ![][image15] requires at least one enabling control from a set of alternative foundational platforms ![][image20], the dependency is captured by:  
![][image21]

### **Modeling Mutual Exclusivity**

Enterprise security architectures frequently require selecting at most one solution from a set of competing options ![][image22] to avoid operational conflict, tool sprawl, or duplicated vendor licensing4:  
![][image23]  
If strategic governance mandates that exactly one option from set ![][image22] must be chosen, the relation tightens into a strict equality constraint:  
![][image24]

### **Formulations for Overlapping Controls and Diminishing Marginal Returns**

Deploying multiple controls that mitigate the same threat vector exhibits diminishing marginal returns; simple addition of independent risk reduction values overestimates the defensive posture2. This structural overlap can be modeled within linear frameworks using two exact mathematical formulations.

#### **The Set-Union Knapsack Formulation**

The Set-Union Knapsack Problem (SUKP) maps candidate controls to an underlying set of elementary threat vectors, attack tactics, or vulnerabilities ![][image25]2. Each threat component ![][image26] is assigned a monetary or operational risk severity weight ![][image27]2. Each candidate control ![][image6] covers a specific subset of threats ![][image28]2. By introducing continuous coverage variables ![][image29] representing whether threat ![][image30] has been mitigated, the objective function shifts from control-level benefits to the union of mitigated threats2:  
![][image31]  
![][image32]  
![][image33]  
![][image34]  
The linear linking constraint permits ![][image35] to reach ![][image36] if one or more controls covering threat ![][image30] are activated2. Because ![][image27] in a maximization objective, the solver drives ![][image35] to its upper bound2. The formulation remains strictly linear while preventing double counting when overlapping controls are funded2.

#### **Pairwise Redundancy Discount Linearization**

When risk reductions are assessed per control but exhibit explicit submodular penalties ![][image37] when both controls ![][image38] and ![][image6] are simultaneously deployed, the formulation translates to a Quadratic Knapsack Problem:  
![][image39]  
To maintain a Mixed-Integer Linear Program solvable by branch-and-cut engines, each bilinear product ![][image40] is replaced by an auxiliary continuous variable ![][image41]:  
![][image42]  
![][image43]  
![][image44]  
![][image33]  
Because each penalty term ![][image45] enters the objective with a negative coefficient, the maximization solver drives ![][image46] toward its lowest feasible value. When both ![][image47] and ![][image10], the inequality ![][image48] forces ![][image49], penalizing the objective by ![][image50]. If either control is unselected, the lower bound ![][image51] allows ![][image52], linearizing pairwise interactions without introducing integer variables.

## **Technical Source Verification and Documentation Reviews**

### **1\. COIN-OR PuLP Optimization Modeler**

* **Source Name:** PuLP Linear Programming Modeler (Official Repository and Technical Documentation)5  
* **Direct URL:** https://github.com/coin-or/pulp5 (Documentation: https://coin-or.github.io/pulp/5)  
* **Status:** VERIFIED5  
* **Content Summary:** PuLP is actively developed under the COIN-OR Foundation5. PyPI records indicate the current production stable release is version 3.3.2, with ongoing 4.0.0 alpha iterations (up to 4.0.0a12)5. PuLP requires Python 3.10 or higher and incorporates a Rust-based extension module (pulp.\_rustcore) for model generation performance5. The library provides symbolic algebraic modeling, allowing variables and constraints to be added to an LpProblem instance via Python operators5.

PuLP connects to multiple backend solvers, including COIN-OR CBC, HiGHS, GLPK, SCIP, CPLEX, and Gurobi5. The default solver interface for CBC is COIN\_CMD5. To provide bundled solver binaries without requiring manual build tools, the maintainers distribute a packaged wheel via pip install pulp\[cbc\]5.  
The following verified syntax illustrates binary variable generation, constraint definition, and model execution in PuLP:

Python  
import pulp

\# Initialize model container with optimization sense  
prob \= pulp.LpProblem("SecurityBudgetModel", pulp.LpMaximize)

\# Declare binary decision variables  
x1 \= pulp.LpVariable("Firewall", cat="Binary")  
x2 \= pulp.LpVariable("EDR", cat=pulp.LpBinary)

\# Add linear objective function via overloaded addition  
prob \+= 40 \* x1 \+ 70 \* x2, "TotalRiskReduction"

\# Add linear constraints  
prob \+= 15 \* x1 \+ 30 \* x2 \<= 35, "BudgetCeiling"  
prob \+= x2 \<= x1, "EDR\_Requires\_Firewall"

\# Execute solve routine via CBC backend  
status \= prob.solve(pulp.PULP\_CBC\_CMD(msg=False))  
print(  
    f"Status: {pulp.LpStatus\[status\]} | Firewall: {pulp.value(x1)} | EDR:"  
    f" {pulp.value(x2)}"  
)

* **Relevance to Budget Optimization Module:** PuLP serves as a high-level modeling layer for security portfolios5. Its symbolic variable indexing permits dynamic constraint generation (such as dependency graphs and mutual exclusivity lists) directly from configuration files without requiring manual index bookkeeping5.

### **2\. SciPy Numerical Optimization Modules (milp and linprog)**

* **Source Name:** SciPy Reference Documentation: scipy.optimize.milp and scipy.optimize.linprog  
  \[cite: 6, 13\]  
* **Direct URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html  
  \[cite: 6\]  
* **Status:** VERIFIED6  
* **Content Summary:** The current stable release of SciPy is 1.18.114. SciPy provides mixed-integer linear programming through scipy.optimize.milp, introduced in version 1.9.0 as a wrapper around the HiGHS C++ optimization library6.

The function signature is defined as:

Python  
scipy.optimize.milp(  
    c, \*, integrality=None, bounds=None, constraints=None, options=None  
)

The solver handles problems in standard minimization form (![][image53])6. Maximization requires negating the objective vector (![][image54])6.  
The vector integrality dictates variable domains (![][image55] for continuous, ![][image56] for integer)6. Binary bounds are enforced by setting bounds=Bounds(lb=0, ub=1) alongside integrality=16. Constraints must be supplied as a LinearConstraint(A, b\_l, b\_u) object6. For one-sided upper-bound inequalities (![][image57]), the lower bound array ![][image58] must be filled with ![][image59] (-np.inf)6.  
The traditional linear programming interface, scipy.optimize.linprog, has the signature:

Python  
scipy.optimize.linprog(  
    c,  
    A\_ub=None,  
    b\_ub=None,  
    A\_eq=None,  
    b\_eq=None,  
    bounds=(0, None),  
    method="highs",  
    callback=None,  
    options=None,  
    x0=None,  
    integrality=None,  
)

When supplied with an integrality array, linprog routes internally to the HiGHS MILP solver13. However, milp remains the preferred API for integer models due to its direct constraint formulation6.  
The following verified syntax demonstrates portfolio optimization using scipy.optimize.milp:

Python  
import numpy as np  
from scipy.optimize import Bounds, LinearConstraint, milp

\# Variables: \[x\_Firewall, x\_EDR\]  
\# Objective: Maximize 40\*x1 \+ 70\*x2 \-\> Minimize \-40\*x1 \- 70\*x2  
c \= \-np.array(\[40.0, 70.0\])

\# Constraints:  
\# Row 0 (Budget):     15\*x1 \+ 30\*x2 \<= 35  
\# Row 1 (Dependency): \-1\*x1 \+  1\*x2 \<=  0  (x2 \<= x1)  
A \= np.array(\[\[15.0, 30.0\], \[-1.0, 1.0\]\])  
b\_u \= np.array(\[35.0, 0.0\])  
b\_l \= np.array(\[-np.inf, \-np.inf\])  
constraints \= LinearConstraint(A, b\_l, b\_u)

\# Variable bounds \[0, 1\] and binary integrality  
integrality \= np.array(\[1, 1\])  
bounds \= Bounds(lb=np.array(\[0.0, 0.0\]), ub=np.array(\[1.0, 1.0\]))

res \= milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)

if res.success:  
    print(f"Optimal Utility: {-res.fun} | Selections: {res.x}")

* **Relevance to Budget Optimization Module:** scipy.optimize.milp provides an integrated solver backend with zero external dependencies beyond NumPy and SciPy6. However, expressing architectural dependencies requires compiling explicit coefficient arrays (![][image15]) and bound vectors (![][image60]), which increases formulation overhead when control dependencies vary dynamically6.

### **3\. Academic Foundations of the Knapsack Problem**

* **Source Name:** *Knapsack Problems: Algorithms and Computer Implementations* (Silvano Martello and Paolo Toth, John Wiley & Sons)3  
* **Direct URL:** https://silvano333.github.io/17 (Academic Institutional Record: https://cris.unibo.it/handle/11585/89729218)  
* **Status:** VERIFIED17  
* **Content Summary:** Martello and Toth's foundational monograph formalizes algorithms and computational implementations for 0/1 knapsacks, subset-sum problems, and bounded/unbounded knapsacks10. The work details exact branch-and-bound strategies (such as the MT1 and MT2 algorithms) that derive upper bounds from the continuous LP relaxation using the Dantzig greedy split-item criterion8. These bounding principles, combined with modern cut generation, remain central to integer programming engines such as HiGHS and CBC5.  
* **Relevance to Budget Optimization Module:** Establishes the mathematical baseline for modeling single-constraint selection problems and provides the bounding theory needed to evaluate branch-and-bound convergence and relative optimality gaps during solver execution3.

### **4\. Real-World Architectural Extensions and Overlap Handling**

* **Source Name:** "An Iterated Two-Phase Local Search for the Set-Union Knapsack Problem" (Z. Wei and J.-K. Hao, *Future Generation Computer Systems*, Elsevier)2  
* **Direct URL:** https://leria-info.univ-angers.fr/\~jinkao.hao/papers/WeiHaoFGCS2019.pdf  
  \[cite: 2\]  
* **Status:** VERIFIED2  
* **Content Summary:** Wei and Hao investigate the Set-Union Knapsack Problem, where each selectable item consists of a subset of weighted elements2. When multiple items containing common elements are selected, the weight or benefit of each shared element is counted only once in the union2. The authors present mixed-integer programming formulations alongside heuristic local-search procedures for large-scale problem instances2.  
* **Relevance to Budget Optimization Module:** Provides the formal mathematical framework required to model overlapping control coverage and defense-in-depth within a linear program2. By treating elementary threat vectors as elements and candidate controls as item sets, the Set-Union formulation avoids heuristic approximations while maintaining exact global optimality guarantees2.

## **Architectural Comparison: PuLP versus SciPy milp**

Selecting an optimization framework requires evaluating mathematical expressiveness, setup overhead, and maintenance ergonomics5. The technical attributes of each library are summarized below:

| Technical Metric | PuLP (v3.3.2 Stable / v4.0.0 Pre-release) | SciPy milp (SciPy v1.18.1 / v1.9.0+) |
| :---- | :---- | :---- |
| **Modeling Paradigm** | Declarative Algebraic Modeling Language (Symbolic)5 | Matrix / Vector Array Numerical Representation6 |
| **Default Solver Backend** | COIN-OR CBC via COIN\_CMD (Modular to HiGHS, SCIP, etc.)5 | HiGHS C++ native library wrapper6 |
| **Variable Typing** | Native categorical declarations (cat="Binary", cat="Integer")5 | Flat 1-D array (0 \= continuous, 1 \= integer)6 |
| **Constraint Syntax** | Symbolic expressions (prob \+= x \+ y \<= 1\)5 | Explicit object instances: LinearConstraint(A, b\_l, b\_u) \[cite: 6\] |
| **Optimization Sense** | Explicitly selectable: LpMaximize or LpMinimize \[cite: 5\] | Strictly minimization (maximization requires sign inversion)6 |
| **Model Introspection** | Native file export (prob.writeLP("model.lp"))11 | Manual coordinate tracking across array slices6 |
| **Distribution Method** | PyPI package with extras: pip install pulp\[cbc\] \[cite: 5\] | Included in core SciPy distribution: pip install scipy \[cite: 14, 15\] |

### **Algebraic Modeling versus Matrix Abstraction**

PuLP operates as an Algebraic Modeling Language (AML) embedded within Python5. It exposes symbolic variables, linear expressions, and relational constraints as native objects5. Engineers can define variable dictionaries indexed by descriptive string identifiers and express real-world logic directly (for example, prob \+= x\["EDR"\] \<= x\["SIEM"\])5.  
In contrast, SciPy's milp requires low-level numerical arrays6. Every control, auxiliary coverage indicator, and penalty term must be assigned a fixed numeric column index in a global matrix ![][image15]6. Adding a prerequisite relationship (![][image61]) requires manually allocating a row in ![][image15], setting column ![][image15] to ![][image62] and column ![][image16] to ![][image63], and defining corresponding bounds in ![][image58] and ![][image64]6.  
When extending a security portfolio to include dozens of overlapping threat vectors or dynamic multi-stage dependencies, constructing matrices manually creates brittle, error-prone translation pipelines2.

### **Solver Execution and Toolchain Integration**

SciPy offers a direct installation footprint14. Because HiGHS is compiled directly into the binary wheels distributed on PyPI, calling milp invokes C++ routines in memory without disk I/O6.  
PuLP interacts with solvers primarily through file-based command-line wrappers or dynamic library bindings5. It constructs intermediate problem files (.lp or .mps), passes them to the solver executable, and reads back the solution vector5.  
While this design introduces minor file I/O latency (typically tens of milliseconds), that overhead is negligible for portfolio optimization problems spanning hundreds or thousands of controls3. Installing the solver is straightforward when using the official extra, pip install pulp\[cbc\], which provisions pre-compiled binaries across Windows, Linux, and macOS platforms5.

### **Model Debugging and Error Isolation**

Mathematical models frequently fail during initial development due to infeasibility, unintended unboundedness, or incorrect constraint combinations19. PuLP provides human-readable introspection through its file export method, prob.writeLP("debug.lp")11. Engineers can inspect the compiled equations directly in plain text to verify that names, coefficients, and bounds align with expected business logic19:  
Subject To Budget\_Limit: 15 Firewall \+ 30 EDR \<= 35 Prereq\_EDR\_requires\_Firewall: \- Firewall \+ EDR \<= 0 Binaries Firewall EDR End  
In SciPy, debugging an infeasible status code (status: 2\) requires manually inspecting array indices and reverse-mapping them back to the input parameters6. This lack of symbolic variable naming complicates root-cause analysis in team development environments6.

## **Technical Recommendation for Student Engineering Teams**

For a student team building a security budget allocation module under schedule constraints, **PuLP is the recommended framework.**  
Although scipy.optimize.milp eliminates external dependencies beyond the standard scientific Python stack, its low-level matrix API imposes significant cognitive overhead6. Students must write custom bookkeeping code to track array coordinates for each decision variable, prerequisite inequality, mutual exclusivity set, and Set-Union coverage indicator2. This index tracking often becomes a primary source of indexing bugs, sign inversion errors, and matrix alignment issues6.  
PuLP allows engineering teams to translate architectural specifications directly into readable Python expressions5. Team members can review model constraints during code reviews without deciphering sparse matrix mappings5.  
Furthermore, PuLP's ability to export human-readable .lp files provides an essential debugging aid for identifying infeasible or conflicting constraints11. The minimal setup requirement of running pip install pulp\[cbc\] is heavily outweighed by faster development cycles, cleaner code separation, and lower implementation risk5.

## **Reference Implementation: Security Investment Optimization Engine**

The production script below implements an enterprise security budget optimization engine in PuLP5. It integrates a hard budget ceiling, multi-control prerequisite dependencies, mutual exclusivity groupings, and the Set-Union formulation to handle overlapping threat vector coverage2.

Python  
"""Enterprise Security Budget Allocation Engine.

Formulation: 0/1 Mixed-Integer Linear Programming via Set-Union Knapsack.  
Requirements: pip install pulp\[cbc\]  
"""

from typing import Any, Dict, List, Set, Tuple  
import pulp

def solve\_security\_allocation(  
    budget: float,  
    controls: Dict\[str, Dict\[str, Any\]\],  
    threat\_landscape: Dict\[str, float\],  
    dependencies: List\[Tuple\[str, str\]\],  
    mutual\_exclusions: List\[List\[str\]\],  
) \-\> Dict\[str, Any\]:  
    """Solves the security portfolio allocation problem.

    :param budget: Total fiscal allocation limit.  
    :param controls: Dictionary of candidate security controls, specifying  
                     cost and covered threat identifiers.  
    :param threat\_landscape: Dictionary mapping threat identifiers to monetary  
                             or impact risk values.  
    :param dependencies: List of (control, prerequisite) pairs indicating  
                         control requires prerequisite to function.  
    :param mutual\_exclusions: List of control lists where at most one control  
                              may be funded per group.  
    :return: Formatted dictionary containing optimization metrics and selected  
    controls.  
    """  
    \# 1\. Instantiate the Mixed-Integer Linear Program  
    prob \= pulp.LpProblem("Security\_Portfolio\_Optimization", pulp.LpMaximize)

    \# 2\. Decision Variables  
    \# Binary variables: x\[j\] \= 1 if control j is funded, 0 otherwise  
    control\_keys \= list(controls.keys())  
    x \= {  
        j: pulp.LpVariable(f"x\_{j}", cat=pulp.LpBinary) for j in control\_keys  
    }

    \# Continuous coverage variables: y\[k\] in \[0, 1\] for each threat vector  
    threat\_keys \= list(threat\_landscape.keys())  
    y \= {  
        k: pulp.LpVariable(f"y\_{k}", lowBound=0.0, upBound=1.0, cat=pulp.LpContinuous)  
        for k in threat\_keys  
    }

    \# 3\. Objective Function: Maximize Union of Mitigated Risk Values  
    prob \+= (  
        pulp.lpSum(\[threat\_landscape\[k\] \* y\[k\] for k in threat\_keys\]),  
        "Total\_Risk\_Mitigated",  
    )

    \# 4\. Primary Budget Constraint  
    prob \+= (  
        pulp.lpSum(\[controls\[j\]\["cost"\] \* x\[j\] for j in control\_keys\])  
        \<= budget,  
        "Budget\_Limit",  
    )

    \# 5\. Set-Union Threat Coverage Constraints  
    \# Forces y\[k\] \<= sum(x\[j\]) across all controls that mitigate threat k  
    for k in threat\_keys:  
        covering\_controls \= \[  
            x\[j\]  
            for j in control\_keys  
            if k in controls\[j\].get("threats", set())  
        \]  
        if covering\_controls:  
            prob \+= y\[k\] \<= pulp.lpSum(covering\_controls), f"Cover\_Threat\_{k}"  
        else:  
            prob \+= y\[k\] \== 0.0, f"Uncoverable\_Threat\_{k}"

    \# 6\. Prerequisite (Precedence) Constraints  
    \# x\_dep \<= x\_prereq (dependent control requires prerequisite control)  
    for dep, prereq in dependencies:  
        if dep in x and prereq in x:  
            prob \+= x\[dep\] \<= x\[prereq\], f"Precedence\_{dep}\_requires\_{prereq}"

    \# 7\. Mutual Exclusivity Constraints (Special Ordered Sets of Type 1\)  
    \# sum(x\[j\]) \<= 1 for all controls within a conflicting group  
    for idx, group in enumerate(mutual\_exclusions):  
        active\_group \= \[x\[j\] for j in group if j in x\]  
        if len(active\_group) \> 1:  
            prob \+= (  
                pulp.lpSum(active\_group) \<= 1.0,  
                f"Mutual\_Exclusion\_Group\_{idx}",  
            )

    \# 8\. Solve Model via COIN-OR CBC Backend  
    solver \= pulp.PULP\_CBC\_CMD(msg=False)  
    solve\_status \= prob.solve(solver)

    status\_str \= pulp.LpStatus\[solve\_status\]  
    if status\_str \!= "Optimal":  
        return {  
            "status": status\_str,  
            "selected\_controls": \[\],  
            "allocated\_expenditure": 0.0,  
            "residual\_budget": budget,  
            "total\_risk\_mitigated": 0.0,  
            "mitigated\_threats": \[\],  
        }

    \# Extract Active Allocations  
    selected\_controls \= \[j for j in control\_keys if pulp.value(x\[j\]) \> 0.5\]  
    total\_cost \= sum(controls\[j\]\["cost"\] for j in selected\_controls)  
    mitigated\_threats \= \[k for k in threat\_keys if pulp.value(y\[k\]) \> 0.5\]  
    total\_risk \= sum(threat\_landscape\[k\] for k in mitigated\_threats)

    return {  
        "status": status\_str,  
        "selected\_controls": selected\_controls,  
        "allocated\_expenditure": total\_cost,  
        "residual\_budget": budget \- total\_cost,  
        "total\_risk\_mitigated": total\_risk,  
        "mitigated\_threats": mitigated\_threats,  
    }

if \_\_name\_\_ \== "\_\_main\_\_":  
    \# Available Budget  
    ORGANIZATIONAL\_BUDGET \= 130.0

    \# Identified Enterprise Threat Vectors with Assessed Risk Exposure Values  
    THREAT\_LANDSCAPE: Dict\[str, float\] \= {  
        "THREAT\_Ransomware": 100.0,  
        "THREAT\_Phishing": 60.0,  
        "THREAT\_DataExfiltration": 80.0,  
        "THREAT\_CredentialDumping": 45.0,  
        "THREAT\_LateralMovement": 55.0,  
    }

    \# Candidate Controls: Financial Costs and Threat Coverage Profiles  
    CONTROLS: Dict\[str, Dict\[str, Any\]\] \= {  
        "Basic\_Email\_Filter": {  
            "cost": 20.0,  
            "threats": {"THREAT\_Phishing"},  
        },  
        "Advanced\_AI\_Email\_Security": {  
            "cost": 45.0,  
            "threats": {"THREAT\_Phishing", "THREAT\_CredentialDumping"},  
        },  
        "Central\_SIEM": {  
            "cost": 30.0,  
            "threats": {"THREAT\_CredentialDumping"},  
        },  
        "EDR\_Platform": {  
            "cost": 50.0,  
            "threats": {"THREAT\_Ransomware", "THREAT\_LateralMovement"},  
        },  
        "Zero\_Trust\_Network\_Segmentation": {  
            "cost": 40.0,  
            "threats": {"THREAT\_LateralMovement", "THREAT\_DataExfiltration"},  
        },  
        "DLP\_Endpoint\_Suite": {  
            "cost": 35.0,  
            "threats": {"THREAT\_DataExfiltration"},  
        },  
    }

    \# Precedence Rules: EDR requires Central SIEM for alert routing  
    PREREQUISITES: List\[Tuple\[str, str\]\] \= \[("EDR\_Platform", "Central\_SIEM")\]

    \# Mutual Exclusivity: Select at most one email filtering tier  
    EXCLUSIONS: List\[List\[str\]\] \= \[  
        \["Basic\_Email\_Filter", "Advanced\_AI\_Email\_Security"\]  
    \]

    \# Run Optimization  
    allocation\_plan \= solve\_security\_allocation(  
        budget=ORGANIZATIONAL\_BUDGET,  
        controls=CONTROLS,  
        threat\_landscape=THREAT\_LANDSCAPE,  
        dependencies=PREREQUISITES,  
        mutual\_exclusions=EXCLUSIONS,  
    )

    print("=" \* 65)  
    print(f"Solver Status       : {allocation\_plan\['status'\]}")  
    print(  
        f"Budget Allocation   : ${allocation\_plan\['allocated\_expenditure'\]} /"  
        f" ${ORGANIZATIONAL\_BUDGET} (Surplus:"  
        f" ${allocation\_plan\['residual\_budget'\]})"  
    )  
    print(  
        f"Risk Value Reduced  : {allocation\_plan\['total\_risk\_mitigated'\]} units"  
    )  
    print(f"Selected Controls   : {allocation\_plan\['selected\_controls'\]}")  
    print(f"Mitigated Threats   : {allocation\_plan\['mitigated\_threats'\]}")  
    print("=" \* 65)

This reference implementation decouples the portfolio definition from the underlying mathematical solver2. The design allows engineering teams to add new threat vectors, adjust dependency graphs, or configure mutually exclusive product tiers without altering the core optimization model2.

#### **Works cited**

> 1. Exact algorithms for the 0–1 Time-Bomb Knapsack Problem, [https://repositori.upf.edu/server/api/core/bitstreams/27ffa338-3b26-4017-8f6c-63be8dc9fe30/content](https://repositori.upf.edu/server/api/core/bitstreams/27ffa338-3b26-4017-8f6c-63be8dc9fe30/content)  
> 2. Iterated two-phase local search for the Set-Union Knapsack Problem, [https://leria-info.univ-angers.fr/\~jinkao.hao/papers/WeiHaoFGCS2019.pdf](https://leria-info.univ-angers.fr/~jinkao.hao/papers/WeiHaoFGCS2019.pdf)  
> 3. An Algorithm for Large Zero-One Knapsack \- NYU Stern, [https://www.stern.nyu.edu/om/faculty/zemel/SCANNED%20PAPERS-SPR%202004/LargeZero-OneKnapsackProblems\_Balas-Zemel.pdf](https://www.stern.nyu.edu/om/faculty/zemel/SCANNED%20PAPERS-SPR%202004/LargeZero-OneKnapsackProblems_Balas-Zemel.pdf)  
> 4. Integer programming techniques 2: cutting planes, [https://ocw.mit.edu/courses/15-053-optimization-methods-in-management-science-spring-2013/ef77e2d86d8419f73494d2970ab76acf\_MIT15\_053S13\_lec13.pdf](https://ocw.mit.edu/courses/15-053-optimization-methods-in-management-science-spring-2013/ef77e2d86d8419f73494d2970ab76acf_MIT15_053S13_lec13.pdf)  
> 5. coin-or/pulp: A python Linear Programming API \- GitHub, [https://github.com/coin-or/pulp](https://github.com/coin-or/pulp)  
> 6. milp — SciPy v1.18.0 Manual, [https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)  
> 7. Knapsack problem: A case study of garden city radio (GCR), Kumasi, [https://academicjournals.org/journal/AJMCSR/article-full-text-pdf/84A238D39964](https://academicjournals.org/journal/AJMCSR/article-full-text-pdf/84A238D39964)  
> 8. Where are the hard knapsack problems?, [https://www.dcs.gla.ac.uk/\~pat/cpM/jchoco/knapsack/papers/hardInstances.pdf](https://www.dcs.gla.ac.uk/~pat/cpM/jchoco/knapsack/papers/hardInstances.pdf)  
> 9. Genetic Algorithm for a class of Knapsack Problems \- arXiv, [https://arxiv.org/pdf/1903.03494](https://arxiv.org/pdf/1903.03494)  
> 10. A Branch-and-Bound Algorithm for Hard Multiple Knapsack Problems, [https://metahack.org/Annals-of-OR-2011.pdf](https://metahack.org/Annals-of-OR-2011.pdf)  
> 11. [https://coin-or.github.io/pulp/](https://coin-or.github.io/pulp/)  
> 12. COIN-OR Foundation \- GitHub, [https://github.com/coin-or](https://github.com/coin-or)  
> 13. linprog(method='highs-ds') — SciPy v1.18.0 Manual, [https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs-ds.html](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs-ds.html)  
> 14. SciPy, [https://scipy.org/](https://scipy.org/)  
> 15. SciPy \- PyPI, [https://pypi.org/project/scipy/](https://pypi.org/project/scipy/)  
> 16. SciPy 1.9.0 Release Notes, [https://docs.scipy.org/doc/scipy/release/1.9.0-notes.html](https://docs.scipy.org/doc/scipy/release/1.9.0-notes.html)  
> 17. Knapsack Problems, [https://silvano333.github.io/](https://silvano333.github.io/)  
> 18. Knapsack problems — An overview of recent advances. Part II \- IRIS, [https://cris.unibo.it/handle/11585/897292](https://cris.unibo.it/handle/11585/897292)  
> 19. How to debug most errors during solving — PuLP 4.0.0a12, [https://coin-or.github.io/pulp/guides/how\_to\_debug.html](https://coin-or.github.io/pulp/guides/how_to_debug.html)  
> 20. From Excel to AMPL, [https://ampl.com/blog/from-excel-to-ampl/](https://ampl.com/blog/from-excel-to-ampl/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAaCAYAAACD+r1hAAAAyUlEQVR4Xu3RwQoBQRzH8b8QN4pIDuIFJO6uHHgC7+EpPIMbF0fOXkBKkZNyUA5KOSt8/zuza1oeYA/7q0/b/GZ3Z2ZXJE7UUkLSGef/dEE6OGGPGrq44I4H+t9bRXJYYoA3NpjZuQK2ONixF31aLfBCz5lr4CqhB/xoeUbV6YZiVp06XZAnVsjacQpz+V01iL5p7IzrYg5+RBkjZPxJLXRLRb8gEzEv0Y+hh285c9IWs8+E0zVxwxo7p/eiPycdLsWcp2KvcSKUD9jWISeibPg3AAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEUAAAAaCAYAAADhVZELAAACf0lEQVR4Xu2YT0gUURzHv5FioeAhKVOhqCiiSxAkiIVgl4g6ZEGHwGtBEHTIqxEdwksIUggiFiqK1MXqYAepo1F0EDwUZESXoCA6FVTfL7/Z9vmaGXf+QLg7H/iw+96b2Z35ze/93tsFCgoK1nLZ7ygAbvodG5U2ukg/RDhBr9P9dJOdEknVBEXoZg/TMbqFTtHjtIGO0kd0kj4vnRBBVQVF7IRlRVPwqrZoptO0nXbSjqBf7KPnHB967d7yof+HvfQznYE9XVm6uF3OcVFEBUUM0NPO+yhSZco2rJ2XfjsNOv88/Ug3e2NJiAvKID0RvL/m9PskDspR+o4u0QN0mL6AzVMFJy1n6BtYKmchKihb6QN6kLbSQ0F/GImConk5D0vB3/QbvUKfBu2T5UMToc9doMf8gRSEBaWeDtGXdIS++nt0OImCopuWc/QXyqnYjfAnrJvVMrgeSmVdiG4gTq0o6+EHRXXoPqywavWppC6lYpm+h1XyOFQjvvidIajofce/ewtXTdlTpRNi8IOi9m5YUDRF78EyJ3d+wrKlzh9IyVlYbcqDsKAIfb6CcYNeCvpyRfUjbklLigr2M7rDH0hBVFCUIcoUTenZoC83dOGaPi3+gMNV2BKrp6MLqwRd7BPYk8yCpolWGQVFr+4mrY/egWW4FgytQrlwhI4jfl+ip6OLWkSyjGqEBfIC3Y747/BRodfqotr0A1aH9Kq2tgxC0+cu/eSMdQVjmdDGqpJCtYeuorxCJeE2XYEVaU3Vkv3uQRsRLd0Kipu+Nc8t+hiV7S1qAk2dt7BNXc2jP3BU1C7S18j2W6hq6KFfYauA/uwpgC2hyo4sP/0LCqqQP+YgeD+hVhIXAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAAsklEQVR4XmNgGNqAFYiF0AXRgRgQnwPin+gS6EAdiF8C8XV0CbIADxALAzEjugQymADEF4D4IRBvB2J+VGkIAPkyhwFiki8Q/wfidBQVUBANpTmAeCsQfwViY4Q0JpAG4gdAfBqIBVGlUIENEP8G4vkMBDxUzoDHfTBAtLUuQPyPgQRrYSGAAmSB2AqImRkgwfIJiPVRVEDBawaEJCi1TAdiFhQVUBAMxLOAeBIDxNThDwBwKR3PC74dWAAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEUAAAAaCAYAAADhVZELAAACf0lEQVR4Xu2XS6hNURjH//KIyLPcZKBkokQSRhi4N0oMkBTllgEDGSh5ZSQDIq9cRYqMPGJCKMkIpZQBiQxIBkommHn8/31rOcuylnP2Prt0z9m/+nX3Xt/e++z77bW+/W2gpqamwXS6KR7sdubRrfHgYEX/yLt/eJKupKP9CRk6KiliJD1Me53nYUkYT5+42HO63Z+QoOOSInbBZoTUtmc93UlH0WPBuPb76FqnzjkX7Mtpv4/+Dwyn/bCnetY5ALuxpS7ejFxSptCLdIxT+ykqmSn6gVZuthkT6W16PQ4UJJcUvVU0A7TEJtCeIBZSOilD6Tr6in6kn+khlE+OEnuX7oFdux1ySVlOj9AhdLP7m6J0Uq7CErEMdvGb9AudHx5UAK33yyif1JBUUlRoX9IT9BE97sZTlErKRnoHVqA8K+iMYN+jOrAhHkzwgM6BrfOck5B/uiFxUhbRG3QHrNC2co1CjKOP6ZY4kGAsfUjPxIEEb+gH/N1bhGp2apk1I06KkrAbdq6usbBxaDXMpJ9QfpnkUHHVtasgTorQw5wLm80q5pPdeCVovX1F/nVWlqN0WzxYklRShJ9pa+ipYLxtNBUPwNZpyDV6GlYodYyeiJ78a1giW2E1fUZnx4GC7EUjKdr2aLZcgc0YbfejwvqitvkbLPNqo1/QxWj8gCq9WAWrFVPdfissgbXhs2D9RBH2w+rSD1ibILWtMf82WQC7J9UoxS7RES7WNr4jlLmbP0hvIR/Pobea3m7v6Xf60/kU1uANWjSb7uHP6dv1qKV+C/tSrXFo6aj4DosD3YYK7T56Adbg6fui61FBVTt9H+19HHYcSkzVjV1NTQfwCw45eA9Kwu31AAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEUAAAAaCAYAAADhVZELAAACi0lEQVR4Xu2XTahNURTH/woR+YhIkRIDZSJFKRNRFBLqGaEMGMiARESvZCLyOSJJMkEZYSKGlAETpaQkUSQpUx//f2tv57z19n73XOc+Pdm/+nXPPeueu89ee5217wUKhULFPLrdn/zfWUJ3+5NNWUhv0Nf0bfA5vUIvBXfSSfGCYUYTifeR8jxdTyfECzK0Ssp0upEepD/oMbql5mX6k36KF/wFxtGTdFVQC6QkTKFPQ+wF3RsvSNAqKRENroGUpDqj6EVYYqa52HCiRVJFSB1HttIDdDw9Uzuv96tRLaau0YLWF3ju7083QCtzl+7yAQxMik9YDq3qEfoQ1SOosteNLYd9ZydySZlFr9GJQb1P0bpS1Kk/wL7Is5R+od99IMN8WE+64ANdkkuK7lUVoIWcSmfWYnVaJ2Ut0pWwEtbcvtJ1LpZiNn1G+9CsGoYil5Q19BTs+7UB5MZpnZQTsKRoBWK5q7m9odvQudNH+ulx5G+0G1JJUaN9Sc/Rx/RsOJ+iVVK0JX8OeubQV7CENRngHuzx0XOeUxNrgk/KCnqH7oM12l4kPssG2KS11Xk0sH7DKP7AxVJo236Hwb8t6p6mo+MFQ+CTons5BGuut+iy6qO9R7uCJq1Xjx4bJaNpUu5jcF/6U3xSxGS6GFaNGmtGON9T1L1VIZr0JhcTi2A7j+J7XCzFTVgj7AWppAhViaplM9rvcEn0bGrCalpahYgGVZIUu4rmjVYlvp8+gu1EbTiMKik6jug+lXxVjI53oEf9JTZXTTrnN9hz2+2A+nwfbOdaQMcMiHbmKH0P+8vxMahjnYvNXr+d4n81xa7TsSE2otEfyCewydSTfRv/yAQKhUKhUCgURgK/AJ6MlVtZkzAaAAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF8AAAAaCAYAAADR2YAqAAADb0lEQVR4Xu2ZTahNURiGP6HI/38iXBORUEiEDBhQRIRSYsSAkcLIREYyoSQlIflJSYQMdFEGDJSIAYWMCCUM/L9P62zWWZ2zz9777LvPvaf91Nu9Z6197t7rXWt937f2NSspKemZjJbGSv3CjoIYKA0NG9udvtIu6ZN0QZpV3V0Yy6Vv0jtpg9Srurs9wfjfUv+ww4MVOcHcRDULu2tw2FhhgHRG+iWtCvraDrZ6p/QhaI8YLl2UXknXzF3HCs3CCGmf9F1aGfT5zDW3A06FHe1GZP7roB3YCVelh9Ioc2Fgi/RZmvf/soawms9LP82t6D8Wb/5s6at1Y/PXSy/NGXNcOixtktZZOmPizD9pLhwt9doa7ZQ4ou92ufnciG0WJQ1iJm15QNy9LHWEHRmIM5+JxQTM8MEUDExLIeZfl95KH6X70tnKZ6oJklszMJn7LZ/EB3Hm09ajzGe1L6j8PkZ6Ju2WZkgvzIWKZphubnLzYpB0z2qbT2hppfks2sT0lrZ6n6M/0sdc8lpstUssJmanJVvNR81VG5Rr9ZQkvFE27pC+mKtmqGpCSKytMB8mmYsaG82NCW9Tsc2SPSQzfMuSmUYS5BDyJkZ7/11dnyvmSj7KxylBX0Srwg4QXpeYWxwnLOXJly9j1I+wo0mobLLW2SH+gWZt0Ae1Ei7jYrF0pfncg1BNpZVqxXMDvjBSemrVMX6qtMz7nAW24ZGwsQnGmysGeNaQS+aM8ic7MpBJSUtS8/GJfNMZtMcSxfjJ0jFzM8cAmEneVbDF/dCyWVpobuBxDxMyR5ofNmYkrtqheHgg3ZWGVNoYB+GKnxE8O4bu8dpqMU56ZO7a7UGfT6Zqh4Fg8B3poLTa3Azels5ZdVLjzeEKc8mYOB3G1UY8kU5LM625t5Bx5gOrkIqNMRwwd+wnJPjhYKK55yHM1iPKE77CkBaRyXzgofzkgDGNkgUrnzCVBiojVtxNc2HDHxS7LimNzAfuRaW2xtxuqEde4TCz+VkggRGaWkES85NCdZcHhZk/zPJ76CzkZT47oiNszEhh5vMyjAloJSTw9+beWPLfrLS7kOunhY0ZIGRzRiGhU+ZSieUOht8wd3LjdNkdoObnv1jPpUVBX1FQAXGgIpclOe1n4pD02NwBhyqopECYVV66NaqCSkpKSmL4C6X81LwFn2qXAAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAaCAYAAAANIPQdAAABf0lEQVR4Xu2XvS8EQRjGX0FCIj7i4yhEokehVYlKIrlCIiE0Chp/iagUWomIEB2JhEalUZAL/4CgU1JIfDzPvbMyJjm7c2TvTOaX/HI7++7u3TMzO7snEolEIn/PIGx3d4ZCAa7DVzjj1P49ffACvsA3+CEBhkxog+fiGbJFtJcaK7TrDe+Qu/ABPsInuGS26bV1XD3hFbIDzsEGIwOfwV64JXqRaumBRTjr4Uj5zHQyh+RUXLbaXfASDosGHjO6jMI12OwWciRzSJdx+Cx6P/4ER/tU9ItqRdUhV+R30zNPvEJy1DjtmuAhfLdq3D9vtX2ZEr0ef0hWN8tnppM5ZDI9ed+tij5c702tHx7BCdMmXHXZvpWUC+fAELwSDbno1L7RCrfhsZFhb+C+aJDJryN1xKdFR/xOtINqgT2CrhU7nqtot/kkXHHTXgLYAXw8BA1X16RTgoTPUq7CQbMgGjQ4GOwEDsADpxYMG7AEd+CeUwsGvhTwn3inW4hE8uETT19Wv4whmV8AAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAaCAYAAAANIPQdAAABvElEQVR4Xu2WzysEYRjHH6GIQn6Xgxzk4MdBOTnJSSkHRZSLwsWf4ejCQclBSSI3aguHvbtI3FwINxfl6Mf3u8+7evc1b7OrbXZ3mk992nmfZ2Z2nnl/jUhCQkJC8WiEg8Y6JxcLGuA7PDa+wfqcMyqcWrgLB6zYGNyBNVasotmC325QNLbhBl04rjtgtaddDnAepsVf5JXoUA7kEL7AV9HxvWSO6Y11Xqnpho/iL/IetrkJ0gTnYJWRBV/CdtFxHnTDfOEfzsDZAhzKXBlMWJHM8ZwcOBSXrXYLvIZ9ogWPGF2G4broIhAl/yrSZRR+SPi+w96+EJ0jUVKUIlcl+AblQtjCkxbPi2evcdhxjzmFX1aO8QWrXSiTovfjA+TrduZKP3viL5Lbyx+yw5Pzbg1+wmeT64JncNy0CVddtrmKTVvxKGFPcar0WjEe81kDv3oY3IfnRhZ7J/qpxEImfs/UHp8S7fEn0RdUKnrgA1wx8pid4oWraKv5JVxxwz4CvPtRhPAlL8J52O/kigJX1+xLiSXcS7kKxxoOERYaO1hYSnSjPXFysWET3sIDeOTkYgM/Cjphs5tISIiGH5fMX2CZvFM6AAAAAElFTkSuQmCC>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF8AAAAaCAYAAADR2YAqAAAC70lEQVR4Xu2ZTchMURjHH6GIfH9uJBuhUBZKshBFko8UJQs2FpKi2CtLdnYkCylJKVEWGh+R2BDZUEh2KMWCfPx/zr1m5nln5r3n3tu8E+dX/96559y5c87/POc5z8xrlkgkEon/lSnSKmme70gUZpQ02jcOxyXptXRWuiZtbOutznhpjW8cYCZJB3xjDzB9sXRVmuv6eoIxj6SZ2TUP+iyt/HtHeZjEUeld9nrQwbhTFsZ70PV145n0Q/oq/bII8zH6nLTOtTekD9Ii114EPvy0dEia4PoGkYXSFemVNNb1xbBC+mIR5k+1EPW8sZXzFlZxs2vvReskdrm+Mky3EBw5E1te1wHPfiA9ltZaiVztiDafG99Yd/OPufZOMIml0nNpi1WfxBzpuvRRui8tkS5In6Qj1r4gZWB8mI3ppNaqz8uJNp+0Qnopa/4ya0ZPVdOBaOfQouqaLb2wkE85N15a2FW0l2WDhSC5aSFg6iTafMzjcC1rPuSRxCJUiSSes1ean13nk7ksjbFQLXU7tDGy6AFJXictspCkyrqINr+OtJOD8URUnkOrst/CGA77DgcLQ1ris2NgsRlrvgvKBk1OtPndDlwmw8S3u/Yi5Acv0VWleqAK+y6t9h01guEEzT3poVVLndHmEzVsa/+lqmHhQX5RYsC899I+C98likBFM8uCCeTm1hzP+bQ+e103dRQN0eYDh9wdaXJL2zdpZ8t1VcjVO3yjIx/8E2mB9NOa+R5z+Obty012xQwLpsWUxcOBgSd9Yw8YH4c5O3V5dl0Yqopb0m7phIXqoszqVwFjMfiudFvaaqESo42xTWve+odxFhaGRXub/R0JODNJ0V4NGxosHSE3U01g/jbX109YcNIOP/IBBhOF+XUnGDORzw5I9JkzFgqEqK3+L7DHwpYvok3Ze+okr9YoS4tw3IaOq5vYTYkekHIwn0VI9AlMv2Hh/xAxVUmiBjD8qXTR2kvkRB+gOqvyA1sikRgRfgOS35kfh6fxjwAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAAAaCAYAAAA38EtuAAAEg0lEQVR4Xu2YXahmYxTH//IR+f7IEDUzQilFDSZFuSDf0lDEpYuhXBEyV0dShJIoiSYX0qCooZFcDGqYUUpxI5pDPqJQQvm2ftZe3nXWPHufc955nU6n91f/ztnPs/fzPs961rPW2luaMmXKMId0Wqnsbzq8Nk6CI0zHm/atHQ3OMr1pWl07VhAY+VnTraZ9St9YPG760fSV6XPTn6ZHTYflmxIY+WPT+toxBhfKf/M3012lbzlwtOkd0+21YzEcZHrQdL98wOBi0w9yY56c2oM3TPdqMrt8gulG099anoaG8+XOMBbHmd6SG7TFdaa/TK/XDvmPrq2Ne8lyNvR+puc0Rj7aKl/YI+r3SgZ/UX5f5ir5cZ80y9nQcIzc2NhlwbAo4nErLARsAImAew9MbZtNJ8ZNBXacEBSbx1+uc1jqo8/QMcaxGk7SqzTyOJ65Vv2JmnEYL8MaY50tGHNWHuoWBBNiUY+p35uBSW/XXEMfaXrPdHB3ndkg7/vatE0eenbLw8xPpjNHtzaphmZul5o+lc8D4RxXdH3BUXJP43e+N+0yvWT6zPSR3BMzVBKc1J3yORNCt5i+lBcBD8jLuha/m86rjX1w9Im9l9SOwklyo+XQEW0tXpNvIsbimYfkyRZOMb2qYY+phibLU4lck9r4n7aoAHAGcggbABjoeXneucV0T9eWmZGXa5SxbM4O09ldH0bGNn2hkTmyOfOCJ1IxvG06tPRl8Bg8noG/SO3rTD+n6wweGx5fEyxesFhDc70pXQfPaLT513f/46FBbHSLNXIjMw8qnXqqGWfI0Ky9Fd72IMIBGsqgxG68hAlTxgXnmn5N15XTTN/Jx88wufkmmA2NQ1TDBxg/wtnp8k1lc2v/fPCewOnOzHbqi8MLNnQkuO0aNjTVCJP9UHOTxpBHQ9TDLCIgJr4rN8oQ2bDMrc/Q4bFsBut5WO6FJGjyAobf9t/dbeLk4RgZxq1envlF7Tk14cZWksiQFJjwOaV9yNBMbrN8stlT4hQQrzEG1UCreqiG5fqpdB3k0MEmvmK6TB6anjZdrvb4mVhHdjbKtshdrKUVi/nd22rjEBiSt77VqY3J3SCfwKmpPRMxHo+onCF/jc+x+ADTy/IxCUckrlZpSMJiETMaGelO+Txvki8c8f8fGiXDOC0kSIz8ZCeSYJ9XAhuIUTMXyDeR53i+9cpNWKynYBBKpG/lR+EJ032mT7o2jv8QM2r/2JXa0yujnfLufbVLvHguizYWTJXBvL7pxP+UfGFENuWO7pmqF9T+8hZ5anZu87/tu+UfyvgsUasV+qmsopJaMEySI0TmvlqekYe8ICAUbKyN8okRjlrHlknWiS8GviqiDHOdkdfOubalfY3cY1lbC8Zq5SjyUf2dAOeiYlky2NGxdnbCrJK/zHDcW1CWtmL8uGDktbXx/4ZEeVFtXGLY6K3yN8HWKz5h8ebaOCZ4+ge1cSkgDETi2ZuQMAkIVevlSRoP36J2aBsX8gSlYC4clhQMfLc8sa5U+ORA+OF7yJQpU6ZMWQH8A5Qf+VzXXq3FAAAAAElFTkSuQmCC>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD4AAAAeCAYAAAB0ba1yAAACFElEQVR4Xu2YzyulURjHn8moYTBEJMqQkoVMSYqUKYqUhezmDxgbFiyEjdI02U2iLEQ25MfCxqwsZCelKCVSQ1Y0Fv4AfL+d9+3e+/S+9F689zr3fuqzOM9zF/ec95zn/BBJkybZ+QLHYT28gd3wHnap32RGta3gK/wupqPn8DNskUhH2Z4XMzBW8gtu6aDt8KtuwxGdAL/hKPyoEzbQDk9hmU6AHvhHB20hA2broMOkmM7HRT78oIPvhHVYq4NPkQen4H+4B0/gt5hfJDecBblwBeao3JNcwl1Y7rQ5CNwW4oXFpS+gL6ET7sBeFfeFU5rFYNppc+TY+UNY4f4oCu6XAzoYEtWwIaC+FMFjeC3mq9NNMVuGF03wVgdD4gd8CKgvLARc11U6kaRkBdQXt+MFOvFCuN3o0X/O0BmGrVFtrvsjMRcAlwkx6/unmCJiBezQHVyFS/CfRKq7C2cGB2TR0Rq495XCEvG/0nE57Iv56ikFr3oXsFEnbCZ6mif6OMuHBh5NeRPrktiHCJ5DODNf7T+605x7aaLpF3PeqBRzDmmTyPKsgwsS8NjqRSH8K6bqn8Ga2HTouHfxDXnjOzc7egUPJPZdK1GwALPOeD1CcHrPwg6diBdeU/0qfdh8EvPkNOa0uaYHYbOY4ssdZ8jJWQk7XKyDYE28X2asZ1nMrEgZ2FnqtfatZg7OiPcbQpqU5xE7gWB50+iNPwAAAABJRU5ErkJggg==>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAbCAYAAACjkdXHAAAA50lEQVR4XmNgGNaAFYidgVgaXYIYEAPE/4HYF12CEBAD4isMEM1FaHIEQTMDRCMIl6PJEQQnoRikeSGaHF7gB8Q8DBAbQZoPQPkEgTAQ74OygxhI1AyybQKUDQplkOaHQCwJV4EDqDBAbFGA8k2B+BsQPwFiGagYVsACxLOAOANJzBiIv0IxiI0T2ALxTwZE9CBjkO0gV2AFINvmMkCSIzIQBOLTDBADotHk4OAMEGujCzJAQvgAA46EArLJCIjPM2BP/BIMkGgDaZ6JLKEPxJ+gEiAM8q8lkvxFJDkYnoQkPwpGAW4AAO2uNQEiybs+AAAAAElFTkSuQmCC>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAZCAYAAADXPsWXAAAA6ElEQVR4Xu2SwQpBQRSGj6QoNnZWCiVlS9lYWdjwDN5EFl7AguIBlBXJXnkTG6VkzQL/MXfGzOmOa2V1v/oWd/6/e+fMXKKYKNpwDY+W/DwPHMGKaUcwhhO5CLrwAW+wJTKHNNzBvgxAHV7hE/ZE5lCCJ1iTAejQjzvRxawMwJbULvh8UiIz6FF0UbuBd1j9VP3oUc6wYFmEQ7iEedP2oEfZi3UmQWqHK/oyCsNXy8Ww62U4u1D4ob/Ro/hK/HV+CR9uRmQG/i+4dIA5kfEoA1L/SNONXBakXjK11pKwDGdB1rCymJj/8wKOpzDUOmiw4wAAAABJRU5ErkJggg==>

[image17]: <data:image/png;base64,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>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIUAAAAaCAYAAACZ6p+qAAAD1ElEQVR4Xu2aS6hNURjH/0IReUQeeRSFlDLAQImJPAZkYECoW5KpyONOPJIJkjxLDGTgOTCQDOTuDESKlIGUukRCUkJ5+/6+vTr7fGc/zj1733vPuXv96p9rf/ucs9da//Wtb61zAI/H4+nL9BeNEY0XDTKxssK+GGEvloWBom+iT6LLooXV4dJyXfRD9F601sQaZqbolOiM6FUofhD/Tx0TLYEOSm/RT3RUtE802MQsk0TD7MU+zhDRBdFfG2iU0aJVop2iP6LdotWhNoo6oB/20L2gTmiig6iYy2pP5dZMxopeiCbagOEQdNassIESMA+aSWmQwlgu6hRNMNc5S09AjTHAxOLgur9J9E60DhWD0Xhc/5xGuRfUAe9/Gf5rYY1xT/Q7FJ+zjKaYI/oqGmoDjUJ33YZmCwuNcA3a2ZyxaTDFMwsUvdSkmSJKAG+KwkwxVfRWtMAGoJmjE9rZzBppcKnhzC2aMpmCfcwsGh1cTjJOyLQBL9wUKxGfCfiAO8LYcxOLIy7TFEGZTMGlmssha6Nt0Oz7RvRa9Es0vHJrFYWb4gDia4Z26DrNh8wq8kh3DYYzhTWtJUDrm+I4dPcUQLffnLAuQ7eJNod/W2aLPqMgU3BL+hG688hL0ZliGnSmcNZwa5xFgNY2BQ+hKC7jP0W3qsP/J2+SKcg40RfRLtFk5KjtuENgR3aa641wB13bVWTxAGoI7sHryVQBWtsUDg482xGdZMwAAXSZSIIZ5T60z26KpleH6+cs9AG4w8jLadF+5HBoDHT/XWhDswjQ+qZwuz1m7sWR6/NF35F8eEdDsAbhBMp1VjESeijFjkxLS/XCIugK9IS0yFPFWdD1NanIcgRofVO43R4VPTPaC20bWYTajDEFWoxm1V2ZbId+EKvbGSaWF7qV5mA6c8fnUV2t3JpJvbuPx9D2bEBttuLhHGMXUVtQE3dW8wHJaZefz/fgfUmzkXGb+qOwGGSc/RJn8q2onaR8Hj5XIFovOonaNuTefbhK1TXAidebkTRTuLXWtoWKZgy+lim5A8kdx4GgaZLiNBrfY4sNRHgCHcC5NhDC9+d78Ng+rj3noYMbzQQ0ALeq/NLrEuLNlNsUrUaaKboCD+nSBr2n4LLNuiGuPXy2uK/C3aFW0gGiN0WDLBMdthd7AdZIzAhF/iakaU3xCLW1Q5JuhK+ph6JMwSzBKr434Uw/IlpjAzlpWlN0J0uh38+0Qb9fSUqjSfD+pO1cT8KiscidGScKD6u4ZX9qYqWAv+/gr65YpPH41wM8E52D/jyhGUzv8Xg8Ho+nxPwDDL3b/ac/FSAAAAAASUVORK5CYII=>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABACAYAAACnZCtBAAAFA0lEQVR4Xu3dW6htUwAG4CEUuV8i5RYi8aCEkvKAkiJJUSSlKCFRJB5OygMnuZRrJCTEA+WWFzuUB4UHt0QdcglJCi9yGX9jzbPmmWftc9Ze++y9Lb6v/qw95uxYa73sv3GZuxQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD4/zhjONCTa/cMB1fJDjXX1Dxe82nNBzWP1jw8ykHjWwEAtm7HmrOHg3MihWgxuXbmcHCVbFdzcs2bNX/XXFhz/ii31/xZc9XGuwEAFrG+5vuafYYX5siNw4GedcOBGR1YWqHtCtdppZXcaXxX89dwsPqytCIHADDRUTVP1FxWs8vg2rw5tmbf4WC1R2nXliOl7NKad0tbxry/tO9sKYUtpWzDcLD6oyhsADCXDq35uuaHmpNqbhm9fqV3z6xSMD6reb205bpZZAnvq5rfS1vWy76svN/z+jetgW9qHivj/WF5nbHOfTUf1VxfWll9r+bzmqN79wztWnNTzfbDC0uQfyOl7LrB+CGj8RsG4wDAv1x+ib89er1bactoD9a8WpY/E5Oi9W1pZWVWKXkpQzuXVtDynk4cvV4Y37YmXiqbzqbldfaOdZ4qbdk37/nj0Vg+x4c1+3U3DWTP2bSzaIs5rLSZtFN6Y8fVvF9zZZm9OAMAaySlqttLll/0WYbbq7Rf9kd0Nw2kUGxp031flj5T2rIUOotsoO/cVsYl8oDSys9aSkF7rfdzv8Dlc+d7Pb60YplZr8gpznyGq0c/9+1f2r35bJOSf2+asnVvzcs1Ow0vAADz75zSftlvTWa3ni+tfEwjBe/cmndKW3Kd1ULNT8PBNZTP3y+ueT38Tq4orWh2su8thW3S6diUsi9KW/6dlOfKuPgtJmU7pXtLhyIAgDmTApDlue4Xfbe/KpvnL+5u6rm2tOeMdTNxs8her8y6TXPwIHu5upKSotMvlJm9WmspYJlVSzJDNryWPWyZueysq3m6bF7sOncOB5bootK+p0kHIgCAOfVjzW+llZ/8N/vY4oLSTicO3VHajFkeD5EZoVlleS8HB3LAYTFZ/ru7tJmrvE4R6Q4apFDmPWcP3pM1l5dWhN4YjXXeqrmr9/NKWFcmz2hlWTl7ybrCmWKc/WvHbLxjc7m22FL0NFKG8z1Ns3QKAMyJbJJfKO1EY/aLpeC8WCafZMzMWrefqit5K+2SmmdrPql5oObn0krPzaPrZ9UcXNrMUqTcLYxexy9l8vPItqUUxWQoy8b5f6eY5gBCloSP3OSOyU4tbWYus3bT7kN7pLSi1k/GAID/gCw59k8sZllv0gNtM6P1TBk/wiJF5PRN7lg5eU/dyck9y+Yl5oQyLphZqh0Wla7MrZTDy+QitmGUvN+lzkbmQEUONKTsdQUsjwXZu38TAEBf/h5l/1RmZtiGz/kayib54cb5SVmOLP1l9ip7wrpHgPQfi5Elxhd6P6+mlKxJS6UAANtUZoaylJe/Qbl+NHZraWXk15rdR2OTZKZu+GiKSVmObmN/TmJmyXR4kCGPt8jp19WU2b6HSvuO8sDg5X5GAIC5lsdmZBkUAIB/oSyB5o+cZ1l1OLMGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwN/4Bz0nEEA0kiyQAAAAASUVORK5CYII=>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIUAAAAaCAYAAACZ6p+qAAAEG0lEQVR4Xu2aXchOWRTHl3xENIh8lCmKNKW4EJGL9wapIUkxoWSaRlPcSdxQcoOQz5IakjRILnylaWjGhY+SG01NpJFoSCIUMqxf69m951mdL8+z3x49z/nVv/e193HaZ+//WXvtdV6RioqKinZniGp07WeFzcUwVS/fEZsw8b19R4v5W/VR9YdqrevrVH5TvVC9Va1zfVHYr3qteqp6KLYAe1TfJC9qEbNVf6rG+A4HY/3WN7Y5fVWbVZ8kYsQYoNqu2isWigJzxVz4j2p8or0MDHSb6lCGNnVfWorDqkW+0fGD6l/VUd/RAfCyPFKN9B2NMErsDXwj6S5bLubAy74jA7acn1T/qZapFte0UGxLCkqarwws9HzfWGOnWIQjhDLWTjQFc8oLwc+mOCk2ibsl3RAwUPW72HVFcB+iAFEiNnmmCKyXyhRNm4IJfCzFWwOTzLX9fYfjimqEb4xEJ5likNSfKPjJv/OiaxRTsHhM4D7JjhLAAK9KOVOwKD1Fp5iCvOmW6onqomqJ6oFY4s8WOaX70jqimGKB6oNqlu9wkLjcl3LbR9GiNQMLPc83OtrBFJfE5jw8yw6xgwBMUJ2X9JczrFPDpgh5AuL3PDaLDY7MtojYkYIHXCn21tys70qlHUxBJBgqFi04+SXhBc4yBbCW78VyOwyUdV0qYUsomjzcR8EoJKNFUFTK2/e+lBNiIfOOqqu+K5V2MAV8p3outkZJeL6iF++MWH3phmqm68uFHOK4FE/earFJxhhFRSM4qNoicU8foTDzf+33PNrFFBzleQ4Kh4HBquuqSYk2D/kI5QXKDA3BBF4VixrAvrVVNTFcIBa+0LREWx4MnGPuAYlbBWVs7LUzfIejHUzBC/ur2HOQ9wV49ndic8ELSu0n+RmijGlKEb4jrBCrZgJuO6J6JhbGGoX9DXMwUDJnr1Pdl5aizOljl9hkcu9g9sDkWh/jYQLToGrKnHS59gD35B4kdGytabySfGOGmg8LnGZyxsk9krlDP9VZsQIj5QMKiT5yRzl9wPeql2Kh+a5qo+perW1V7Rqcy6BaTZ4pQoTwSi4MC8pz5mXofF+5Jtn9zAX34Bjfx/UFLogle1kl+Z/F+rlP2vPQxth97kA7+dVtST+WRjMFsE9PVf0iVopeIxaqwzFoutg3hVaTZ4qykNWflkgT1yRs1WnPw3oMl/Qv1Bg7K6+KagoPSQ4hlG8euP0v1bi6K1pDDFOw33KfLzqq9QC8cMekue3Z06OmwAjJELxB8iueSQhtPnfI0rna/ylLDFPw4Wypb2wBbFNHJHsLaoQeNQWQzPjsttXwsESwUJjJCqN5xDwRNQpbw1jf2ATUhYjq5IEcDjqOOWJ/CEQxi58Vljjz11c/ytdh+oqKioqKiooO5jOOb+ucpAqkgwAAAABJRU5ErkJggg==>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABZCAYAAACDvXgSAAAFEUlEQVR4Xu3dXcifYxwH8EtMRCmUZLJJSZORvCRR2g4ki2y1EDUHWCsiVjsxBw7WUigvoZQTrZYT5G0HC0fIW5JoeWlNI1biADN+v6779v8/957H89//fz/Ps9bnU9/ac1331rPr6Nfvuu/rKgUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAjmWRf5q8GVkTWT1CHox8MvR3MwcKAABz4tkyKLo+78yNKgu4PyPndycAAJjcKZH3y6BoWzR1emQXRjZ3BwEA6E9bsO2LXNSZG9XDkbu6gwAAzOzoyFHdwRm8UAZF247OHAAAPTo+si7ycuTcztxsVpZB0XZTZw4AgB6cEPm51G7ZOLIb1xZsX0XOmjoNAHDkuj/yVKlblNkByz9fNeWJ8Z0eeTKypdQPCCZ1TmRPGRRuo26pziZ/z/x/X1fqGtxc6hr09e8DAIwtC5TbIzdGtkXeKnXL8sfhh8a0tNSO2j3diQnldmhbsF3WmRtHrsGHpa7BrlLX4KFS12DV0HMAAPPu0ciG5s/HRP6KXBn5NPJT+9A0LimjdZ62Numjs9b1ThkUbXlW2ySG12B7qWuQv3OuwfL2IQCAhZCF18nNn0+LfBs547/Z6WWhtjNyYmd8Jnlo7d5Su219urTUIz7aom1c+f8ZXoPssM22BgAAC2Jj5L7uYEe+2/V45LtS3/k6FHng7dpStxsv6MyNK//NLNayKOxDrsEkxR8AQO/yK8t8f+u4yGulbgWmLMzWtw8NuSFyR+SHyNmduVFdU+r7Yvnu2Sjbqv8nu2xPl/FvP2jlGuQXrLkGuS3cyjXIrhsAwIL5tdT7ObND9XdkcTP+XqnFUFeeg5byIvUVwxNjyGItO22jbq125eG5fRygm++o5RosKXUNdjfj+TVquwYnRd4u9XfOAm5TMw4AMOeeiXwcebUMCpf8UvTq4YcayyJnlroVmtuG10+dnlfZAezrHLbszk23Bh8NPZPXWeW7bSk7i5MWqwAAvcvO2r1DP+dRHfm+10LIbuAv3cE5lu/ste/3PVLqFjIAwGHlxTL1Xa4sYJ4f+nkmedzGbDnULdHfy/xfS7UzckupHb3s7AEAMI18nyw7a5N8YPBZGf9jieyqZacxi1UAAKaRna1JDsg9L/JSqYfjjiu3Q/v40AEA4IiSX2i+Xsb7wCC3ce8sg8N1+ziiY9KjSAAAjjjZVdsfWT1i8qOE/DtflkGhNultCAAAzODyyPc95ZUCAAAAAAAAAAAAAADQyMNu8+5TV0kBAByGvimDM9OWRL4eTAEAMF+ye9beSZqXsx/bjOc1Vre2DzWeiJzaGQMAoAdHRzZEtkW2lHrFVFpXpr91YG3kQHcwbIpc3B0EAGByeyOrSr0DdHsztrwcfMPBFaUWcDsj7zbPtZZGdpfJ7hEFAGAGWWgtLvUe0F3N2GwFW2ZYduj+6IwBANCT7KplZyzfU/tgaHymLdGVkX2RjZE1kRWRzZFFQ88AANCjHaUWX7+V+uFA6+7IY+Xgoi1/vi3yRmRr5ItmzNEeAABzbE+pW6GH4trI/lK3Un1wAAAwR7Iz9kCp76A915mbTfuxwfpycCcOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAj2r/5zNFA8B3cgQAAAABJRU5ErkJggg==>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAaCAYAAACzdqxAAAABTUlEQVR4Xu2TvytFYRyHv0IpJBkMSNlkMFixsFJ0lfI/GCzKzKBkkMlmkMFisaDcUmaLMmIxsZnkx/Ppe97u+957rk53MJ2nnrrn/bzvue/5nPeYlfw3s3iMj/iCS2ncwI75PHmPh2lcYxQruI8/5n/yF+/m8+5wFefSuBHt5ByvsbsuCwzjjfmN1+qyXLSgipP4imNJ6szgNn7iLfamcT7zeIr9+IFTaWx9eGS+Ae32II2bs4Wb2W8tXIgysY4r2GGeL6dxPl14htPZtRZu1GKbMH/znTiEbzge5U0JNWg3Qjc+wbbsWrsN6KlaqkGo4yr2mHeqfoWe7MJarEHoVDzjCO5F46rhyQrWEI6ZFgUezHtUz7vRuCr7tgLHTC9DX88lDkbj+vK+cDEaG8Ar8/7bo/EG9DjalSYGw0tR3zqz+mMRzwnGp6akpKQIv4PRRHq+fjjcAAAAAElFTkSuQmCC>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABZCAYAAACDvXgSAAAEi0lEQVR4Xu3dT8jlUxgH8EdmikyGiJTCJBKx8G+B0iw0s7HwJ6NhgQVJUULEQtNkoSlNoUSymgbZSFOyGFajKTSZSKmhLDTFhuXgeTr3dn/3Z2beO/d3h/dOn099m997zn3vO8un5/zOOREAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAq8a3mb9HOZC5Z8a8ldnX+d3KEwEAwMKdlnk2JkXX1dPTM7s/81dmU38CAIDh1sakYPsss356emb7M7v6gwAALMadmSPRirb6d14PROvaAQCwYFVkPR+TTtsl09NLaV1/4BjOjvZOHgDAUjgck6Kt3m1bNldmPso8nDmzN9f3SLSO4KuZ93pzAACr1t0xWRr9vTe3mlWH8NrMocyW6akVPRcKNgBgyZwXky5bLRXWpoRFqI5XHQnyZLRlyJszO0fj8zo9czCzcfQ8DwUbALCUqrtWBVsd1XFfb25eezPbMx9mfsh8nNmceTOzZvKxmVUn7VC0ztoQCjYAYClVV+3dmHTa5j3qY+z2mHTStkb7zrIj89To+URUN+3rUebtrI0p2ACApVU7RccF27YYdlxHd9fp2zEp2I6misNZNjzU/6eWVatbN2TZVsEGACy1l6IVV0MKor4/ox3Qu0iXResI1vtxZ/XmVqJgAwCWWnWv9vQH51BF1LjLVgVgvcs2dkvneag6ouPXaJsaZqVgAwCWUnXUaododylzXlWsVUftrsxN0Qq2eq532upvjJda6x7T6pDVztGhBVT9zcf6gz11sO7FmTeibYCo53OmPgEAsIrVrQe/9QcHqPPddme+i7YrtHahfpN5pvOZ2zIXRdtNWl2vk63+xvgdvXGGFooAAP+JKq4q/5efonW7AAA4ilqyrM7akB2hQ32SOaM/2FOduFpOXSkAAKeUel/tg5j/zLX6/ToXbYgNmVv7gwAAtCKtNgbMW6yVLzL7+oMzuiLaO2x1GXtdjQUAQEftCK1l0FoOPVFV4N0b7YX92khwzfT0zGoJ9oIYfmsBAMAppwqlulXg9WgXs8+SxzPvRNvl2d1hOcu7ZwAAnKAvMz8vKIs4sw0AAAAAAAAAAAAAAAAAgFmtyXyaWdefOI6vol3S3vV5Zn9vDACAk+TyzMtx9Ds5q8B7LXOwM3ZptJsOdnbGAABYgBcyu6NdDVXqIN0q1I6n7vq8MfNLZ2xT5nDmqs4YAAAD1a0E1S27fpSyOfNK/Pt2g7H6/I7MhZkfoxV4D0VbTtVdAwA4SbZmzh89r1Sw1ee2RSvQ9mauy2zJbIj2PQAALNi5Mb1RYHy36LE8nblj9Lw9JhfGV3etvgsAgAWrpdC6B7RrbebFaMueXRujXfL+x+jnR6MVeA9mjmS+z9wwmgMAYKBavtyTeT/aO2kAAKwyVaQdyOzKrO/NAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAEvkHxou5y0GwL2MAAAAASUVORK5CYII=>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABZCAYAAACDvXgSAAAEP0lEQVR4Xu3dT6jlYxgH8EdmikyGiJSiSUqUhX8LlCw0s7HwJzQsZKGkKKERC02ThaY0hZoIq2mwk6ZkcVmNptBEpCwoqyk2LAfP03tO53d/M3P97jnn3rnn+nzq2/zmfc85d/v0vO/7eyMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANozvMv+McjzzwMAczBztfLfydAAAMHfnZF6ISdF1/fLpwR7J/J3Z2Z8AAGB2W2NSsH2e2b58erBjmUP9QQAA5uPezMloRVv9O61Ho3XtAACYsyqy9sSk03bV8ulN7cJoe/IAABbCiZgUbbW3bTN7IlpH8PXMB705AIAN6/6YLI3+0ZvbrF4MBRsAsGAuiUmXrZYK61DCPJwf7ZUgz0Rbhrwtc2A0fjYp2ACAhVTdtSrY6lUdD/XmprWU2Zf5OPNT5pPMrszbmS2Tj607BRsAsJCqq/ZeTDpt077qY+yumHTSdkf7zbI/8+zoeTW2Za4YkCEnVhVsAMDCqpOi44Jtbwwrfs6ke+r0nZgUbKdTxeF6HnhQsAEAC+2VaMXVvPaxlb+ivaB3FjpsAAAjtdfsSH9wChfEpMtWBWDtZRu7vfM8xHmZ9zO/Dsi17SsrUrABAAupOmp1QrS7lDmtKtaqo3Zf5tZoBVs91562+hvjLljdY1onSOvk6HoUUNWluzLzVrQDEPV80bJPAABsYHsyv/cHZ1Dvdzuc+SHaqdA6hfpt5vnOZ+6Mtoy5FK3rtdbqb4z36I2zHoUiAMDMqriqnC2/ROt2AQBwGrVkWZ21IZv118qn0fapAQDQU/vVPorp37lW3/+mP7hKOzJ39AcBAGhFWh0MmLZYK19mjvYHB6rTnLWHrS5jr6uxAADoqBOhtQxay6GrVQXeg9E27NdBghuWTw9WS7CXZc7tTwAA/N9VoVS3CrwZ7WL2IXkq8260U57dE5b2ngEArIGv4tSXzU6bebyzDQAAAAAAAAAAAAAAAACAobZkPsts60+s4Otol7R3fZE51hsDAGCNXJN5NXNwlK4q8N7IfN8ZuzraTQcHOmMAAMzBS5nD0a6GKvUi3SrUVlJ3fd6S+a0ztjNzInNdZwwAgBnVrQTVLbtplLIr81qcervBWH1+f+byzM/RCrzHoy2n6q4BAKyR3ZlLR8//VbDV5/ZGK9CWMjdmHs7siPY7AADM2cWx/KDA+G7RM3kuc8/oeV9MLoyv7lr9FgAAc1ZLoXUPaNfWzMvRlj277o52yfufo/8/Ga3AeyxzMvNj5ubRHAAAM6rlyyOZD6PtSQMAYIOpIu145lBme28OAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWyL9bIbPEdQhnNwAAAABJRU5ErkJggg==>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIoAAAAaCAYAAABo4cQnAAADzElEQVR4Xu2aS6hNURjHP6HIOyIhl1AeAyWKyC0MDBjIQEmZKUkehYHBlZSBJI9I6mYgJRN5ZCBukWdhYGCiDDxKSQlFXt/Pt1f2WWevfc9xt7PvuWf96t/prO/cfc7e+7++71trX5FIJBKJGCNV45PXSDbjEg30A63CUtUP1U3VVtWAynAk4Yjqueqn6oIXq5sZqtOeDkrlTD3rxeemYo1mhZhJJvoBj0mq4f5gi7Jc9UE11g/UwxjVNtUX1S/VCdUyqUxXzNq3qm+qo2J/UxZnxH5nHqRbfusqP9Ci9FOdU630A/WC40hPn1XzvBiQ2i+qdvuBEiC7ZRmF2XJXLNs400ej/IXr1uPrcVXswpItsliseijlZhJHyChphko0ik8hRnkldmFX+4GEHapOsRRWNq1klNGqQan3tAOUVc4vDe8Zz6MQo1B26EGm+oEEys56f7AkWsUomOKeWK+1UzVM9VpsUn9XXVHNSj7zRvVOtVnCk7kQo3BRb6iG+IGEJ5Ldu2TBMdbWqUV//rI2WsUo68RWbV1iKxZKvzPBRrHzu65qS8YGq96rZibvfVgE9Oh6kEXIKDS0IUK9S6PoL3ZxyHpcMJb0eTS7Udia2KWaL9aYYwiM4Dgg1ZNllORXBUzGsdh7WiL/sFFJX5L3BdTINf5gg2lTfVI9VbVLOL06mt0ojk1i55FebXJuXWIr1DQLxRYl6Z7GZ6/qq+qlantlqHv4EXllBwNN8QdLgJrdIZb9TlaGqugrRqE39LM994OJ/Sg1Bh2qLd5YmsliJSyvcuSCUaj7WTBz9yevtTJb7CbVIxqzWiD9koaZFXn0FaO8EJv9E1JjVADOrTM1RtnBOPQnTCj6G39l1CH5RuoWDojTFqTGuCF7xL4cJ/Ymamlm+c18ZoNUPxBjd5LYeQk/I6LxY+Ou3Rt3OCNyI0PL0o9inwlNQhe/rxrhxRzEKT8OVj63pbppdSWKcz0l2dschax6KD1cmEtiz3Joeo5J73xWEjKKq90uS/ly8MT5juqWVM86B8+T+AyfzYIMS0k4LmGzXRNb2ob6O4zKMTBb6Hv8nfI2saXwZalsbpkYz8QmNlkjqwIUYhQOzEqClMV+ScjhvYGQUeqFGxUySqOgZNCHhIzir0y4T/4mnINsknc+hRilmSjKKIf8gRKYI3Y+WTe+aKJR/gHSNsvJMiE7HBbL4o2g5YxCmn4g9k8506W6We0ObhArs7Kh1P/vHpBSRI/DJiWTK6t36dNgDv5vhg04Xtm5jVTzWGyhsk81zYtFIpFIJBKJNDW/ATGO1vEsxSIfAAAAAElFTkSuQmCC>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAaCAYAAAAXHBSTAAACRUlEQVR4Xu2WP0hWURjGn8ii6B+RixTYEEQtDRWBOTgYKa6CZNDSkFNDUQ1KFOIgThWIRFGNQYOLiBRlS4ENtURQi0YaBBEEtQTp8/Dew3c93HPv+ZQU4vzgh3znPfd+nve85z0fkEgk/hVP6Wf6jX7yYmvFSfqY3vW8Qrdk3qb3c7FbdD8CdNJhukgnvNha0Uy76U36l17PPrfQDbSBtmXjv+gA7aLbUMI12KL0dz25APs/9vqBjN10xh8sYh/9QmcRflkVylg//Y5aeahczsIyrmxX0UjfwxYVQu+LqqZ22JY/gW2z2AT7ko1uUgkH6Dt6h+70YvVwnP6GlVeIe4ispiFYdi5ln8/Qj/QtnXSTStC8HsTtRhmu9N74gQyV3kva6geKmKZ/YJO1QxfpCTpP52rTggxi9QtShahStCjtRhFHYQmMOiJ60QdYa1cpCpXRabrHTQpwBFZ+TRVWoYQqsTqTh7yYUNIewHYzCi1K/qAPUV/WlT01Gd1zZbqzGsJ1X5WeysxH5/s17NxVsgN2MI/Rw/QV7V02oxx1Tn3hanmE8tLTTj6nu/xAEdrqfHb08DjdTLfSc9l4CN30Hf7gCnCLCnU2/dro8wdDuLvEoV8XerEaxhg9lYuFuExfwHZtpehZnWt1Xf26cOhsjyJyh4QuzGf0YG5MD3+lU3QEtrgqdAbV0mfpDcQ9U4SqRgvTXaXLW+X2k17NT4phuz8A63iynoYhlNXzdAG15uNUOcegy17NR9XTBivvRCKRSCT+C5YAkTdwzCRAtSwAAAAASUVORK5CYII=>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAaCAYAAAANIPQdAAACLklEQVR4Xu2XTyhlYRjG3wlFQxgylA0padSYRCk1pShpppSysFAslKYmZmqiWdhY2Fgwi2nERjaSFWUlZTF/KBbGrGZhQxYSGRtN43m855x77nfHPWfOPam5zq9+nfv9kfPd732+D5GIiIiI8CiDTbAEPjDG0oLncAd+sp7f44f/fxrhKcyw2lmii33mzLhjHsEP8DV8aIwFoQaewC2jvxgewUqjP44CmG305VqGwXt4DCdFsxSUF/AP3DD6+Z7sbzf6Hfht78JL+EY0xNx6lsSeaLDDIAf2wUO4LMEOi3eSfJEDRv8NrOePMA9uwp/wMXwJf8NfsN6ZHQ7MUgf8Blustl+8FsnxBLi9dEx00ivXWANch4WwH16I5oG5CJMKOCv+chtokTZfRMuz1tXH3ZyTWFmxFLjb3PWwYU7PYLc5YJDSIq/gqsQOHy5sWnShJBMuwSmrHRbVovlkTplZL7wOHo7fCieMutosoTXRfBI+mdceZ0ZqMIef4bZoPv3m8ik8l8TLn+/nGSUuctzVXoT5rjbLgHdTHXwr+ouGXeNeMGvMHK8R5o9fYlDsQ9GOEZ8jsNWZcQsToj+4YlkaP3xTqj/gkOiJ3Czeh4RNkejieFfyc6pwUYNwBnZZT15/vq4k1jUPgL+9CEt1QfTenDfGkvEEfhV/eftXmL9e2Cb+v/CkHIjWe7n1mX9AVMXNSAOYR96X3Ol92Cn6b05awRza8CT0expGRERE3D+uASZwZkhlGSx8AAAAAElFTkSuQmCC>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAaCAYAAAADiYpyAAACe0lEQVR4Xu2YTcgNURjH/5IilK98RHlJZMNCshILFhYkKUJZWLDwsZRYkCTKAjsRVrLxkaJsKCVSlFJKFqSsKIqNfPz/PTPumefOmTvn3ovX+86vft2a59wzZ55zzjPnXqChoaGhM8voOeeOID6/JD4YOE4voDiu03QgaHPZxcNYGzPpCfqTfqcH6cIgPoleoT/oXbo1iHXLSHoE7QnO3dtqGmUl3UZfwsb+kK6hY4I26uc9/UQP0VFBrJSdsM6e0IkuJnSDe3ScD3TBCvoctuo2Zq6nMwIn/G5dzRT6Ajb2sgkaC5u8dT4QQwmIdSZuwZLRC9qCj+lsH+gBjbdqAlfRO7CE1OIL/YDilgjRjeb6i4lcoqv9xR4YQS/CEnHGxXKOZdZGnT2g430gIymrEW6ifNa6RX3lK3mDi+UkrWRltiqrIimrEc76Cz2yBH1eyeqwqjN1FOtMVXgPXeQDJdxGf1dEp20hkiZQBSdWbIQKTmxbqAB+RL2qfAP9rRGdCvxoJGwLcT4zRlJWK1ASHtFZPtAlnzMX+0CGVvEcf7EKJWG/v5gxDzb4fqBatBtWlAeKoa5QEt7Azh0e3eto9lmbqfQ1ioPTrF2nB2CnQM9hWH3QQew+0g9a+q72tpL8tsRTraZRdsG2hsaYP7DGugV2XtEkJqP99pVehR1xVTw3IZ5RFdb8PS5j7f4keuh99Bt9Bhu36tU1Oj1ol4Q61dtjM6z4dDyTo/Ue16r4l0yma+l2Os3F/goqUtqjS31guKGVox88+uFTh5NorwUx69SIQUG+LWLv8CGP9qNOiMvpK7qgGB4+6MHf0adIPLUNRfSnSZ23SkPDf8ov2GqE1PBVttYAAAAASUVORK5CYII=>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFUAAAAaCAYAAADG+xDjAAADQElEQVR4Xu2YS6hNURjHP3lEXpcrEiMxUG6UKKVMpAwopa5SDCSlO/EoYXInN2PMKI9k4DFggIlQJsqA5FEkj4kiiZBHHv+ftZe7znIea5+7z8np7l/9O3uttc/ea/33t7619jYrKSkpntHSDGlm9ttORpq7LxobtXU0i6XH0nHpYNTWarqkI9IzaU3U1tFg6gVpQtxgLpKWSdOlEVFbXvj/nLgy46QNE1NXSE/MRdId6YG0pOKMNDBzrrmZ8D5q8wwLU5dK76QDWZm8i7nU5aFH+iV9yH4/VTb/5b8ydby0X3orXTM38EPSRmm9pU3Z2NT55q53W5riTxLTzEVrrSlcDxaiF1aQqd3277QqkrvSYWlS3JCD2FQGR1TdCOqAY+pWB3WpFGbqZOmV9E3aZYNRQ+cuSmeycrPMlnotLRrrEZu6x+qbui2oS6UQU8lBRNBE6ab01Ab3gAyCi1/Kys3Sb0M3FPKaSnteCjGVKYJ8B/uy+lHSeemntFLaIn00l8PIZakslC7b4Ma5llLoGFM9t8ytmAuy8izpeSaOgelENBPVqWDEG+llA/EQG9Fxpn43N839KxjRSZQSrQzYRy4rdh7Ip1fiyiaJTW20UCUPPqBQU+ncvqDso8A/bfIs+ZYtUB54SGfjyiaJTSW1sK9k+8Q2yuP7midNeQo31RvIokI57Cxt7AcXSbvNDWZn1tYIrnfdXNQOhdhUWCv9kPZmZe7FMXUe9shXpa/mXmVrwX8Z32vps7lX35hcph6TvkjnzJmHqbyu+VWbqf9I2mFux7DcXGdT6TWXn/uleRUt6VQzlf5tN2cCLxFHs+NNwTnAekA6q2UIEcqYYxGx3NeTy1ToMndxOs0FNwRtTKfT0n3pVFCfBzb+7CJYFOPOjwnOq0U1Uz3d0mZpldV+2AOW05AqJJnKkyb6tgZ1fFTAPL74eMgz5CimMMdTs/PaST1TUyAYmsmzIUmm+qTel5X9Bwk+VIT492si+aG0zurnp1YwVFNPWNrWrR5JpgLTkv0n05u8NK6y+Q+Y7SGBV0virQZT2Z4xQwiGPIS7g2bwX/5Zc5JM7RR6pHvmXhb4bSekQv+iwh6+pKSkpKQN/AZKecp/cGwZlQAAAABJRU5ErkJggg==>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAcCAYAAAC3f0UFAAAA50lEQVR4Xu2SqwpCQRCGR1BQvIMogu9gspgtFrMYbOIj+AQWu5itYrcYThRMBqNBsVoNgpf/dy8c1j1dwQ++sDNzdmdnj8hvU4cneINDJ/dBCW7hFTacnBcWH2DFTfi4wCWMuwkfTzhyg1E8YCu0jsFEaG3JwjOs6TUvuYMrmDFFhg4cwyacwBRsww3Mh+resHABpzCtY2yhais0TK5FXZDj64na2Qv7ZL9FOIB3OJOIEXICnAThZQJ4FNVCX8csnC1bIKZ4L+oXmMOkzr2P4qvx9YjpP4A52NVxS0FCX2t4QtmJ/fk2XgTqIybkPiUQAAAAAElFTkSuQmCC>

[image31]: <data:image/png;base64,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>

[image32]: <data:image/png;base64,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>

[image33]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABkCAYAAAA7WWxhAAAFhUlEQVR4Xu3dX8jdcxwH8O8yIsKQJWqMG7EofxaNlnZhZDGUmlIrDflTFHLlxgUiLSmiDRdSkpuVcPFcrMjckFKkNi2KTMkukPh++p6fc873+XOe83t+O8+zZ69Xvds53+/v7Hmec/Xp+zclAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgEW3Iuf+nPdytvb+3Tf0BAAAi2pdzsU5Uzmn5KzNOTD4AAAAi29lzs7e6y053w/0AQCwBGxIZZQtfJNzY84d/W4AABbbjlSmQ8OenJdyju93AwAAAAAAAAAAAAAAy9WLOT90lCcSAACduy/n316eSeXIjlG5K+e5VA7RbT4biWM/VicAADr3beoXXXFsRxvnpfL5D+sOAAAW7rqcP1MpuP6p+sbxYM5vdSMAAN2Iw3GbUbaPeu/bODPnkrpxmdmYpk8TR27NubD/GABA9+Ke0KZoe7zqOxasyllRN87g45yDqXxPf6T+potDvbar+o8CAHQripVYw9YUbWuGu5elk3J+zHm/7hgh7lc9nHNF1R7v47uLK70AAI6I01K/YHstLe97Qx/J+TXngrpjHrbk7EtlVG6Qgg0AmIi7U79o63oTwZ05r6RS2Mxn+vGxVJ4/LpXRsHh9/dAT4zknlSLt2bpjDLG+bypnW9V+dSrf19aqHQCgczGqFqNrTdEWo25deDjnrZybcr5LpRiby8059+TclvNuKpshtuf8PPjQGHalUqydXHeMaW3OT2l4OjS+o79yPh9oAwA44mKNVhRscdTH7VXfuKI4a854OzGV//fefvc0L6RyTEhYmfN3zoacL3N+aR4aQ+xejWLt+bqjhThgOH7/QTFaGKNrbX43AIDWYqdoM8oWC/PbijVisavymoG2etQu3g/uTI2dlmf0XsftCftzzv2/d7qH0uj1dqem8jPeSO3WrTWm0vSCLTSFXBSHAAATE9N/MXIU67Paej3NXODMV9xR+mjduEBR3O1PZZp1PmvpBsXfEhsOak+l0hc7SAEAJiIKmRiRWugi+jfT+AXbmlTWsMX06Z5UpkNDbDx4oHlogWIjww05n+asr/rmEn9LrIerxfq16Bs10gcA0Jk4CLaLA3QvSmVKNYqtEAVNrEWLkai4FSGO19iZSmHX+D3n61R+fqyhi7tKw940PNoXhdxZObcMtLURxemTae4bHmKH6aZUrvHa3Hsfiau9oliLUbfzm4cBAI6kGN2KC+HrdWYLdXYvMbJVO5BKMdSIAirWgjXTlc1nZxLHa0TRBgBwzPikl0mKgq0ZRRtXrJEbdx0aAMBRKaYqn04L22AQo2KX1o0jxDRkbCxoI85Ci3s8R4lRw/qy9jrXJoUfALDExXqxuMy8rWaTQpybNo7YidpsKhhXTIfOtGMTAGDZiVG1KLbajjDFGWexQ3J/1T6XjalsNviiap+POFj3q5x3Uvdr7QAAlpwrUzmhv81xFLGBIIquuJYpCraXh7vnFMXhbJsQRonfNQ7UBQBY9mJ0qrnNYKH5LBntAgDoXJzOH4v2u0jbjQMAAAAAAAAAAAAAAMBRYH3OlrpxFpfnfJBzOJUbBwAAWGJOSOU8NAUbAMCEvJ2zN41/24GCDQBgAuLGgRgt25HKZexhapbszjk9HuhRsAEATMiq1O4idQUbAMCEXJZzYOD91CzZnYywAQAsil29zNemVK6kintED+WsG+4GAKBrMR26rW4EAGDxHcx5NWdz3QEAwNIQ69FW140AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABPyH/JM/Sx/f5NUAAAAAElFTkSuQmCC>

[image34]: <data:image/png;base64,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>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAbCAYAAACeA7ShAAABXUlEQVR4Xu2TvytGcRTGH0lRfuTHQLyJiclAKQmDwVvsSllkkL/DoEwyUEoGg1ilpPROlNmrlFBiMiiMeJ7Ovfc993UvZWC5T32Gc77nnPs953sukCnT36qZVJc7f6MO8kjeyJTzD5AbMup836qG7MEK3pMdUhGcrZJ3Mh7YP0qB22QClqgCoc5hH9CHQlWRSmfHlCcjZA1WTEVDPZEDlGa5TC5ISxSRolvYTRqd74MsOVvyY0iVEnXLUCqqR+l2vj4y7OxUvZJ+Z/ci3qI0A2uxh6yTAhlz55H8vBrIIeItqrUtMkjmySQsx3cTScnPZJdckxfEV0Jta6azsML1sJb1ul+kAP0FbQFKbHfnmtcDbIl148QiSrwj04HdSa7IcRRh2iT7sLkWYQ+zSLp8UC05IjnYMC9hhVrLYk7IHGyBT8kKWUDCmuiFzsgGGULyhteh5FeLTUgolOkf9QmIyDmPPrb0+wAAAABJRU5ErkJggg==>

[image36]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABHUlEQVR4Xu2UsWoCQRCGJ0gKQVASG3sRTCWks7BKoYWNjYUP4Bvo04iksBEbu1QilkmboGVsBRtBCwPqP453zK5G3eZAvA8+Dmb39p89do8o5BZ5gGkYsQcukIB5+GgP2HDAC+zDX5gyRv/nCXZJ3mnBOSzpCRruIgZf4RJO6bqgItzAuqol4Q/8gFFVN3ANapMEvakaNzwk2VlW1Q1cg75I5vN7mne4hWWr7uMaxPPOBTWtuo9rEM8NJGhBAQUF9ulOHQa+jx2SoIqqG7gG9UgW1BfUO952Az7cCV/APziDOXN4Dy+qj+0z/IQjGD/UqnB9eB7B3XuLaIckHXp8wwnMqBpfyjEcwBpcwQa5/yuvgn9hBZIg3mVIyD2xA2v9UFrDJCNuAAAAAElFTkSuQmCC>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAaCAYAAAAEy1RnAAACkElEQVR4Xu2XTYhNYRjH/xNTNMrkc4SUzAKN8ZkSVjayNIWwUWIjRWExSUlZTnI3E8nKgpRkI4uRhflQZjFiQRkLolCKBcX8/55zmnOfe2bue8+9407u+dUv3fc5Z5znPc/73OcCOTk5jcJh+i7yp4tNV1rpRtpOm10siA56iL6iv1ysGubQo3S5D1RJG/1Ib9J79DOdUXRFIEvp28ha0UR30gG6DRkfzDGXPqILE2t76enE52DO0j/0lA/UEL3xAuzNzHexEGbRB0ivRj37Qb+YhnZ+EYr/2PaiK6YGJazEtQGVlP4SOkq/+wAs6Wt+MUkLvQw7F320l36iL+iC8cumlNn0CH1P78KOQjk2wRKeKGm9OL3AVIboMF0WfX4Du+kOnRlf9I9Qte2hT+lmF/OUS7oP1jxLOI7SHVFj+EG3JNbEOnrCrYkzGN+wrMTJPoMlHNLkMiWtztdPj7n1D0gvbZ2Rh25NfKEb/GIF6HjFZb0GYaUtMiXdSb9F/ybRDTcQ/p9nRQ2sG9ZL1JQqpVwj0/d2CfFO+Tcat3ud5wMuViuuwya+k7A3nQXdp6P42wdgOfgK/os65n3YICLm0duw3dMu6ryfpxfoCliD2x1duxb2wKqG1B1NQaNiATaY1Ar1kpewoxqzlfZgkkrVTSOwB39N98G+nx/TJ7Bk19P9sHO+2G7DDtjG6MxokKkner5BWHVqmPqKgOrR2VIy8aCuRJKfVea36FWU7t5Kusut1QONt0q6C5UNOBOyGlbyms5WuZjKvdqvq2mJGoIGGJ39iy52CZNMPQ5VkHpG/LO1nOfstvqhB/bJqbTVBxoCNTg1Mv3mfu5i/y3qjldgI6M6Z0Ogbq+foCHzcU5OHRgDFG2AcGSvS+EAAAAASUVORK5CYII=>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAcCAYAAACtQ6WLAAAAkElEQVR4XmNgGBxAEIgZ0QVBgBWI/wOxJ7oECAgD8XMg1kSXgAEOdAGCgJkBYiwGUAHi00D8GojlkSVcgLifAeL8dCCOQJYEOdsUiDmBeAcQKyJLwoAOEL9nwBEADUD8D10QBPiB+AQQXwdiZSAORJa0AeLfQDwJiEsZ0BzlywAJUxC9nAGLf0HBJokuOOIBACXsEVMbAsH9AAAAAElFTkSuQmCC>

[image39]: <data:image/png;base64,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>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAaCAYAAAAwspV7AAAB50lEQVR4Xu2VzyulURjHH6Eo+R1NlB9pahZYiCIzpVgoZEdEzWpqGhvK2saKP8CsJguxsJSZ1XRtbJRssEB+JBuhlIUUvt95zmnOPb33eu+lbur91KfOc8773vc85zznXJGIiIiI90UBLINZJi42fWHJhhUwz8S5sNz0p8U6PIfXcBMumfgGTjnPJYKJnIm+cwu/w2N4AXdgzf9Hw8HV6TDtSrgPp2ETPIRHZiwZIzDftH/AJ9gAZ0170oyFgkv71Ylb4B3MEf3IF1jojJNqWOTEH+G4aXPFfsEHE3NizabfZ0I08Rf5JppZMpg1JxYEa2hXwq0uS2XA7/Txs0wHu9Kr/kCq8IRxG4Oy/AR7nDgIe+qIXWlbQyyDYdG6DY3NrB4uwEfRLLlqQ3BNdNKsoXn4Acb4osOi6ETa4CW8h52wFP6W+C3i5GdEr4uYJLhy2MkPb8A5OAiv4F+4LPrDpBZ2wXZ4avos/aJXwbboMyvwBO7BPokv8kbR1belEnQA/sHl50Vp4eXnxi4z8I/fKZocsyf8ELfLxkGUiG71q7E1NwqrvLFU4TXR6nemQ7fo1vHuqfPGUoWJMck3gVsbWJwpwK3b8jszBf9fx+BneOCNZQye0J+ip7TXG8sYPNH8w092KiNC8wxYU0pVXgjtwgAAAABJRU5ErkJggg==>

[image41]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFkAAAAaCAYAAADcx/BtAAADOElEQVR4Xu2ZS6hNURjHP6GIvPIsrySSZykDYeBRHjHwCCnM7lAxMJYUAwYykpIkeSQSeQ08JsqI8ogkhkQRBuTx//ft1Vn3a+991jpnnXs69+5f/bv3fmvfu/b+329961v7iFRUVLSfCZnGQv3NWCvhXJyTcw8yY72Od9BJ6DA0woy1Es7FOTn/ejPW6zhjAxkDocmSxvh+0DRosB0Qnb/PmUxDtkKfofvQa+ghNLV2SRTTodPQV2ihGSN90uRN0G9ot6jhw6F70EtoYu2yusyFXkDfoH/QD+lQk69An6ALonX1ALQ50xTvujKsyX+hy9AALzZLNLOfeLFQuLG9lxaYzDrm75jMBta4VDDDtkDbpfmOwJrMrLMxZxSzMpbkJo+Hbove6C9RM1iT7kjcUqvHBuipDTaINbTMZGZ5LMlNvg59hz5AH6FHohvHKv+iJuGquAsttQMNYg0tM5ljsSQ32WeU6JJmNjv4/Q5ohRdzzJOwkrIXOii1Q0SRQht8a2jHmMzScMsGwTjoDbTPxLnJnIOGmnge+6W2Wor0FlrnfqEO1tCOMHkB9CD72go2QsdtsAmsoWUm06hYkpu8WDSD/U2O7c8a7+dmmSnat3JVpMAaSpNvSPdyM1+0s3juxUJJavIi6LHoyYbL+apoh8HOgmWAvSu7ApYLZ9BOaAk0WuIegJvfTck/psZiTWYp+yN66iPcJ3hiYz8+O4s50/kP4b2UwRXNJuAntNKMkWCTORE7C8I2jpnGG2CddTfBZX4eOiG1zXCtaD3mf5i1NIYh0DNom+jbLPc3Y7Em09QjoqYcgq6JmrTcu4ZJw2dhS8dMzcOv475sRgebzBtjN+Fwr/Es3JBW26BoxxGTyQ724DTkFfRFuj/MLu+6MqzJjkmiq2+ZFHc9I6XY5FCCTQ6Fx9Ixou2af2w9JZr17aDI5BDmSHirWERSk3kzXH68sT1enNlA87u8WE/SqMksT8dssAGSmkxoqH3XwFJBkznWDi6JLvnYT0ZmQMNsMAJXUjl/UpN9aC4f7iJ01Iz1JO4Aw1cAeftIq+BcnJNz53UdSaCxZ0V36XptUEWDcMdO8dFORUVFx/Af6nC7C/WyLl0AAAAASUVORK5CYII=>

[image42]: <data:image/png;base64,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>

[image43]: <data:image/png;base64,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>

[image44]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABACAYAAACnZCtBAAAEVUlEQVR4Xu3dS8jtUxgH4CUUkXskynFLohiQiEiuiZCiCGWg5JaJcj0TyUBR5DZwmZi4DVwnQopQJi5FBhRCjKQol/dt7e2svdrfty/ft79z2ud56lf7v9Y5nX326G29a61/KQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALDxDoycHNmhn1iQhyNn94ONfm6X7nnR8nfYpx8EAJjVJZFT+sE5nB75NPJk5PPIiaPTC3Fe5Nl+cGCnMjp3cOTLyBnN2KI9GPm3HwQAmNcDkZ9KXSWbVRZHPzbPR0d+HYwv2u39wMDmQVp7ds/zyEJ0535wBbmit1c/CACwFrtFfoi8VGZra2aB9nHzvF+pq2yHNWOLcmyp/17v1VLn1su+pRa195TpCzYAYDuVxVG22X4ZPJ8W2X3L9Lo5KfJB5OIyuUDJVa53muf8Pvl8fTO2SN+X2ood5ulS26Vpx8gtkd8jbwzGppV/N3+DTwafp3Vz5JvIz5ETujkAYMntH/ks8l3kt8hbkS9G/sT6e67UVbfViraVCraV2pXrLVfTWrmydsDg81WRx0v9LrPsJ7si8lWphessq435Z7No3LXUgu210WkAYHtyRKknMls3dc/pyjJbwTF0VKnF2nWltkpXs7ULtizQ9h58zn1qbQF3Y6l7yf6MvNmMj5P793IfX7Y+53V+8zkLxI36DQCAbczxkbf7wVKLjdYekcfKbJv/s/WXp0ZzD1q2Q6extQu2/P8NW6ArnRzN4mlSi/aOyL2l/m5rld/pn8hZ/QQAsNxypezyMnracT2u5Ei5zytbrYf2E1M4rtQCbyjbkbmHK/fbbZR3S11pe69saYcOZXvzkVJ/v3O6uXGynTnP4YtWFmovlNmKZQBgCVwbeaV5zrZobojPAu6JUu/9Gnqo1IIjTzeuZnj68a7B53lkgTPuWo8cT1kk5fdcbR/cWm1u0sqC6flSV96y+BquxE2SK40XRD6KnNnNTSNXF2/rBwGA5bYpcuTg85eltvjuL7UIurTUVaXcr5WGd39dFDlo8HnRbog8Fbks8kfk6mYuW5F/RS5sxtbbsDAbt6J1a+T1yIf9xAweLbXlPE27NK8zyQJ23HUjAMASa1+rlEVa3/bLAwj9vWP3lY19HVMWZNeUlQ8pLLJgS4f3A408YTvL1RzjZLGWpz4nvW4qC+UsqOdtpwIAS2h4Ue25zViu8nzbPK8kT5bm3rVJWeuN/flez3GrX8vimMjfpb76Kve/5fUrAAD/y71iL0bubsZylSc3/k+SJzrzOotJWctq0SGR9/vBJXNq5OtS382ab33YNDILANC4M/JMqfu18g41AAC2MS+Xekdbnvxc5KlMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACApfQflU6MiLHm5G0AAAAASUVORK5CYII=>

[image45]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD4AAAAaCAYAAADv/O9kAAAClElEQVR4Xu2YS6iNURTHl6KI8swlyiGRvJOkKMrEgAEpJUOPAROKuhnc0h0xYoKUJEnGDCSdMlGKDKQ8ColSGJkg/H+tvTv77O+o87i373T6fvXrttf3OHt/e+21d9esoqKionMOyg/yt9yZXRtoVstD8rNckl0beBhwXU7L4gPPqNydBweV2XKy+SzX5Yqmq93B+2Yk7alyUtIuFTpyUj6Vn+RF+cV6T/Mz8m/wlFwk78pack9pMAM35KvQrsm35p3tFXaFj+Yf8498Lvc23dEjE+T8NiWduR82yB/yhZwTYjHNv4Z2CrM2PYuRLcflmiyewj3nrPG7KTybpz6/wW8tzOIFGAz7bjvesUYKXzCfWf5GqOZsY/UkFnlpxc5skt/s/4WQjLoqj+UXAvetuKT2mb9zfRYfE+LMMvA9SZwDS/4xuoWZu24+kFazXQpx4KQ6KR9hG2PgzOBhK85GJ5BdO5I22bIraZcG6fdLbgntK+ZF6L15PdhvPmvnQ/tEuA/mmq/NI1Y86BDnXSyNn/KxvC0fmL9vsRwxr/LpkXileWaQbWTKuMH6uybfyZvmZ3TSkix4aN7JmtwuN8tVPBTgWEsneR7TVD4qL5l/AD5a3NLmhevrgnzYoRCDrdbIxNNJfNzggMGMRvhxZjRlRE7JYjPlE/NZT+GDxUrNB6H4YspEecuKa5/iSsalS6Q02OrY8hYEI2vNO7kxibULp0KeXSpnJXFSn3i+e5QCX5/ODJuvz8gBaz4DdAJZQracteazAcWV0x1H3b6gVUfoOIPvllY7xhtrFNu+grV6z7wQvpbLmy93xTL5yLy4PbNiPegLGCjn78s2dv+d2Sa/m29jVPu+hV0g3YZ6JVb+fCepqAj8A4u/cVXxqq0gAAAAAElFTkSuQmCC>

[image46]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAaCAYAAACzdqxAAAABRElEQVR4Xu3UPyhFYRjH8UeXUjd/ktzEJIuSlFJmynCLQhmMViYlMRusFovBSsqkKDEoKSsZZKAMFpNk4/vzvpz3vgPOuXe63V99Ovc8z7nndN7znGNWSy3Vlzq0ocHv59CUtLOlD7f4wDV6sYwVcxfMHJ3sBY94xRsO0RIeVG4GcRwXySIG4iIZxZz9cWdjOEJ33CDPmIhqzbjAFuqj3k+K2DP3ACuWWWwjH9Qm0Rnsp84wzvGOJ+ziCtO+v4QhnFhyYa2nJkfTdOf7JenAmf+th6ap0MhpKvTnRkyhgAV/nNLqt1rze3QFva/oZQhHSifS7WsbZgT9UU1ZNzeW8fH/zqa5tzAcNy2Llmc1qKVKO24wjpmg3oMHcyOaOfpuxC+AlmHffpnfNNHJ17CDS8yXdMuIHtIBTrFhyZewIvmenCrKJ+SUK4bsR8e1AAAAAElFTkSuQmCC>

[image47]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAZCAYAAABkdu2NAAABTUlEQVR4Xu2WO0vEQBSFj7iChfjAB4paKHYighY2lraKhSBoabP1Nrb+ANHCwtrCSgvBRrCxFGy1snHBn6B2Ps7dO2HHkcDMNjHhfvCxmbkk5GRnbgIYhmF0Tj+dDifLzhF9ox/0m579LpefQTpG91HRgBkdBeyFPp3unPF/IingAN2mXc5zektH6Sn0QqmM0E26leBC68w4kgLWocGELOAGnaBNlDygLL89bzxEH+gsNOyi02cK+q8XSXTAkGX6Dt1/eTSgIYskKaCE6aE1ekm/vJrM73jjWNag15GbiPWkdWYc0QGlSz7SdTpJX+irV1+hV+54yR0/t8uFER0wW5Kyz6TZfKIdcJxe01XonjuENp47Vy+SY2jAC9oX1P4gzWTY/QrSePLefwf0JpysCtL6n+gudDlXDmkc8l6cozNBrRLM03voF71hGIbxAx4NTPuAaBgsAAAAAElFTkSuQmCC>

[image48]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIMAAAAaCAYAAACU9O/tAAAC2UlEQVR4Xu2ZS6hNURzGP6GIPK9XMUGKcJUykBnyiiSKlImBkQwMlO7UwAATQyVJipIy8MhEBhRTBmRAUswUBkp83/mfxbI6j332Onfv0z3/X33dc9Y6e+97//vb/8e5gOM4juM4zvAxi1qWLlbMJGo5NT3dqJhBiEVHNlN7qanpRh+YRr2nrqUbFSIjXKW+UhuTvSo5gvpj0RW59Tz1kRpL9spykfpG/aJ+Iy8Aupkz0sUCrKNew64vfUc9Zgix+IH8WFTOfuoV9QyWNXLJDcBM5N9EPZF1mSFwBvmxaDAHlnIDszE+aT0wGWYEGULmyLlWbgDcDE0WUw9hJ/kJS5krqUfU0uhz48kd6hN1HOXSdVYA4Gb4yz1YvflAfaGeUm+o7fGHKmAJrPZ9Ru+GyAoA3AwtmUcdgmWHgF4fpbZGa4H1yEvvgWACNZfzk70iFA2AftdFMOPFUibc0WJdklGK0IsZVCLT63RSXL470TczqCQ8SBdhwXtLnU7Wp1A3UDxYKTLZGliJKFseAkUDMAprXJUFY2nKUVZM16WTjSO704sZFOv0Ou30jtpjh3WlL2bYQD1p/qyC0Di+RPE/tBO5AfAy0UQ3RhkhbhZXU7ui9/1CafowdR9WYuJylENWAOBmaLCJeg775kxN5F3YRKFJQgE6SO2DlQmVC3GM2kKNwFJuEXSesyjXD3RD9VQBuI3yJSvXDDK1yoy+9NkG6wnq4BJKxkLfI2iSEBovH8NOpD5Ae+IAdZO6jH9P8W5Yv6DgqabVRXgKWqlXyppBzZ0yQnp9qcz5ytIuFoUzhFK2poeA3Lwweh9QA7MzXYRNGEUzw6BT1gxDxwtqAazGKyMErsCyyERApWZVuuj8j4J0jlpLnYrW58JMciJa64QmBmWYdGxqpxV2mDNo6ManDZFKhMygPWdIkQnUNN2iLiR7zpAhA1yHTRhh4nCGFE0g+le34ziOM6H5A+znuV0VJgjhAAAAAElFTkSuQmCC>

[image49]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAABqElEQVR4Xu2XzStFQRjGX6F8lY98lpVsRFLKQnZSPmIhVsqWnYW/wdLO0k5SVooFsriyoCysbMjGklJkZcPz9N7J3Ck5cy7dY8yvft17Zs5073tn5plzRSKRSCQ7VMMuWOZ2hMgovII5WFfYFRbL8Am+wHf5BwUbpiVlwQ2wyrquh5XWdVbxLrgdHokOehPd+N3wGHZa92UV74L34Su8hw/wDN7AMfumIuAPOAznPJyCtRycAO+CbZrgvBTGO98viKahS7+UftmnLpjL99BtBG3wFq467RVwWzw/5BdIVfAAPM2//jW8C+b+4szaAdUDJ6zrYqiBB6JfKqmPsJeDE+BV8BC8gM+iwbUnmtRMaA5mgMyILmkubbIIR2AzvM63lRI+gLDgc/nmVOE5y4QmPJpORAdyX7KPzMIduCGfQTYpun8HRZO9VJiZdc3JFzPNdGUqG8phq3VtuIPjbqNocmdhhn+cS9giegRxZg2boqshKPiouQb74IrV3ij6QyxZbcHA4rjcbbicWTD7goaFdsBduO70BQmL3BJNbpPkQcNk59/ISCRjfABRAFsZ2XVoQAAAAABJRU5ErkJggg==>

[image50]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABcAAAAbCAYAAACX6BTbAAABk0lEQVR4Xu2UvyuFURjHv0JRCuVXmZSUEoOVicGiJDL4A0wySMpuMIhkkjJJfiwGuVmVgTIok5QMBjZlkML3e597rnPPffPjfd/BcD/16fY+z+2853mec16gxH+iit7TR3pDmwvTyaikS/SDHtCKwnRyJmGLz4eJNNiib7QvTMRF7Wig5fSFHsH6n4gWukef6CVsiKm15JZu0urc8wR9p4P5f8SkiT7Qdi/WSO9oqxeLhUpfC2K9iO63TtBAEBPddBo2szwa3jWKy9ciUf3WLGaDmO7ANj2hNX5CO9Sp8IP19ALWkk467uX+RA99DmL99BXWEu1+ClbuIuy2uqGLBboLO2EdXjyL/piB7VZoqGqTjmEt3adtdIyOoPg7owvmWjvsxfOo9FN6SM9h1WzQMzpHy+gobJH13LNQZeq3WquPnH4j0XGUuplCC9R9pbOogqEgJjR87Vwvj4V2qaPZRWe8uBu+5hIbVbJKV2CzcPzYkt+iF7i2OdQS7dwdiFTQosewj91ykEuMFryiOyhsU4nv+QTBCD+/mD3AXQAAAABJRU5ErkJggg==>

[image51]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAACVUlEQVR4Xu2XP0hVYRjGH0nBMNTKTEEXdUnEFCFIgoYwMsgh1ARBwUVwaXCIwNXRRXQpt4igIYIGUxqKlqDBKYSixSExCFGkQRB9Ht57vOd83j/H+5/L+cGPo+937rnnvef93u87QERERERp0Exv00Za4YwVDd3UFL3qDmTJXbpBX8SOP4LDxeMCHaWbtBO5eRK36C7s2qIKlnjv6RklgpJV0u/oH1oTHA7FDfqPfnfiDXSbtjnxhNTTat//dbBfLZ+0wm58Ducr90f0mH524pdi8UEnHqCJrsFOPIQ9gQ66Tlt85+WLWljCSnzZGUvGM6ROeNqJB/hAD+gW/Uu/0p90wH9SAbhIJ2Cl3u6MuaRLWOOhuEJHEGwq+nuc3vPFPLqRfdl7if6GJRumoeUkYZXvRzdIrtNfdNaJV9LXsC/JFM1br5Q1n8OSdcI99EvsWAiUnJLcgc3h85KuaWk8Kf2wJ+tvUGr7KTtdhqhcV2Hr8Rgynw436T7ObjRUjaoY3X9CtHh/o3uwxvUe1qnVofVrDdMhWEnrYkLz7Q5szXO/MBlqQouw9TdX6L6OEJ/zOj5HimardVYdWmhp+gQrB81LjYnH9A1dQvzCD2Hztw/W2YuF7meGvoQ9GB3/x+IJUTmpK3toi6YNuIu65wM3COvcYZ9wPtF8naT3kdmu7Qzavl2DLUF6sh4rsGooK7TVnKdd9Kkvfhn2Q6Tc0fhQQ9QqoCmQTlXUE/tYcVBy3huJh8pZCWusrFGierd9SxecsbJESb6CdW6vk5c16ux6jYyIKDFOAAJMbOpJP+myAAAAAElFTkSuQmCC>

[image52]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAAB9UlEQVR4Xu2XzysEYRjHH6GE8iM/y0kuIj9SipSDyI84iJPiqFwcHOQPcHRzwk2bclIckAO5KAcnF3JxUSSRHJT4fntm7Mxrd3a31e7sNJ/6NLvPO7M7zzvv+7zviISEhIT4g3rYA2tgntEWOPrhFdywjtfu5mDRDV9gvvW9UDTxzt8zAkQzfIaXRrwKPsBGIx6Tcljk+F4m2mt+ZBx+w1MjXmrFR4y4izp4JHrip+jEb4LHsMFxnp9YFu+E5424i334Du/hIzyHN3DQeVIasAN74VQKjsESXhyHRAmzPSkq4bS4yzs/z8ABR8ymTbIz7P8lYQ7fQzMIauEtXDLiBTAi+ieZJu2EO+CZdcwFEhUttseF84tP1lmgWPY9K10KFMMD0RtJ1ifYwovj0A7f5O9Gg6ORyxXvPyZcvC/gq2jh2hOt1KzQ7C0WkAnRIc0fI7OwT3TNM/8wk/C+viRab3hcEY9iy3WWFZpwaToR7V3OS7aRSbgD1yX6w6Oi87dLtLJnC97PAtwUfTA8fljxmLC6sirbcIvGDbjJHRw2g6KVO5tP2IbzdQ4OifdSljTcvlWLLkF8sjZboqMhUHCruQpb4aIjXiHaEZ47mlyFydlvJDYczkyYbYGGifKFexeuGW2BhElui1Zuu5IHGlZ2vkaGhPiMH/O4YzT36jNfAAAAAElFTkSuQmCC>

[image53]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAAAaCAYAAAAKYioIAAACgUlEQVR4Xu2Xv2sVQRDHJ2hAUeOvwkIrTRNIIRgsREyjWPij0EJBMaUQtDGFSSeIoCAEQvwDLARBwUZBUPBZiQoKNlpYGBGEiIiCIgrR7zezww37OG8fycmRtx/48nbnbud252Zn74lklgQ7oTfQ+xKNFbd2F5ehla7/Dtrs+ntdu6s45dproNvQcmcbcO1GsBHaHxtrhkE4FxubxCroIfQHWhFdq5MT0O7Y2CQYjHvy/wMzBW2Kjd0Ot9Hn2FgXG6De0ObvaneNsI5QPZHdYLbE16p8VsH7mRXmw+A2+h3Z/sW6IMI5ch2V2X1adBt8h4ahSdFvgjnoJrQeOhZsv6C30Pb5kTrxluh4yhZe5XNtuK8MTn4P9El0HH/HoQehz3nQ/2toKIwp4xn0Afom+uxHoc+MO+Lua4OL2Sb6Bp5CB4P9oujDH0PXgm0Q+gLdD32L/ojooi0wVT4ZuDKYHRegn6L+GcS7os/tlK1Qf2jb3I9C+6CvoodGJZzwIddnm7YbUmwRy5CZ0Dd2iGZHvFXKfF53No9NnplghZWn3gEpFpgKx426/mHRZ5M+0Yz0H4ulpCyi7sBcEr0+Le31aqHwFLPAdETKIuoOjH0PsbguJjbvj5E9iZRF1B2Ylqgf+lsMeBIx8+x49zVllyQ8hwWPEz4uRQqzTdstKY42/mF7Cc2GvsH9+kP0BDNSfXpYFFmwTzrbFugOdNXZUrCXwPE8zXg4cKsugyZEDxT/P6uN86IOTHxj5tSLb9n3W6IFkr/ezrGpPmMYQBZMBpkn0SvoiWjgO605DMgL6Dl0FjojmjXsX5HEwts0mG0Merw1OyX+qGR7oT4zmUwmk8lkGs1f1OywU9yw+SgAAAAASUVORK5CYII=>

[image54]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD4AAAAaCAYAAADv/O9kAAABN0lEQVR4Xu2Uv0tCURTHj0OQFP7IIQIXw8XJwdECBwdBWqItRHDOycF/oiGif6BRcG0ImlpzEhsdFGoVhCaH/B7uVd+7T30+wXpPzgc++N653wde7rmHSBAEQRCEfSIEE/o3aMQsz7N9uBKGdfit7cNLW8K/8CYbsAPvYR5+wnd4bckthUM9mNbvX/ANHs0TdgrwxqO7IgXbpE74l9SmeR8V+GzJObiDT2Rv7ysYsbz/BYfwzIOcZ6owA5PwA8Z1nTMH+tkBhzhcMhf+AT6h4YbyVSyrz+YU4aNRW0kWjuG5uRBAmvDWLK4iB3/gsbngwiup++TFXcJt/0LqIDeC7/UDLYbarNYlZyv5mQs4MYtuROGI1ARswQGpQREkarRlV3Gr8xQ8pTWT0Mfwfz4xi4IgCIIg7B9TrMk8TOo7/tUAAAAASUVORK5CYII=>

[image55]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAbCAYAAABFuB6DAAAAxUlEQVR4XmNgGHpAAIitgFgOiFnR5OBACIgfAPFcIN4CxG+B2BNZAQhwAvFmIBaF8hmBOAGIP8EUwIAHEP9DExMB4qsMEEPAAKR7PgOmQh4gPgDEmjABQSA+DcRfYQJIYCEQ+8I4IB0gh+NSWA7jGDNAFBFUqM8A8R1BhZJA/JCBCIW4PAMKjaVAHAQTYAHiNUD8HyYABbDgAfkBDiIYMBXCApwfTRwcTPuAOBqIW4H4GxCXoahAAnYMEIWBQCyMJjcKqAAAupomGBIjvyAAAAAASUVORK5CYII=>

[image56]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAbCAYAAABFuB6DAAAAUUlEQVR4XmNgGJqAEYhVgJgZXQIZaAHxRiB+AMSSqFIQoAvEV4D4GxD/B+KHDDgUsgKxOBAbA/FXBjwKYWBUIZ0UggRBkqDoQ8c8SOpGAb0AAG8LIV6z4plOAAAAAElFTkSuQmCC>

[image57]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEkAAAAaCAYAAAD7aXGFAAAC9ElEQVR4Xu2YS6hNURjHPyHk/YiELhKJpAyUkIGBkkdSJmYGJkYMTAyUbjGRMDBQSomBlIFHUo5HDEgpj/JIJEIoZaTw//nWdvZe7rln73vOPq7u/tev9l7fOnet/b3W6ppVqlSpH2qVGBIPVqpronghpsSGfqi54r54LWpiVMZaonaJV2JqbOigRoqV8WAPmiA2iFPicGQrTQvER/FNLIlsnRBZfEC8F2MiWyMNEifE+thQhljkirmjfop1WXMp4gOXmq+7UQzNmnOJYBLU0kttsrgjVpiXGU7alJmRFRHnAxu9NxPOwCmPzNddljUX0nbz/bI++yjNWfvEIfOFRpsvujszwzVTXBMfxDPzLNgT3i+KsX9mNhb95q04KeZFtqJiv/SjH+KlefP+LM6k5rRNRHNGeCYSOKm7bv6tLnHLPOo48qb55o6JS9a8RHHOfvN+065DYZJ5NrI2TRwtFF+sWGY31VYxIhpj0QtieHjnA3eYpzOaLd6Ju2K8WC7mBFsz8Tdw1EFr3VlJqaUDOl28sTYePGQPZcNCMTVrXN80eeb09djF6dvMy+6c9a3suOyeNc/m1alxnhkjkC2LdKQP0Y9i4YDeLpQ4hzm9Nfc8GizWinvmZcx7XiWlRtaQPYnopeytUYALiZOMXsTJFotF4gslizKXD6HMPon5wUbDpmyHhfeiImBcA/jovFcB9sYea1Z3CG3jsvn+WxIfed78RFpsfzc4Nvg9sMbcTkNm4QfmJUo607hp4OiqtSm9g+hbm+PBSJTbcfHEPOO7xFPzAJJZs8TeME5VIHrnc2uyVyJPBqR7z86Unee4NwGbvmEetevmpYGTcRQOTzKq08IZt8VD8VUcsfpNnQQA+mfiJEqRgNITSxEZSLmNC+9kHBFMTrx/peQSmZzEaZFtp8XR8Eyjj682A14EkSzigJkWnsmsvNeVjovSoFT5t0YetvjPWhLN/bF5L6K/cuVYZD2f6ANe6RbBzTw+rCpVqlSp0v+qXwRililClAu0AAAAAElFTkSuQmCC>

[image58]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAbCAYAAABMU775AAABG0lEQVR4Xu2SvS9EQRRHf4KEZBuJEKGxnW1EK3RaCq1ap99Ep1BIVOptdhuJaBR6oST+AuKjEQWVaDk3d94z74NZNSc5eTtz7765c++T/g5z+IhveFCK/cg4nuMHbpRiSU7xRX76r3jCSxwrB1JkZQ7jRHgmGcF37OEdXsvLHoiT6mjKT9zB0bC3hct5xjes4JGK5a2qOppK+duqjmEdu+H3nnzG93lUfj8bxXy8CbvYidZ2+nG01hQ+qNgIm6U1ZzasrQc3uJRn6OuPMW15szLW8Banoz0N4SE2wnoRX3E/z/CyrUzLLTCDF3iCz7iJgyFmLzyTV1GLfS2Tqra89n79YCdZ11vysfWNNeZK/jkulGJJ7J5Z8/5J8QlqxC3HfsgRzgAAAABJRU5ErkJggg==>

[image59]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAZCAYAAAC2JufVAAABI0lEQVR4Xu2Uu04CQRSGfwKFBhJiSIwEEyoaWqIVFbGwsbIwvAIPgA/AO0ACIYRQqYmRisb3sLHR0kQ7rbj4n5yZ7DBBoditmC/5srvnzO6cnRsQCAQC+8UxTftBhwNaNNfEOaMvdEUX9I6errUAqtD8F/2hg/V0fBzSJ3rpxLJ0Ai3gnF7Tb3rjtLG0/IBLCjqsu1gw7YUaHdKMebbk6TP9pB+0jegdlxHN+UGLdPS+ow+IPnRFb829Txk6Wq+05OUsY+iPxsp/RQlLaGEdbB6pRIqq0y42dyhTOEe0+GVt+UzpkR+Mgws6Q7Tb5CqdyVQL7sLv0YqxDz1CEqNB36CLWqbsnp44eTm7mtDCrI9OPjGk420Ho2woafPnjgsEAgGPXxAiNp/WQSvkAAAAAElFTkSuQmCC>

[image60]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAaCAYAAADBuc72AAAB4klEQVR4Xu2WsStFURzHv0JRBkqkLJTBwmBTNgMDSTaZJIu/wCbZTDIqIZkN9hc2JYsJiZQMDEKU8P127vHOOd7rvXvve4O6n/r27jm/+7733Pv7nd+9QEbG/6CXuqVeqLUgloYzVNi3lTqkvqnpIJaGCVTB94B6hHm6laIBVfD9QoXS4zCMKvja9NRTbUEsKSvwfaVUKEVv1DZ1TZ1SM1SNe1IClHbXVyWQyrcb5s6XqMZo7oMa+j0jGffwfReQ0ncRf3elLrAVHc9ST9RAPlwW4W6fjOasbyzszuwP5mW44YznqRZnXAr5PsP3tTXr+pZNO3UFfxFNMIZanFBNbUa/5SLfE/i+Ofi+seigbuAvQj3vjuqKxrqYLhoH+e7C99Vmcn1jUUftwTxFMQhTj24rUZ0VWqiezisK1658c/B9V5H3nYJ5c13APH2h0tD/itJJHVH71AM158Rs2qWQd+qTGgsDEcfwfWudmDaWMmVLSjeUc+JFUZPXnYVN2aY97AqWZWo0nIzQwor5CpXASHSsFnnpxGKjtOoLSL+2x1o03kHy97huUNkU4zCbug8l0l8MpfWc6oFpOS5q3Go1iYxhvJUxpX4dpk2qpydGC2wOJ2EWnxZ9YtqysBsvIyOjWvwA3tdd9GrJqtMAAAAASUVORK5CYII=>

[image61]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAAAaCAYAAAD/nKG4AAACrElEQVR4Xu2XS6hNURjHP6G8Qp5JEklJMVCUZMRIHpmQojBQUkSRujMjKaUomYiSR8oEyUAYmJAojwl5JKJQokjh/+vbq73OOsc5+56z6Q7Wr3511l77nr3P+h5rXbNMJpPJZP4zg+QiOSSdyJQMlivkPXk9mcuI4XKLPClnJHMDllFyvHkJwNji2r9itOyT7+WhZK4byMph0Xhoca12rso38pO8I88U489yT3RfXRAUFonFYtF6geBulK/lF7ndvJRfyAdyenlr7/Dii4vPk+VTuVfOk8/k82KuDsbJo+YLNTKZ65YN8rh5Oe+Qv+VjOav4vLu8tTdI083ReIH8Zr4L8fCl1j7yRPWAvJlc7wS96a15r+I53TJbborG9L2fckkxnm9lW4ER5lXz1XwhP5hnJF42/77KbDP/kqqExb2bTlRgijxsXu47k7luIaOoBCqkHfvkSzm1GI+Rt+XDcEMniECITBXIiCPymnyVzPWH0OgPmreEXiBwF639+Yw57rlijRvCKfkxGreEHY9ynGBlZAJz5PJoHLNGbjWP0rtkrhvILnrZMfOsqwLvPcnKXTvtUeutOQBkHb+R946v0asvRNeaCGU007xJ/jJfdbJsnXkd/+34EBZxpfnf1QmLsNoaI98KsoEF2iUXyh9W9is2k1XF5xgWk998Wp4w/420g44BYiG4+Zb5WYdsIRVvyLPmD2zFXDnN/AE02P70uTohUPS88/K+PGfei2jiT6yxuUMowbhUOY/Rfh6ZZ2lbiCIH0ADRjMcpfDm9iqjgJas/s/oDAaeMeC8Wh7IL45RWJQiMyTYqrVYoP9I+QF/r2BgHCJQoi7Isusai0qvI0Fr/3ZpoXuvx1kwpVt0NOcdQLuFs08l2u1o3pEcG2C+/y7XRtUwmk8lkMk38AZLygLDnNNWAAAAAAElFTkSuQmCC>

[image62]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAZCAYAAABHLbxYAAABRUlEQVR4Xu2VvUoDQRSFr4UQ0URBGxG7+AKxTEoLGzvBwmDtG6Sz0DewVkLeIWBKiZ1PofYKglooRM9hXJhc9udOZARxPvhY9s7szNmdnV2RROJ/sQ4buljBPNyCLbii2qKwCt/hnm4oYQ4+wiG8hHdw2e9goSfVk3IiBqR8kp9SfU3GAhzBNVWfwF1VK8US1GdJwoJuw1dYU3WOca5qpcQOeiiuv4bhr8WNZyJ2UI5fFPRe3MY0ETvoQGYIyknY4HsGj3LqNG9ZQoNeyAxBT+GD8gU+5dTpsbtsitCgf2bpizbTG7yBdd1QROygHfgBF1WdY/TFfaNNhAbdEDcJXwv+Fn2ybybH9OnCA++cf6Xx99GMNWi2e7UMlsGJr2DbqxHe0DM8Efcq3MLmVA8D1qA/ZRPuiwvKJx8Ml3BHFxOJROJ3+AIgQ1IrBxta8wAAAABJRU5ErkJggg==>

[image63]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAZCAYAAABHLbxYAAABKElEQVR4Xu2VMUoDQRiFn4WgaDQQG5F0yQVMmRwgjZ1gYQ6QG9h5iNQRSZ02oKUknaeI9hYWWiSgvse4MP4kcSfMgsH54GPJP8PM2935s0Ai8b84pge2+AvbtE5PadmMFUKFzuiZHVjBFn2hI3pDp/TQnxALbaSAUk/yE/mD7tJ7emTqH7RtalHZR1jQBn2jO6auNXqmFpXQoJdw8y0K/wC3XiGEBr3C8qBPcI1ZCKFBB1gjqJpCA3lU42i+JTRoH2sE1ebPOR1i8fkJDboxr35ZM73TCS3ZgViEBm3ROd0zda1xi8XHKwoncJt04T6LPtl/pl63T4deeL/1VRp/X6OTda9VwTK08R1tejWhG3ql13BH4ZHWfsz4Q1TpOVxQPflEIpHYJL4A/XVH7C3ukKEAAAAASUVORK5CYII=>

[image64]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAaCAYAAAC6nQw6AAABJklEQVR4Xu2SIUtEQRRGr6igYBFEEQTR5gbtoj/AoIhsMy8Wk9FmsG0SoyBaLBaDXTQK/gJFtBncJEb1fNyZ9e2s7M5jwbQHDo+9M2/ffHeuWZ9cFvAVP/AoWSvFBN7iN24na6W5xnfz0/XEl/UYKxJjDeNkeJZmBD/xHJ/xwTzmQHFTDvPmJzrA0VDbxdXmjkz2rf22tvAsqXVEsXRjS0n9EE+SWkem8AnHC7UxvMGdQq0r0/hirY3VLKnZc4VaV4bwwvwUYhkbWA+/q7iJG+anF4p9af5uCzN4h1f4hjUcDGtqumKfmp86xt4L621oCPXFvwZREdVHoVF5xJXf5XzWzPsoFFF/OouLzR2ZrOO9ebRj83GpmM9fadSzGFt9ipfT57/5AV5DKmJgO6uOAAAAAElFTkSuQmCC>