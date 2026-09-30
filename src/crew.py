from crewai import Crew
from agents.agents import fraud_detector, audit_logger, report_agent
from workflows.fraud_detection_workflow as workflow
crew = Crew(
    agents=[fraud_detector, audit_logger, report_agent],
    workflow=workflow.workflow
)

if __name__ == "__main__":
    crew.run()