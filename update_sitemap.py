#!/usr/bin/env python3
"""
Automatically update sitemap.xml with last modification dates from git or file system.

Usage:
    python3 update_sitemap.py
    python3 update_sitemap.py --use-filesystem  # Use file modification dates instead of git
"""

import os
import sys
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import argparse
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Route to template file mapping
ROUTE_TO_FILE = {
    "/": "templates/index.html"
}

# Priority mapping (can be customized)
PRIORITY_MAP = {
    "/": 1.0,
    "/page_route": 0.9,
    "/page_route": 0.8,
}

# Change frequency mapping
CHANGEFREQ_MAP = {
    "/": "weekly",
    "/page_route": "weekly",
    "/page_route": "daily",
    "/page_route": "monthly",
    "/page_route": "yearly",
}


def get_git_lastmod(file_path: Path) -> Tuple[Optional[str], Optional[bool]]:
    """
    Get last modification date from git log.
    
    Returns:
        tuple: (date_string, is_tracked) - date string and whether file is tracked in git
    """
    try:
        # Get the most recent commit date for this file
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", str(file_path)],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            # Parse git date format: "2025-11-12 10:30:45 +0300"
            git_date = result.stdout.strip().split()[0]  # Get just the date part
            return git_date, True
        else:
            # File not in git
            return None, False
    except subprocess.CalledProcessError:
        # File not tracked in git
        return None, False
    except FileNotFoundError:
        # Git not available
        return None, None


def get_file_lastmod(file_path: Path) -> str:
    """Get last modification date from file system."""
    try:
        if file_path.exists():
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        else:
            return datetime.now().strftime("%Y-%m-%d")
    except OSError:
        return datetime.now().strftime("%Y-%m-%d")


def update_sitemap(use_filesystem: bool = False):
    """Update sitemap.xml with current lastmod dates."""
    sitemap_path = project_root / "seo" / "sitemap.xml"
    
    if not sitemap_path.exists():
        print(f"❌ Error: sitemap.xml not found at {sitemap_path}")
        sys.exit(1)
    
    # Parse existing sitemap
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    
    # Namespace
    ns = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    
    updated_count = 0
    
    # Update each URL entry
    for url_elem in root.findall("sitemap:url", ns):
        loc_elem = url_elem.find("sitemap:loc", ns)
        if loc_elem is None:
            continue
        
        url_path = loc_elem.text.strip()
        # Extract path from full URL
        if "yourdomainname.com" in url_path:
            path = url_path.split("yourdomainname.com")[1] or "/"
        else:
            continue
        
        # Get corresponding template file
        template_file = ROUTE_TO_FILE.get(path)
        if not template_file:
            print(f"⚠️  Warning: No template mapping for {path}, skipping...")
            continue
        
        template_path = project_root / template_file
        
        # Get last modification date
        if use_filesystem:
            lastmod_date = get_file_lastmod(template_path)
            source = "filesystem"
            is_tracked = None
        else:
            lastmod_date, is_tracked = get_git_lastmod(template_path)
            if lastmod_date is None:
                if is_tracked is False:
                    # File not tracked in git - warn and use filesystem
                    print(f"⚠️  Warning: {template_file} not tracked in git, using filesystem date")
                    lastmod_date = get_file_lastmod(template_path)
                    source = "filesystem (not in git)"
                elif is_tracked is None:
                    # Git not available - fallback to filesystem
                    lastmod_date = get_file_lastmod(template_path)
                    source = "filesystem (git unavailable)"
                else:
                    lastmod_date = get_file_lastmod(template_path)
                    source = "filesystem"
            else:
                source = "git"
        
        # Update lastmod element
        lastmod_elem = url_elem.find("sitemap:lastmod", ns)
        if lastmod_elem is not None:
            old_date = lastmod_elem.text
            lastmod_elem.text = lastmod_date
            if old_date != lastmod_date:
                print(f"✅ Updated {path}: {old_date} → {lastmod_date} ({source})")
                updated_count += 1
            else:
                print(f"ℹ️  {path}: already up to date ({lastmod_date})")
        else:
            # Create lastmod element if it doesn't exist (with namespace)
            lastmod_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            lastmod_elem.text = lastmod_date
            print(f"✅ Added lastmod for {path}: {lastmod_date} ({source})")
            updated_count += 1
        
        # Ensure priority and changefreq are set correctly
        priority_elem = url_elem.find("sitemap:priority", ns)
        if priority_elem is None and path in PRIORITY_MAP:
            # Create priority element if it doesn't exist
            priority_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
            priority_elem.text = str(PRIORITY_MAP[path])
            updated_count += 1
        elif priority_elem is not None and path in PRIORITY_MAP:
            priority_elem.text = str(PRIORITY_MAP[path])
        
        changefreq_elem = url_elem.find("sitemap:changefreq", ns)
        if changefreq_elem is None and path in CHANGEFREQ_MAP:
            # Create changefreq element if it doesn't exist
            changefreq_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
            changefreq_elem.text = CHANGEFREQ_MAP[path]
            updated_count += 1
        elif changefreq_elem is not None and path in CHANGEFREQ_MAP:
            changefreq_elem.text = CHANGEFREQ_MAP[path]
    
    # Write updated sitemap to temporary file first (atomic write)
    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        delete=False,
        suffix='.xml',
        dir=sitemap_path.parent
    ) as tmpfile:
        tmp_path = Path(tmpfile.name)
        
        # Write XML with proper escaping
        tmpfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        tmpfile.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        
        for url_elem in root.findall("sitemap:url", ns):
            loc_elem = url_elem.find("sitemap:loc", ns)
            lastmod_elem = url_elem.find("sitemap:lastmod", ns)
            changefreq_elem = url_elem.find("sitemap:changefreq", ns)
            priority_elem = url_elem.find("sitemap:priority", ns)
            
            if loc_elem is None:
                continue
            
            # XML escape all text content (though ElementTree should handle this, we're being explicit)
            loc_text = saxutils.escape(loc_elem.text) if loc_elem.text else ""
            lastmod_text = saxutils.escape(lastmod_elem.text) if lastmod_elem is not None and lastmod_elem.text else None
            changefreq_text = saxutils.escape(changefreq_elem.text) if changefreq_elem is not None and changefreq_elem.text else None
            priority_text = saxutils.escape(priority_elem.text) if priority_elem is not None and priority_elem.text else None
            
            tmpfile.write('    <url>\n')
            tmpfile.write(f'        <loc>{loc_text}</loc>\n')
            if lastmod_text:
                tmpfile.write(f'        <lastmod>{lastmod_text}</lastmod>\n')
            if changefreq_text:
                tmpfile.write(f'        <changefreq>{changefreq_text}</changefreq>\n')
            if priority_text:
                tmpfile.write(f'        <priority>{priority_text}</priority>\n')
            tmpfile.write('    </url>\n')
        
        tmpfile.write('</urlset>\n')
    
    # Atomically replace the original file
    try:
        shutil.move(str(tmp_path), str(sitemap_path))
        print(f"\n✅ Sitemap updated successfully! ({updated_count} entries modified)")
        print(f"📄 Location: {sitemap_path}")
    except Exception as e:
        # Clean up temp file on error
        if tmp_path.exists():
            tmp_path.unlink()
        raise Exception(f"Failed to replace sitemap.xml: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Update sitemap.xml with last modification dates from git or file system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 update_sitemap.py
  python3 update_sitemap.py --use-filesystem
  python3 update_sitemap.py --version

This script automatically updates lastmod dates in sitemap.xml based on:
  - Git commit history (default, most accurate)
  - File system modification dates (fallback or with --use-filesystem flag)
        """
    )
    parser.add_argument(
        "--use-filesystem",
        action="store_true",
        help="Use file system modification dates instead of git"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="update_sitemap.py 1.0.0"
    )
    
    args = parser.parse_args()
    
    print("🔄 Updating sitemap.xml...")
    print(f"📁 Project root: {project_root}")
    print(f"🔍 Method: {'filesystem' if args.use_filesystem else 'git (with filesystem fallback)'}\n")
    
    try:
        update_sitemap(use_filesystem=args.use_filesystem)
    except Exception as e:
        print(f"❌ Error updating sitemap: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

