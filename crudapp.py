import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure page
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Function to get a connection from Streamlit's secrets
@st.cache_resource
def get_connection():
    conn = sqlite3.connect(st.secrets["sqlite_db"], check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

cnx = get_connection()

# Initialize database if it doesn't exist
def init_db():
    cursor = cnx.cursor()
    
    # Create users table for authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create default admin user if no users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Default admin credentials: admin/admin123
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", admin_password, "admin")
        )
    
    # Check if new employee schema exists
    cursor.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "first_name" not in columns:
        # Migrate old schema to new schema
        cursor.execute("DROP TABLE IF EXISTS employees")
        cursor.execute("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER,
                position TEXT,
                department TEXT DEFAULT 'General',
                hire_date DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO employees (first_name, last_name, age, position, department) VALUES
            ('Alice', 'Johnson', 28, 'Manager', 'Management'),
            ('Bob', 'Smith', 32, 'Developer', 'Engineering'),
            ('Charlie', 'Brown', 26, 'Designer', 'Design'),
            ('Diana', 'Prince', 30, 'Analyst', 'Analytics'),
            ('Edward', 'Norton', 35, 'Project Manager', 'Management')
        """)
        cnx.commit()
    cursor.close()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def login_user(username, password):
    cursor = cnx.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    cursor.close()
    
    if user and verify_password(password, get_user_password_hash(username)):
        return {"id": user[0], "username": user[1], "role": user[2]}
    return None

def get_user_password_hash(username):
    cursor = cnx.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def is_authenticated():
    return st.session_state.get("authenticated", False)

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Login page
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Employee Management System</h1>
        <p>Please log in to access the system</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.subheader("Login")
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if username and password:
                    user = login_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
            
            st.divider()
            st.info("**Default credentials:**\n- Username: admin\n- Password: admin123")

init_db()

#b. Create Operation
def create_record():
    st.header("➕ Add New Employee")
    
    with st.container():
        st.markdown("### Employee Information")
        
        # Form layout with columns
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", placeholder="Enter first name")
            age = st.number_input("Age", min_value=18, max_value=100, value=25, help="Employee must be at least 18 years old")
        
        with col2:
            last_name = st.text_input("Last Name", placeholder="Enter last name")
            position = st.selectbox("Position", 
                                  ["Software Developer", "Project Manager", "Designer", "Analyst", 
                                   "Marketing Specialist", "HR Manager", "Sales Representative", "Other"],
                                  help="Select the employee's role")
        
        # Additional fields in expandable section
        with st.expander("📝 Additional Information"):
            department = st.selectbox("Department", 
                                    ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations", "Other"])
            email = st.text_input("Email Address", placeholder="employee@company.com")
            phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
        
        # Validation and submission
        if st.button("➕ Add Employee", type="primary", use_container_width=True):
            # Validation
            errors = []
            if not first_name.strip():
                errors.append("First name is required")
            if not last_name.strip():
                errors.append("Last name is required")
            if not position:
                errors.append("Position is required")
            if email and "@" not in email:
                errors.append("Please enter a valid email address")
            
            if errors:
                st.error("Please fix the following errors:")
                for error in errors:
                    st.write(f"• {error}")
            else:
                cursor = cnx.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO employees (first_name, last_name, age, position) VALUES (?, ?, ?, ?)",
                        (first_name.strip(), last_name.strip(), age, position)
                    )
                    cnx.commit()
                    
                    # Success message with employee details
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Employee <strong>{first_name} {last_name}</strong> has been added successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Clear form by rerunning
                    st.rerun()
                    
                except sqlite3.Error as err:
                    st.error(f"Database error: {err}")
                finally:
                    cursor.close()

#c. Read Operation
def read_records_pandas():
    st.header("📋 Employee Directory (DataFrame View)")
    
    # Search and filter section
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search employees", placeholder="Search by name or position...")
        
        with col2:
            position_filter = st.selectbox("Filter by Position", 
                                         ["All Positions", "Software Developer", "Project Manager", "Designer", 
                                          "Analyst", "Marketing Specialist", "HR Manager", "Sales Representative"])
        
        with col3:
            sort_by = st.selectbox("Sort by", ["ID", "First Name", "Last Name", "Age", "Position"])
    
    # Build query
    query = "SELECT id, first_name, last_name, age, position FROM employees WHERE 1=1"
    params = []
    
    if search_term:
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR position LIKE ?)"
        params.extend([f"%{search_term}%"] * 3)
    
    if position_filter != "All Positions":
        query += " AND position = ?"
        params.append(position_filter)
    
    # Sorting
    sort_columns = {
        "ID": "id",
        "First Name": "first_name", 
        "Last Name": "last_name",
        "Age": "age",
        "Position": "position"
    }
    query += f" ORDER BY {sort_columns[sort_by]}"
    
    try:
        data = pd.read_sql(query, cnx, params=params) if params else pd.read_sql(query, cnx)
        
        if not data.empty:
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Employees", len(data))
            with col2:
                st.metric("Average Age", f"{data['age'].mean():.1f}")
            with col3:
                st.metric("Youngest", data['age'].min())
            with col4:
                st.metric("Oldest", data['age'].max())
            
            # Pagination
            records_per_page = st.slider("Records per page", 5, 50, 10)
            total_records = len(data)
            total_pages = (total_records + records_per_page - 1) // records_per_page
            
            if total_pages > 1:
                page = st.number_input("Page", 1, total_pages, 1) - 1
                start_idx = page * records_per_page
                end_idx = start_idx + records_per_page
                paginated_data = data.iloc[start_idx:end_idx]
                
                st.info(f"Showing {start_idx + 1}-{min(end_idx, total_records)} of {total_records} employees")
            else:
                paginated_data = data
            
            # Display data with styling
            st.dataframe(
                paginated_data,
                use_container_width=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "first_name": st.column_config.TextColumn("First Name", width="medium"),
                    "last_name": st.column_config.TextColumn("Last Name", width="medium"),
                    "age": st.column_config.NumberColumn("Age", width="small"),
                    "position": st.column_config.TextColumn("Position", width="large")
                }
            )
        else:
            st.info("🤷‍♂️ No employees found matching your criteria")
            
    except sqlite3.Error as err:
        st.error(f"Database error: {err}")

def read_records_no_pandas():
    st.subheader("View Records (No Pandas)")
    
    # Search functionality
    search_term = st.text_input("🔍 Search by name or position")
    
    query = "SELECT id, first_name, last_name, age, position FROM employees"
    if search_term:
        query += f" WHERE first_name LIKE ? OR last_name LIKE ? OR position LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        cursor = cnx.cursor()
        cursor.execute(query, params)
        records = cursor.fetchall()
        cursor.close()
    else:
        cursor = cnx.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
    
    if records:
        # Pagination
        records_per_page = st.slider("Records per page", 1, 20, 5)
        total_records = len(records)
        total_pages = (total_records + records_per_page - 1) // records_per_page
        
        page = st.number_input("Page", 1, total_pages) - 1
        start_idx = page * records_per_page
        end_idx = start_idx + records_per_page
        paginated_records = records[start_idx:end_idx]
        
        st.write(f"Showing {start_idx + 1}-{min(end_idx, total_records)} of {total_records} records")
        for row in paginated_records:
            st.write(f"**ID:** {row[0]} | **Name:** {row[1]} {row[2]} | **Age:** {row[3]} | **Position:** {row[4]}")
    else:
        st.info("No records found")

# Data Visualization Functions
def show_data_visualization():
    st.header("📊 Data Analytics Dashboard")
    
    # Get data for visualization
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM employees")
    data = cursor.fetchall()
    cursor.close()
    
    if not data:
        st.info("No data available for visualization")
        return
    
    df = pd.DataFrame(data, columns=['id', 'first_name', 'last_name', 'age', 'position', 'department', 'hire_date', 'created_at'])
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "👥 Demographics", "🏢 Departments", "📅 Trends"])
    
    with tab1:
        show_overview_charts(df)
    
    with tab2:
        show_demographics_charts(df)
    
    with tab3:
        show_department_charts(df)
    
    with tab4:
        show_trends_charts(df)

def show_overview_charts(df):
    st.subheader("Employee Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", len(df))
    
    with col2:
        st.metric("Average Age", f"{df['age'].mean():.1f}")
    
    with col3:
        st.metric("Departments", df['department'].nunique())
    
    with col4:
        st.metric("Positions", df['position'].nunique())
    
    # Age distribution histogram
    fig_age = px.histogram(df, x='age', nbins=10, title="Age Distribution",
                          color_discrete_sequence=['#667eea'])
    fig_age.update_layout(showlegend=False)
    st.plotly_chart(fig_age, use_container_width=True)

def show_demographics_charts(df):
    st.subheader("Demographics Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age groups pie chart
        df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 45, 55, 100], 
                                labels=['18-25', '26-35', '36-45', '46-55', '55+'])
        age_group_counts = df['age_group'].value_counts()
        
        fig_age_groups = px.pie(values=age_group_counts.values, names=age_group_counts.index,
                               title="Age Groups Distribution", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_age_groups, use_container_width=True)
    
    with col2:
        # Gender distribution (assuming from names - simplified)
        df['gender'] = df['first_name'].apply(lambda x: 'Female' if x.endswith(('a', 'e', 'i', 'y')) else 'Male')
        gender_counts = df['gender'].value_counts()
        
        fig_gender = px.pie(values=gender_counts.values, names=gender_counts.index,
                           title="Gender Distribution", color_discrete_sequence=['#FF69B4', '#4169E1'])
        st.plotly_chart(fig_gender, use_container_width=True)

def show_department_charts(df):
    st.subheader("Department Analysis")
    
    # Department distribution
    dept_counts = df['department'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_dept_bar = px.bar(dept_counts, x=dept_counts.index, y=dept_counts.values,
                             title="Employees by Department", color=dept_counts.index,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_dept_bar.update_layout(xaxis_title="Department", yaxis_title="Count")
        st.plotly_chart(fig_dept_bar, use_container_width=True)
    
    with col2:
        # Average age by department
        avg_age_dept = df.groupby('department')['age'].mean().round(1)
        fig_avg_age = px.bar(avg_age_dept, x=avg_age_dept.index, y=avg_age_dept.values,
                           title="Average Age by Department", color=avg_age_dept.index,
                           color_discrete_sequence=px.colors.qualitative.Pastel2)
        fig_avg_age.update_layout(xaxis_title="Department", yaxis_title="Average Age")
        st.plotly_chart(fig_avg_age, use_container_width=True)

def show_trends_charts(df):
    st.subheader("Trends & Insights")
    
    # Position distribution
    position_counts = df['position'].value_counts()
    
    fig_positions = px.bar(position_counts, x=position_counts.index, y=position_counts.values,
                          title="Employees by Position", color=position_counts.values,
                          color_continuous_scale='Blues')
    fig_positions.update_layout(xaxis_title="Position", yaxis_title="Count")
    st.plotly_chart(fig_positions, use_container_width=True)
    
    # Age vs Position scatter plot
    fig_scatter = px.scatter(df, x='age', y='position', color='department',
                           title="Age Distribution by Position and Department",
                           size_max=10)
    st.plotly_chart(fig_scatter, use_container_width=True)

#d. Update Operation
def update_record():
    st.header("✏️ Update Employee Information")
    
    # Get all employees
    cursor = cnx.cursor()
    cursor.execute("SELECT id, first_name, last_name, position FROM employees ORDER BY last_name, first_name")
    employees = cursor.fetchall()
    cursor.close()
    
    if not employees:
        st.warning("No employees found to update")
        return
    
    # Employee selection with better display
    employee_options = [f"{emp[0]} - {emp[1]} {emp[2]} ({emp[3]})" for emp in employees]
    employee_dict = {opt: emp[0] for opt, emp in zip(employee_options, employees)}
    
    selected_employee = st.selectbox(
        "Select Employee to Update",
        employee_options,
        help="Choose an employee from the list"
    )
    
    if selected_employee:
        employee_id = employee_dict[selected_employee]
        
        # Get current data
        cursor = cnx.cursor()
        cursor.execute("SELECT first_name, last_name, age, position FROM employees WHERE id = ?", (employee_id,))
        current_data = cursor.fetchone()
        cursor.close()
        
        if current_data:
            first_name, last_name, age, position = current_data
            
            # Update form in a nice container
            with st.container():
                st.markdown("### Current Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Name:** {first_name} {last_name}")
                    st.info(f"**Age:** {age}")
                with col2:
                    st.info(f"**Position:** {position}")
                
                st.divider()
                st.markdown("### Update Information")
                
                # Form fields
                col1, col2 = st.columns(2)
                with col1:
                    new_first_name = st.text_input("First Name", value=first_name)
                    new_age = st.number_input("Age", min_value=18, max_value=100, value=age)
                
                with col2:
                    new_last_name = st.text_input("Last Name", value=last_name)
                    new_position = st.selectbox("Position", 
                                              ["Software Developer", "Project Manager", "Designer", "Analyst", 
                                               "Marketing Specialist", "HR Manager", "Sales Representative", "Other"],
                                              index=["Software Developer", "Project Manager", "Designer", "Analyst", 
                                                    "Marketing Specialist", "HR Manager", "Sales Representative", "Other"].index(position) 
                                                    if position in ["Software Developer", "Project Manager", "Designer", "Analyst", 
                                                                   "Marketing Specialist", "HR Manager", "Sales Representative", "Other"] 
                                                    else 0)
                
                # Update button
                if st.button("💾 Update Employee", type="primary", use_container_width=True):
                    # Validation
                    if not new_first_name.strip() or not new_last_name.strip():
                        st.error("First and last names are required")
                    else:
                        cursor = cnx.cursor()
                        try:
                            cursor.execute(
                                "UPDATE employees SET first_name = ?, last_name = ?, age = ?, position = ? WHERE id = ?",
                                (new_first_name.strip(), new_last_name.strip(), new_age, new_position, employee_id)
                            )
                            cnx.commit()
                            
                            st.markdown(f"""
                            <div class="success-message">
                                ✅ Employee information updated successfully!
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.rerun()
                            
                        except sqlite3.Error as err:
                            st.error(f"Database error: {err}")
                        finally:
                            cursor.close()

#e. Delete Operation
def delete_record():
    st.header("🗑️ Remove Employee")
    
    # Get all employees
    cursor = cnx.cursor()
    cursor.execute("SELECT id, first_name, last_name, position FROM employees ORDER BY last_name, first_name")
    employees = cursor.fetchall()
    cursor.close()
    
    if not employees:
        st.warning("No employees found to delete")
        return
    
    # Employee selection
    employee_options = [f"{emp[0]} - {emp[1]} {emp[2]} ({emp[3]})" for emp in employees]
    employee_dict = {opt: emp[0] for opt, emp in zip(employee_options, employees)}
    
    selected_employee = st.selectbox(
        "Select Employee to Remove",
        employee_options,
        help="⚠️ This action cannot be undone"
    )
    
    if selected_employee:
        employee_id = employee_dict[selected_employee]
        
        # Get employee details for confirmation
        cursor = cnx.cursor()
        cursor.execute("SELECT first_name, last_name, age, position FROM employees WHERE id = ?", (employee_id,))
        emp_data = cursor.fetchone()
        cursor.close()
        
        if emp_data:
            first_name, last_name, age, position = emp_data
            
            # Display employee info in a warning box
            st.markdown(f"""
            <div class="warning-message">
                <h4>⚠️ Confirm Deletion</h4>
                <p>You are about to delete the following employee:</p>
                <ul>
                    <li><strong>Name:</strong> {first_name} {last_name}</li>
                    <li><strong>Age:</strong> {age}</li>
                    <li><strong>Position:</strong> {position}</li>
                </ul>
                <p>This action cannot be undone.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Confirmation checkbox
            confirm_delete = st.checkbox("I understand this action cannot be undone")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Delete Employee", type="secondary", use_container_width=True, disabled=not confirm_delete):
                    if confirm_delete:
                        cursor = cnx.cursor()
                        try:
                            cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
                            cnx.commit()
                            
                            st.success(f"✅ Employee {first_name} {last_name} has been removed from the system")
                            st.rerun()
                            
                        except sqlite3.Error as err:
                            st.error(f"Database error: {err}")
                        finally:
                            cursor.close()
            
            with col2:
                st.button("Cancel", use_container_width=True, on_click=lambda: st.rerun())

#Putting It All Together
def main():
    # Check authentication
    if not is_authenticated():
        login_page()
        return
    
    # Header with gradient background
    st.markdown(f"""
    <div class="main-header">
        <h1>👥 Employee Management System</h1>
        <p>Welcome back, {st.session_state.user['username']}! | Role: {st.session_state.user['role'].title()}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with statistics and navigation
    with st.sidebar:
        st.title("📊 Dashboard")
        
        # User info
        st.write(f"**User:** {st.session_state.user['username']}")
        st.write(f"**Role:** {st.session_state.user['role'].title()}")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.divider()
        
        # Get statistics
        cursor = cnx.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(age) FROM employees")
        avg_age = cursor.fetchone()[0]
        
        cursor.execute("SELECT position, COUNT(*) as count FROM employees GROUP BY position ORDER BY count DESC LIMIT 1")
        most_common_position = cursor.fetchone()
        cursor.close()
        
        # Display metrics
        st.metric("Total Employees", total_employees)
        if avg_age:
            st.metric("Average Age", f"{avg_age:.1f}")
        if most_common_position:
            st.metric("Most Common Role", most_common_position[0])
        
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        menu = ["🏠 Home", "➕ Create", "📋 Read (Pandas)", "📄 Read (No Pandas)", "✏️ Update", "🗑️ Delete", "📊 Analytics"]
        choice = st.radio("Choose an action:", menu, label_visibility="collapsed")
        
        # Quick actions
        st.divider()
        st.subheader("Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.button("📊 Export Data", use_container_width=True):
            # Export functionality
            cursor = cnx.cursor()
            cursor.execute("SELECT * FROM employees")
            data = cursor.fetchall()
            cursor.close()
            
            if data:
                df = pd.DataFrame(data, columns=['ID', 'First Name', 'Last Name', 'Age', 'Position', 'Department', 'Hire Date', 'Created At'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data to export")

    # Main content area
    if choice == "🏠 Home":
        show_home_page()
    elif choice == "➕ Create":
        create_record()
    elif choice == "📋 Read (Pandas)":
        read_records_pandas()
    elif choice == "📄 Read (No Pandas)":
        read_records_no_pandas()
    elif choice == "✏️ Update":
        update_record()
    elif choice == "🗑️ Delete":
        delete_record()
    elif choice == "📊 Analytics":
        show_data_visualization()

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Built with ❤️ using Streamlit | Employee Management System v3.0</p>
    </div>
    """, unsafe_allow_html=True)

def show_home_page():
    st.header("Welcome to Employee Management System")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Create**\n\nAdd new employee records with detailed information including name, age, and position.")
    
    with col2:
        st.success("**Read**\n\nView and search through employee records with pagination support.")
    
    with col3:
        st.warning("**Update**\n\nModify existing employee information with easy-to-use forms.")
    
    st.divider()
    
    # Recent activity
    st.subheader("Recent Activity")
    cursor = cnx.cursor()
    cursor.execute("SELECT first_name, last_name, position FROM employees ORDER BY id DESC LIMIT 5")
    recent = cursor.fetchall()
    cursor.close()
    
    if recent:
        for emp in recent:
            st.write(f"• {emp[0]} {emp[1]} - {emp[2]}")
    else:
        st.info("No employees in the system yet. Start by adding some records!")

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Built with ❤️ using Streamlit | Employee Management System v2.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
#close the connection
#cnx.close()