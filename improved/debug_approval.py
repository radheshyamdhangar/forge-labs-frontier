from compliance_agent import ComplianceAgent

agent = ComplianceAgent()
response = agent.process('Who approves a $100,000 loan?', verbose=True)
print(f'\nAnswer: {response.answer[:200]}...')
print(f'Compliant: {response.compliant}')
print(f'Confidence: {response.confidence:.0%}')
print(f'Contains approval: {"approv" in response.answer.lower()}')
print(f'Contains loan: {"loan" in response.answer.lower()}')
