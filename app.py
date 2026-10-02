import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import csv
from generate_section import (
    write_section, revise_section, check_missing, check_citations,
    check_quotes, check_unquoted_citations, export_to_docx,
    extract_uploaded_text, SECTION_FACTS, slugify
)
from location_lookup import get_postcode_coords, find_nearest_by_type, RAIL_CODES, BUS_CODES

with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f"Welcome, {st.session_state['name']}")

    st.title("DAS Writing Assistant")

    @st.cache_data
    def load_naptan():
        with open("reference_data/naptan.csv", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return list(reader), reader.fieldnames

    @st.cache_data
    def load_onspd():
        with open("reference_data/onspd.csv", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return list(reader), reader.fieldnames

    st.subheader("Look up site location (optional)")
    postcode_input = st.text_input("Site postcode")

    if st.button("Find nearby transport links"):
        with st.spinner("Searching local transport data..."):
            onspd_rows, onspd_fields = load_onspd()
            coords = get_postcode_coords(postcode_input, onspd_rows, onspd_fields)

            if coords is None:
                st.error("Postcode not found — check it's typed correctly.")
            else:
                lat, lon = coords
                naptan_rows, naptan_fields = load_naptan()
                rail_name, rail_dist = find_nearest_by_type(lat, lon, naptan_rows, naptan_fields, RAIL_CODES)
                bus_name, bus_dist = find_nearest_by_type(lat, lon, naptan_rows, naptan_fields, BUS_CODES)
                st.session_state["suggested_public_transport"] = (
                    f"Nearest train station: {rail_name} ({rail_dist} km). "
                    f"Nearest bus stop: {bus_name} ({bus_dist} km)."
                )
                st.success("Found it — check the Public transport field below.")

    section_name = st.selectbox("Section to write", list(SECTION_FACTS.keys()))

    site_facts = {}
    for field_label in SECTION_FACTS[section_name]:
        key = slugify(field_label)
        default_value = st.session_state.get(f"suggested_{key}", "")
        site_facts[key] = st.text_input(field_label.capitalize(), value=default_value, key=key)

    additional_comments = st.text_area("Additional comments or site-specific information (optional)")
    site_facts["additional_comments"] = additional_comments

    uploaded_files = None
    if section_name == "Planning Policy":
        uploaded_files = st.file_uploader(
            "Upload local planning policy documents (optional)",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )

    output_key = f"generated_{section_name}"

    just_generated = False
    if st.button("Generate"):
        missing = check_missing(section_name, site_facts)
        if missing:
            st.info(f"No information given for: {', '.join(missing)} — the AI will write around this rather than invent it.")

        uploaded_text = extract_uploaded_text(uploaded_files) if uploaded_files else None

        with st.spinner("Writing..."):
            output = st.write_stream(write_section(section_name, site_facts, uploaded_policy_text=uploaded_text))
        st.session_state[output_key] = output
        just_generated = True

    if output_key in st.session_state:
        output = st.session_state[output_key]
        if not just_generated:
            st.write(output)

        flagged = check_citations(output)
        if flagged:
            st.error(f"Unverified citations, please check before using: {', '.join(flagged)}")

        bad_quotes = check_quotes(output)
        if bad_quotes:
            st.warning("These quoted passages don't exactly match the source text: " + " | ".join(bad_quotes))

        unquoted = check_unquoted_citations(output)
        if unquoted:
            st.warning("These sentences cite a source but don't quote it directly — check they're not paraphrasing: " + " | ".join(unquoted))

        if not flagged and not bad_quotes and not unquoted:
            docx_buffer = export_to_docx(section_name, output)
            st.download_button(
                label="Download as Word document",
                data=docx_buffer,
                file_name=f"{section_name.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        st.subheader("Ask for changes")
        feedback = st.text_area("What would you like to adjust about this text?", key=f"feedback_{section_name}")
        if st.button("Regenerate with feedback"):
            uploaded_text = extract_uploaded_text(uploaded_files) if uploaded_files else None
            with st.spinner("Revising..."):
                revised = st.write_stream(
                    revise_section(section_name, site_facts, output, feedback, uploaded_policy_text=uploaded_text)
                )
            st.session_state[output_key] = revised
            st.rerun()

elif st.session_state["authentication_status"] is False:
    st.error("Username or password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")