---
title: Topic Generator
---

# Topic Generator

Generates a random topic for a joke.



```yaml
name: Topic Generator
description: Generates a random topic for a joke.
metadata:
  domain: communication
  complexity: low
model: gpt-4o-mini
modelParameters:
  temperature: 0.7
messages:
  - role: system
    content: "You are a creative assistant."
  - role: user
    content: "Give me a random topic for a joke. Output ONLY the topic name."
testData:
  - inputs: {}
    expected: "Chickens"
evaluators: []

```
