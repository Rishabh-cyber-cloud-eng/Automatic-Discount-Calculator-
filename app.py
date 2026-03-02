import streamlit as st
import pandas as pd
import numpy as np
import os
import io

# ==========================================
# PAGE CONFIGURATION & BRANDING
# ==========================================
st.set_page_config(page_title="Automatic Discount Calculator", layout="wide", initial_sidebar_state="expanded")

st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-bottom: 0px;'>AUTOMATIC DISCOUNT CALCULATOR</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #4F46E5; font-family: sans-serif; font-weight: bold; margin-top: 0px;'>MADE BY CA RISHABH MALPANI</h3>", unsafe_allow_html=True)
st.divider()

# --- SESSION STATE INITIALIZATION ---
if 'merged_df' not in st.session_state:
    st.session_state.merged_df = None
if 'available_cols' not in st.session_state:
    st.session_state.available_cols = ["(Upload data to see columns)"] 
if 'staged_custom_rules' not in st.session_state:
    st.session_state.staged_custom_rules = pd.DataFrame()
if 'staged_adv_formula' not in st.session_state:
    st.session_state.staged_adv_formula = None

# ==========================================
# SERVER-SIDE STORAGE SETUP (Survives Refresh)
# ==========================================
UPLOAD_DIR = "uploaded_files"
# Create the directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ==========================================
# SIDEBAR: PREVIOUS UPLOADS HISTORY
# ==========================================
st.sidebar.header("📁 Previous Uploads")
st.sidebar.markdown("Files saved on the server (Survives Refresh):")

# Scan the actual folder on the server for saved files
saved_files = os.listdir(UPLOAD_DIR)

if saved_files:
    for fname in saved_files:
        file_path = os.path.join(UPLOAD_DIR, fname)
        with open(file_path, "rb") as f:
            fbytes = f.read()
            
        mime_type = "text/csv" if fname.endswith('.csv') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        st.sidebar.download_button(
            label=f"⬇️ {fname}",
            data=fbytes,
            file_name=fname,
            mime=mime_type,
            use_container_width=True
        )
else:
    st.sidebar.info("No files uploaded yet.")

# ==========================================
# FILE LOADING HELPER
# ==========================================
master_file_path = "Master_Dealer_File.xlsx"
ledger_file_path = "Sales_Ledger_Template.xlsx"
policy_file_path = "Discount policy.pdf" # Exact match with your GitHub repo!

def load_local_file(filepath):
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None

# ==========================================
# STEP 1: DOWNLOAD TEMPLATES & POLICY (Always Visible)
# ==========================================
with st.expander("📁 STEP 1: Download Discount Policy & Formatting Templates", expanded=True):
    
    # --- PROMINENT POLICY DOWNLOAD BOX ---
    st.info("📄 **FY26 Global Trade Discount Policy**\n\nPlease review the standard policy and settlement rules before proceeding to the calculation engine.")
    policy_bytes = load_local_file(policy_file_path)
    
    if policy_bytes:
        st.download_button(
            label="📥 Click Here to Download Discount Policy", 
            data=policy_bytes, 
            file_name="Discount policy.pdf", 
            mime="application/pdf", 
            type="primary", 
            use_container_width=True
        )
    else:
        st.warning("⚠️ 'Discount policy.pdf' not found on the server. Please ensure the filename matches exactly.")
        
    st.divider()
    st.markdown("Use these sample templates to test the app's functionality:")
    
    # --- TEMPLATE DOWNLOAD BOXES ---
    col_t1, col_t2 = st.columns(2)
    master_bytes = load_local_file(master_file_path)
    ledger_bytes = load_local_file(ledger_file_path)
    
    with col_t1:
        if master_bytes:
            st.download_button("📥 Download Master Dealer Template", data=master_bytes, file_name="Master_Dealer_File.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
        else:
            st.warning("Master_Dealer_File.xlsx not found in directory.")
            
    with col_t2:
        if ledger_bytes:
            st.download_button("📥 Download Sales Ledger Template", data=ledger_bytes, file_name="Sales_Ledger_Template.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
        else:
            st.warning("Sales_Ledger_Template.xlsx not found in directory.")

# ==========================================
# STEP 2: UPLOAD & REVIEW DATA
# ==========================================
st.subheader("📊 STEP 2: Upload & Review Data")
col_u1, col_u2 = st.columns(2)
with col_u1:
    master_file = st.file_uploader("Upload Master Dealer File", type=['xlsx', 'csv'])
with col_u2:
    ledger_file = st.file_uploader("Upload Sales Ledger", type=['xlsx', 'csv'])

master_df = None
ledger_df = None

# Save uploaded files physically to the server folder
if master_file:
    file_path = os.path.join(UPLOAD_DIR, master_file.name)
    if not os.path.exists(file_path): # Only save if it's not already there
        with open(file_path, "wb") as f:
            f.write(master_file.getbuffer())
        st.rerun() # Refresh app to update sidebar

if ledger_file:
    file_path = os.path.join(UPLOAD_DIR, ledger_file.name)
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(ledger_file.getbuffer())
        st.rerun()

if master_file and ledger_file:
    master_df = pd.read_excel(master_file) if master_file.name.endswith('.xlsx') else pd.read_csv(master_file)
    ledger_df = pd.read_excel(ledger_file) if ledger_file.name.endswith('.xlsx') else pd.read_csv(ledger_file)
    
    master_df.columns = master_df.columns.str.strip()
    ledger_df.columns = ledger_df.columns.str.strip()
    
    if 'Dealer_Code' in master_df.columns and 'Dealer_Code' in ledger_df.columns:
        master_df['Dealer_Code'] = master_df['Dealer_Code'].astype(str).str.strip()
        ledger_df['Dealer_Code'] = ledger_df['Dealer_Code'].astype(str).str.strip()
        st.success("✅ Files successfully loaded.")
        
        with st.expander("🔍 REVIEW: Master Dealer File", expanded=False):
            st.dataframe(master_df.head(5), use_container_width=True)
        with st.expander("🔍 REVIEW: Sales Ledger File", expanded=False):
            st.dataframe(ledger_df.head(5), use_container_width=True)
    else:
        st.error("CRITICAL ERROR: 'Dealer_Code' column is missing from your files.")

st.divider()

# ==========================================
# STEP 3: DYNAMIC VLOOKUP MAPPER
# ==========================================
st.subheader("🔗 STEP 3: Excel-Style VLOOKUP Builder")
st.markdown("Map columns from your Master File into your Sales Ledger. *(`Dealer_Tier` is merged automatically).*")

if not (master_file and ledger_file):
    st.info("🔒 Please upload both files in **STEP 2** to unlock the VLOOKUP Data Mapper.")
else:
    extra_master_cols = [col for col in master_df.columns if col not in ['Dealer_Code', 'Dealer_Tier']]
    
    vlookup_template = pd.DataFrame({
        "Source_Master_Column": pd.Series(dtype='str'),
        "New_Ledger_Column_Name": pd.Series(dtype='str')
    })
    
    vlookup_grid = st.data_editor(
        vlookup_template,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Source_Master_Column": st.column_config.SelectboxColumn("Source Column (From Master)", options=extra_master_cols, required=True),
            "New_Ledger_Column_Name": st.column_config.TextColumn("New Name in Ledger (Optional)", required=False)
        }
    )
    
    if st.button("🔄 Execute VLOOKUP & Merge Data", type="secondary"):
        extract_cols = ['Dealer_Code', 'Dealer_Tier']
        rename_dict = {}
        
        vlookup_clean = vlookup_grid.dropna(subset=['Source_Master_Column'])
        for _, row in vlookup_clean.iterrows():
            src_col = row['Source_Master_Column']
            if src_col in master_df.columns:
                extract_cols.append(src_col)
                new_name = str(row['New_Ledger_Column_Name']).strip()
                if new_name != "" and new_name != "nan":
                    rename_dict[src_col] = new_name
        
        master_subset = master_df[list(set(extract_cols))].rename(columns=rename_dict)
        st.session_state.merged_df = pd.merge(ledger_df, master_subset, on='Dealer_Code', how='left')
        st.session_state.available_cols = st.session_state.merged_df.columns.tolist()
        
        st.success("✅ Data VLOOKUP Complete! Proceed to Step 4.")
        with st.expander("🔍 Preview Merged Ledger Data", expanded=True):
            st.dataframe(st.session_state.merged_df.head(5), use_container_width=True)

st.divider()

# ==========================================
# STEP 4: RULES ENGINE DASHBOARD 
# ==========================================
st.subheader("⚙️ STEP 4: Configure Computing Engine")
st.markdown("Configure your standard policies and custom stacking rules below.")

tab1, tab2, tab3 = st.tabs(["🏛️ Standard Policy (Base Rules)", "⚡ Custom Scenarios (Rule Stacking)", "🧠 Advanced Formula"])

with tab1:
    st.markdown("**FY26 Global Trade Discount & Settlement Policy Configuration**")
    col_m1, col_m2 = st.columns([1.5, 1])
    
    with col_m1:
        st.caption("Base Volume Discount Matrix")
        default_matrix = pd.DataFrame({
            "Dealer_Tier": ["Platinum", "Platinum", "Platinum", "Gold", "Gold", "Gold", "Silver", "Silver", "Unregistered/Direct"],
            "Min_Qty": [1, 500, 1000, 1, 500, 1000, 1, 1000, 1],
            "Max_Qty": [499, 999, 999999, 499, 999, 999999, 999, 999999, 999999],
            "Discount_Percent": [5.0, 8.5, 12.0, 2.0, 5.0, 7.5, 0.0, 3.0, 0.0]
        })
        edited_matrix = st.data_editor(default_matrix, num_rows="dynamic", use_container_width=True)
        
    with col_m2:
        st.caption("Seasonal & Category Modifiers")
        elec_boost_month = st.multiselect("Electronics Boost (+2%)", [1,2,3,4,5,6,7, 8, 9, 10, 11, 12], default=[7, 8])
        elec_penalty_month = st.multiselect("Electronics Penalty (-1%)", [1,2,3,4,5,6,7, 8, 9, 10, 11, 12], default=[9])
        services_override = st.checkbox("Services strictly receive 0% volume discount", value=True)
        
        st.caption("Settlement Rules")
        early_days = st.number_input("Early Settlement (Days)", value=15)
        early_rebate = st.number_input("Early Rebate ($)", value=500.0)
        late_days = st.number_input("Late Penalty (Days)", value=45)
        late_penalty_pct = st.number_input("Late Penalty (%)", value=2.0)

with tab2:
    st.markdown("**Dynamic Custom Rule Grid (Rule Stacking)**")
    st.info("Click '+' to add scenarios. You MUST click 'Stage Custom Rules' below to save them for calculation.")
    
    custom_rules_template = pd.DataFrame({
        "Column_Name": pd.Series(dtype='str'),
        "Operator": pd.Series(dtype='str'),
        "Value": pd.Series(dtype='str'),
        "Action": pd.Series(dtype='str'),
        "Amount_Pct": pd.Series(dtype='float')
    })
    
    edited_custom_rules = st.data_editor(
        custom_rules_template,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Column_Name": st.column_config.SelectboxColumn("Target Column", options=st.session_state.available_cols, required=True),
            "Operator": st.column_config.SelectboxColumn("Condition", options=["Equals", "Not Equals", "Contains"], required=True),
            "Value": st.column_config.TextColumn("Condition Value", required=True),
            "Action": st.column_config.SelectboxColumn("Action to Take", options=["Add (%)", "Subtract (%)", "Set Discount To (%)"], required=True),
            "Amount_Pct": st.column_config.NumberColumn("Amount (%)", min_value=0.0, step=0.1, required=True)
        }
    )
    
    if st.button("✅ STAGE THESE CUSTOM RULES FOR CALCULATION", type="primary"):
        st.session_state.staged_custom_rules = edited_custom_rules.dropna(subset=['Column_Name', 'Operator', 'Value', 'Action', 'Amount_Pct'])
        st.success(f"Successfully staged {len(st.session_state.staged_custom_rules)} custom rule(s) for the engine!")

with tab3:
    st.markdown("**Advanced Formula Evaluator (Escape Hatch)**")
    advanced_formula = st.text_input("Enter Pandas query condition (e.g., `Quantity > 500 and Product_Category == 'Spares'`):", value="")
    advanced_action_amt = st.number_input("Add to Discount (%) if condition is met:", step=0.1, value=0.0)
    
    if st.button("✅ STAGE THIS ADVANCED FORMULA", type="primary"):
        st.session_state.staged_adv_formula = {"formula": advanced_formula, "amount": advanced_action_amt}
        st.success("Advanced Formula successfully staged for the engine!")

st.divider()

# ==========================================
# STEP 5: COMPUTATION ENGINE 
# ==========================================
st.subheader("🚀 STEP 5: Execution")

if st.session_state.merged_df is None:
     st.info("🔒 Ensure you have uploaded data and completed STEP 3 to unlock the Final Execution Engine.")
else:
    st.markdown("Ensure you have staged your custom rules before clicking Calculate.")
    if st.button("⚡ APPROVE LOGICS & CALCULATE FINAL OUTPUT", use_container_width=True, type="primary"):
        with st.spinner("Engaging Computing Engine..."):
            
            df = st.session_state.merged_df.copy()
            
            # Pre-process datatypes safely
            df['Dealer_Tier'] = df['Dealer_Tier'].fillna('Unregistered/Direct').astype(str).str.strip()
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0).astype(int)
            df['Gross_Invoice_Value'] = pd.to_numeric(df['Gross_Invoice_Value'], errors='coerce').fillna(0.0)
            df['Invoice_Date'] = pd.to_datetime(df['Invoice_Date'], errors='coerce')
            if 'Payment_Receipt_Date' in df.columns:
                df['Payment_Receipt_Date'] = df['Payment_Receipt_Date'].replace(['PENDING', 'pending'], pd.NaT)
                df['Payment_Receipt_Date'] = pd.to_datetime(df['Payment_Receipt_Date'], errors='coerce')

            df['Base_Discount_%'] = 0.0
            df['Policy_Modifiers_%'] = 0.0
            df['Custom_Adjustments_%'] = 0.0
            
            # --- 1. BASE MATRIX CALCULATOR ---
            for index, row in edited_matrix.iterrows():
                mask = (df['Dealer_Tier'] == row['Dealer_Tier']) & (df['Quantity'] >= row['Min_Qty']) & (df['Quantity'] <= row['Max_Qty'])
                df.loc[mask, 'Base_Discount_%'] = row['Discount_Percent']
                
            # --- 2. STANDARD POLICY MODIFIERS ---
            if services_override and 'Product_Category' in df.columns:
                df.loc[df['Product_Category'] == 'Services', 'Base_Discount_%'] = 0.0
                
            if 'Product_Category' in df.columns and 'Invoice_Date' in df.columns:
                elec_mask = df['Product_Category'] == 'Electronics'
                inv_month = df['Invoice_Date'].dt.month
                df.loc[elec_mask & inv_month.isin(elec_boost_month), 'Policy_Modifiers_%'] += 2.0
                df.loc[elec_mask & inv_month.isin(elec_penalty_month), 'Policy_Modifiers_%'] -= 1.0
            
            # --- 3. DYNAMIC CUSTOM RULE STACKING ---
            if not st.session_state.staged_custom_rules.empty:
                for idx, rule in st.session_state.staged_custom_rules.iterrows():
                    cond_col = rule['Column_Name']
                    operator = rule['Operator']
                    cond_val = str(rule['Value']).lower().strip()
                    action = rule['Action']
                    action_amt = float(rule['Amount_Pct'])
                    
                    if pd.notna(cond_col) and cond_col in df.columns:
                        col_data = df[cond_col].astype(str).str.lower().str.strip()
                        custom_mask = pd.Series(False, index=df.index)
                        
                        if operator == "Equals":
                            custom_mask = col_data == cond_val
                        elif operator == "Not Equals":
                            custom_mask = col_data != cond_val
                        elif operator == "Contains":
                            custom_mask = col_data.str.contains(cond_val, na=False)
                        
                        if action == "Add (%)":
                            df.loc[custom_mask, 'Custom_Adjustments_%'] += action_amt
                        elif action == "Subtract (%)":
                            df.loc[custom_mask, 'Custom_Adjustments_%'] -= action_amt
                        elif action == "Set Discount To (%)":
                            df.loc[custom_mask, 'Base_Discount_%'] = action_amt
                            df.loc[custom_mask, 'Policy_Modifiers_%'] = 0.0
            
            # --- 4. ADVANCED FORMULA ENGINE ---
            if st.session_state.staged_adv_formula is not None:
                adv_form = st.session_state.staged_adv_formula["formula"]
                adv_amt = st.session_state.staged_adv_formula["amount"]
                if adv_form.strip() != "" and adv_amt != 0.0:
                    try:
                        adv_mask = df.eval(adv_form)
                        df.loc[adv_mask, 'Custom_Adjustments_%'] += adv_amt
                    except Exception as e:
                        st.error(f"Advanced Formula Error: {e}. Skipping this rule.")
            
            # --- 5. AGGREGATE FINAL DISCOUNT ---
            df['Final_Discount_%'] = df['Base_Discount_%'] + df['Policy_Modifiers_%'] + df['Custom_Adjustments_%']
            df['Final_Discount_%'] = df['Final_Discount_%'].clip(lower=0.0) 
            df['Discount_Amount'] = df['Gross_Invoice_Value'] * (df['Final_Discount_%'] / 100.0)
            
            # --- 6. SETTLEMENT COMPUTATION ---
            df['Penalty_Percentage_%'] = 0.0
            df['Settlement_Adjustment_Amount'] = 0.0
            
            if 'Invoice_Date' in df.columns and 'Payment_Receipt_Date' in df.columns:
                valid_dates_mask = df['Invoice_Date'].notnull() & df['Payment_Receipt_Date'].notnull()
                days_gap = (df['Payment_Receipt_Date'] - df['Invoice_Date']).dt.days
                
                early_mask = valid_dates_mask & (days_gap <= early_days)
                df.loc[early_mask, 'Settlement_Adjustment_Amount'] = -early_rebate
                
                late_mask = valid_dates_mask & (days_gap > late_days)
                df.loc[late_mask, 'Penalty_Percentage_%'] = late_penalty_pct
                df.loc[late_mask, 'Settlement_Adjustment_Amount'] = df['Gross_Invoice_Value'] * (late_penalty_pct / 100.0)
            
            # --- 7. FINAL NET COMPUTATION ---
            df['Final_Net_Amount'] = df['Gross_Invoice_Value'] - df['Discount_Amount'] + df['Settlement_Adjustment_Amount']
            df['Final_Net_Amount'] = df['Final_Net_Amount'].clip(lower=0.0)
            
            base_cols = [col for col in st.session_state.available_cols if col != "(Upload data to see columns)"]
            calc_cols = ['Base_Discount_%', 'Policy_Modifiers_%', 'Custom_Adjustments_%', 'Final_Discount_%', 'Discount_Amount', 
                         'Penalty_Percentage_%', 'Settlement_Adjustment_Amount', 'Final_Net_Amount']
            
            output_cols = [col for col in base_cols + calc_cols if col in df.columns]
            output_df = df[output_cols]
            
            st.success("✅ Engine Computation Complete!")
            st.dataframe(output_df.head(15), use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                output_df.to_excel(writer, index=False, sheet_name='Computed_Output')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Computed Output (Excel)", 
                data=processed_data, 
                file_name="Calculated_Automatic_Discount.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
