

import os
import json
import streamlit as st

# Path to your JSON directory
json_dir = "Papers"
json_files = sorted(f for f in os.listdir(json_dir) if f.endswith(".json"))

# Load and organize all papers by subject area
papers_by_subject = {}

for filename in json_files:
    file_path = os.path.join(json_dir, filename)
    with open(file_path) as f:
        data = json.load(f)

    subject_areas = data.get("subject_area", {}).get("areas", [])
    for area in subject_areas:
        subject = area["name"]
        if subject not in papers_by_subject:
            papers_by_subject[subject] = []
        papers_by_subject[subject].append({"filename": filename, "data": data})

# Page setup
st.set_page_config(page_title="📄 Scientific Paper Explorer", layout="wide")
st.title("📄 Scientific Paper Explorer")

# Split screen into 3 columns
col1, col2, col3 = st.columns([2, 3, 6])

# ------------- Column 1: Subject Area Selection -------------
with col1:
    st.header("📚 Subject Areas")
    subject_list = sorted(papers_by_subject.keys())
    selected_subject = st.radio("Select a subject area", subject_list)

# ------------- Column 2: Paper Selection (based on subject) -------------
with col2:
    st.header("📄 Papers")
    if selected_subject:
        paper_list = [p["filename"] for p in papers_by_subject[selected_subject]]
        selected_paper = st.radio("Choose a paper", paper_list, key="paper_radio")
    else:
        selected_paper = None

# ---------- Function to Render Paper Content ----------
def render_paper(data):
    for section, content in data.items():
        st.markdown(f"## 🔹 {section.replace('_', ' ').title()}")

        if isinstance(content, dict) and "answer" in content:
            st.markdown("**✅ Answer**")
            answer = content["answer"]
            if isinstance(answer, list):
                for i, a in enumerate(answer, 1):
                    st.markdown(f"{i}. {a}")
            else:
                st.markdown(answer)

            st.markdown("**📌 Evidence**")
            evidence = content.get("evidence", "")
            if isinstance(evidence, list):
                for e in evidence:
                    st.markdown(f"- {e}")
            else:
                st.markdown(evidence)

            st.markdown("---")

        elif section == "method":
            st.subheader("🔄 Steps")
            for step in content.get("steps", []):
                st.markdown(f"- **{step['step']}**")
                st.markdown(f"  - 📥 Input: {step['input']}")
                st.markdown(f"  - 📤 Output: {step['output']}")
                st.markdown(f"  - 📌 Evidence: {step['evidence']}")
                st.markdown("---")

            if content.get("tools"):
                st.subheader("🛠️ Tools")
                for tool in content["tools"]:
                    st.markdown(f"- **{tool['name']}**: {tool['description']}")
                    st.markdown(f"  - 📌 Evidence: {tool['evidence']}")

            if content.get("benchmark_datasets"):
                st.subheader("📚 Benchmark Datasets")
                for d in content["benchmark_datasets"]:
                    st.markdown(f"- **{d['name']}**")
                    st.markdown(f"  - 📊 Description: {d['data_description']}")
                    st.markdown(f"  - 🔧 Usage: {d['usage']}")
                    st.markdown(f"  - 📌 Evidence: {d['evidence']}")

            if content.get("evaluation_metrics"):
                st.subheader("📏 Evaluation Metrics")
                for m in content["evaluation_metrics"]:
                    st.markdown(f"- **{m['name']}**")
                    st.markdown(f"  - 🎯 Purpose: {m['purpose']}")
                    st.markdown(f"  - ⚙️ Application: {m['application']}")
                    st.markdown(f"  - 📌 Evidence: {m['evidence']}")

        elif section == "method_type":
            st.subheader("🧠 Method Types")
            for m in content.get("methods", []):
                st.markdown(f"- **{m['name']}**: {m['description']}")
                st.markdown(f"  - 📌 Evidence: {m['evidence']}")

        elif section == "subject_area":
            st.subheader("🧪 Subject Areas")
            for s in content.get("areas", []):
                st.markdown(f"- **{s['name']}**: {s['description']}")
                st.markdown(f"  - 📌 Evidence: {s['evidence']}")

        elif section == "performance_summary":
            if content.get("performance_summary"):
                st.subheader("📈 Performance Summary")
                for p in content["performance_summary"]:
                    st.markdown(f"- {p['summary']}")
                    st.markdown(f"  - 📌 Evidence: {p['evidence']}")

            if content.get("baselines"):
                st.subheader("📊 Baselines")
                for b in content["baselines"]:
                    st.markdown(f"- {b['name']}: {b['description']}")
                    st.markdown(f"  - 📌 Evidence: {b['evidence']}")

            if content.get("benchmark_datasets"):
                st.subheader("🧪 Benchmark Datasets")
                for d in content["benchmark_datasets"]:
                    st.markdown(f"- **{d['name']}**")
                    st.markdown(f"  - 📊 Description: {d['data_description']}")
                    st.markdown(f"  - 🔧 Usage: {d['usage']}")
                    st.markdown(f"  - 📌 Evidence: {d['evidence']}")

            if content.get("evaluation_metrics"):
                st.subheader("📏 Evaluation Metrics")
                for m in content["evaluation_metrics"]:
                    st.markdown(f"- **{m['name']}**")
                    st.markdown(f"  - Purpose: {m['purpose']}")
                    st.markdown(f"  - Application: {m['application']}")
                    st.markdown(f"  - 📌 Evidence: {m['evidence']}")

        elif section == "benchmark_dataset":
            if content is None:
                st.warning("No benchmark dataset was used.")
            else:
                st.markdown(content)

        elif section == "limitations":
            for item in content.get("limitations", []):
                st.markdown(f"- **{item['name']}**: {item['description']}")
                st.markdown(f"  - 📌 Evidence: {item['evidence']}")

        elif section == "future_directions":
            for i, item in enumerate(content.get("future_directions", []), 1):
                st.markdown(f"### {i}. {item['name']}")
                st.markdown(f"{item['description']}")
                st.markdown(f"📌 **Evidence**: {item['evidence']}")
                st.markdown("---")

        elif section == "resource_link":
            st.markdown("### 🔗 Resource Link")
            st.markdown(f"[{content['answer']}]({content['answer']})")
            st.markdown(f"📌 **Evidence**: {content.get('evidence', 'No evidence provided.')}")
            st.markdown("---")

        else:
            st.markdown("ℹ️ Unrecognized format. Raw content below:")
            st.json(content)

# ------------- Column 3: Paper Viewer -------------
with col3:
    st.header("📑 Paper Summary")
    if selected_paper:
        selected_data = next((p["data"] for p in papers_by_subject[selected_subject] if p["filename"] == selected_paper), None)
        if selected_data:
            render_paper(selected_data)
        else:
            st.warning("Failed to load selected paper.")
    else:
        st.info("Please select a paper to view details.")
