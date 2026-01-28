#!/usr/bin/env python3
"""
Session Management for Paper Search

Creates and manages search sessions with metadata tracking.
Supports session creation, extension, and merging.

Usage:
    # Create new session
    python create_session.py \
        --topic "change detection" \
        --search-type comprehensive \
        --create \
        --output artifacts/session_20250128_143026

    # Extend existing session
    python create_session.py \
        --parent-session session_20250128_143026 \
        --extend \
        --output artifacts/session_20250128_150000
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def generate_session_id(topic: str) -> str:
    """Generate unique session ID from timestamp and topic"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Extract keywords from topic (first 2-3 words)
    keywords = "_".join(topic.lower().split()[:3])
    return f"session_{timestamp}_{keywords}"


def load_session_index(artifacts_dir: Path) -> Dict[str, Any]:
    """Load or create sessions index"""
    index_path = artifacts_dir / "sessions_index.json"
    if index_path.exists():
        with open(index_path, 'r') as f:
            return json.load(f)
    return {"sessions": []}


def save_session_index(artifacts_dir: Path, index: Dict[str, Any]):
    """Save sessions index"""
    index_path = artifacts_dir / "sessions_index.json"
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)


def load_parent_session(artifacts_dir: Path, parent_id: str) -> Dict[str, Any]:
    """Load parent session metadata"""
    parent_path = artifacts_dir / parent_id / "metadata.json"
    if not parent_path.exists():
        raise FileNotFoundError(f"Parent session not found: {parent_id}")

    with open(parent_path, 'r') as f:
        return json.load(f)


def load_parent_papers(artifacts_dir: Path, parent_id: str) -> list:
    """Load parent session papers"""
    papers_path = artifacts_dir / parent_id / "deduplicated.json"
    if not papers_path.exists():
        raise FileNotFoundError(f"Parent papers not found: {parent_id}")

    with open(papers_path, 'r') as f:
        return json.load(f)


def merge_papers(parent_papers: list, new_papers: list) -> list:
    """Merge parent and new papers, deduplicating by title/DOI"""
    # Use set to track seen papers
    seen = set()
    merged = []

    # Add parent papers first
    for paper in parent_papers:
        key = (paper.get('title', ''), paper.get('doi', ''))
        if key not in seen:
            seen.add(key)
            merged.append(paper)

    # Add new papers (avoid duplicates)
    for paper in new_papers:
        key = (paper.get('title', ''), paper.get('doi', ''))
        if key not in seen:
            seen.add(key)
            merged.append(paper)

    return merged


@click.group()
def cli():
    """Session management for paper search"""
    pass


@cli.command()
@click.option('--topic', required=True, help='Research topic')
@click.option('--search-type', required=True,
              type=click.Choice(['quick', 'comprehensive']),
              help='Type of search')
@click.option('--time-range', help='Time range (e.g., "last_5_years")')
@click.option('--min-citations', type=int, default=0, help='Minimum citations')
@click.option('--venues', help='Comma-separated list of venues')
@click.option('--max-papers', type=int, help='Maximum papers')
@click.option('--query', help='Search query used')
@click.option('--categories', help='Comma-separated arXiv categories')
@click.option('--year-from', type=int, help='Start year')
@click.option('--year-to', type=int, help='End year')
@click.option('--sources', help='Comma-separated sources')
@click.option('--output', required=True, type=click.Path(), help='Output session directory')
@click.option('--verbose', is_flag=True)
def create(topic, search_type, time_range, min_citations, venues, max_papers,
           query, categories, year_from, year_to, sources, output, verbose):
    """Create a new search session"""
    try:
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        if verbose:
            click.echo(f"Creating session: {output_path.name}")

        # Build metadata
        metadata = {
            "session_id": output_path.name,
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "search_type": search_type,
            "user_preferences": {
                "time_range": time_range,
                "min_citations": min_citations,
                "venues": venues.split(',') if venues else [],
                "max_papers": max_papers
            },
            "search_parameters": {
                "query": query or topic,
                "categories": categories.split(',') if categories else [],
                "year_from": year_from,
                "year_to": year_to,
                "min_citations": min_citations,
                "sources": sources.split(',') if sources else []
            },
            "results_summary": {},
            "parent_session": None,
            "child_sessions": [],
            "status": "created"
        }

        # Save metadata
        metadata_path = output_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Update sessions index
        artifacts_dir = output_path.parent
        index = load_session_index(artifacts_dir)
        index["sessions"].append({
            "session_id": output_path.name,
            "timestamp": metadata["timestamp"],
            "topic": topic,
            "search_type": search_type,
            "total_papers": 0,
            "status": "created"
        })
        save_session_index(artifacts_dir, index)

        click.echo(f"✓ Created session: {output_path.name}")
        click.echo(f"  Metadata: {metadata_path}")
        click.echo(f"  Search type: {search_type}")

    except Exception as e:
        click.echo(f"Error creating session: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--parent-session', required=True, help='Parent session ID')
@click.option('--new-papers', type=click.Path(exists=True), help='New papers JSON file')
@click.option('--output', required=True, type=click.Path(), help='Extended session directory')
@click.option('--verbose', is_flag=True)
def extend(parent_session, new_papers, output, verbose):
    """Extend an existing session with new papers"""
    try:
        # Find artifacts directory
        output_path = Path(output)
        artifacts_dir = output_path.parent

        if verbose:
            click.echo(f"Extending session: {parent_session}")

        # Load parent session
        parent_metadata = load_parent_session(artifacts_dir, parent_session)
        parent_papers = load_parent_papers(artifacts_dir, parent_session)

        if verbose:
            click.echo(f"  Parent has {len(parent_papers)} papers")

        # Load new papers
        if new_papers:
            with open(new_papers, 'r') as f:
                new_papers_data = json.load(f)
            # Handle both list and dict formats
            if isinstance(new_papers_data, dict):
                new_papers_list = new_papers_data.get('papers', [])
            else:
                new_papers_list = new_papers_data
        else:
            new_papers_list = []

        if verbose:
            click.echo(f"  New papers: {len(new_papers_list)}")

        # Merge papers
        merged_papers = merge_papers(parent_papers, new_papers_list)

        if verbose:
            click.echo(f"  Merged: {len(merged_papers)} papers")

        # Create extended session
        output_path.mkdir(parents=True, exist_ok=True)

        # Create metadata for extended session
        metadata = {
            "session_id": output_path.name,
            "timestamp": datetime.now().isoformat(),
            "topic": parent_metadata["topic"] + " (extended)",
            "search_type": parent_metadata["search_type"],
            "user_preferences": parent_metadata["user_preferences"],
            "search_parameters": parent_metadata["search_parameters"],
            "results_summary": parent_metadata["results_summary"],
            "parent_session": parent_session,
            "child_sessions": [],
            "status": "extended"
        }

        # Save metadata
        metadata_path = output_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save merged papers
        papers_path = output_path / "deduplicated.json"
        with open(papers_path, 'w') as f:
            json.dump(merged_papers, f, indent=2)

        # Update parent's child_sessions
        parent_metadata_path = artifacts_dir / parent_session / "metadata.json"
        with open(parent_metadata_path, 'r') as f:
            parent_meta = json.load(f)
        parent_meta["child_sessions"].append(output_path.name)
        with open(parent_metadata_path, 'w') as f:
            json.dump(parent_meta, f, indent=2)

        # Update sessions index
        index = load_session_index(artifacts_dir)
        index["sessions"].append({
            "session_id": output_path.name,
            "timestamp": metadata["timestamp"],
            "topic": metadata["topic"],
            "search_type": metadata["search_type"],
            "total_papers": len(merged_papers),
            "status": "extended"
        })
        save_session_index(artifacts_dir, index)

        click.echo(f"✓ Extended session: {output_path.name}")
        click.echo(f"  Parent: {parent_session}")
        click.echo(f"  Total papers: {len(merged_papers)}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error extending session: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--session-dir', required=True, type=click.Path(exists=True))
@click.option('--total-papers', type=int, required=True, help='Total paper count')
@click.option('--year-from', type=int, help='Year range start')
@click.option('--year-to', type=int, help='Year range end')
@click.option('--top-venues', help='JSON string of venue counts')
@click.option('--citation-stats', help='JSON string of citation stats')
@click.option('--verbose', is_flag=True)
def update(session_dir, total_papers, year_from, year_to, top_venues, citation_stats, verbose):
    """Update session metadata with results summary"""
    try:
        session_path = Path(session_dir)
        metadata_path = session_path / "metadata.json"

        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        # Load existing metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Update with results summary
        metadata["results_summary"] = {
            "total_papers": total_papers,
            "year_range": [year_from, year_to] if year_from and year_to else [],
            "top_venues": json.loads(top_venues) if top_venues else {},
            "citation_stats": json.loads(citation_stats) if citation_stats else {}
        }
        metadata["status"] = "completed"

        # Save updated metadata
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Update sessions index
        artifacts_dir = session_path.parent
        index = load_session_index(artifacts_dir)
        for session in index["sessions"]:
            if session["session_id"] == session_path.name:
                session["total_papers"] = total_papers
                session["status"] = "completed"
                break
        save_session_index(artifacts_dir, index)

        click.echo(f"✓ Updated session: {session_path.name}")
        click.echo(f"  Total papers: {total_papers}")
        click.echo(f"  Status: completed")

    except Exception as e:
        click.echo(f"Error updating session: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--artifacts-dir', type=click.Path(exists=True), default='artifacts')
@click.option('--verbose', is_flag=True)
def list(artifacts_dir, verbose):
    """List all sessions"""
    try:
        artifacts_path = Path(artifacts_dir)
        index = load_session_index(artifacts_path)

        if not index["sessions"]:
            click.echo("No sessions found")
            return

        click.echo(f"\n{'='*60}")
        click.echo(f"Total sessions: {len(index['sessions'])}")
        click.echo(f"{'='*60}\n")

        for session in index["sessions"]:
            click.echo(f"Session: {session['session_id']}")
            click.echo(f"  Topic: {session['topic']}")
            click.echo(f"  Type: {session['search_type']}")
            click.echo(f"  Papers: {session['total_papers']}")
            click.echo(f"  Status: {session['status']}")
            click.echo(f"  Created: {session['timestamp']}")
            click.echo()

    except Exception as e:
        click.echo(f"Error listing sessions: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
