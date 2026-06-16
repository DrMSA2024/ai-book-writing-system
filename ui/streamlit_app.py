"""Streamlit web interface."""

import streamlit as st
import asyncio
from pathlib import Path

from src.models.book_profile import BookProfile, BookType, WritingStyle, AcademicLevel
from src.orchestration.workflow import BookWritingWorkflow
from src.config import Config


def init_session_state():
    """Initialize session state."""
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    if "current_profile" not in st.session_state:
        st.session_state.current_profile = None
    if "workflow_result" not in st.session_state:
        st.session_state.workflow_result = None


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Book Writing System",
        page_icon="📚",
        layout="wide",
    )

    st.title("📚 Autonomous Book Writing System")
    st.markdown("---")

    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Create Book", "My Books", "Settings"],
    )

    init_session_state()

    if page == "Home":
        show_home()
    elif page == "Create Book":
        show_create_book()
    elif page == "My Books":
        show_my_books()
    elif page == "Settings":
        show_settings()


def show_home():
    """Show home page."""
    st.header("Welcome to the Autonomous Book Writing System")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Features
        - 🤖 Multi-Agent AI System
        - 📖 Complete Book Generation
        - 📝 LaTeX & PDF Export
        - ✨ AI Humanization
        - 🎨 Image Generation Prompts
        - ✅ Quality Assurance
        """)

    with col2:
        st.markdown("""
        ### Supported Book Types
        1. Academic Textbook
        2. Research Monograph
        3. Technical Handbook
        4. Competitive Exam Book
        5. Lab Manual
        6. Novel
        7. Biography
        8. Self Help
        9. Children's Book
        10. Question Bank
        """)

    st.markdown("---")
    st.info("📚 Get started by clicking 'Create Book' in the sidebar!")


def show_create_book():
    """Show create book page."""
    st.header("Create a New Book")

    with st.form("book_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("📖 Book Title", placeholder="Enter book title")
            author = st.text_input("✍️ Author Name", placeholder="Enter author name")
            subject = st.text_input("📚 Subject Area", placeholder="e.g., Machine Learning")
            target_readers = st.text_input(
                "👥 Target Readers",
                placeholder="e.g., Computer Science Students",
            )

        with col2:
            book_type = st.selectbox(
                "📚 Book Type",
                [bt.value for bt in BookType],
            )
            academic_level = st.selectbox(
                "🎓 Academic Level",
                [al.value for al in AcademicLevel],
            )
            writing_style = st.selectbox(
                "✒️ Writing Style",
                [ws.value for ws in WritingStyle],
            )
            total_pages = st.slider(
                "📄 Total Pages Target",
                min_value=50,
                max_value=1000,
                value=300,
                step=50,
            )

        submitted = st.form_submit_button("🚀 Create Book")

        if submitted:
            if not title or not author or not subject:
                st.error("Please fill in all required fields")
                return

            # Create profile
            profile = BookProfile(
                title=title,
                author=author,
                subject_area=subject,
                book_type=BookType(book_type),
                academic_level=AcademicLevel(academic_level),
                writing_style=WritingStyle(writing_style),
                target_readers=target_readers or subject,
                language="English",
                total_pages=total_pages,
            )

            st.session_state.current_profile = profile
            st.success("✓ Profile created! Starting workflow...")

            # Execute workflow
            with st.spinner("🔄 Processing book... This may take a few minutes..."):
                try:
                    workflow = BookWritingWorkflow()
                    result = asyncio.run(workflow.execute(profile))
                    st.session_state.workflow_result = result

                    if result["status"] == "success":
                        st.success(f"✓ Book created successfully!")
                        st.info(f"📁 Location: {result['book_dir']}")
                        st.info(f"📖 Chapters: {result['chapters']}")
                    else:
                        st.error(f"✗ Error: {result.get('error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def show_my_books():
    """Show my books page."""
    st.header("My Books")

    try:
        from src.memory.memory_manager import MemoryManager

        memory = MemoryManager(
            db_path=Config.MEMORY_DB,
            vector_store_path=Config.CHROMADB_PATH,
        )
        books = memory.get_all_books()

        if not books:
            st.info("No books found. Create your first book to get started!")
            return

        for book in books:
            with st.expander(f"📚 {book['title']} by {book['author']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Type:** {book['book_type']}")
                    st.write(f"**Subject:** {book['subject_area']}")
                    st.write(f"**Pages:** {book['total_pages']}")

                with col2:
                    st.write(f"**Created:** {book.get('created_at', 'N/A')}")
                    st.write(f"**Updated:** {book.get('updated_at', 'N/A')}")

    except Exception as e:
        st.error(f"Error loading books: {str(e)}")


def show_settings():
    """Show settings page."""
    st.header("Settings")

    st.subheader("DeepSeek API")
    api_key = st.text_input(
        "API Key",
        value=Config.DEEPSEEK_API_KEY[:10] + "***" if Config.DEEPSEEK_API_KEY else "",
        type="password",
    )

    st.subheader("Book Settings")
    col1, col2 = st.columns(2)

    with col1:
        humanization_level = st.selectbox(
            "Humanization Level",
            ["natural", "strict", "slight_imperfections"],
        )
        ai_score_target = st.slider(
            "Target AI Score",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05,
        )

    with col2:
        include_examples = st.checkbox("Include Examples", value=True)
        include_exercises = st.checkbox("Include Exercises", value=True)
        include_illustrations = st.checkbox(
            "Include Illustrations", value=True
        )

    if st.button("💾 Save Settings"):
        st.success("✓ Settings saved!")


if __name__ == "__main__":
    Config.setup()
    Config.validate()
    main()
