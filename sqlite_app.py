import streamlit as st
import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt

# Database file path
db_file = 'student_records.db'

sample_data = [
    ('Alice Johnson', 19, 'Computer Science'),
    ('Bob Smith', 20, 'Engineering'),
    ('Charlie Brown', 21, 'Biology'),
    ('Diana Prince', 22, 'Mathematics'),
    ('Edward Norton', 18, 'Physics')
]

def get_connection():
    """Create and return a database connection."""
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as err:
        st.error(f"Database connection error: {err}")
        return None

def initialize_database():
    """Initialize the database with sample data if it doesn't exist."""
    if not os.path.exists(db_file):
        try:
            conn = get_connection()
            if conn is None:
                return
            
            cursor = conn.cursor()

            # Create students table
            cursor.execute('''
                CREATE TABLE students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    major TEXT
                )
            ''')

            # Insert sample data
            cursor.executemany('INSERT INTO students (name, age, major) VALUES (?, ?, ?)', sample_data)
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            st.error(f"Database initialization error: {err}")

def migrate_database():
    """Migrate existing database and align it with the sample data."""
    try:
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()

        # Check if the students table exists and contains the expected columns
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        if not columns:
            conn.close()
            return

        column_names = [col[1] for col in columns]
        if 'grade' in column_names and 'major' not in column_names:
            try:
                cursor.execute("ALTER TABLE students RENAME COLUMN grade TO major")
                conn.commit()
                st.info("Database migrated: 'grade' column renamed to 'major'")
                column_names = [col[1] for col in cursor.execute("PRAGMA table_info(students)").fetchall()]
            except sqlite3.Error as err:
                st.warning(f"Column rename error: {err}")

        # Ensure sample rows are present and correct
        updated = False
        cursor.execute("SELECT name, age, major FROM students")
        existing = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

        for name, age, major in sample_data:
            try:
                if name in existing:
                    if existing[name] != (age, major):
                        cursor.execute(
                            "UPDATE students SET age = ?, major = ? WHERE name = ?",
                            (age, major, name)
                        )
                        updated = True
                else:
                    cursor.execute(
                        "INSERT INTO students (name, age, major) VALUES (?, ?, ?)",
                        (name, age, major)
                    )
                    updated = True
            except sqlite3.Error as err:
                st.warning(f"Data sync error for {name}: {err}")

        if updated:
            conn.commit()
            st.info("Sample data was synchronized to the database.")

        conn.close()
    except sqlite3.Error as err:
        st.warning(f"Database migration error: {err}")

def get_data():
    """Fetch data from the students table."""
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        return pd.DataFrame(result, columns=columns)
    except sqlite3.Error as err:
        st.error(f"Error fetching data: {err}")
        return pd.DataFrame()

def delete_student(student_id):
    """Delete a student record from the database."""
    try:
        conn = get_connection()
        if conn is None:
            st.error("Failed to connect to database for deletion.")
            return False
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as err:
        st.error(f"Error deleting student: {err}")
        return False

def update_student(student_id, name, age, major):
    """Update a student record in the database."""
    try:
        conn = get_connection()
        if conn is None:
            st.error("Failed to connect to database for update.")
            return False
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, age = ?, major = ? WHERE id = ?",
            (name, age, major, student_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as err:
        st.error(f"Error updating student: {err}")
        return False

# Initialize database on first run
initialize_database()

# Migrate database if needed
migrate_database()

# Main Streamlit app
def main():
    st.title("Student Records Database (SQLite)")
    st.write("This app displays student information from a local SQLite database.")
    st.info("✅ Using SQLite - no MySQL setup required!")

    # Fetch and display data
    df = get_data()
    if not df.empty:
        st.success("Successfully connected to database!")
        
        # Add filtering section
        st.subheader("Filter Students")
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter by major
            majors = df['major'].unique().tolist()
            selected_majors = st.multiselect(
                "Select Major(s):",
                options=majors,
                default=majors
            )
        
        with col2:
            # Filter by age range
            min_age, max_age = int(df['age'].min()), int(df['age'].max())
            age_range = st.slider(
                "Select Age Range:",
                min_value=min_age,
                max_value=max_age,
                value=(min_age, max_age)
            )
        
        # Apply filters
        filtered_df = df[
            (df['major'].isin(selected_majors)) &
            (df['age'] >= age_range[0]) &
            (df['age'] <= age_range[1])
        ]
        
        st.subheader(f"Filtered Results ({len(filtered_df)} records)")
        st.dataframe(filtered_df)

        # Data Visualization
        st.subheader("Data Visualization")
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Bar chart: Students by Major
            st.write("**Students by Major**")
            major_counts = filtered_df['major'].value_counts()
            fig, ax = plt.subplots(figsize=(8, 5))
            major_counts.plot(kind='bar', ax=ax, color='steelblue')
            ax.set_xlabel("Major")
            ax.set_ylabel("Number of Students")
            ax.set_title("Distribution of Students by Major")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        
        with viz_col2:
            # Histogram: Age Distribution
            st.write("**Age Distribution**")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(filtered_df['age'], bins=10, color='coral', edgecolor='black')
            ax.set_xlabel("Age")
            ax.set_ylabel("Frequency")
            ax.set_title("Age Distribution of Students")
            st.pyplot(fig)

        # Add some interactivity
        st.subheader("Add New Student")
        with st.form("add_student"):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=15, max_value=50, value=18)
            major = st.text_input("Major")
            submitted = st.form_submit_button("Add Student")

            if submitted:
                if not name:
                    st.error("Please enter a student name.")
                elif not major:
                    st.error("Please enter a major.")
                else:
                    try:
                        conn = get_connection()
                        if conn is None:
                            st.error("Failed to connect to database.")
                        else:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO students (name, age, major) VALUES (?, ?, ?)",
                                         (name, age, major))
                            conn.commit()
                            conn.close()
                            st.success(f"Successfully added {name} to the database!")
                            st.rerun()
                    except sqlite3.IntegrityError as err:
                        st.error(f"Data integrity error: {err}")
                    except sqlite3.Error as err:
                        st.error(f"Database error while adding student: {err}")

        # Update Student Section
        st.subheader("Update Student")
        df_all = get_data()
        if not df_all.empty:
            try:
                student_options = df_all.set_index('id')['name'].to_dict()
                selected_student_id = st.selectbox(
                    "Select a student to update:",
                    options=student_options.keys(),
                    format_func=lambda x: student_options[x]
                )
                
                student_record = df_all[df_all['id'] == selected_student_id].iloc[0]
                
                with st.form("update_student"):
                    new_name = st.text_input("Name", value=student_record['name'])
                    new_age = st.number_input("Age", min_value=15, max_value=50, value=int(student_record['age']))
                    new_major = st.text_input("Major", value=student_record['major'])
                    update_submitted = st.form_submit_button("Update Student")
                    
                    if update_submitted:
                        if not new_name or not new_major:
                            st.error("Name and Major cannot be empty.")
                        else:
                            if update_student(selected_student_id, new_name, new_age, new_major):
                                st.success(f"Successfully updated {new_name}!")
                                st.rerun()
            except Exception as err:
                st.error(f"Error in update section: {err}")

        # Delete Student Section
        st.subheader("Delete Student")
        if not df_all.empty:
            try:
                student_delete_options = df_all.set_index('id')['name'].to_dict()
                selected_delete_id = st.selectbox(
                    "Select a student to delete:",
                    options=student_delete_options.keys(),
                    format_func=lambda x: student_delete_options[x],
                    key="delete_selectbox"
                )
                
                col_delete1, col_delete2 = st.columns(2)
                with col_delete1:
                    confirm_delete = st.checkbox("I confirm the deletion")
                
                with col_delete2:
                    if st.button("Delete Student", disabled=not confirm_delete):
                        try:
                            student_name = student_delete_options[selected_delete_id]
                            if delete_student(selected_delete_id):
                                st.success(f"Successfully deleted {student_name} from the database!")
                                st.rerun()
                        except KeyError as err:
                            st.error(f"Student not found: {err}")
                        except Exception as err:
                            st.error(f"Error deleting student: {err}")
            except Exception as err:
                st.error(f"Error in delete section: {err}")
    else:
        st.warning("No data to display.")

if __name__ == "__main__":
    main()