import pandas as pd
import math
import streamlit as st

def process_row(
    Site_Number, link_section, aadt_value, per_hgvs, year, lanes, value1, value2, df_psv_lookup
):
    # Helper function to round up values
    def roundup(value):
        return math.ceil(value)

    # Design period calculation
    if year == 0:
        design_period = 0
    else:
        design_period = (20 + 2025) - year

    # Calculation for AADT_HGVS
    if per_hgvs >= 11:
        result1 = per_hgvs
        AADT_HGVS = (result1 * (aadt_value / 100))
    else:
        result2 = 11
        AADT_HGVS = ((result2 * aadt_value) / 100)

    # Total projected AADT_HGVs
    total_projected_aadt_hgvs = AADT_HGVS * ((1 + 1.54 / 100) ** design_period)
    AADT_HGVS = round(AADT_HGVS)
    total_projected_aadt_hgvs = round(total_projected_aadt_hgvs)

    # Lane details
    lane1 = lane2 = lane3 = lane4 = lane_details_lane1 = lane_details_lane2 = lane_details_lane3 = lane_details_lane4 = 0

    if lanes == 1:
        lane1 = 100
        lane_details_lane1 = total_projected_aadt_hgvs
    elif lanes > 1 and lanes <= 3:
        if total_projected_aadt_hgvs < 5000:
            lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
            lane2 = round(100 - (100 - (0.0036 * total_projected_aadt_hgvs)))
        elif total_projected_aadt_hgvs >= 5000 and total_projected_aadt_hgvs < 25000:
            lane1 = round(89 - (0.0014 * total_projected_aadt_hgvs))
            lane2 = round(100 - lane1)
        elif total_projected_aadt_hgvs >= 25000:
            lane1 = 54
            lane2 = 100 - 54
            lane3 = 0
        lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = round(total_projected_aadt_hgvs * (lane2 / 100))

    elif lanes >= 4:
        if total_projected_aadt_hgvs <= 10500:
            lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
            lane_2_3 = (total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100))
            lane2 = round(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
            lane4 = 0
        elif total_projected_aadt_hgvs > 10500 and total_projected_aadt_hgvs < 25000:
            lane1 = round(75 - (0.0012 * total_projected_aadt_hgvs))
            lane_2_3 = (total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100))
            lane2 = round(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
            lane4 = 0
        elif total_projected_aadt_hgvs >= 25000:
            lane1 = 45
            lane_2_3 = (total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100))
            lane2 = round(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
            lane4 = 0
        lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = round((total_projected_aadt_hgvs - lane_details_lane1) * (lane2/100))
        lane_details_lane3 = round((total_projected_aadt_hgvs - (lane_details_lane1+lane_details_lane2)))

    # PSV Calculation - Placeholder logic (based on the upload of the PSV lookup table)
    def lookup_psv(lane_value):
        result = "NA"
        if lane_value > 0 and df_psv_lookup is not None:
            # Find the matching range column
            range_column = None
            for col in df_psv_lookup.columns:
                if '-' in col:
                    try:
                        col_range = list(map(float, col.split('-')))
                        if col_range[0] <= lane_value <= col_range[1]:
                            range_column = col
                            break
                    except:
                        continue
            if range_column:
                filtered_df = df_psv_lookup[
                    (df_psv_lookup['SiteCategory'].astype(str).str.strip().str.lower() == str(value1).strip().lower()) &
                    (df_psv_lookup['IL'].astype(float) == float(value2))
                ]
                if not filtered_df.empty:
                    result = filtered_df.iloc[0][range_column]
                else:
                    result = "No matching result found."
            else:
                result = "No matching range found"
        return result

    result1 = lookup_psv(lane_details_lane1)
    result2 = lookup_psv(lane_details_lane2)
    result3 = lookup_psv(lane_details_lane3)

    # Return result as dict (row for table)
    return {
        "Site Number": Site_Number,
        "Link Section": link_section,
        "AADT Value": aadt_value,
        "percent hgv": per_hgvs,
        "Year of Data": year,
        "Lanes": lanes,
        "AADT of HGVs": AADT_HGVS,
        "Design Period": design_period,
        "Total Projected AADT of HGVs": total_projected_aadt_hgvs,
        "% HGV in Lane 1": lane1,
        "% HGV in Lane 2": lane2 if lanes > 1 else 'NA',
        "% HGV in Lane 3": lane3 if lanes > 2 else 'NA',
        "% HGV in Lane 4": lane4 if lanes > 3 else 'NA',
        "Design traffic Lane 1": lane_details_lane1,
        "Design traffic Lane 2": lane_details_lane2,
        "Design traffic Lane 3": lane_details_lane3,
        "Design traffic Lane 4": lane_details_lane4,
        "Min.PSV Lane 1": result1,
        "Min.PSV Lane 2": result2,
        "Min.PSV Lane 3": result3
    }

# --- Main Streamlit App ---
st.title("Polished Stone Value (PSV) Calculator Results")

# Mode selection
input_mode = st.sidebar.radio("Select Input Mode:", ("Manual Entry", "Bulk Upload (CSV)"))

# PSV lookup table
st.sidebar.header("Upload DMRB CD 236 table 3.3b")
psv_lookup_file = st.sidebar.file_uploader("Upload PSV Lookup Excel file", type=["xlsx"])
df_psv_lookup = pd.read_excel(psv_lookup_file) if psv_lookup_file is not None else None

results_list = []

if input_mode == "Bulk Upload (CSV)":
    st.sidebar.header("Bulk CSV Upload")
    csv_file = st.sidebar.file_uploader("Upload Input CSV File", type=["csv"])
    if csv_file is not None:
        df_input = pd.read_csv(csv_file)
        # Standardize column names (strip spaces, fix typos, lower)
        df_input.columns = [col.strip().replace("categroy", "category").replace("Link section Number", "Link Section").replace("Year ", "Year").replace("Number of lanes", "Lanes").replace("AADT Value", "AADT Value").replace("% HGVs", "percent hgv").replace("IL Value", "IL Value") for col in df_input.columns]
        # Check for required columns
        expected_cols = ["Site Number","Link Section","AADT Value","percent hgv","Year","Lanes","Site category","IL Value"]
        # Mapping for possible variants
        mapping = {
            "Site category": ["Site category", "Site Category", "Site categroy"],
            "Link Section": ["Link Section", "Link section Number"],
            "AADT Value": ["AADT Value"],
            "percent hgv": ["percent hgv", "% HGVs"],
            "Year": ["Year", "Year "],
            "Lanes": ["Lanes", "Number of lanes"],
            "IL Value": ["IL Value"]
        }
        # Map columns to expected names
        for std, alts in mapping.items():
            for alt in alts:
                if alt in df_input.columns:
                    df_input.rename(columns={alt: std}, inplace=True)

        # Process each row and collect results
        for idx, row in df_input.iterrows():
            try:
                res = process_row(
                    Site_Number=row["Site Number"],
                    link_section=row["Link Section"],
                    aadt_value=row["AADT Value"],
                    per_hgvs=row["percent hgv"],
                    year=row["Year"],
                    lanes=int(row["Lanes"]),
                    value1=row["Site category"],
                    value2=row["IL Value"],
                    df_psv_lookup=df_psv_lookup
                )
                results_list.append(res)
            except Exception as e:
                st.warning(f"Row {idx+1} skipped due to error: {e}")

        st.subheader("Bulk PSV Calculation Results")
        if results_list:
            df_results = pd.DataFrame(results_list)
            st.write(df_results)
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="Download All Results as CSV",
                data=csv,
                file_name="psv_results_bulk.csv",
                mime="text/csv"
            )
        else:
            st.write("No results processed. Check your input files.")

else:
    # Manual Entry (same as your sidebar code, with session state)
    st.sidebar.header("Manual Entry")
    Site_Number = st.sidebar.text_input("Enter Site Number:")
    link_section = st.sidebar.text_input("Enter Link Section:")
    aadt_value = st.sidebar.number_input("Enter AADT value:", min_value=0)
    per_hgvs = st.sidebar.number_input("Enter % of HGVs:")
    year = st.sidebar.number_input("Enter Year", min_value=0)
    lanes = st.sidebar.number_input("Enter number of lanes", min_value=1)
    value1 = st.sidebar.text_input("Enter Site Category:")
    value2 = st.sidebar.number_input("Enter IL value:")

    if "results_list" not in st.session_state:
        st.session_state.results_list = []

    if st.sidebar.button("Add Entry"):
        res = process_row(
            Site_Number, link_section, aadt_value, per_hgvs, year, lanes, value1, value2, df_psv_lookup
        )
        st.session_state.results_list.append(res)

    st.subheader("Manual PSV Calculation Results:")
    if st.session_state.results_list:
        df_results = pd.DataFrame(st.session_state.results_list)
        st.write(df_results)
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="Download All Results as CSV",
            data=csv,
            file_name="psv_results.csv",
            mime="text/csv"
        )
    else:
        st.write("No results added yet.")

