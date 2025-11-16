I wanted to share my new idea Automated Sitemap.xml Last Modification Date Updater
beacuse i love own simple tools and powerful of lovable by me Python


Benefits of the script:
 - static files are served faster (NGINX can cache them)
 - less load on the database (updates daily/weekly, not with every request)
 - also you can run via cron automatically if need to
 - easier debugging and logging

What do you think?

# update_sitemap.py

**Automated Sitemap.xml Last Modification Date Updater**

A production-ready Python script that automatically updates `lastmod` dates in `sitemap.xml` based on Git commit history or file system modification dates. Perfect for maintaining accurate SEO metadata without manual intervention.

## ✨ Features

- 🔄 **Automatic Date Detection**: Uses Git commit history (most accurate) or file system modification dates
- 🛡️ **Atomic Writing**: Safe file updates using temporary files to prevent corruption
- 🔍 **Smart Fallback**: Automatically falls back to filesystem if Git is unavailable
- ⚠️ **Warning System**: Alerts when files aren't tracked in Git
- 🔒 **XML Safety**: Proper XML escaping for all content
- 📊 **Detailed Logging**: Clear output showing what was updated and why
- 🎯 **Configurable**: Easy to customize routes, priorities, and change frequencies

## 📋 Requirements

- Python 3.7+
- Git (optional, for commit-based dates)
- Standard library only (no external dependencies)

## 🚀 Quick Start

### Basic Usage

```bash
# Update sitemap using Git commit dates (recommended)
python3 update_sitemap.py

# Use file system modification dates instead
python3 update_sitemap.py --use-filesystem

# Show version
python3 update_sitemap.py --version
```

### Integration with CI/CD

Add to your GitHub Actions workflow:

```yaml
- name: Update sitemap.xml
  run: python3 update_sitemap.py || echo "⚠️  Warning: sitemap update failed, continuing..."
```

## 📖 How It Works

1. **Reads existing sitemap.xml** from `seo/sitemap.xml`
2. **Maps routes to template files** (configurable in `ROUTE_TO_FILE`)
3. **Gets last modification date** from:
   - Git commit history (default, most accurate)
   - File system modification time (fallback)
4. **Updates XML elements**:
   - `lastmod` - Last modification date
   - `changefreq` - Change frequency (from `CHANGEFREQ_MAP`)
   - `priority` - Page priority (from `PRIORITY_MAP`)
5. **Writes atomically** to prevent file corruption

## ⚙️ Configuration

### Route Mapping

Edit `ROUTE_TO_FILE` dictionary to map URLs to template files:

```python
ROUTE_TO_FILE = {
    "/": "templates/self.html",
    "/blog": "templates/blog.html",
    "/about": "templates/about.html",
    # Add your routes here
}
```

### Priority Settings

Customize page priorities in `PRIORITY_MAP`:

```python
PRIORITY_MAP = {
    "/": 1.0,        # Highest priority
    "/blog": 0.8,
    "/about": 0.7,
    "/privacy": 0.3, # Lowest priority
}
```

### Change Frequency

Set update frequency in `CHANGEFREQ_MAP`:

```python
CHANGEFREQ_MAP = {
    "/": "weekly",
    "/blog": "daily",
    "/about": "monthly",
    "/privacy": "yearly",
}
```

Valid values: `always`, `hourly`, `daily`, `weekly`, `monthly`, `yearly`, `never`

## 📝 Example Output

```
🔄 Updating sitemap.xml...
📁 Project root: /path/to/project
🔍 Method: git (with filesystem fallback)

✅ Updated /: 2025-01-09 → 2025-11-12 (git)
✅ Updated /blog: 2025-01-09 → 2025-11-11 (git)
⚠️  Warning: templates/new-page.html not tracked in git, using filesystem date
ℹ️  /about: already up to date (2025-11-12)

✅ Sitemap updated successfully! (2 entries modified)
📄 Location: /path/to/project/seo/sitemap.xml
```

## 🔧 Advanced Usage

### Custom Project Structure

If your project structure differs, modify the `project_root` detection:

```python
# Default: assumes script is in tools/ directory
project_root = Path(__file__).parent.parent

# Custom: specify absolute path
project_root = Path("/path/to/your/project")
```

### Adding Dynamic Routes

For blog posts or dynamic content, extend the script:

```python
# Example: Auto-discover blog posts
blog_dir = project_root / "templates/blog"
for blog_file in blog_dir.glob("*.html"):
    route = "/blog/" + blog_file.stem
    ROUTE_TO_FILE[route] = str(blog_file.relative_to(project_root))
    PRIORITY_MAP[route] = 0.7
    CHANGEFREQ_MAP[route] = "monthly"
```

## 🛡️ Safety Features

### Atomic Writing

The script uses temporary files to ensure safe updates:

1. Writes to temporary file first
2. Validates content
3. Atomically replaces original file
4. Cleans up on errors

### XML Escaping

All text content is properly escaped using `xml.sax.saxutils.escape()` to prevent XML injection.

### Error Handling

- Graceful fallback if Git is unavailable
- Warnings for untracked files
- Detailed error messages with stack traces
- Automatic cleanup of temporary files

## 📊 Best Practices

1. **Use Git dates by default** - More accurate than filesystem dates
2. **Run before deployment** - Include in CI/CD pipeline
3. **Review warnings** - Check files not tracked in Git
4. **Customize priorities** - Match your site structure
5. **Test locally first** - Verify output before deploying

## 🐛 Troubleshooting

### "File not tracked in git" warnings

**Solution**: Add files to Git or use `--use-filesystem` flag

```bash
git add templates/new-page.html
python3 update_sitemap.py
```

### "Git not available" errors

**Solution**: Use filesystem dates instead

```bash
python3 update_sitemap.py --use-filesystem
```

### Sitemap.xml not found

**Solution**: Ensure `seo/sitemap.xml` exists or modify path in script

## 📄 License

This script is part of the eliteself.tech project. Feel free to use, modify, and distribute according to your project's license.

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Dynamic route discovery
- Support for image/video sitemaps
- Database-driven content detection
- Multi-language sitemap support
- Performance optimizations

## 📚 Related Tools

- `cache_buster.py` - Cache busting for static assets

## 🔗 Resources

- [Sitemap Protocol](https://www.sitemaps.org/protocol.html)
- [Google Sitemap Guidelines](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- [Yandex Sitemap Documentation](https://yandex.com/support/webmaster/sitemap/what-is-sitemap.html)

---

☯️ powered by AI co-creation team<br>
🛠️ built with 🤍 by eliteself.tech / technologies of your success ✨

