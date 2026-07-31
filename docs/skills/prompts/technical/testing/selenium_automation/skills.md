# Domain Agent Skills: Technical Testing Selenium automation

## Metadata
- **Domain Namespace:** technical.testing.selenium_automation
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Security Testing: OWASP ZAP Integration
<!-- VALIDATION_METADATA: {"variables": [], "metadata": {}} -->
### Description
Configure Selenium to route traffic through the OWASP ZAP proxy for security scanning.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| None | | | |


### Core Instructions
```text
[SYSTEM]
Write a Java snippet to configure ChromeOptions and DesiredCapabilities to route traffic through a local proxy at localhost:8888. Ensure the configuration accepts insecure SSL certificates to allow for ZAP interception and scanning.

[USER]
Configure Chrome WebDriver to proxy through ZAP (localhost:8888) and ignore SSL errors.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['setProxy']
```

---

## Skill: Synchronization Strategy: Explicit Waits
<!-- VALIDATION_METADATA: {"variables": [{"name": "code_snippet", "description": "The source code to analyze or modify", "required": true}, {"name": "code", "description": "Auto-extracted variable code", "required": false}], "metadata": {}} -->
### Description
Replace brittle Thread.sleep() calls with dynamic Explicit or Fluent waits.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `code_snippet` | String | The source code to analyze or modify | Yes |
| `code` | String | Auto-extracted variable code | No |


### Core Instructions
```text
[SYSTEM]
Refactor the provided Selenium script (Java or Python) to remove all 'time.sleep()' or 'Thread.sleep()' calls. Replace them with WebDriverWait using 'ExpectedConditions'. Specifically, wait for elements to be visible or clickable (e.g., an ID like 'submit-btn' or 'dynamic-content') with a defined timeout (e.g., 10-15 seconds) and handle potential TimeoutExceptions gracefully.

[USER]
Refactor the following code to use Explicit Waits:

<code>
{{ code_snippet }}
</code>
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['WebDriverWait wait']
```

---

## Skill: Selenium Migration: Script Conversion
<!-- VALIDATION_METADATA: {"variables": [{"name": "package_name", "description": "The name or identifier", "required": true}, {"name": "selenese_code", "description": "The source code to analyze or modify", "required": true}], "metadata": {}} -->
### Description
Translate recorded browser actions (Selenese) from Selenium IDE into structured Java test scripts.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `package_name` | String | The name or identifier | Yes |
| `selenese_code` | String | The source code to analyze or modify | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Selenium developer. Analyze the provided Selenese HTML or project file and convert the commands into a functional Java test class. Use the Page Object Model (POM) pattern, include explicit WebDriverWait commands for each interaction, and ensure compatibility with TestNG or JUnit. Refactor any hardcoded pauses into ExpectedConditions and ensure correct imports (e.g., from com.thoughtworks.selenium or Selenium 4).

[USER]
Convert the following Selenese code/script to a robust Java Selenium test class.

<selenese_code>
{{ selenese_code }}
</selenese_code>

<package_name>
{{ package_name }}
</package_name>
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['public class LoginTest {']
```

---

## Skill: Driver Configuration: WebDriver Initialization
<!-- VALIDATION_METADATA: {"variables": [{"name": "browser", "description": "The target browser (e.g., Chrome, Firefox)", "required": true}, {"name": "proxy_url", "description": "The URL to process or reference", "required": true}], "metadata": {}} -->
### Description
Initialize and configure WebDriver instances with specific browser options.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `browser` | String | The target browser (e.g., Chrome, Firefox) | Yes |
| `proxy_url` | String | The URL to process or reference | Yes |


### Core Instructions
```text
[SYSTEM]
Write a script to initialize a WebDriver (e.g., InternetExplorerDriver or ChromeDriver) using Capabilities/Options. Configure proxy settings for HTTP, FTP, and SSL (e.g., 'localhost:8080'). If using Selenium Base, provide the 'sbase' command to install the latest driver executable to the correct directory.

[USER]
Create a WebDriver initialization script with the following requirements.

Browser: {{ browser }}
Proxy: {{ proxy_url }}
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['ChromeOptions']
```

---

## Skill: Framework Best Practices: Locator Strategy
<!-- VALIDATION_METADATA: {"variables": [{"name": "locators", "description": "The locators to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Transition from brittle XPaths to robust locators like ID or CSS selectors.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `locators` | String | The locators to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
Review the provided code snippet containing dynamic or brittle XPaths (e.g., '//div@class="dynamic-class"'). Refactor the locators to use By.id, CSS selectors targeting data-action attributes, or other robust selection strategies as per best practices.

[USER]
Optimize the following Selenium locators for stability.

<locators>
{{ locators }}
</locators>
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['By.id']
```

---

## Skill: Architecture Design: Page Object Model
<!-- VALIDATION_METADATA: {"variables": [{"name": "html_source", "description": "The html source to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Implement the Page Object Model pattern to separate UI locators from test logic.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `html_source` | String | The html source to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
Act as a Selenium automation expert. Create a Java class following the Page Object Model (POM) for a 'Login' page based on the provided HTML source or specifications. Use @FindBy annotations or private By locators for fields (username, password, login button) and implement public methods (e.g., 'loginValidUser') that return appropriate page objects. Ensure the constructor initializes elements using PageFactory.initElements.

[USER]
Create a POM class for the following page source/spec:

<html_source>
{{ html_source }}
</html_source>
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['@FindBy(id = ']
```

---

## Skill: Advanced Design Patterns: Fluent Interface
<!-- VALIDATION_METADATA: {"variables": [{"name": "java_class", "description": "The java class to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Extend Page Objects with method chaining to create a more readable test API.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `java_class` | String | The java class to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
Modify existing Page Object classes to implement a Fluent Interface. Ensure that every method performing an action (e.g., 'setUsername', 'setPassword') returns 'this' (the current page instance). Create an example test method demonstrating action chaining: page.open().login('user', 'pass').verifySuccess();.

[USER]
Refactor the following Page Object to use a Fluent Interface.

<java_class>
{{ java_class }}
</java_class>
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['public LoginPage setUsername']
```

---

## Skill: Cross-Browser Infrastructure: Selenium Grid
<!-- VALIDATION_METADATA: {"variables": [{"name": "browser_count", "description": "The browser count to use for this prompt", "required": true}, {"name": "grid_version", "description": "The grid version to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Configure a Selenium Grid Hub and Nodes to distribute test execution.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `browser_count` | String | The browser count to use for this prompt | Yes |
| `grid_version` | String | The grid version to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
Provide the command-line instructions to initialize a Selenium Grid (2.0 or 4.0) infrastructure. Show how to launch a hub on port 4444 and register a node that supports multiple instances of Chrome and Firefox. Include parameters for platform settings and explain how to verify registration via terminal output or the Grid console.

[USER]
Provide instructions for setting up Selenium Grid {{ grid_version }} with {{ browser_count }} nodes for Chrome and Firefox.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['java -jar selenium-server']
```

---

## Skill: Test Environment: Python & Selenium Base
<!-- VALIDATION_METADATA: {"variables": [], "metadata": {}} -->
### Description
Install the Selenium Base framework and environment using the Python package manager.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| None | | | |


### Core Instructions
```text
[SYSTEM]
Using pip3, provide the command to install the 'selenium-base' package within a Python virtual environment and explain how to verify the installation with the 'sbase' command.

[USER]
Provide instructions to set up SeleniumBase in a python virtual environment.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['pip install seleniumbase']
```

---

## Skill: Framework Implementation: Data-Driven Testing
<!-- VALIDATION_METADATA: {"variables": [], "metadata": {}} -->
### Description
Utilize data providers to execute the same test logic with multiple sets of data.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| None | | | |


### Core Instructions
```text
[SYSTEM]
Write a TestNG @DataProvider method in Java that returns a 2D object array of credentials (usernames/passwords) and map it to a @Test method to perform data-driven login verification.

[USER]
Create a data-driven test for login functionality using TestNG DataProvider.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['@DataProvider']
```

---

## Skill: Project Configuration: Maven Setup
<!-- VALIDATION_METADATA: {"variables": [{"name": "java_version", "description": "The java version to use for this prompt", "required": true}, {"name": "test_framework", "description": "The test framework to use for this prompt", "required": true}, {"name": "artifactId", "description": "Auto-extracted variable artifactId", "required": false}], "metadata": {}} -->
### Description
Set up a Maven project structure and pom.xml file with necessary Selenium client libraries.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `java_version` | String | The java version to use for this prompt | Yes |
| `test_framework` | String | The test framework to use for this prompt | Yes |
| `artifactId` | String | Auto-extracted variable artifactId | No |


### Core Instructions
```text
[SYSTEM]
Generate a Maven pom.xml file for a Java-based Selenium automation project. Include dependencies for 'selenium-java', 'testng' or 'junit', and 'webdrivermanager'. Configure the 'maven-surefire-plugin' for parallel execution, set the modelVersion to 4.0.0, and specify Java compiler source/target versions (e.g., 1.8 or 11) as required.

[USER]
Generate a pom.xml for a Selenium project.

Target Java Version: {{ java_version }}
Test Framework: {{ test_framework }}
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['<artifactId>selenium-java</artifactId>']
```

---

## Skill: Reporting and Maintenance: Custom Reports
<!-- VALIDATION_METADATA: {"variables": [{"name": "framework", "description": "The testing framework (e.g., TestNG, JUnit)", "required": true}, {"name": "report_format", "description": "The report format to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Integrate reporting libraries and screenshot utilities to capture execution evidence.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `framework` | String | The testing framework (e.g., TestNG, JUnit) | Yes |
| `report_format` | String | The report format to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
Create a Java listener or utility method to generate test reports (e.g., PDF via iText) or capture screenshots using the 'TakesScreenshot' interface. The output should include test status (PASS/FAIL), execution time, and embedded links to images for failed cases.

[USER]
Implement a Test Listener for reporting and screenshots.

Framework: {{ framework }}
Report Format: {{ report_format }}
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['implements ITestListener']
```

---

## Skill: Execution Optimization: Parallel Testing
<!-- VALIDATION_METADATA: {"variables": [{"name": "language", "description": "The programming or natural language to use", "required": true}, {"name": "WebDriver", "description": "Auto-extracted variable WebDriver", "required": false}], "metadata": {}} -->
### Description
Configure the automation suite to execute multiple tests simultaneously.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `language` | String | The programming or natural language to use | Yes |
| `WebDriver` | String | Auto-extracted variable WebDriver | No |


### Core Instructions
```text
[SYSTEM]
Configure a TestNG suite for parallel execution by providing a 'testng.xml' file with the parallel attribute set to 'methods'. Additionally, develop a C# or Java method to ensure thread safety (e.g., using 'ThreadLocal') and a 'Dispose' routine to identify and kill browser processes (chrome, firefox, edge) to maintain a clean state.

[USER]
Create a parallel execution configuration for TestNG and a thread-safe WebDriver factory.

<language>
{{ language }}
</language>
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['ThreadLocal<WebDriver>']
```
