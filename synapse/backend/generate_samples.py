from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

pdf_path = Path("synapse/backend/sample_data/quantum_computing_whitepaper.pdf")
doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
styles = getSampleStyleSheet()

title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#0f172a'))
h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=13, leading=17, textColor=colors.HexColor('#1e293b'))
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=15, textColor=colors.HexColor('#334155'))

story = []
story.append(Paragraph('Quantum Information Science & Cryogenic Systems', title_style))
story.append(Spacer(1, 10))
story.append(Paragraph('<b>Document Reference:</b> MIT-IBM-Q-2026 | <b>Classification:</b> Peer-Reviewed Research Whitepaper', body_style))
story.append(Spacer(1, 14))

story.append(Paragraph('1. Foundations of Quantum Superposition and Entanglement', h2_style))
story.append(Spacer(1, 6))
story.append(Paragraph('Quantum computing fundamentally diverges from classical von Neumann architectures through principles of quantum superposition and entanglement. Qubits represent linear combinations of orthogonal basis states |0> and |1>. By manipulating phase and amplitude interference, an N-qubit quantum processor calculates over an exponential parameter space of dimension 2^N simultaneously.', body_style))
story.append(Spacer(1, 12))

story.append(Paragraph('2. Cryogenic Engineering and Thermal Noise Mitigation', h2_style))
story.append(Spacer(1, 6))
story.append('Superconducting transmon circuits constructed with submicron Josephson junctions undergo phase transitions into superconducting regimes below critical temperatures. Thermal fluctuations introduce severe quasiparticle excitation, dephasing quantum wavefunctions into classical states. To ensure quantum coherence and avoid decoherence, quantum chips are housed inside multi-stage cryogenic dilution refrigerators cooled to approximately 15 millikelvin (-273.135 degrees Celsius). Concentric copper radiation shields absorb ambient blackbody radiation.')
story[-1] = Paragraph(story[-1], body_style)
story.append(Spacer(1, 12))

story.append(Paragraph('3. Asymmetric Cryptography and Shor Factorization', h2_style))
story.append(Spacer(1, 6))
story.append('Peter Shor algorithm demonstrated that fault-tolerant quantum computers can execute modular exponentiation and order finding in polynomial time O((log N)^3) steps. This capability poses a fundamental existential threat to global public key encryption, including RSA-2048, Diffie-Hellman, and ECDSA. The National Institute of Standards and Technology (NIST) has codified quantum-resilient lattice cryptography standards, including ML-KEM and ML-DSA, to replace classical cryptographic protocols before cryptographically relevant quantum computers arrive.')
story[-1] = Paragraph(story[-1], body_style)

doc.build(story)
print(f"Generated {pdf_path} ({pdf_path.stat().st_size} bytes)")
