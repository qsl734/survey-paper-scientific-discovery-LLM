import os
import json
import streamlit as st

# 📁 Path to your JSON folder
json_dir = "Papers"

# 🔍 Get all JSON files in the folder
json_files = sorted(f for f in os.listdir(json_dir) if f.endswith(".json"))

# 🎯 App Title
st.set_page_config(page_title="Paper Summary Viewer", layout="wide")
st.title("📄 Scientific Paper Summarizer")

# ─────────────────────────────
# 📜 Sidebar: Search & Select
# ─────────────────────────────
with st.sidebar:
    st.header("🔎 Search Papers")
    search_query = st.text_input("Search by filename")

    # Filter files based on query
    if search_query:
        filtered_files = [f for f in json_files if search_query.lower() in f.lower()]
    else:
        filtered_files = json_files

    st.markdown("### 📂 Matching Papers")
    for file in filtered_files:
        if st.button(file):
            st.session_state["selected_file"] = file

# 📦 Main Content Area
st.header("📑 Summary")

if "selected_file" in st.session_state:
    selected_file = st.session_state["selected_file"]
    file_path = os.path.join(json_dir, selected_file)

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # ─────────────
    # Display paper metadata
    # ─────────────
    paper_title = data.get("paper_title", "Untitled Paper")
    st.subheader(f"📝 {paper_title}")

    authors = data.get("authors", "")
    if authors:
        st.markdown(f"👩‍🔬 **Authors**: {authors}")

    published = data.get("published", "")
    if published:
        st.markdown(f"📅 **Published**: {published}")

    link = data.get("link", "")
    if link:
        st.markdown(f"🔗 [Paper Link]({link})")

    st.markdown("---")

    # ─────────────
    # Loop through all other sections
    # ─────────────
    for section, content in data.items():
        if section in ["paper_title", "authors", "published", "link"]:
            continue  # Skip metadata

        st.markdown(f"## 🔹 {section.replace('_', ' ').title()}")

        # Handle sections with "answer" and "evidence"
        if isinstance(content, dict) and "answer" in content:
            answer = content.get("answer", "")
            evidence = content.get("evidence", "")

            st.markdown("**✅ Answer**")
            if isinstance(answer, list):
                for i, a in enumerate(answer, 1):
                    st.markdown(f"{i}. {a}")
            else:
                st.markdown(answer)

            st.markdown("**📌 Evidence**")
            if isinstance(evidence, list):
                for e in evidence:
                    st.markdown(f"- {e}")
            else:
                st.markdown(evidence)

            st.markdown("---")

        # ─────────────
        # METHOD section
        # ─────────────
        elif section == "method":
            st.subheader("🔄 Steps")
            for step in content.get("steps", []):
                st.markdown(f"- **{step.get('step','')}**")
                st.markdown(f"  - 📥 Input: {step.get('input','')}")
                st.markdown(f"  - 📤 Output: {step.get('output','')}")
                st.markdown(f"  - 📌 Evidence: {step.get('evidence','')}")
                st.markdown("---")

            # 🛠️ Tools
            tools = content.get("tools", [])
            if isinstance(tools, str):
                tools = [tools]
            if tools:
                st.subheader("🛠️ Tools")
                for tool in tools:
                    if isinstance(tool, dict):
                        name = tool.get("name", "Unnamed Tool")
                        desc = tool.get("description", "")
                        evidence = tool.get("evidence", "")
                        st.markdown(f"- **{name}**: {desc}")
                        if evidence:
                            st.markdown(f"  - 📌 Evidence: {evidence}")
                    else:
                        st.markdown(f"- {tool}")

            # 📚 Benchmark Datasets
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

            # 📏 Evaluation Metrics
            metrics = content.get("evaluation_metrics", [])
            if isinstance(metrics, dict):
                metrics = [metrics]
            if metrics:
                st.subheader("📏 Evaluation Metrics")
                for m in metrics:
                    if isinstance(m, dict):
                        st.markdown(f"- **{m.get('name','')}**: {m.get('description','')}")
                        if "purpose" in m:
                            st.markdown(f"  - 🎯 Purpose: {m.get('purpose','')}")
                        if "application" in m:
                            st.markdown(f"  - ⚙️ Application: {m.get('application','')}")
                        if "evidence" in m:
                            st.markdown(f"  - 📌 Evidence: {m.get('evidence','')}")
                    else:
                        st.markdown(f"- {m}")

        # ─────────────
        # Other sections: handle dict, list, string
        # ─────────────
        elif isinstance(content, dict):
            for key, value in content.items():
                st.markdown(f"- **{key}**: {value}")

        elif isinstance(content, list):
            for i, item in enumerate(content, 1):
                st.markdown(f"{i}. {item}")

        elif isinstance(content, str):
            st.markdown(content)

        else:
            st.markdown("ℹ️ Unrecognized format. Raw content below:")
            st.json(content)

else:
    st.info("Select a paper from the sidebar to begin.")
