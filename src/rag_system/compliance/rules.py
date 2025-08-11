
import re

def lint(text: str) -> list[dict]:
    findings = []

    # Long sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    long = [s for s in sentences if len(s.split()) > 25]
    if long:
        findings.append({
            "ruleId": "sentence-length",
            "title": "Short sentences",
            "message": f"{len(long)} sentence(s) exceed ~25 words. Split and front-load the key point.",
            "severity": "warn",
            "query_for_guideline": "write short sentences"
        })

    # Passive voice (naive)
    passive_matches = re.findall(r'\b(is|are|was|were|been|be|being)\s+\w+ed\b', text, re.IGNORECASE)
    if len(passive_matches) > 3:
        findings.append({
            "ruleId": "active-voice",
            "title": "Use active voice",
            "message": 'Detected several passive constructions. Prefer subject–verb–object with "you" where possible.',
            "severity": "warn",
            "query_for_guideline": "use active voice"
        })

    # Link text
    if re.search(r'click here|read more|learn more', text, re.IGNORECASE):
        findings.append({
            "ruleId": "link-text",
            "title": "Make link text descriptive",
            "message": 'Replace "click here/read more" with meaningful link text that names the target.',
            "severity": "info",
            "query_for_guideline": "write effective links"
        })

    # Jargon
    if re.search(r'utilize|facilitate|leverage|paradigm|robust|synergy', text, re.IGNORECASE):
        findings.append({
            "ruleId": "plain-words",
            "title": "Prefer plain words",
            "message": "Replace jargon with simple, familiar words.",
            "severity": "info",
            "query_for_guideline": "use plain words"
        })
        
    return findings
