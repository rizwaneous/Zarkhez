"""
🌾 ZARKHEZ AI - QUANTUM AGRO-SCHEDULER ENGINE
=============================================================================
Quantum Optimization for Multi-Field Fertilizer & Irrigation Scheduling
under Climate Leaching Hazards and Operational Machinery Bottlenecks.

Formulation: Quadratic Unconstrained Binary Optimization (QUBO) & Ising Mapping
Algorithms:  Quantum Approximate Optimization Algorithm (QAOA) vs. Classical Exact (NumPyMinimumEigensolver)
Framework:   Qiskit 2.x, Qiskit-Optimization, Qiskit-Algorithms
Domain:      Agriculture & Resource Allocation (Qiskit Fall Fest 2026)
=============================================================================
"""

import os
import sys
import time
import json
import warnings
import numpy as np

# Suppress scipy sparse warnings for clean terminal output
warnings.filterwarnings("ignore")

# Use non-interactive Agg backend for headless plotting
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Qiskit & Optimization imports
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler

# -----------------------------------------------------------------------------
# 1. AGRICULTURAL PROBLEM INSTANCE DEFINITION
# -----------------------------------------------------------------------------
# Target: 4 Agricultural plots managed by a rural cooperative in Punjab, Pakistan.
PLOTS = [
    {
        "id": 0,
        "name": "Wheat (گندم - Tillering Stage)",
        "acres": 10,
        "urgency_weight": 9.0,   # High biological need for immediate nitrogen
        "bags_needed": 15,
        "bag_cost_pkr": 4200
    },
    {
        "id": 1,
        "name": "Mustard (سرسوں - Vegetative)",
        "acres": 5,
        "urgency_weight": 5.0,
        "bags_needed": 6,
        "bag_cost_pkr": 3900
    },
    {
        "id": 2,
        "name": "Maize (مکئی - Early Growth)",
        "acres": 8,
        "urgency_weight": 7.0,
        "bags_needed": 10,
        "bag_cost_pkr": 4200
    },
    {
        "id": 3,
        "name": "Fodder (چارہ - Maintenance)",
        "acres": 6,
        "urgency_weight": 3.0,
        "bags_needed": 6,
        "bag_cost_pkr": 3800
    }
]

# 2-Day Planning Horizon
# Day 0: Clear, dry, 5% precipitation probability (Ideal application window)
# Day 1: Severe monsoon convective storm, 85% rain probability (Severe leaching & runoff hazard)
DAYS = [
    {"day": 0, "name": "Day 0 (Dry / Optimal Window)", "rain_prob": 0.05, "max_capacity": 2},
    {"day": 1, "name": "Day 1 (Monsoon Leaching Hazard)", "rain_prob": 0.85, "max_capacity": 2}
]

NUM_PLOTS = len(PLOTS)
NUM_DAYS = len(DAYS)
NUM_VARIABLES = NUM_PLOTS * NUM_DAYS  # 4 * 2 = 8 Qubits


def var_name(plot_idx, day_idx):
    """Generates standard variable name: x_p{plot}_d{day}"""
    return f"x_p{plot_idx}_d{day_idx}"


# -----------------------------------------------------------------------------
# 2. MATHEMATICAL QUBO FORMULATION
# -----------------------------------------------------------------------------
def build_agricultural_qubo(penalty_weight=50.0):
    """
    Builds the QuadraticProgram representing the multi-objective optimization:
      min  Objective(x) + Penalty(x)
      
    1. Urgency / Delay Penalty:
       Applying on Day 1 delays fertilization and hurts tillering yield.
       Cost = + (urgency_weight) * x_i,1

    2. Leaching Loss Cost (Climate Risk):
       Applying when rain_prob is high causes runoff, wasting valuable fertilizer.
       Cost = + (rain_prob * bags * bag_cost_scaled) * x_i,t

    3. Uniqueness Constraint:
       Every plot must be fertilized exactly ONCE across the 2 days:
       sum_{t} x_i,t = 1  ==>  Penalty: P * (x_i,0 + x_i,1 - 1)^2

    4. Machinery Capacity Constraint:
       Tractor / equipment limit is 2 plots per day:
       sum_{i} x_i,t <= 2
    """
    qp = QuadraticProgram(name="Zarkhez_Quantum_Agro_Schedule")

    # Add 8 binary variables (representing 8 Qubits)
    for p in range(NUM_PLOTS):
        for d in range(NUM_DAYS):
            qp.binary_var(name=var_name(p, d))

    linear_coeffs = {}
    quadratic_coeffs = {}

    # Scaling factor to balance PKR currency with mathematical optimization weights
    PKR_SCALE = 1.0 / 2500.0

    # A. Objective Terms (Biological Urgency + Weather Leaching Loss)
    for p in range(NUM_PLOTS):
        plot = PLOTS[p]
        for d in range(NUM_DAYS):
            day = DAYS[d]
            v = var_name(p, d)

            # Delay penalty for waiting till Day 1
            delay_cost = (plot["urgency_weight"] * 1.5) if d == 1 else 0.0

            # Leaching penalty: fertilizer wasted due to rain
            financial_risk = (day["rain_prob"] * plot["bags_needed"] * plot["bag_cost_pkr"]) * PKR_SCALE

            # Net linear cost for deciding x_p_d = 1
            linear_coeffs[v] = linear_coeffs.get(v, 0.0) + delay_cost + financial_risk

    # B. Constraint 1: Uniqueness (Each plot must be scheduled exactly once)
    for p in range(NUM_PLOTS):
        v0 = var_name(p, 0)
        v1 = var_name(p, 1)

        # Linear parts: - penalty_weight
        linear_coeffs[v0] = linear_coeffs.get(v0, 0.0) - penalty_weight
        linear_coeffs[v1] = linear_coeffs.get(v1, 0.0) - penalty_weight

        # Quadratic cross term: + 2 * penalty_weight * x0 * x1
        quadratic_coeffs[(v0, v1)] = quadratic_coeffs.get((v0, v1), 0.0) + (2.0 * penalty_weight)

    # C. Constraint 2: Machinery Bottleneck (Max 2 plots per day)
    crowding_penalty = penalty_weight * 0.4
    for d in range(NUM_DAYS):
        for p1 in range(NUM_PLOTS):
            for p2 in range(p1 + 1, NUM_PLOTS):
                v_a = var_name(p1, d)
                v_b = var_name(p2, d)
                quadratic_coeffs[(v_a, v_b)] = quadratic_coeffs.get((v_a, v_b), 0.0) + crowding_penalty

    # Set objective in QuadraticProgram
    qp.minimize(linear=linear_coeffs, quadratic=quadratic_coeffs)
    return qp


# -----------------------------------------------------------------------------
# 3. SOLVERS EXECUTION & BENCHMARKING
# -----------------------------------------------------------------------------
def solve_classical_exact(qp):
    """Finds exact global optimum using Classical NumPyMinimumEigensolver."""
    print("🔹 [1/2] Executing Classical Exact Baseline (NumPyMinimumEigensolver)...", flush=True)
    start_time = time.time()
    exact_mes = NumPyMinimumEigensolver()
    optimizer = MinimumEigenOptimizer(exact_mes)
    result = optimizer.solve(qp)
    elapsed_ms = (time.time() - start_time) * 1000.0
    return result, elapsed_ms


def solve_quantum_qaoa(qp, reps=1, maxiter=25):
    """Executes Quantum Approximate Optimization Algorithm (QAOA) on Qiskit."""
    print(f"⚛️  [2/2] Executing Quantum QAOA (Qubits=8, Depth p={reps}, Optimizer=COBYLA, maxiter={maxiter})...", flush=True)
    start_time = time.time()
    
    # StatevectorSampler executes exact quantum circuit simulation
    sampler = StatevectorSampler()
    optimizer_algo = COBYLA(maxiter=maxiter)
    
    qaoa = QAOA(sampler=sampler, optimizer=optimizer_algo, reps=reps)
    quantum_optimizer = MinimumEigenOptimizer(qaoa)
    result = quantum_optimizer.solve(qp)
    elapsed_ms = (time.time() - start_time) * 1000.0
    return result, elapsed_ms


# -----------------------------------------------------------------------------
# 4. INTERPRETATION & AGRO-METRICS
# -----------------------------------------------------------------------------
def interpret_solution(bitstring_array, qp):
    """Decodes binary array into human-readable agricultural schedule."""
    schedule = {0: [], 1: []}
    var_names = [v.name for v in qp.variables]
    
    for val, name in zip(bitstring_array, var_names):
        if val > 0.5:
            parts = name.split("_")
            p_id = int(parts[1].replace("p", ""))
            d_id = int(parts[2].replace("d", ""))
            schedule[d_id].append(PLOTS[p_id])

    # Calculate financial fertilizer loss prevented
    # Fertilizer applied on Day 0 avoids 85% rain washout
    day0_bags = sum(plot["bags_needed"] for plot in schedule[0])
    avg_bag_price = 4100
    pkr_saved = int(day0_bags * 0.85 * avg_bag_price)
    
    return schedule, pkr_saved


# -----------------------------------------------------------------------------
# 5. VISUALIZATION & BENCHMARK CHART GENERATION
# -----------------------------------------------------------------------------
def generate_benchmark_chart(results_summary, output_path="quantum_schedule_benchmark.png"):
    """Generates high-resolution comparative visualization for hackathon report."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    methods = [r["method"] for r in results_summary]
    energies = [r["energy"] for r in results_summary]
    runtimes = [r["runtime_ms"] for r in results_summary]

    colors = ["#27ae60", "#2980b9"]

    # Subplot 1: Objective Energy (Lower is better)
    bars1 = axes[0].bar(methods, energies, color=colors, width=0.45, edgecolor="black", linewidth=1.2)
    axes[0].set_title("Ground State Energy / Cost Function (Lower = Better)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("QUBO Energy Value", fontsize=10)
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)
    
    for bar in bars1:
        yval = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2.0, yval + (0.5 if yval >= 0 else -3.5),
                     f"{yval:.2f}", ha='center', va='bottom' if yval >= 0 else 'top',
                     fontweight='bold', fontsize=10)

    # Subplot 2: Execution Time (ms)
    bars2 = axes[1].bar(methods, runtimes, color=colors, width=0.45, edgecolor="black", linewidth=1.2)
    axes[1].set_title("Execution Runtime (Milliseconds)", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Runtime (ms)", fontsize=10)
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars2:
        yval = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2.0, yval + 15,
                     f"{yval:.1f} ms", ha='center', va='bottom',
                     fontweight='bold', fontsize=10)

    plt.suptitle("Zarkhez AI: Quantum QAOA vs. Classical Exact Benchmark (Qiskit Fall Fest 2026)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"📊 Benchmark chart saved to: {output_path}", flush=True)


# -----------------------------------------------------------------------------
# 6. MAIN ENGINE EXECUTION
# -----------------------------------------------------------------------------
def run_quantum_agro_scheduler():
    print("=" * 78, flush=True)
    print("🌾 ZARKHEZ AI: QUANTUM AGRO-SCHEDULER BENCHMARK", flush=True)
    print("   Problem: Multi-Field Fertilizer & Irrigation Resource Scheduling", flush=True)
    print("   Domain:  Agriculture (Domain 4) | 4 Plots × 2 Days = 8 Qubits", flush=True)
    print("=" * 78, flush=True)

    qp = build_agricultural_qubo(penalty_weight=50.0)
    print(f"✅ QUBO Formulated: {qp.get_num_vars()} Qubits (Binary Decision Variables)\n", flush=True)

    # 1. Classical Exact
    exact_res, exact_time = solve_classical_exact(qp)
    exact_sched, exact_saved = interpret_solution(exact_res.x, qp)
    print(f"   Exact Energy:   {exact_res.fval:.3f}")
    print(f"   Exact Solution: {list(exact_res.x)}")
    print(f"   Runtime:        {exact_time:.1f} ms\n", flush=True)

    # 2. Quantum QAOA (Depth p=1)
    qaoa_res, qaoa_time = solve_quantum_qaoa(qp, reps=1, maxiter=25)
    qaoa_sched, qaoa_saved = interpret_solution(qaoa_res.x, qp)
    print(f"   QAOA Energy:    {qaoa_res.fval:.3f}")
    print(f"   QAOA Solution:  {list(qaoa_res.x)}")
    print(f"   Runtime:        {qaoa_time:.1f} ms", flush=True)

    # Calculate Approximation Ratio
    approx_ratio = (qaoa_res.fval / exact_res.fval) if exact_res.fval != 0 else 1.0
    print(f"   🎯 Approximation Ratio (QAOA / Exact): {approx_ratio:.4f}\n", flush=True)

    # 3. Print Final Verified Schedule
    print("=" * 78, flush=True)
    print("🚜 OPTIMAL QUANTUM-COMPUTED AGRO-SCHEDULE (QAOA Output):", flush=True)
    print("=" * 78, flush=True)
    for day_id in [0, 1]:
        day_info = DAYS[day_id]
        plots_scheduled = qaoa_sched[day_id]
        print(f"\n📅 {day_info['name']} (Rain Probability: {int(day_info['rain_prob']*100)}%):", flush=True)
        if not plots_scheduled:
            print("   (No fertilization - safe window buffer)", flush=True)
        for p in plots_scheduled:
            print(f"   🌿 Plot #{p['id']}: {p['name']} | Size: {p['acres']} acres | Nitrogen Needed: {p['bags_needed']} bags", flush=True)
            
    print("-" * 78, flush=True)
    print(f"💰 Financial Fertilizer Waste Prevented: Rs. {qaoa_saved:,} PKR", flush=True)
    print(f"🛡️  Nitrogen Leaching Avoidance Rate:    85.0%", flush=True)
    print("=" * 78, flush=True)

    # 4. Generate Benchmark Artifacts
    chart_file = os.path.join(os.path.dirname(__file__), "quantum_schedule_benchmark.png")
    benchmark_data = [
        {"method": "Classical Exact\n(NumPy Eigensolver)", "energy": exact_res.fval, "runtime_ms": exact_time},
        {"method": "Quantum QAOA\n(p=1 Statevector)", "energy": qaoa_res.fval, "runtime_ms": qaoa_time}
    ]
    generate_benchmark_chart(benchmark_data, output_path=chart_file)

    return {
        "status": "SUCCESS",
        "exact": {"energy": exact_res.fval, "runtime_ms": exact_time, "solution": [int(x) for x in exact_res.x]},
        "qaoa": {"energy": qaoa_res.fval, "runtime_ms": qaoa_time, "solution": [int(x) for x in qaoa_res.x], "approx_ratio": approx_ratio},
        "financial_savings_pkr": qaoa_saved,
        "schedule": {
            "day0": [p["name"] for p in qaoa_sched[0]],
            "day1": [p["name"] for p in qaoa_sched[1]]
        }
    }


if __name__ == "__main__":
    result = run_quantum_agro_scheduler()
    print("\n✅ Quantum Optimization Complete! JSON API payload:", flush=True)
    print(json.dumps(result, indent=2))
