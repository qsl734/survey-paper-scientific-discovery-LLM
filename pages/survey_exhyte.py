import os
import json
import re
import streamlit as st
from openai import OpenAI
from dateutil import parser

# --------------------------
# Configuration
# --------------------------
JSON_FOLDER = "/home/mdh121/i_created_scripts/paper_summary_pipeline/paper_survey_app/exhyte_data"
st.set_page_config(page_title="Scientific Survey Generator", layout="wide")

# Sidebar: OpenAI API key input
st.sidebar.header("🔑 OpenAI API Key")
openai_api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key:",
    type="password",
    placeholder="sk-...",
)

if not openai_api_key:
    st.sidebar.warning("Please enter your OpenAI API key to generate surveys.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)
# --------------------------
# Streamlit UI
# --------------------------

st.title("Scientific Survey Generator")
st.write("Generate a structured, scientific-style survey from selected JSON paper files.")

# Sidebar header
st.sidebar.header("📂 Select Papers for Survey")

# --------------------------
# Load JSON files and extract titles + year
# --------------------------
available_files = [f for f in os.listdir(JSON_FOLDER) if f.endswith(".json")]

if not available_files:
    st.sidebar.warning(f"No JSON files found in '{JSON_FOLDER}' folder.")
    st.stop()

paper_titles = {}  # title -> filename
paper_years = {}   # title -> year

for file_name in available_files:
    file_path = os.path.join(JSON_FOLDER, file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        title = data.get("paper_title", file_name.replace(".json", ""))
        paper_titles[title] = file_name

        # Extract year robustly
        published_raw = data.get("published", "")
        year = None
        try:
            dt = parser.parse(published_raw, fuzzy=True, default=None)
            if dt:
                year = dt.year
        except Exception:
            match = re.search(r"(\d{4})", published_raw)
            if match:
                year = int(match.group(1))

        paper_years[title] = year
    except Exception:
        paper_titles[file_name.replace(".json", "")] = file_name
        paper_years[file_name.replace(".json", "")] = None

# --------------------------
# Sidebar: Year filter
# --------------------------
available_years = sorted({y for y in paper_years.values() if y is not None}, reverse=True)
selected_years = st.sidebar.multiselect(
    "Filter papers by publication year:",
    options=available_years,
    default=available_years  # show all by default
)

# --------------------------
# Filter paper titles by selected years
# --------------------------
filtered_titles = [
    title for title, year in paper_years.items()
    if year in selected_years
]

# --------------------------
# Paper selection
# --------------------------
selected_titles = st.sidebar.multiselect(
    "Choose one or more papers:",
    options=filtered_titles,
    default=filtered_titles[:2] if filtered_titles else []
)

# --- Define the survey prompt template ---
# survey_prompt_template = """
# You are a scientific writer tasked with summarizing multiple LLM-guided workflow papers from structured JSON files.
# Each JSON file contains information about a workflow, including:

# - Inputs to the Workflow: describe user inputs and research context.
# - E1:Query Structuring- explain how raw queries or tasks are transformed into structured forms.
# - E2:Data Retrieval- summarize how relevant data and literature are collected.
# - E3:Knowledge Assembly- explain how structured knowledge is extracted and represented.
# - H1:Hypothesis/Idea Generation- describe how systems synthesize hypotheses or ideas.
# - H2:Hypothesis or Idea Prioritization- outline how hypotheses are evaluated or ranked.
# - T1:Experimental Design Generation - describe how experiment are designed and executed to test generated ideas or hypotheses.
# - T2:Iterative refinement: Refinement describe feedback and continuous improvement mechanisms.
# - Publication details: paper title, authors, publication date, link

# Your task is to generate a *survey-style, scientific-article summary* comparing the workflows in terms of these stages.

# Follow these rules: I found that survey often time do not include all stages in the workflow. 
# Please make sure it includes all. Even if it has only one papper in one json avalilable. 
# Also make sure paragraph always start with a bold face. 
# 1. Keep the stage definitions explicitly in the text (Inputs, Query Structuring, Data Retrieval, Hypothesis/Idea Generation, Iterative Refinement, Conclusion).
# 2. Integrate information from all JSON files provided.
# 3. Use formal scientific language, in full paragraphs (no bullet points).
# 4. Cite the papers within the paragraph using the authors and year from the JSON files.
# 5. Do not include any information beyond the JSON files.
# 6. End with a References section listing all papers with title, authors, publication date, and link.

# Input:
# Below are the JSON workflow descriptions:

# Output:
# A multi-paragraph, stage-preserving scientific survey comparing the workflows, with in-text citations and a reference list.
# """

survey_prompt_template = """
You are a scientific writer tasked with summarizing multiple LLM-guided workflow papers based on structured JSON files.

Each JSON file contains information about a discovery workflow with the following standardized sections:
1. Inputs to the Workflow
2. E1: Query Structuring
3. E2: Data Retrieval
4. E3: Knowledge Assembly
5. H1: Hypothesis/Idea Generation
6. H2: Hypothesis or Idea Prioritization
7. T1: Experimental Design Generation
8. T2: Iterative Refinement
9. Publication Details (title, authors, publication date, and link)

---

### OBJECTIVE
Generate a *scientific survey-style summary* that compares and synthesizes the workflows from all provided JSON files.

---

### OUTPUT REQUIREMENTS
Your output **must follow the exact same section order and headings** as the input schema, formatted as follows:

**Inputs to the Workflow**  
[Write one or more formal paragraphs integrating all JSONs that describe what users provided — goals, datasets, research context, or formal specifications. Cite papers using author and year.]

**E1: Query Structuring**  
[Summarize how queries or tasks were structured, reformulated, or decomposed. Cite all relevant papers.]

**E2: Data Retrieval**  
[Describe how relevant data, literature, or other sources were gathered or filtered. Cite all relevant papers.]

**E3: Knowledge Assembly**  
[Explain how structured knowledge was constructed, encoded, or represented. Cite all relevant papers.]

**H1: Hypothesis/Idea Generation**  
[Describe how the systems generated hypotheses or ideas, including tools or reasoning strategies. Cite all relevant papers.]

**H2: Hypothesis or Idea Prioritization**  
[Describe how hypotheses were ranked, filtered, or evaluated. Cite all relevant papers.]

**T1: Experimental Design Generation**  
[Summarize how experiments were planned or designed to test generated hypotheses. Cite all relevant papers.]

**T2: Iterative Refinement**  
[Describe any feedback loops or iterative improvement mechanisms used in the workflow. Cite all relevant papers.]

**Conclusion**  
[Provide an integrative summary comparing how the workflows collectively advance automated scientific discovery.]

**References**  
[List all papers, formatted as: Authors (Year). Title. Publication Date. Link.]

---

### ADDITIONAL RULES
1. Every section heading (Inputs to the Workflow, E1, E2, etc.) **must appear in the output** — even if only one paper contributes.
2. Each paragraph **must begin with a bolded heading**, as shown above.
3. Use **formal academic writing** — complete sentences, no bullet points.
4. Only use information contained in the JSON files.
5. Ensure in-text citations follow the form *(Author et al., Year)*.
6. Always include a final **References** section with full paper metadata.

---

### INPUT
Below are the JSON workflow descriptions:

### OUTPUT
A structured, stage-preserving, multi-paragraph scientific survey comparing the workflows, formatted according to the stage order above.
"""


# --------------------------
# Generate Survey
# --------------------------
if st.sidebar.button("🚀 Generate Survey Summary"):
    if not selected_titles:
        st.warning("Please select at least one paper.")
        st.stop()

    try:
        json_objects = []
        for title in selected_titles:
            file_name = paper_titles[title]
            file_path = os.path.join(JSON_FOLDER, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            json_objects.append(data)

        user_content = f"Here are {len(json_objects)} JSON files representing selected papers:\n" + "\n\n".join(
            json.dumps(obj, indent=2) for obj in json_objects
        )

        messages = [
            {"role": "system", "content": "You are a helpful assistant for writing scientific surveys."},
            {"role": "user", "content": survey_prompt_template + "\n\n" + user_content},
        ]

        with st.spinner("Generating survey summary... this may take a minute ⏳"):
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
                temperature=0.1,
                max_tokens=12000,
            )

        survey_text = response.choices[0].message.content.strip()

        st.subheader("📘 Generated Survey Summary")
        st.markdown(survey_text)

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Select papers by title from the sidebar and click 'Generate Survey Summary' to start.")