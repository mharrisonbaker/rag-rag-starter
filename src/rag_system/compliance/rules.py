import re

def lint(text: str) -> list[dict]:
    findings = []

    # Long sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    long_sentences = [s for s in sentences if len(s.split()) > 25]
    if long_sentences:
        findings.append({
            "ruleId": "sentence-length",
            "title": "Short sentences",
            "message": f"{len(long_sentences)} sentence(s) exceed ~25 words. Split and front-load the key point.",
            "severity": "warn",
            "query_for_guideline": "write short sentences",
            "trigger_text": long_sentences[0] # Add the first long sentence
        })

    # Passive voice (naive)
    passive_matches = list(re.finditer(r'\b(is|are|was|were|been|be|being)\s+\w+ed\b', text, re.IGNORECASE))
    if len(passive_matches) > 3:
        findings.append({
            "ruleId": "active-voice",
            "title": "Use active voice",
            "message": 'Detected several passive constructions. Prefer subject–verb–object with "you" where possible.',
            "severity": "warn",
            "query_for_guideline": "use active voice",
            "trigger_text": passive_matches[0].group(0) # Add the first passive match
        })

    # Link text
    link_text_matches = list(re.finditer(r'click here|read more|learn more', text, re.IGNORECASE))
    if link_text_matches:
        findings.append({
            "ruleId": "link-text",
            "title": "Make link text descriptive",
            "message": 'Replace "click here/read more" with meaningful link text that names the target.',
            "severity": "info",
            "query_for_guideline": "write effective links",
            "trigger_text": link_text_matches[0].group(0) # Add the first link text match
        })

    # Jargon
    jargon_matches = list(re.finditer(r'utilize|facilitate|leverage|paradigm|robust|synergy', text, re.IGNORECASE))
    if jargon_matches:
        findings.append({
            "ruleId": "plain-words",
            "title": "Prefer plain words",
            "message": "Replace jargon with simple, familiar words.",
            "severity": "info",
            "query_for_guideline": "use plain words",
            "trigger_text": jargon_matches[0].group(0) # Add the first jargon word
        })
        
    return findings