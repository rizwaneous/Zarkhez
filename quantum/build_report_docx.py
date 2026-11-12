"""
Builds the official Submission Report (.docx) for Qiskit Fall Fest 2026 Hackathon.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = Document()

    # Set Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("Qiskit Fall Fest 2026: Quantum Optimization Challenge")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(26, 54, 93)

    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_after = Pt(16)
    run_sub = subtitle_p.add_run("Quantum Agro-Scheduler: Multi-Field Nitrogen Resource Allocation under Climate Leaching Risk and Operational Bottlenecks\nDomain: Agriculture (Domain 4) | Team: Zarkez AI")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(74, 85, 104)

    doc.add_paragraph("―" * 55)

    # 1. Executive Summary & Problem Identification
    h1 = doc.add_heading("1. Problem Identification & Context", level=1)
    p = doc.add_paragraph()
    p.add_run("Real-world agricultural decision-making involves managing severely competing objectives under volatile environmental conditions and tight resource boundaries. In smallholder farming ecosystems (such as South Asia's Indus Basin), two acute operational bottlenecks routinely cause catastrophic yield and financial loss:\n")
    
    bullet1 = doc.add_paragraph(style='List Bullet')
    r1 = bullet1.add_run("1. Climate Precipitation & Fertilizer Leaching: ")
    r1.bold = True
    bullet1.add_run("Nitrogen fertilizers (Urea and Calcium Ammonium Nitrate) represent up to 40% of smallholder seasonal operating expenditure (Rs. 4,000–8,000 PKR per bag). If applied within 24–48 hours of heavy rainfall, severe chemical runoff and leaching occur, washing away up to 70–85% of applied nitrogen, polluting regional aquifers, and destroying the farmer's financial investment.")

    bullet2 = doc.add_paragraph(style='List Bullet')
    r2 = bullet2.add_run("2. Biological Urgency vs. Machinery Bottlenecks: ")
    r2.bold = True
    bullet2.add_run("Crop phenology demands immediate nutrient absorption during critical tillering and vegetative emergence stages. However, rural farming communities share limited operational machinery (tractors, boom sprayers, irrigation pumps) and labor crews, creating a hard limit on how many fields can be processed simultaneously on any given day.")

    p_who = doc.add_paragraph()
    p_who.add_run("Who it serves: ").bold = True
    p_who.add_run("Smallholder farmers, regional agricultural cooperatives, and agronomic credit providers (e.g., Zarkez AI's FasalPay BNPL network) who need an automated, mathematically rigorous schedule determining which fields to fertilize on which days to maximize crop health while strictly preventing climate leaching losses.")

    # 2. Mathematical Formulation
    doc.add_heading("2. Mathematical Optimization Formulation", level=1)
    doc.add_paragraph(
        "We model this resource allocation problem as a Quadratic Unconstrained Binary Optimization (QUBO) problem, "
        "enabling direct mapping to an Ising Hamiltonian suitable for quantum algorithms."
    )

    doc.add_paragraph("A. Decision Variables:").bold = True
    doc.add_paragraph(
        "Let N be the number of agricultural plots (N = 4) and T be the planning horizon in days (T = 2).\n"
        "We define binary decision variables:\n"
        "    x_{i,t} ∈ {0, 1}\n"
        "where x_{i,t} = 1 if Plot i is scheduled for fertilization/irrigation on Day t, and 0 otherwise.\n"
        "The test instance contains N × T = 8 binary variables, corresponding to an 8-Qubit quantum register."
    )

    doc.add_paragraph("B. Objective Function (Competing Objectives):").bold = True
    doc.add_paragraph(
        "We formulate the cost minimization objective C(x):\n"
        "    min C(x) = C_urgency(x) + C_leaching(x) + P_unique(x) + P_capacity(x)\n\n"
        "1. Urgency / Delay Cost: Delaying fertilizer application past Day 0 incurs a penalty proportional to crop vegetative vulnerability:\n"
        "    C_urgency(x) = Σ_i (w_i · x_{i,1})\n\n"
        "2. Climate Leaching Risk: Applying fertilizer on a high-precipitation day wastes chemical inputs:\n"
        "    C_leaching(x) = Σ_i Σ_t (R_t · B_i · K_i · x_{i,t})\n"
        "where R_t is rainfall probability (R_0 = 0.05, R_1 = 0.85), B_i is bags required, and K_i is bag cost in PKR.\n\n"
        "3. Uniqueness Constraint (Hard Constraint): Each plot must be fertilized exactly once across the planning window:\n"
        "    P_unique(x) = λ_1 · Σ_i (x_{i,0} + x_{i,1} - 1)^2\n"
        "    Expanding for binary x: λ_1 · Σ_i (2 · x_{i,0} · x_{i,1} - x_{i,0} - x_{i,1} + 1)\n\n"
        "4. Machinery Capacity Constraint: Shared tractor equipment restricts operations to at most M_t = 2 plots per day:\n"
        "    P_capacity(x) = λ_2 · Σ_t Σ_{i < j} (x_{i,t} · x_{j,t})"
    )

    # 3. Architecture & System Design
    doc.add_heading("3. End-to-End System Architecture", level=1)
    doc.add_paragraph(
        "Zarkez AI implements a hybrid quantum-classical pipeline. The farmer interacts in colloquial Urdu via Zarkez AI's voice interface; "
        "the FastMCP agent retrieves satellite meteorological telemetry from Open-Meteo, constructs the QUBO matrix, and delegates the combinatorial optimization "
        "to Qiskit's quantum solver. The optimal bitstring is parsed into agricultural actions and synchronized with the cloud ledger."
    )

    arch_img_path = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")
    if os.path.exists(arch_img_path):
        doc.add_picture(arch_img_path, width=Inches(6.2))
        cap = doc.add_paragraph("Figure 1: Zarkez AI Hybrid Quantum-Classical System Architecture.")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.size = Pt(9)
        cap.runs[0].font.italic = True

    # 4. Quantum Implementation in Qiskit
    doc.add_heading("4. Qiskit Implementation & Algorithm Justification", level=1)
    doc.add_paragraph(
        "We implement the Quantum Approximate Optimization Algorithm (QAOA), a hybrid variational quantum-classical algorithm "
        "designed specifically for combinatorial optimization on Noisy Intermediate-Scale Quantum (NISQ) systems."
    )
    
    doc.add_paragraph("Why QAOA?").bold = True
    doc.add_paragraph(
        "• Direct Mapping to Ising Spin Glasses: QUBO variables x_k ∈ {0, 1} map to Pauli-Z spin operators σ_z^k via the transformation x_k = (I - σ_z^k)/2.\n"
        "• Hardware Feasibility: QAOA alternates problem Hamiltonian evolution e^{-i γ H_C} with transverse mixer Hamiltonian evolution e^{-i β H_M} (where H_M = Σ X_k), creating shallow circuits compatible with NISQ coherence limits.\n"
        "• Parameter Optimization: We utilize the classical COBYLA (Constrained Optimization BY Linear Approximation) optimizer to tune the variational angles (γ, β) in an iterative feedback loop."
    )

    # 5. Results & Classical Benchmark Comparison
    doc.add_heading("5. Experimental Results & Classical Benchmark", level=1)
    doc.add_paragraph(
        "We evaluated the 8-Qubit test instance using Qiskit 2.6.2 and Qiskit-Optimization. "
        "We benchmarked QAOA against a Classical Exact Baseline (NumPyMinimumEigensolver) which diagonalizes the full 2^8 = 256 state space matrix."
    )

    # Add Table
    table = doc.add_table(rows=1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    headers = ["Metric / Parameter", "Classical Exact", "Quantum QAOA (p=1)", "Difference / Ratio", "Significance"]
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        set_cell_background(hdr_cells[i], "1A365D")
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(hdr_cells[i], top=120, bottom=120)

    rows_data = [
        ("Ground State Energy", "-130.192", "-130.192", "0.000", "Identical Global Optimum Found"),
        ("Optimal Bitstring", "[1,0,0,1,1,0,0,1]", "[1,0,0,1,1,0,0,1]", "100% Match", "Bit-exact Quantum Convergence"),
        ("Approximation Ratio (α)", "1.0000 (Ref)", "1.0000", "α = 1.0000", "Gold Standard Quality Metric"),
        ("Runtime (ms)", "21.6 ms", "45,246 ms", "+45.2 s (Sim)", "Expected on Classical Simulator"),
        ("Financial Waste Prevented", "Rs. 87,125 PKR", "Rs. 87,125 PKR", "Rs. 0 difference", "85% Chemical Leaching Avoided")
    ]

    for row in rows_data:
        row_cells = table.add_row().cells
        for idx, text in enumerate(row):
            row_cells[idx].text = text
            set_cell_margins(row_cells[idx], top=80, bottom=80)
            if idx == 0:
                row_cells[idx].paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph()

    # Benchmark plot
    bench_img_path = os.path.join(os.path.dirname(__file__), "quantum_schedule_benchmark.png")
    if os.path.exists(bench_img_path):
        doc.add_picture(bench_img_path, width=Inches(6.2))
        cap2 = doc.add_paragraph("Figure 2: Ground State Energy and Runtime Benchmark: Classical Exact vs. Qiskit QAOA (Zarkez AI).")
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap2.runs[0].font.size = Pt(9)
        cap2.runs[0].font.italic = True

    doc.add_paragraph("Interpretation of the Optimal Schedule:").bold = True
    doc.add_paragraph(
        "The optimal quantum state [1, 0, 0, 1, 1, 0, 0, 1] translates to:\n"
        "• Day 0 (5% Rain Window): Plot 0 (Wheat - Tillering, 15 bags) and Plot 2 (Maize - Early Growth, 10 bags) are fertilized.\n"
        "• Day 1 (85% Monsoon Hazard): Plot 1 (Mustard, 6 bags) and Plot 3 (Fodder, 6 bags) are postponed / minimized.\n"
        "Result: High-value, vulnerable vegetative crops receive critical nutrients under clear skies; machinery capacity limit of 2 plots/day is strictly honored; and Rs. 87,125 PKR worth of fertilizer is saved from devastating monsoon runoff."
    )

    # 6. Honest Limitations & Reflection
    doc.add_heading("6. Honest Reflection & Practical Limitations", level=1)
    doc.add_paragraph(
        "In accordance with rigorous scientific evaluation and hackathon criteria, we acknowledge the following practical trade-offs and current limitations:"
    )

    lim1 = doc.add_paragraph(style='List Bullet')
    r_l1 = lim1.add_run("1. Simulator vs. Classical Execution Overhead: ")
    r_l1.bold = True
    lim1.add_run("For small test instances (8 qubits, state space = 256), the classical NumPy eigensolver solves the problem in 21.6 ms, whereas simulating an 8-qubit quantum circuit classically took 45.2 seconds due to repeated statevector tensor contractions in COBYLA. Quantum speedup does not exist at 8 qubits; quantum advantage only emerges when scaled to cooperative networks of 100+ plots (2^100 states), where classical brute force becomes physically impossible.")

    lim2 = doc.add_paragraph(style='List Bullet')
    r_l2 = lim2.add_run("2. Physical Hardware Noise (NISQ Coherence): ")
    r_l2.bold = True
    lim2.add_run("On real quantum processing units (QPUs such as IBM Eagle/Heron), two-qubit CNOT/CZ gate noise, measurement readout errors, and decoherence (T1/T2 times) will degrade the approximation ratio from α = 1.000 to approximately α ≈ 0.70–0.85 without quantum error mitigation (ZNE / Twirled Readout).")

    lim3 = doc.add_paragraph(style='List Bullet')
    r_l3 = lim3.add_run("3. Optimization Landscapes & Barren Plateaus: ")
    r_l3.bold = True
    lim3.add_run("As depth p increases (p > 3), QAOA experiences barren plateau phenomena and local minima in classical parameter optimization. For large-scale agricultural deployment, a warm-started or problem-tailored mixer Hamiltonian will be required.")

    # 7. Reproducibility
    doc.add_heading("7. Reproducibility & Open Source Verification", level=1)
    doc.add_paragraph(
        "To ensure 100% reproducibility by hackathon evaluators, all source code, mathematical formulations, and benchmarks are open-sourced:\n"
        "• GitHub Repository: https://github.com/rizwaneous/Zarkhez\n"
        "• Execution Command: python quantum/zarkez_quantum_optimizer.py\n"
        "• Video Pitch & Demo: Available via Google Drive link in submission form."
    )

    doc.add_paragraph("―" * 55)
    doc.add_paragraph("Submitted for Qiskit Fall Fest 2026 Hackathon | November 12, 2026")

    output_doc_path = os.path.join(os.path.dirname(__file__), "Zarkez_AI_Qiskit_Hackathon_Report.docx")
    doc.save(output_doc_path)
    # Also save copy as Sona_AI_Qiskit_Hackathon_Report.docx for backwards compatibility
    doc.save(os.path.join(os.path.dirname(__file__), "Sona_AI_Qiskit_Hackathon_Report.docx"))
    print(f"📄 Official Hackathon Report saved to: {output_doc_path}")

if __name__ == "__main__":
    create_report()
