import os
import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_reviewer_agent():
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    from agents.code_review.reviewer_agent import CodeReviewerAgent
    agent = CodeReviewerAgent()
    
    # Sample code to review
    sample_code = """
def process_data(data):
    # Potential SQL Injection
    query = f"SELECT * FROM users WHERE id = {data['id']}"
    print(f"Executing: {query}")
    
    # Unused variable
    result = "processed"
    
    return data
    """
    
    logger.info("Starting code review test...")
    try:
        # We'll use a dummy file path
        report = await agent.review_file("src/test_sample.py", sample_code)
        
        print("\n=== Code Review Report ===")
        print(f"Quality Score: {report.get('score', 0)}/100")
        print(f"Summary: {report.get('summary', 'No summary')}")
        print("\nIssues Found:")
        for issue in report.get("issues", []):
            print(f"- [{issue.get('severity', 'low').upper()}] {issue.get('file_path', 'unknown')}:{issue.get('line_number', 0)} - {issue.get('issue_type', 'bug')}")
            print(f"  Message: {issue.get('description', 'No description')}")
            print(f"  Fix: {issue.get('suggested_fix', 'No fix')}")
        print("==========================\n")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_reviewer_agent())
