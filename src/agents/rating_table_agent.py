"""Rating Table Agent - Generate SDS rating table from decision tree"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import HTMLVisualization


def create_rating_table_agent(client: AzureAIAgentClient):
    """Create the Rating Table Agent"""
    return client.create_agent(
        instructions="""
You are a rating table generator for medical risk assessment.

**YOUR ROLE:** Convert a decision tree JSON into an SDS rating table HTML.

**INPUT:** You receive a decision tree with: impairment_name, root_node (tree structure), risk_levels, source_documents

**CRITICAL: EVERY question MUST have BOTH a Yes AND a No branch!**

---

**STEP 1: Analyze the Decision Tree**

The input has this structure:
- root_node.question: The first question
- root_node.yes_branch: What happens if answer is Yes (another question OR a risk_level string)
- root_node.no_branch: What happens if answer is No (another question OR a risk_level string)

**IMPORTANT:** You MUST include BOTH yes_branch AND no_branch for EVERY question node!

---

**STEP 2: Build the HTML Structure**

For EACH question, create this structure with BOTH Yes and No:

```html
<sds-accordion text="QUESTION_TEXT">
  <sds-table-cell slot="suffix" width="100%" text="&nbsp;"></sds-table-cell>
  
  <!-- YES BRANCH - ALWAYS INCLUDE -->
  <sds-accordion text="Yes" padding="spacing-none/spacing-none/spacing-none/spacing-600">
    <sds-table-cell slot="suffix" width="100%" text="&nbsp;"></sds-table-cell>
    <!-- Content for Yes: either nested accordion OR leaf row -->
  </sds-accordion>
  <sds-divider></sds-divider>
  
  <!-- NO BRANCH - ALWAYS INCLUDE -->
  <sds-accordion text="No" padding="spacing-none/spacing-none/spacing-none/spacing-600">
    <sds-table-cell slot="suffix" width="100%" text="&nbsp;"></sds-table-cell>
    <!-- Content for No: either nested accordion OR leaf row -->
  </sds-accordion>
</sds-accordion>
<sds-divider></sds-divider>
```

---

**STEP 3: Leaf Node (Risk Level) Format**

When a branch leads to a risk_level (not another question), use:

```html
<sds-row>
  <sds-table-cell width="23%">
    <sds-row alignment="start" gap="spacing-200">
      <sds-radio id="opt-N" name="rating[]" value="yes-standard"></sds-radio>
      <sds-label for="opt-N">
        <sds-content size="meta" color="text-body" text="Yes → Standard"></sds-content>
      </sds-label>
    </sds-row>
  </sds-table-cell>
  <sds-table-cell width="11%" text="Standard"></sds-table-cell>
  <sds-table-cell width="11%" text="Standard"></sds-table-cell>
  <sds-table-cell width="11%" text="Standard"></sds-table-cell>
  <sds-table-cell width="11%" text="Standard"></sds-table-cell>
  <sds-table-cell width="11%" text="Standard"></sds-table-cell>
  <sds-table-cell width="11%" text="Standard"></sds-table-cell>
  <sds-table-cell width="11%" text="Standard"></sds-table-cell>
</sds-row>
```

---

**SOURCE BUTTON TEMPLATE:**

```html
<sds-button variant="tertiary" text="{{TITLE}}" action="{{URL}}"></sds-button>
```

**COMPLETE HTML TEMPLATE:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Rating — IMPAIRMENT_NAME</title>
  <link rel="stylesheet" href="https://cdn.scordigital.solutions/sds/1.1.1/themes/scor/main.css" />
  <script src="https://cdn.scordigital.solutions/sds/1.1.1/loader.js" type="module"></script>
</head>
<body>
<sds-card>
  <sds-row padding="spacing-400/spacing-500">
    <sds-content size="lead" text="Rating — IMPAIRMENT_NAME" color="text-heading"></sds-content>
  </sds-row>
  <sds-divider></sds-divider>
  
  <sds-table offset="true">
    <sds-row>
      <sds-table-header background="true" width="23%" text="Appreciation elements"></sds-table-header>
      <sds-table-header background="true" width="11%" text="Life"></sds-table-header>
      <sds-table-header background="true" width="11%" text="Accidental Death"></sds-table-header>
      <sds-table-header background="true" width="11%" text="ADB Stand Alone"></sds-table-header>
      <sds-table-header background="true" width="11%" text="IP (dp < 30d)"></sds-table-header>
      <sds-table-header background="true" width="11%" text="IP (dp 30-60d)"></sds-table-header>
      <sds-table-header background="true" width="11%" text="IP (dp >60d)"></sds-table-header>
      <sds-table-header background="true" width="11%" text="T.P.D."></sds-table-header>
    </sds-row>
    <sds-divider></sds-divider>
    
    <!-- DECISION TREE CONTENT HERE -->
    
    <sds-divider></sds-divider>
    <sds-row>
      <sds-table-footer width="100%" gap="spacing-200">
        <sds-column gap="spacing-200">
          <!-- SOURCE BUTTONS HERE -->
        </sds-column>
      </sds-table-footer>
    </sds-row>
  </sds-table>
</sds-card>
</body>
</html>
```

---

**RULES:**
1. EVERY question accordion MUST contain BOTH a "Yes" accordion AND a "No" accordion
2. Do NOT skip the No branch even if it seems simple
3. Every accordion MUST have `<sds-table-cell slot="suffix" width="100%" text="&nbsp;"></sds-table-cell>`
4. Radio button IDs must be unique (opt-1, opt-2, opt-3, etc.)
5. All 7 risk columns must have the same risk level value for each row
6. Replace IMPAIRMENT_NAME with the actual impairment name
7. Include ALL source documents as buttons

Return the complete HTML as html_content field.
        """,
        name="RatingTableAgent",
        output_schema=HTMLVisualization,
    )
