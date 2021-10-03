import os
import sys
import typing

import streamlit as st

import kiara_streamlit
from kiara import Kiara
from kiara.data.onboarding.batch import BatchOnboard
from kiara_streamlit.components.mgmt import ComponentMgmt

st.set_page_config(
        page_title="kiara-streamlit component gallery",
    layout="wide"
)

@st.experimental_singleton
def onboard_files(_kiara: Kiara):

    aliases = _kiara.data_store.alias_names
    if aliases:
        all_match = True
        for alias in ["journals_file_bundle", "journal_edges_file", "journal_nodes_file", "text_corpus_file_bundle", "labels_array", "journal_nodes_table", "journal_edges_table", "cities_array"]:
            if alias not in aliases:
                all_match = False
                break
        if all_match:
            print("Data already onboarded.")
            return

    base_folder = os.path.dirname(__file__)
    data_folder = os.path.join(base_folder, "data")
    pipeline_folder = os.path.join(base_folder, "pipelines")

    inputs = {
        "edges_file_path": os.path.join(data_folder, "journals/JournalEdges1902.csv"),
        "nodes_file_path": os.path.join(data_folder, "journals/JournalNodes1902.csv"),
        "journals_folder_path": os.path.join(data_folder, "journals"),
        "text_corpus_folder_path": os.path.join(data_folder, "text_corpus"),
        "city_column_name": "City",
        "label_column_name": "Label"
    }
    pipeline = os.path.join(pipeline_folder, "gallery_onboarding.yaml")

    store_config_dict = {
        "outputs": [
            {"alias_template": "{{ field_name }}"}
        ]
    }

    onboard_config = {
        "module_type": pipeline,
        "inputs": inputs,
        "store_config": store_config_dict
    }

    # store_config = ValueStoreConfig(**store_config_dict)
    onboarder = BatchOnboard.create(kiara=_kiara, **onboard_config)
    print(f"kiara data store: {_kiara.data_store.base_path}")
    with st.spinner('Onboarding example data...'):
        results = onboarder.run("test")
        aliases = set()
        for _a in results.values():
            aliases.update(_a)
        print(f"Onboarded example data, available aliases: {', '.join(aliases)}")

    return True

kiara_streamlit.init(kiara_config={"extra_pipeline_folders": [], "data_store": "/tmp/markus"})
# kiara_streamlit.init(kiara_config={"extra_pipeline_folders": []})

onboarded = onboard_files(_kiara=st.kiara)

component_mgmt: ComponentMgmt = st.kiara_components

component_collection = st.sidebar.selectbox("Select a component collection", options=component_mgmt.component_collections)

all_funcs = sorted(component_mgmt.get_components_of_collection(component_collection=component_collection).keys())

func_name = st.selectbox(label="Component", options=["-- all --"] + all_funcs)

if func_name == "-- all --":
    for func_name, model in component_mgmt.get_components_of_collection(component_collection=component_collection).items():
        component_mgmt.render_component_doc(component_collection=component_collection, component_name=func_name)
else:
    component_mgmt.render_component_doc(component_collection=component_collection, component_name=func_name)




