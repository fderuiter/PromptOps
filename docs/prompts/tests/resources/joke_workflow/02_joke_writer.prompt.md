---
title: Joke Writer
---

# Joke Writer

Writes a joke about a given topic.



```yaml
name: Joke Writer
description: Writes a joke about a given topic.
metadata:
  domain: communication
  complexity: low
model: gpt-4o-mini
modelParameters:
  temperature: 0.7
variables:
  - name: topic
    description: "The topic of the joke"
messages:
  - role: system
    content: "You are a professional comedian."
  - role: user
    content: "Write a short joke about {{topic}}."
testData:
  - inputs:
      topic: "Chickens"
    expected: "Why did the chicken cross the road? To get to the other side!"
evaluators: []

```
