import streamlit as st
from urllib.parse import urlparse
import datetime
import pytz
from datetime import timedelta
import random
import time
import nav

import oci
from oci.object_storage import ObjectStorageClient
from oci.object_storage.models import CreatePreauthenticatedRequestDetails
import genai_agent_service_bmc_python_client

CONFIG_PROFILE = "CHICAGO"  # API Key
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
object_storage_client = ObjectStorageClient(config)

nav.Navbar()

st.sidebar.info("..")

if st.session_state.get("page", "GenAI Agent (beta)") != st.session_state.current_page:
    # Clear all session state data
    st.session_state.clear()

    # Store the current page for the next comparison
    st.session_state.current_page = st.session_state.get("page", "GenAI Agent (beta)")

AVATAR_MAPPING = {
    "user": ":material/record_voice_over:",
    "assistant": "images/o.png"
}

with st.sidebar:

    if st.button("Reset Chat", type="primary", use_container_width=True, help="Reset chat history and clear screen"):
        st.session_state.messages = []
        # agent_endpoint_id = agent_options[selected_display_name]
        st.session_state.session_id = None
        st.toast("Chat reset!")
        #st.rerun()

    st.info("This RAG agent is designed to answer questions related to MyHelp documents (4+k).")
    st.info('Try asking "How to reset my SSO?"')

    on = st.toggle("Show Agent Endpoint", value=False)
    if on:
        agent_options = {}
        for key, value in st.secrets.items():
            if key.startswith("agent_endpoint_"):
                display_name = key.replace("agent_endpoint_", "").replace("_", " ").title()
                agent_options[display_name] = value

        agent_display_names = list(agent_options.keys())
        if "selected_display_name" not in st.session_state:
            st.session_state.selected_display_name = random.choice(agent_display_names) #set to 0 for static

        selected_display_name = st.selectbox(
            "Choose Agent Endpoint:",
            agent_display_names,
            index=agent_display_names.index(st.session_state.selected_display_name)  # Find index of selected agent
        )

        # Update selected_display_name in session state
        st.session_state.selected_display_name = selected_display_name

        agent_endpoint_id = agent_options[selected_display_name]


st.header("Oracle GenAI Agent Chat")
st.subheader("Powered by Oracle Generative AI Agents (Beta)")
st.info('`This RAG agent answers questions about Oracle Cloud. Click on the home tab to learn more.`')

# Initialize chat history and session ID in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Create GenAI Agent Runtime Client (only if session_id is None)
if st.session_state.session_id is None:
    genai_agent_runtime_client = genai_agent_service_bmc_python_client.GenerativeAiAgentRuntimeClient(
        config=config,
        service_endpoint=st.secrets['service_endpoint'],
        retry_strategy=oci.retry.NoneRetryStrategy(),
        timeout=(10, 240)
    )

    # Create session
    create_session_details = genai_agent_service_bmc_python_client.models.CreateSessionDetails(
        display_name="display_name", idle_timeout_in_seconds=10, description="description"
    )
    create_session_response = genai_agent_runtime_client.create_session(create_session_details, st.secrets['agent_endpoint_id'])

    # Store session ID
    st.session_state.session_id = create_session_response.data.id

    # Check if welcome message exists and append to message history
    if hasattr(create_session_response.data, 'welcome_message'):
        st.session_state.messages.append({"role": "assistant", "content": create_session_response.data.welcome_message})

# Display chat messages
for message in st.session_state.messages:
    avatar = AVATAR_MAPPING.get(message["role"], "images/o.png")  # Default to "o.png" if not found
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Get user input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=":material/record_voice_over:"):
        st.markdown(user_input)

    # Execute session (re-use the existing session)
    genai_agent_runtime_client = genai_agent_service_bmc_python_client.GenerativeAiAgentRuntimeClient(
        config=config,
        service_endpoint=st.secrets['service_endpoint'],
        retry_strategy=oci.retry.NoneRetryStrategy(),
        timeout=(10, 240)
    )
    # Display a spinner while waiting for the response
    with st.spinner("Working..."):  # Spinner for visual feedback
        execute_session_details = genai_agent_service_bmc_python_client.models.ExecuteSessionDetails(
            user_message=str(user_input), should_stream=False  # You can set this to True for streaming responses
        )
        execute_session_response = genai_agent_runtime_client.execute_session(st.secrets['agent_endpoint_id'], st.session_state.session_id, execute_session_details)

    # # Display agent response
    # if execute_session_response.status == 200:
    #     response_content = execute_session_response.data.message.content
    #     st.session_state.messages.append({"role": "assistant", "content": response_content.text})
    #     with st.chat_message("assistant", avatar="o.png"):
    #         st.markdown(response_content.text)

    # Display agent response in chunks to simulate streaming
    # Thanks to saileshan.x.subhakaran@oracle.com for this
    response_content = None
    if execute_session_response.status == 200:
        response_content = execute_session_response.data.message.content
        response_parts = response_content.text.split(' ')  # Split response into words for simulation
        displayed_response = ""
        response_placeholder = st.empty()
        for part in response_parts:
            displayed_response += part + ' '
            response_placeholder.markdown(displayed_response)
            time.sleep(0.025)  # Adjust delay as needed
        st.session_state.messages.append({"role": "assistant", "content": response_content.text})

    #  # Display citations with direct URLs - not recommended but OK if your bucket is public
    # if response_content.citations:
    #     with st.expander("Citations"):
    #         for i, citation in enumerate(response_content.citations, start=1):
    #             st.write(f"**Citation {i}:**")

    #             # Extract the path after '/o/' and decode
    #             parsed_url = urlparse(citation.source_location.url)
    #             path_parts = parsed_url.path.split("/o/")
    #             if len(path_parts) > 1:
    #                 display_path = unquote(path_parts[1])
    #             else:
    #                 display_path = parsed_url.netloc  # Fallback to domain if '/o/' not found

    #             # Use Markdown for a cleaner link presentation
    #             st.markdown(f"**Source:** [{display_path}]({citation.source_location.url})")

    # Display citations with PAR URLs
    if response_content.citations:
        with st.expander("Citations"):
            for i, citation in enumerate(response_content.citations, start=1):
                st.write(f"**Citation {i}:**")

                parsed_url = urlparse(citation.source_location.url)
                path_parts = parsed_url.path.split("/")
                # print(citation.source_location.url)
                if len(path_parts) >= 5 and path_parts[1] == "n" and path_parts[3] == "b":
                    namespace_name = path_parts[2]
                    bucket_name = path_parts[4]
                    object_name = citation.source_location.url.split("o/")[-1]
                    display_path = object_name

                    # Generate PAR URL
                    try:
                        par_details = CreatePreauthenticatedRequestDetails(
                            name=f"Download_{object_name}",
                            access_type="ObjectRead",
                            time_expires=datetime.datetime.now(pytz.timezone('UTC')) + timedelta(minutes=5), # 5 minute expiry, adjust as necessary for your security needs
                            object_name=object_name
                        )
                        par = object_storage_client.create_preauthenticated_request(
                            namespace_name,
                            bucket_name,
                            par_details
                        )

                        object_storage_endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}"

                        par_url = object_storage_endpoint + par.data.access_uri

                        st.markdown(f"**Source:** [{display_path}]({par_url})")
                    except Exception as e:
                        st.error(f"Failed to generate PAR URL for {display_path}: {e}")
                else:
                    st.markdown(f"**Source:** [{citation.source_location.url}]({citation.source_location.url})")
                    st.error(f"Citation {i} does not reference a valid object storage URL.")

                st.text_area("Citation Text", value=citation.source_text, height=200)

    else:
        st.error(f"API request failed with status: {execute_session_response.status}")
