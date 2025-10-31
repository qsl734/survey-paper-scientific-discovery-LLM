import os
import json
import streamlit as st

# 📁 Path to your JSON folder
json_dir = "Papers"

# 🔍 Get all JSON files in the folder
json_files = sorted(f for f in os.listdir(json_dir) if f.endswith(".json"))

# 🔄 Load and organize papers by subject area
papers_by_subject = {}
for filename in json_files:
    file_path = os.path.join(json_dir, filename)
    with open(file_path) as f:
        data = json.load(f)

    subject_areas = data.get("subject_area", {}).get("areas", [])
    for area in subject_areas:
        if isinstance(area, dict):
            subject = area.get("name", "Unknown")
        else:
            subject = str(area)
        if subject not in papers_by_subject:
            papers_by_subject[subject] = []
        papers_by_subject[subject].append({"filename": filename, "data": data})

# ───────────── Page Setup ─────────────
st.set_page_config(page_title="📄 Scientific Paper Explorer", layout="wide")
st.title("📄 Scientific Paper Explorer")

# Split screen into 3 columns
col1, col2, col3 = st.columns([2, 3, 6])

# ------------- Column 1: Subject Area Selection -------------
with col1:
    st.header("📚 Subject Areas")
    subject_list = sorted(papers_by_subject.keys())
    selected_subject = st.radio("Select a subject area", subject_list) if subject_list else None

# ------------- Column 2: Paper Selection -------------
with col2:
    st.header("📄 Papers")
    if selected_subject:
        paper_list = [p["filename"] for p in papers_by_subject[selected_subject]]
        selected_paper = st.radio("Choose a paper", paper_list, key="paper_radio") if paper_list else None
    else:
        selected_paper = None

# ---------- Function to Render Paper Content ----------
def render_paper(data):
    # Display paper title and authors first
    title = data.get("paper_title", "Untitled Paper")
    authors = data.get("authors", "Unknown Authors")
    st.subheader(f"📝 {title}")
    st.markdown(f"**Authors:** {authors}")
    link = data.get("link", "")
    if link:
        st.markdown(f"[📎 Paper Link]({link})")
    st.markdown("---")

    for section, content in data.items():
        if section in ["paper_title", "authors", "link"]:
            continue

        st.markdown(f"## 🔹 {section.replace('_',' ').title()}")

        # Sections with answer/evidence
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

        # Method section
        elif section == "method":
            st.subheader("🔄 Steps")
            for step in content.get("steps", []):
                st.markdown(f"- **{step.get('step','')}**")
                st.markdown(f"  - 📥 Input: {step.get('input','')}")
                st.markdown(f"  - 📤 Output: {step.get('output','')}")
                st.markdown(f"  - 📌 Evidence: {step.get('evidence','')}")
                st.markdown("---")

            # Tools
            tools = content.get("tools", [])
            if isinstance(tools, str):
                tools = [tools]
            if tools:
                st.subheader("🛠️ Tools")
                for tool in tools:
                    if isinstance(tool, dict):
                        st.markdown(f"- **{tool.get('name','Unnamed Tool')}**: {tool.get('description','')}")
                        if tool.get("evidence"):
                            st.markdown(f"  - 📌 Evidence: {tool.get('evidence','')}")
                    else:
                        st.markdown(f"- {tool}")

            # Benchmark Datasets
            datasets = content.get("benchmark_datasets", [])
            if isinstance(datasets, dict):
                datasets = [datasets]
            if datasets:
                st.subheader("📚 Benchmark Datasets")
                for d in datasets:
                    if isinstance(d, dict):
                        st.markdown(f"- **{d.get('name','')}**")
                        if "data_description" in d:
                            st.markdown(f"  - 📊 Description: {d.get('data_description','')}")
                        if "usage" in d:
                            st.markdown(f"  - 🔧 Usage: {d.get('usage','')}")
                        if "evidence" in d:
                            st.markdown(f"  - 📌 Evidence: {d.get('evidence','')}")
                    else:
                        st.markdown(f"- {d}")

            # Evaluation Metrics
            metrics = content.get("evaluation_metrics", [])
            if isinstance(metrics, dict):
                metrics = [metrics]
            if metrics:
                st.subheader("📏 Evaluation Metrics")
                for m in metrics:
                    if isinstance(m, dict):
                        st.markdown(f"- **{m.get('name','')}**: {m.get('description','')}")
                        if m.get("purpose"):
                            st.markdown(f"  - 🎯 Purpose: {m.get('purpose','')}")
                        if m.get("application"):
                            st.markdown(f"  - ⚙️ Application: {m.get('application','')}")
                        if m.get("evidence"):
                            st.markdown(f"  - 📌 Evidence: {m.get('evidence','')}")
                    else:
                        st.markdown(f"- {m}")

        # Other sections
        elif section == "method_type":
            st.subheader("🧠 Method Types")
            for m in content.get("methods", []):
                st.markdown(f"- **{m.get('name','')}**: {m.get('description','')}")
                st.markdown(f"  - 📌 Evidence: {m.get('evidence','')}")

        elif section == "subject_area":
            st.subheader("🧪 Subject Areas")
            for s in content.get("areas", []):
                if isinstance(s, dict):
                    st.markdown(f"- **{s.get('name','')}**: {s.get('description','')}")
                    if s.get("evidence"):
                        st.markdown(f"  - 📌 Evidence: {s.get('evidence','')}")
                else:
                    st.markdown(f"- {s}")
            evidence = content.get("evidence", [])
            if evidence:
                st.markdown("📌 Evidence:")
                for e in evidence:
                    st.markdown(f"- {e}")

        elif section == "performance_summary":
            st.subheader("📈 Performance Summary")
            for p in content.get("performance_summary", []):
                if isinstance(p, dict):
                    st.markdown(f"- {p.get('summary','')}")
                    if p.get("evidence"):
                        st.markdown(f"  - 📌 Evidence: {p.get('evidence','')}")
                else:
                    st.markdown(f"- {p}")

            baselines = content.get("baselines", [])
            if baselines:
                st.subheader("📊 Baselines")
                if isinstance(baselines, dict):
                    baselines = [baselines]
                for b in baselines:
                    if isinstance(b, dict):
                        st.markdown(f"- **{b.get('name','')}**: {b.get('description','')}")
                        if b.get("evidence"):
                            st.markdown(f"  - 📌 Evidence: {b.get('evidence','')}")

        elif section == "limitations":
            st.subheader("⚠️ Limitations")
            for item in content.get("limitations", []):
                label = item.get("label") or item.get("name") or "Unnamed"
                desc = item.get("explanation") or item.get("description") or ""
                st.markdown(f"- **{label}**: {desc}")
                if item.get("evidence"):
                    st.markdown(f"  - 📌 Evidence: {item.get('evidence')}")

        elif section == "future_directions":
            st.subheader("🔮 Future Directions")
            for i, item in enumerate(content.get("future_directions", []), 1):
                name = item.get("name") or ""
                desc = item.get("description") or ""
                st.markdown(f"**{i}. {name}** — {desc}")
                if item.get("evidence"):
                    st.markdown(f"📌 Evidence: {item.get('evidence')}")
                st.markdown("---")

        elif section == "resource_link":
            st.markdown("### 🔗 Resource Link")
            answer = content.get("answer", "")
            if answer:
                st.markdown(f"[{answer}]({answer})")
            st.markdown(f"📌 Evidence: {content.get('evidence','No evidence provided.')}")
            st.markdown("---")

        else:
            st.markdown("ℹ️ Unrecognized format. Raw content below:")
            st.json(content)

# ------------- Column 3: Paper Viewer -------------
with col3:
    st.header("📑 Paper Summary")
    if selected_paper:
        selected_data = next(
            (p["data"] for p in papers_by_subject[selected_subject] if p["filename"] == selected_paper),
            None
        )
        if selected_data:
            render_paper(selected_data)
        else:
            st.warning("Failed to load selected paper.")
    else:
        st.info("Please select a paper to view details.")
