import streamlit as st
import os
from dotenv import load_dotenv
from analyzer import StackTraceAnalyzer
from sandbox import DockerSandbox

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI Stack Trace Investigator", page_icon="🔍", layout="wide")

st.title("🔍 AI Stack Trace Investigator")
st.markdown("Analyze stack traces and errors using AI, and automatically run reproduction code in a secure sandbox.")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("Error: OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    error_input = st.text_area("Stack Trace / Error Output", height=300, placeholder="Paste your stack trace here...")
    
with col2:
    st.subheader("Code Context (Optional)")
    code_context = st.text_area("Relevant Source Code", height=300, placeholder="Paste relevant code here...")

if st.button("Analyze Stack Trace", type="primary"):
    if not error_input.strip():
        st.warning("Please provide a stack trace to analyze.")
    else:
        with st.spinner("Analyzing with AI..."):
            analyzer = StackTraceAnalyzer()
            try:
                result = analyzer.analyze(error_input, code_context)
                st.session_state["analysis_result"] = result
            except Exception as e:
                st.error(f"Failed to analyze: {e}")

if "analysis_result" in st.session_state:
    st.divider()
    result = st.session_state["analysis_result"]
    
    st.header("Analysis Results")
    
    if result.causes:
        st.subheader("🧠 Likely Causes")
        for i, cause in enumerate(result.causes):
            with st.expander(f"Cause {i+1}: {cause.description} (Likelihood: {cause.likelihood})", expanded=(i==0)):
                st.markdown(f"**Fix Suggestion:**\n{cause.fix_suggestion}")
                
    if result.missing_evidence:
        st.subheader("❓ Missing Evidence / Questions")
        for item in result.missing_evidence:
            st.markdown(f"- {item}")
            
    if result.reproduction_code:
        st.subheader("💻 Reproduction Code")
        st.code(result.reproduction_code, language="python")
        
        if st.button("Run in Sandbox 🚀"):
            with st.spinner("Running in Docker sandbox..."):
                sandbox = DockerSandbox()
                res = sandbox.run_reproduction(result.reproduction_code)
                
                if res["status"] == "success":
                    exit_code = res.get("exit_code")
                    logs = res.get("logs", "")
                    
                    if exit_code == 0:
                        st.success(f"Sandbox executed successfully (Exit Code: 0)")
                    else:
                        st.error(f"Sandbox execution failed (Exit Code: {exit_code})")
                        
                    if logs:
                        st.text_area("Sandbox Logs", logs, height=200)
                else:
                    st.error(f"Sandbox error: {res.get('message')}")
