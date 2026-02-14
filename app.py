import streamlit as st
from agent_graph import app
from langgraph.types import Command

st.set_page_config(
    page_title="Agentic Instagram Upload Bot",
    layout="centered"
)

st.title("📸 Agentic Instagram Upload Bot")

# ================= Session State =================
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "ig-thread-001"

if "interrupt_payload" not in st.session_state:
    st.session_state.interrupt_payload = None

# ================= Helpers =================
def run_until_interrupt(input_or_command):
    """
    Runs the LangGraph until the next interrupt
    and stores interrupt payload in session state.
    """
    st.session_state.interrupt_payload = None

    for event in app.stream(
        input_or_command,
        config={"configurable": {"thread_id": st.session_state.thread_id}}
    ):
        if "__interrupt__" in event:
            interrupt_obj = event["__interrupt__"][0]
            st.session_state.interrupt_payload = interrupt_obj.value
            return

# ================= Input =================
keyword = st.text_input(
    "Enter news topic",
    placeholder="Any news topic"
)

# ================= Start Agent =================
if st.button("🚀 Run Agent"):
    if not keyword:
        st.warning("Please enter a keyword")
    else:
        run_until_interrupt({
            "keyword": f"Recent news about {keyword} as of today",
            "content": None,
            "image_source": None,
            "image_path": None,
            "decision": None,
            "edited_caption": None,
        })

# ================= Human Review =================
if st.session_state.interrupt_payload:
    data = st.session_state.interrupt_payload

    st.divider()
    st.subheader("🧠 Human Review Required")

    # ---- Image ----
    if data.get("image_path"):
        st.image(data["image_path"], use_container_width=True)

    # ---- Caption ----
    edited_caption = st.text_area(
        "Caption",
        value=data.get("caption", ""),
        height=140
    )

    # ---- Buttons ----
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✅ Approve"):
            run_until_interrupt(
                Command(resume={"decision": "APPROVE"})
            )
            st.success("📸 Posted to Instagram")

    with col2:
        if st.button("✏️ Edit"):
            run_until_interrupt(
                Command(resume={
                    "decision": "EDIT",
                    "edited_caption": edited_caption
                })
            )

    with col3:
        if st.button("🔄 Regenerate"):
            run_until_interrupt(
                Command(resume={"decision": "REGENERATE"})
            )

    with col4:
        if st.button("🔁 Switch Image"):
            run_until_interrupt(
                Command(resume={"decision": "SWITCH_IMAGE_SOURCE"})
            )
