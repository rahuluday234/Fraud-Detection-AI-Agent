from crewai import Agent

fraud_detector = Agent(
    role="Fraud Detector",
    goal="Identify fraudulent transactions",
    backstory="AI agent trained to detect fraud in financial datasets.",
    skills=["./skills/fraud-detection"]
)

audit_logger = Agent(
    role="Audit Logger",
    goal="Log suspected frauds into audit trail",
    backstory="Ensures compliance and auditability.",
    skills=["./skills/fraud-detection"]
)

report_agent = Agent(
    role="Report Generator",
    goal="Export suspected frauds into CSV",
    backstory="Prepares shareable fraud detection reports.",
    skills=["./skills/fraud-detection"]
)