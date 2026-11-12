"""
Generates the High-Resolution System Architecture Diagram for the Qiskit Hackathon Report.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Title
ax.text(50, 95, "ZARKHEZ AI: HYBRID QUANTUM-CLASSICAL AGRI-OPTIMIZATION ARCHITECTURE",
        ha="center", va="center", fontsize=15, fontweight="bold", color="#1a365d")
ax.text(50, 91, "Multi-Field Resource & Fertilizer Scheduling under Climate Risk (Domain 4: Agriculture)",
        ha="center", va="center", fontsize=11, fontstyle="italic", color="#4a5568")

# 1. Front-End / Ingestion Layer (Left)
box1 = patches.FancyBboxPatch((4, 52), 26, 32, boxstyle="round,pad=1.5",
                             edgecolor="#2b6cb0", facecolor="#ebf8ff", linewidth=2)
ax.add_patch(box1)
ax.text(17, 80, "FARMER / COOPERATIVE INTERFACE", ha="center", va="center", fontsize=10, fontweight="bold", color="#2b6cb0")
ax.text(17, 73, "• Voice-First Colloquial Urdu", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(17, 67, "• Multi-Field Acreage Data", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(17, 61, "• Crop Phenology Stage", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(17, 55, "• Machinery / Tractor Limits", ha="center", va="center", fontsize=9, color="#2d3748")

# 2. FastMCP Orchestrator & Telemetry (Center-Top)
box2 = patches.FancyBboxPatch((37, 52), 26, 32, boxstyle="round,pad=1.5",
                             edgecolor="#2f855a", facecolor="#f0fff4", linewidth=2)
ax.add_patch(box2)
ax.text(50, 80, "FastMCP AGENT ORCHESTRATOR", ha="center", va="center", fontsize=10, fontweight="bold", color="#2f855a")
ax.text(50, 73, "• Open-Meteo Satellite Rain Prob", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(50, 67, "• Nitrogen Leaching Hazard Model", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(50, 61, "• Zarkhez Agronomy Dosage Engine", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(50, 55, "• QUBO Matrix Mathematical Builder", ha="center", va="center", fontsize=9, color="#2d3748")

# 3. Qiskit Quantum Engine (Center-Bottom)
box3 = patches.FancyBboxPatch((37, 8), 26, 36, boxstyle="round,pad=1.5",
                             edgecolor="#6b46c1", facecolor="#faf5ff", linewidth=2)
ax.add_patch(box3)
ax.text(50, 40, "⚛️ QISKIT QUANTUM SOLVER", ha="center", va="center", fontsize=11, fontweight="bold", color="#6b46c1")
ax.text(50, 34, "• Problem Mapping to 8 Qubits", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(50, 28, "• Ising Hamiltonian Formulation", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(50, 22, "• QAOA Variational Circuit (p=1)", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(50, 16, "• StatevectorSampler / Aer Sim", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(50, 10, "• Classical Exact NumPy Baseline", ha="center", va="center", fontsize=9, color="#2d3748")

# 4. Actionable Fulfillment & Fintech (Right)
box4 = patches.FancyBboxPatch((70, 52), 26, 32, boxstyle="round,pad=1.5",
                             edgecolor="#c05621", facecolor="#fffaf0", linewidth=2)
ax.add_patch(box4)
ax.text(83, 80, "ACTION & FULFILLMENT", ha="center", va="center", fontsize=10, fontweight="bold", color="#c05621")
ax.text(83, 73, "• Optimal Schedule Dispatched", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(83, 67, "• Rs. 87,125 Fertilizer Saved", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(83, 61, "• 85% Runoff Loss Prevented", ha="center", va="center", fontsize=9, color="#2d3748")
ax.text(83, 55, "• FasalPay BNPL Credit Sync", ha="center", va="center", fontsize=9, color="#2d3748")

# Arrows
arrow_kw = dict(arrowstyle="->", lw=2.5, color="#4a5568")

# Box1 -> Box2
ax.annotate("", xy=(37, 68), xytext=(30, 68), arrowprops=arrow_kw)
ax.text(33.5, 71, "Input", ha="center", fontsize=8, fontweight="bold", color="#4a5568")

# Box2 -> Box3
ax.annotate("", xy=(50, 44), xytext=(50, 52), arrowprops=arrow_kw)
ax.text(54, 48, "QUBO", ha="center", fontsize=8, fontweight="bold", color="#6b46c1")

# Box3 -> Box2
ax.annotate("", xy=(58, 52), xytext=(58, 44), arrowprops=dict(arrowstyle="->", lw=2, color="#6b46c1", linestyle="--"))
ax.text(65, 48, "QAOA Result", ha="center", fontsize=8, color="#6b46c1")

# Box2 -> Box4
ax.annotate("", xy=(70, 68), xytext=(63, 68), arrowprops=arrow_kw)
ax.text(66.5, 71, "Execute", ha="center", fontsize=8, fontweight="bold", color="#4a5568")

# Footer
ax.text(50, 2, "Qiskit Fall Fest 2026 Hackathon | Domain 4: Agriculture | Team Zarkhez AI",
        ha="center", va="center", fontsize=9, color="#718096")

output_file = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")
plt.tight_layout()
plt.savefig(output_file, bbox_inches="tight")
print(f"Architecture diagram saved to: {output_file}")
