import subprocess
import os

def auto_commit_to_git(commit_message="Auto-update from Streamlit dashboard"):
    try:
        repo_path = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["git", "-C", repo_path, "add", "."], check=True)
        subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "-C", repo_path, "push"], check=True)
        print("✅ Changes committed and pushed to Git.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Commit and push changes to Git.")
    parser.add_argument("--msg", type=str, default="Auto-update from Streamlit dashboard", help="Git commit message")
    args = parser.parse_args()
    auto_commit_to_git(args.msg)