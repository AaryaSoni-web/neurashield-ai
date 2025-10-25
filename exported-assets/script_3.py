
import zipfile
import os

# Create a ZIP file containing all three files
zip_filename = 'neurashield-ai-website.zip'

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('home.html')
    zipf.write('home.css')
    zipf.write('home.js')

# Get file sizes
html_size = os.path.getsize('home.html')
css_size = os.path.getsize('home.css')
js_size = os.path.getsize('home.js')
zip_size = os.path.getsize(zip_filename)

print("="*60)
print("📦 ZIP FILE CREATED SUCCESSFULLY!")
print("="*60)
print(f"\n✅ Package: {zip_filename}")
print(f"   Total size: {zip_size:,} bytes ({zip_size/1024:.1f} KB)\n")
print("📄 Files included:")
print(f"   • home.html  - {html_size:,} bytes ({html_size/1024:.1f} KB)")
print(f"   • home.css   - {css_size:,} bytes ({css_size/1024:.1f} KB)")
print(f"   • home.js    - {js_size:,} bytes ({js_size/1024:.1f} KB)")
print("\n" + "="*60)
print("🎉 READY TO USE!")
print("="*60)
print("\n📥 Download the ZIP file and extract it")
print("🌐 Open home.html in any modern browser")
print("✨ Enjoy your professional NeuraShield.AI dashboard!\n")
