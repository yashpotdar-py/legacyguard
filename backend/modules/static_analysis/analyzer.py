import subprocess
import tempfile
import json
import os


def analyze_code(code: str) -> dict:
    """
    Analyze a given Python code snippet using Bandit (a static analysis tool).
    The function writes the code to a temporary file, runs Bandit,
    and returns the parsed JSON output.
    """
    # Create a temporary file for the code snippet
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp_file:
        tmp_file.write(code)
        tmp_file_path = tmp_file.name

    try:
        # Build the Bandit command - do not JSON encode it
        cmd = f"bandit -r {tmp_file_path} -f json"

        # For security tools like Bandit, we need to handle all exit codes
        # Bandit returns exit code 1 when it finds security issues, which is a success from our perspective
        try:
            # Try normal execution first
            result = subprocess.check_output(cmd, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            # Bandit found security issues (exit code 1) or had another issue
            # We still want to parse the output if it exists
            if e.returncode == 1 and e.output:
                # This is expected when security issues are found
                result = e.output
            else:
                # This is an actual error
                raise

        try:
            # Parse the JSON output
            analysis = json.loads(result)
        except json.JSONDecodeError:
            # Handle case where output is not valid JSON
            analysis = {
                "error": "Failed to parse Bandit output as JSON", "raw_output": result}

    except subprocess.CalledProcessError as e:
        # Handle case where Bandit command fails with other return codes
        analysis = {
            "error": f"Bandit execution failed with return code {e.returncode}",
            "raw_output": e.output if hasattr(e, 'output') else "No output captured"
        }
    except FileNotFoundError:
        # Specifically catch the case where Bandit is not installed
        analysis = {
            "error": "Bandit not found. Make sure it's installed (pip install bandit) and in your PATH."}
    except Exception as e:
        # Catch any other unexpected errors
        analysis = {"error": f"Unexpected error: {str(e)}"}
    finally:
        # Clean up the temporary file
        os.remove(tmp_file_path)

    return analysis


# Example usage
if __name__ == "__main__":
    sample_code = """
def insecure_function(user_input):
    eval(user_input)  # This is dangerous!
    """
    analysis_result = analyze_code(sample_code)

    # Print a more user-friendly summary of the results
    if "error" in analysis_result and "raw_output" in analysis_result:
        # If we have raw_output, try to parse it even if there was an "error"
        # (which might just be a non-zero exit code)
        print("Error Analysis")
        try:
            parsed_output = json.loads(analysis_result["raw_output"])
            print("Security scan completed with the following results:")

            # Extract and display the security issues found
            if "results" in parsed_output and parsed_output["results"]:
                print(
                    f"Found {len(parsed_output['results'])} security issues:")
                for i, issue in enumerate(parsed_output["results"], 1):
                    print(f"\nIssue {i}:")
                    print(
                        f"  Severity: {issue.get('issue_severity', 'Unknown')}")
                    print(
                        f"  Confidence: {issue.get('issue_confidence', 'Unknown')}")
                    print(
                        f"  Description: {issue.get('issue_text', 'No description')}")
                    if "more_info" in issue:
                        print(f"  More info: {issue['more_info']}")
                    print(f"  Code: \n{issue.get('code', 'No code sample')}")
            else:
                print("No security issues found.")

            # Also print the original result for reference
            print("\nFull analysis result:")
            print(json.dumps(analysis_result, indent=2))
        except (json.JSONDecodeError, KeyError):
            # If parsing fails, fall back to the original output
            print(json.dumps(analysis_result, indent=2))
    else:
        # If there's no error or the format is different, print the full analysis
        print("Full Analysis")
        print(json.dumps(analysis_result, indent=2))
