import os
import json
import streamlit as st

# 📁 Path to your JSON folder
json_dir = json_dir = "Papers"

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

    # Search input box
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

    with open(file_path) as f:
        data = json.load(f)

    for section, content in data.items():
        st.markdown(f"## 🔹 {section.replace('_', ' ').title()}")

        # Handle dictionary sections with "answer"
        if isinstance(content, dict) and "answer" in content:
            answer = content["answer"]
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
        # 🔍 METHOD Section
        # ─────────────
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

        # ─────────────
        # 🧠 METHOD TYPE Section
        # ─────────────
        elif section == "method_type":
            st.subheader("🧠 Method Types")
            for m in content.get("methods", []):
                st.markdown(f"- **{m['name']}**: {m['description']}")
                st.markdown(f"  - 📌 Evidence: {m['evidence']}")

        # ─────────────
        # 🧪 SUBJECT AREA Section
        # ─────────────
        elif section == "subject_area":
            st.subheader("🧪 Subject Areas")
            for s in content.get("areas", []):
                st.markdown(f"- **{s['name']}**: {s['description']}")
                st.markdown(f"  - 📌 Evidence: {s['evidence']}")

        # ─────────────
        # 🧪 PERFORMANCE SUMMARY Section
        # ─────────────
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

        # ─────────────
        # 🧪 benchmark_dataset Section
        # ─────────────
        elif section == "benchmark_dataset":
            if content is None:
                st.warning("No benchmark dataset was used.")
            else:
                st.markdown(content)

        # ─────────────
        # 🧪 limitations
        # ─────────────
        elif section == "limitations":
            for item in content.get("limitations", []):
                st.markdown(f"- **{item['name']}**: {item['description']}")
                st.markdown(f"  - 📌 Evidence: {item['evidence']}")

        # ─────────────
        # 🧪 future_directions Section
        # ─────────────
        elif section == "future_directions":
            for i, item in enumerate(content.get("future_directions", []), 1):
                st.markdown(f"### {i}. {item['name']}")
                st.markdown(f"{item['description']}")
                st.markdown(f"📌 **Evidence**: {item['evidence']}")
                st.markdown("---")

        # ─────────────
        # 🧪 resource_link Section
        # ─────────────
        elif section == "resource_link":
            st.markdown("### 🔗 Resource Link")
            st.markdown(f"[{content['answer']}]({content['answer']})")
            st.markdown(f"📌 **Evidence**: {content.get('evidence', 'No evidence provided.')}")
            st.markdown("---")

        else:
            st.markdown("ℹ️ Unrecognized format. Raw content below:")
            st.json(content)

else:
    st.info("Select a paper from the sidebar to begin.")
