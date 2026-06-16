"""Sample book generation example."""

import asyncio
from pathlib import Path

from src.config import Config
from src.models.book_profile import BookProfile, BookType, WritingStyle, AcademicLevel
from src.orchestration.workflow import BookWritingWorkflow


async def main():
    """Generate sample book."""
    # Setup
    Config.setup()
    Config.validate()

    print("\n" + "=" * 60)
    print("  Autonomous Book Writing System - Sample Execution")
    print("=" * 60 + "\n")

    # Create book profile
    profile = BookProfile(
        title="Machine Learning Fundamentals",
        author="Dr. AI Assistant",
        subject_area="Machine Learning & Artificial Intelligence",
        book_type=BookType.ACADEMIC_TEXTBOOK,
        academic_level=AcademicLevel.UNDERGRADUATE,
        writing_style=WritingStyle.FORMAL,
        target_readers="Computer Science Students and AI Enthusiasts",
        language="English",
        total_pages=300,
        include_examples=True,
        include_exercises=True,
        include_illustrations=True,
        include_bibliography=True,
        humanization_level="natural",
        ai_score_target=0.10,
    )

    print(f"📖 Book Profile:")
    print(f"   Title: {profile.title}")
    print(f"   Author: {profile.author}")
    print(f"   Type: {profile.book_type}")
    print(f"   Pages: {profile.total_pages}")
    print(f"   Subject: {profile.subject_area}\n")

    # Initialize workflow
    print("🚀 Initializing workflow...\n")
    workflow = BookWritingWorkflow()

    # Execute workflow
    print("⚙️  Executing book writing workflow...\n")
    result = await workflow.execute(profile)

    # Print results
    print("\n" + "=" * 60)
    if result["status"] == "success":
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"📚 Book: {profile.title}")
        print(f"📁 Location: {result['book_dir']}")
        print(f"📖 Chapters: {result['chapters']}")
        print(f"✨ Status: {result['state']}")
    else:
        print("❌ WORKFLOW FAILED")
        print("=" * 60)
        print(f"Error: {result.get('error')}")
        print(f"State: {result.get('state')}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
