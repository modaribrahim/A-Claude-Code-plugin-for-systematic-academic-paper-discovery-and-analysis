#!/usr/bin/env python3
"""
Input Selection and Validation for Paper Analysis

Helps users select which search session to analyze and validates compatibility.

Usage:
    # List available sessions
    python select_input.py \
        --search-dir /path/to/searching-papers-v2/artifacts \
        --list

    # Validate and get input path
    python select_input.py \
        --search-dir /path/to/searching-papers-v2/artifacts \
        --session session_20250128_143026 \
        --output analysis_config.json
"""

import click
import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def list_sessions(artifacts_dir: Path) -> List[Dict[str, Any]]:
    """List all available sessions"""
    index_path = artifacts_dir / "sessions_index.json"

    if not index_path.exists():
        # Try to find session folders manually
        session_dirs = [d for d in artifacts_dir.iterdir()
                       if d.is_dir() and d.name.startswith("session_")]
        sessions = []
        for session_dir in session_dirs:
            metadata_path = session_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                sessions.append({
                    "session_id": session_dir.name,
                    "path": str(session_dir),
                    "topic": metadata.get("topic", "Unknown"),
                    "search_type": metadata.get("search_type", "unknown"),
                    "total_papers": metadata.get("results_summary", {}).get("total_papers", 0),
                    "status": metadata.get("status", "unknown")
                })
        return sessions

    with open(index_path, 'r') as f:
        index = json.load(f)

    # Add full paths
    for session in index.get("sessions", []):
        session["path"] = str(artifacts_dir / session["session_id"])

    return index.get("sessions", [])


def validate_session(session_dir: Path) -> Dict[str, Any]:
    """Validate that a session is compatible for analysis"""
    errors = []
    warnings = []

    # Check session exists
    if not session_dir.exists():
        errors.append(f"Session directory not found: {session_dir}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Check metadata.json
    metadata_path = session_dir / "metadata.json"
    if not metadata_path.exists():
        errors.append("metadata.json not found")
    else:
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            errors.append("metadata.json is invalid JSON")
        except Exception as e:
            errors.append(f"Error reading metadata.json: {e}")

    # Check deduplicated.json
    papers_path = session_dir / "deduplicated.json"
    if not papers_path.exists():
        errors.append("deduplicated.json not found (this is the main paper collection)")
    else:
        try:
            with open(papers_path, 'r') as f:
                papers = json.load(f)

            if not isinstance(papers, list):
                errors.append("deduplicated.json should contain a list of papers")
            elif len(papers) == 0:
                warnings.append("deduplicated.json is empty (no papers found)")
            else:
                # Check paper schema
                sample = papers[0]
                required_fields = ['title']
                missing = [f for f in required_fields if f not in sample]
                if missing:
                    warnings.append(f"Some papers missing fields: {missing}")

        except json.JSONDecodeError:
            errors.append("deduplicated.json is invalid JSON")
        except Exception as e:
            errors.append(f"Error reading deduplicated.json: {e}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


@click.command()
@click.option('--search-dir', type=click.Path(exists=True), help='Path to searching-papers-v2/artifacts')
@click.option('--session', help='Session ID to select')
@click.option('--custom-json', type=click.Path(exists=True), help='Custom JSON file (not from search stage)')
@click.option('--output', type=click.Path(), help='Output analysis config JSON')
@click.option('--list', 'list_sessions', is_flag=True, help='List available sessions')
@click.option('--validate', is_flag=True, help='Only validate, don\'t create config')
@click.option('--verbose', is_flag=True)
def main(search_dir, session, custom_json, output, list_sessions, validate, verbose):
    """Select and validate input for paper analysis"""

    try:
        # List available sessions
        if list_sessions or not session and not custom_json:
            if not search_dir:
                click.echo("Error: --search-dir required when listing sessions", err=True)
                sys.exit(1)

            search_path = Path(search_dir)
            sessions = list_sessions(search_path)

            if not sessions:
                click.echo(f"No sessions found in {search_dir}")
                click.echo("\nYou can also use --custom-json to analyze any paper collection.")
                return

            click.echo(f"\n{'='*70}")
            click.echo(f"Available Sessions in {search_dir}")
            click.echo(f"{'='*70}\n")

            for i, s in enumerate(sessions, 1):
                status_symbol = "✓" if s["status"] == "completed" else "⚠"
                click.echo(f"{i}. {status_symbol} {s['session_id']}")
                click.echo(f"   Topic: {s['topic']}")
                click.echo(f"   Type: {s['search_type']}")
                click.echo(f"   Papers: {s['total_papers']}")
                click.echo(f"   Status: {s['status']}")
                click.echo(f"   Path: {s.get('path', s['session_id'])}")
                click.echo()

            click.echo("Usage:")
            click.echo("  python select_input.py --search-dir <path> --session <session_id> --output config.json")
            click.echo("  python select_input.py --custom-json <path> --output config.json")
            return

        # Validate session
        if session:
            if not search_dir:
                click.echo("Error: --search-dir required when using --session", err=True)
                sys.exit(1)

            search_path = Path(search_dir)
            session_path = search_path / session

            if verbose:
                click.echo(f"Validating session: {session}")

            validation = validate_session(session_path)

            # Print validation results
            if validation["errors"]:
                click.echo("Errors:", err=True)
                for error in validation["errors"]:
                    click.echo(f"  ❌ {error}", err=True)

            if validation["warnings"]:
                click.echo("Warnings:")
                for warning in validation["warnings"]:
                    click.echo(f"  ⚠️  {warning}")

            if not validation["valid"]:
                click.echo(f"\n❌ Session validation failed", err=True)
                sys.exit(1)

            # Load metadata
            metadata_path = session_path / "metadata.json"
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Load papers count
            papers_path = session_path / "deduplicated.json"
            with open(papers_path, 'r') as f:
                papers = json.load(f)
            paper_count = len(papers)

            if verbose:
                click.echo(f"✓ Session validated")
                click.echo(f"  Papers: {paper_count}")
                click.echo(f"  Search type: {metadata.get('search_type')}")

            # Create analysis config
            config = {
                "input_type": "session",
                "input_path": str(session_path / "deduplicated.json"),
                "session_id": session,
                "session_path": str(session_path),
                "metadata": metadata,
                "paper_count": paper_count,
                "search_type": metadata.get("search_type"),
                "analysis_type": "full" if paper_count > 100 else "quick"
            }

        elif custom_json:
            custom_path = Path(custom_json)

            if verbose:
                click.echo(f"Validating custom JSON: {custom_json}")

            # Load papers
            with open(custom_path, 'r') as f:
                papers = json.load(f)

            if not isinstance(papers, list):
                click.echo("Error: Custom JSON must contain a list of papers", err=True)
                sys.exit(1)

            paper_count = len(papers)

            # Basic validation
            if paper_count == 0:
                click.echo("Warning: No papers found in file", err=True)
            else:
                sample = papers[0]
                if 'title' not in sample:
                    click.echo("Warning: Papers missing 'title' field", err=True)

            if verbose:
                click.echo(f"✓ Custom JSON validated")
                click.echo(f"  Papers: {paper_count}")

            # Create analysis config
            config = {
                "input_type": "custom",
                "input_path": str(custom_path),
                "paper_count": paper_count,
                "search_type": "custom",
                "analysis_type": "full" if paper_count > 100 else "quick"
            }

        else:
            click.echo("Error: Must specify --session or --custom-json", err=True)
            sys.exit(1)

        if validate:
            # Just validating, don't create config
            click.echo("\n✓ Validation passed")
            return

        # Save config
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)

            click.echo(f"\n✓ Analysis config saved to: {output}")
            click.echo(f"  Input: {config['input_path']}")
            click.echo(f"  Papers: {config['paper_count']}")
            click.echo(f"  Analysis type: {config['analysis_type']}")
        else:
            # Print to stdout
            click.echo("\n" + "="*70)
            click.echo("Analysis Configuration")
            click.echo("="*70)
            click.echo(json.dumps(config, indent=2))

    except FileNotFoundError as e:
        click.echo(f"Error: File not found: {e}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
