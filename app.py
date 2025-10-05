# app.py
import streamlit as st
import time
import requests

BACKEND_URL = "http://127.0.0.1:8000"  # 👈 change to your backend host/port

st.set_page_config(
    page_title="Hospital Incident Assistant",
    page_icon="🩺",
    layout="wide",
)

# ---------- THEME HEADER ----------
st.markdown(
    """
    <div style="background: radial-gradient(1200px 400px at 10% -20%, #9AE6B4 0%, transparent 60%),
                         radial-gradient(800px 300px at 90% -10%, #90CDF4 0%, transparent 60%); padding: 20px; border-radius: 24px; border:1px solid #e7e7e7;">
      <h1 style="margin:0; font-size: 32px;">🏥 Hospital Incident Assistant</h1>
      <p style="margin:6px 0 0; font-size:14px; opacity:.9;">Raise, triage, and solve incidents with JCI/HA guidance.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.subheader("Quick Stats")
    
    # Test backend connection first
    try:
        test_r = requests.get("http://127.0.0.1:8000/test", timeout=5)
        if test_r.status_code == 200:
            st.success("✅ Connected")
        else:
            st.error("❌ Backend not responding properly")
    except Exception as e:
        st.error(f"❌ Backend not reachable: {e}")
    
    # Get ticket statistics
    try:
        stats_r = requests.get("http://127.0.0.1:8000/ticket-stats", timeout=5)
        if stats_r.status_code == 200:
            stats = stats_r.json().get("stats", {})
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Tickets", stats.get("total_tickets", 0))
                st.metric("Open Tickets", stats.get("open_tickets", 0))
            with col2:
                st.metric("In Progress", stats.get("in_progress_tickets", 0))
                st.metric("Critical", stats.get("critical_tickets", 0))
        else:
            st.warning("⚠️ Could not fetch ticket stats")
    except Exception as e:
        st.warning("⚠️ Could not fetch ticket stats")
    
    st.divider()
    st.caption("⚙️ Connected to backend ")

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["📝 Raise Incident", "📊 Ticket Status", "🤖 Chatbot (Solve/Triage)"])

# === TAB 1: Incident Submission ===
with tab1:
    st.markdown("### Submit a New Incident")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Patient Name", placeholder="e.g., Dr. Sharma")
        department = st.text_input("Department", placeholder="e.g., ICU")
        organisation_name = st.text_input("Organisation Name", placeholder="e.g., City Hospital")
        speciality = st.text_input("Speciality", placeholder="e.g., Cardiology")
        priority = st.select_slider(
            "Priority",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium"
        )
        status_init = st.selectbox(
            "Initial Status",
            options=["Open", "In Progress", "Resolved", "Closed"],
            index=0
        )
        harm_severity = st.selectbox(
            "Harm Severity",
            options=["None", "Mild", "Moderate", "Severe", "Death"],
            index=0
        )
        verification = st.selectbox(
            "Verification",
            options=["Pending", "Verified", "Rejected"],
            index=0
        )

    with col2:
        issue_type = st.selectbox(
            "Issue Type (JCI/HA)",
            options=[
                "Patient Safety", "Medication", "Infection Control", "Facility Safety",
                "Clinical Governance", "Data Privacy", "Emergency", "Staffing",
                "Equipment", "Cleanliness", "Medical Records", "Waste Management",
                "Pharmacy", "Other"
            ],
            index=13,  # Default "Other"
        )
        description = st.text_area("Describe the issue", height=130)
        created_by = st.text_input("Created By", placeholder="e.g., Staff ID or Name")
        # Dates
        incident_date = st.date_input("Incident Date")
        reported_date = st.date_input("Reported Date")
        updated_at = st.date_input("Updated At (Date)")

    if st.button("🚀 Submit Incident", type="primary", use_container_width=True):
        if not (name and department and description):
            st.error("Please fill name, department and description.")
        else:
            payload = {
                "name": name,
                "department": department,
                "issue_type": issue_type,
                "description": description,
                "priority": priority,
                # New optional/extra fields
                "status": status_init,
                "reported_date": str(reported_date) if reported_date else None,
                "verification": verification,
                "created_by": created_by,
                "updated_at": str(updated_at) if updated_at else None,
                "incident_date": str(incident_date) if incident_date else None,
                "organisation_name": organisation_name,
                "speciality": speciality,
                "harm_severity": harm_severity,
            }
            try:
                # Change POST endpoint to /ticket (or /tickets/create if that's your backend)
                r = requests.post(f"http://127.0.0.1:8000/ticket", json=payload)
                if r.status_code == 200:
                    ticket_id = r.json().get("ticket_id", "N/A")
                    st.success(f"✅ Ticket created: {ticket_id}")
                    st.info("💡 You can check the ticket status in the 'Ticket Status' tab")
                else:
                    st.error(f"❌ Failed to create ticket: {r.text}")
            except Exception as e:
                st.error(f"⚠️ Could not connect to backend: {e}")

# === TAB 2: Ticket Status ===
with tab2:
    st.markdown("### 📊 Ticket Status Dashboard")
    
    # Search by ticket ID
    col1, col2 = st.columns([2, 1])
    with col1:
        search_ticket_id = st.text_input("Search by Ticket ID", placeholder="Enter ticket ID (e.g., ABC12345)")
    with col2:
        if st.button("🔍 Search", use_container_width=True):
            if search_ticket_id:
                try:
                    r = requests.get(f"http://127.0.0.1:8000/ticket/{search_ticket_id}/status")
                    if r.status_code == 200:
                        ticket = r.json().get("ticket")
                        st.success(f"✅ Found ticket: {search_ticket_id}")
                        
                        # Display ticket details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {ticket.get('name', '-')}")
                            st.write(f"**Department:** {ticket.get('department', '-')}")
                            st.write(f"**Issue Type:** {ticket.get('issue_type', '-')}")
                            st.write(f"**Organisation:** {ticket.get('organisation_name', '-')}")
                            st.write(f"**Speciality:** {ticket.get('speciality', '-')}")
                            st.write(f"**Harm Severity:** {ticket.get('harm_severity', '-')}")
                            st.write(f"**Verification:** {ticket.get('verification', '-')}")
                        with col2:
                            st.write(f"**Priority:** {ticket.get('priority', '-')}")
                            st.write(f"**Status:** {ticket.get('status', '-')}")
                            st.write(f"**Created:** {ticket.get('created_at', '-')}")
                            st.write(f"**Incident Date:** {ticket.get('incident_date', '-')}")
                            st.write(f"**Reported Date:** {ticket.get('reported_date', '-')}")
                            st.write(f"**Updated At:** {ticket.get('updated_at', '-')}")
                        st.write(f"**Description:** {ticket.get('description', '-')}")
                        st.write(f"**Created By:** {ticket.get('created_by', '-')}")
                        
                        # Status update
                        st.markdown("### Update Status")
                        new_status = st.selectbox(
                            "New Status",
                            options=["Open", "In Progress", "Resolved", "Closed"],
                            index=["Open", "In Progress", "Resolved", "Closed"].index(ticket.get('status', 'Open'))
                        )
                        
                        if st.button("🔄 Update Status"):
                            try:
                                update_r = requests.put(
                                    f"http://127.0.0.1:8000/ticket/{search_ticket_id}/status",
                                    json={"status": new_status}
                                )
                                if update_r.status_code == 200:
                                    st.success(f"✅ Status updated to: {new_status}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to update status: {update_r.text}")
                            except Exception as e:
                                st.error(f"⚠️ Error updating status: {e}")
                    else:
                        st.error(f"❌ Ticket not found: {search_ticket_id}")
                except Exception as e:
                    st.error(f"⚠️ Error searching ticket: {e}")
    
    st.markdown("---")
    
    # Display all tickets
    st.markdown("### 📋 All Tickets")
    try:
        r = requests.get("http://127.0.0.1:8000/tickets")
        if r.status_code == 200:
            tickets_data = r.json().get("tickets", [])
            if tickets_data:
                import pandas as pd
                df = pd.DataFrame(tickets_data)
                if 'ticket_id' in df.columns and 'status' in df.columns:
                    display_df = df[["ticket_id", "status"]]
                    st.dataframe(display_df, use_container_width=True)

                    st.markdown("#### Close a Ticket")
                    for idx, row in display_df.iterrows():
                        ticket_id = row['ticket_id']
                        status = row['status']
                        cols = st.columns([2, 2, 1])
                        cols[0].write(f"**{ticket_id}**")
                        cols[1].write(f"{status}")
                        if status != "Closed":
                            if cols[2].button(f"Close Ticket", key=f"close_{ticket_id}"):
                                try:
                                    update_r = requests.put(
                                        f"http://127.0.0.1:8000/ticket/{ticket_id}/status",
                                        json={"status": "Closed"}
                                    )
                                    if update_r.status_code == 200:
                                        st.success(f"Ticket {ticket_id} closed.")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to close ticket {ticket_id}: {update_r.text}")
                                except Exception as e:
                                    st.error(f"Error closing ticket {ticket_id}: {e}")
                        else:
                            cols[2].write(":white_check_mark: Closed")
                else:
                    st.info("No ticket_id or status fields found in tickets.")
            else:
                st.info("No tickets found in database.")
        else:
            st.error(f"Failed to fetch tickets: {r.text}")
    except Exception as e:
        st.error(f"Could not fetch tickets: {e}")

# === TAB 3: Chatbot ===
with tab3:
    st.markdown("### Ask the Incident Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display history
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar=("🧑" if m["role"] == "user" else "🤖")):
            st.markdown(m["content"])

    user_query = st.chat_input(
        "Ask about JCI/HA policy, triage steps, or type 'raise incident'..."
    )

    if user_query:
        # Show user msg
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_query)

        # Send to backend
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    r = requests.post("http://127.0.0.1:8000/chat", json={"query": user_query})
                    if r.status_code == 200:
                        answer = r.json().get("answer", "(no response)")
                    else:
                        answer = f"❌ Backend error: {r.text}"
                except Exception as e:
                    answer = f"⚠️ Could not connect to backend: {e}"

                time.sleep(0.2)
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

    st.caption("💡 Connected to backend API for real responses.")
