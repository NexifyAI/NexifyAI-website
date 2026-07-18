#!/usr/bin/env python3
"""Nexify AI website cleanup and fix script.

Handles:
1. Footer cleanup across all pages (remove Sign In/Sign Up, remove social icons)
2. About page - remove Company Info section
3. Contact page - remove left form, single-column layout
4. Pilot Apply FAQ - fix SVG sizing, add inline width/height
5. Syntax validation with node --check
6. i18n key consistency check (EN/NL/FR)
"""

import os
import re
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path('/app/data/所有对话/主对话/nexifyai-chatbot')

PAGES = [
    'index.html', 'about.html', 'contact.html', 'privacy.html', 'terms.html',
    'pilot-apply.html', 'solutions-restaurants.html', 'solutions-general-practice.html',
    'solutions-law-firms.html', 'solutions-real-estate.html', 'demo.html',
    'pricing-subscription.html', 'pricing-payg.html', 'pricing-custom.html',
    'login.html', 'pilot-results.html', 'demo-phone.html', '404.html'
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def remove_line_containing(text, pattern):
    """Remove entire lines that match the given regex pattern."""
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if not re.search(pattern, line):
            new_lines.append(line)
    return '\n'.join(new_lines)

def remove_copy_key(text, key):
    """Remove a key from the copy object, handling all quote styles.
    
    Handles escaped quotes within values (e.g. 'S\'inscrire').
    """
    # Single-quoted string pattern (handles escaped quotes): '(?:[^'\\]|\\.)*'
    sq_str = r"'(?:[^'\\]|\\.)*'"
    # Double-quoted string pattern (handles escaped quotes): "(?:[^"\\]|\\.)*"
    dq_str = r'"(?:[^"\\]|\\.)*"'
    
    # Pattern 1: Unquoted key, single-quoted value:  keyName:'value',  or  keyName: 'value',
    pattern = r"[ \t]*" + re.escape(key) + r"[ \t]*:[ \t]*" + sq_str + r"[ \t]*,?[ \t]*\n"
    text = re.sub(pattern, '', text)
    
    # Pattern 2: Double-quoted key, double-quoted value:  "keyName": "value",
    pattern = r'[ \t]*"' + re.escape(key) + r'"[ \t]*:[ \t]*' + dq_str + r'[ \t]*,?[ \t]*\n'
    text = re.sub(pattern, '', text)
    
    # Pattern 3: Unquoted key, double-quoted value
    pattern = r'[ \t]*' + re.escape(key) + r'[ \t]*:[ \t]*' + dq_str + r'[ \t]*,?[ \t]*\n'
    text = re.sub(pattern, '', text)
    
    # Pattern 4: Double-quoted key, single-quoted value
    pattern = r'[ \t]*"' + re.escape(key) + r'"[ \t]*:[ \t]*' + sq_str + r'[ \t]*,?[ \t]*\n'
    text = re.sub(pattern, '', text)
    
    return text

def remove_css_rule(text, selector):
    """Remove a CSS rule block for the given selector.
    
    Handles simple single-line rules and multi-line rules.
    Assumes the selector starts a CSS rule and the rule ends at }.
    """
    # Pattern matches the selector line and everything up to and including the closing }
    # selector{...} on one or more lines
    pattern = r'[ \t]*' + re.escape(selector) + r'\{[^}]*\}[ \t]*\n?'
    text = re.sub(pattern, '', text)
    return text

def remove_html_element(text, tag_with_class, multiline=True):
    """Remove an HTML element by tag and class, including its contents.
    
    Uses a regex that matches from the opening tag to its matching closing tag.
    Only works for elements that don't contain nested same-tag elements.
    """
    if not multiline:
        return text
    
    # For div with specific class: <div class="foo"> to </div>
    # This is tricky with regex because of nesting. We use a simpler approach:
    # find the opening line, find the matching closing </div> by counting.
    
    lines = text.split('\n')
    result = []
    skip_depth = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if skip_depth > 0:
            # Count opening and closing divs
            opens = len(re.findall(r'<div[\s>]', line, re.IGNORECASE))
            closes = len(re.findall(r'</div>', line, re.IGNORECASE))
            skip_depth += opens - closes
            if skip_depth <= 0:
                # Don't add this line (it's the closing tag), but stop skipping
                skip_depth = 0
            i += 1
            continue
        
        if re.search(tag_with_class, line):
            # Start skipping
            opens = len(re.findall(r'<div[\s>]', line, re.IGNORECASE))
            closes = len(re.findall(r'</div>', line, re.IGNORECASE))
            net_opens = opens - closes
            if net_opens > 0:
                skip_depth = net_opens
            else:
                # Self-contained line, just skip it
                pass
            i += 1
            continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)

def remove_section_by_comment(text, start_comment):
    """Remove an HTML section that starts with a specific comment.
    
    Removes from the comment line through the matching </section>.
    """
    lines = text.split('\n')
    result = []
    skipping = False
    depth = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if not skipping and start_comment in line:
            skipping = True
            depth = 0
        
        if skipping:
            # Count section tags
            opens = len(re.findall(r'<section[\s>]', line, re.IGNORECASE))
            closes = len(re.findall(r'</section>', line, re.IGNORECASE))
            depth += opens - closes
            if depth <= 0 and closes > 0:
                skipping = False
            i += 1
            continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)

# ---------------------------------------------------------------------------
# 1. Footer cleanup
# ---------------------------------------------------------------------------

def fix_footer(page_path):
    """Clean up footer: remove Sign In/Sign Up links, remove social icons div."""
    content = read_file(page_path)
    original = content
    
    # 1a. Remove Sign In li
    content = re.sub(r'[ \t]*<li><a[^>]*data-i18n="footerSignin"[^>]*>.*?</a></li>[ \t]*\n?', 
                     '', content)
    
    # 1b. Remove Sign Up li
    content = re.sub(r'[ \t]*<li><a[^>]*data-i18n="footerSignup"[^>]*>.*?</a></li>[ \t]*\n?', 
                     '', content)
    
    # 1c. Remove footer-social div (and its contents)
    # Find the div with class "footer-social" and remove it entirely
    lines = content.split('\n')
    new_lines = []
    skip_depth = 0
    for line in lines:
        if skip_depth > 0:
            opens = len(re.findall(r'<div[\s>]', line, re.IGNORECASE))
            closes = len(re.findall(r'</div>', line, re.IGNORECASE))
            skip_depth += opens - closes
            if skip_depth <= 0:
                skip_depth = 0
            continue
        
        if re.search(r'class="footer-social"', line):
            opens = len(re.findall(r'<div[\s>]', line, re.IGNORECASE))
            closes = len(re.findall(r'</div>', line, re.IGNORECASE))
            net = opens - closes
            if net > 0:
                skip_depth = net
            # else: self-contained, just skip line
            continue
        
        new_lines.append(line)
    content = '\n'.join(new_lines)
    
    # 1d. Remove footer-social CSS rules
    css_selectors = [
        '.footer-social',
        '.footer-social a',
        '.footer-social a:hover',
        '.footer-social svg',
    ]
    for sel in css_selectors:
        content = remove_css_rule(content, sel)
    
    # 1e. Remove footerSignin and footerSignup from copy objects
    content = remove_copy_key(content, 'footerSignin')
    content = remove_copy_key(content, 'footerSignup')
    
    if content != original:
        write_file(page_path, content)
        return True
    return False

# ---------------------------------------------------------------------------
# 2. About page - remove Company Info section
# ---------------------------------------------------------------------------

def fix_about_page(page_path):
    """Remove Company Details section from about page."""
    content = read_file(page_path)
    original = content
    
    # 2a. Remove the entire Company Details section (by comment)
    content = remove_section_by_comment(content, 'Company Details')
    
    # 2b. Remove Company Details CSS section
    lines = content.split('\n')
    company_section_start = None
    next_section_start = None
    for i, line in enumerate(lines):
        if '/* ---------- Company Details ---------- */' in line:
            company_section_start = i
        elif company_section_start is not None and re.match(r'\s*/\* ----------', line):
            next_section_start = i
            break
    
    if company_section_start is not None and next_section_start is not None:
        lines = lines[:company_section_start] + lines[next_section_start:]
        content = '\n'.join(lines)
    
    # Also remove responsive .company-details rule
    content = re.sub(r'[ \t]*\.company-details\{[^}]*\}[ \t]*\n?', '', content)
    
    # 2c. Remove copy keys
    keys_to_remove = [
        'aboutCompanyTitle', 'aboutCompanySub',
        'companyNameLabel', 'companyAddressLabel',
        'companyKvkLabel', 'companyEmailLabel',
    ]
    for key in keys_to_remove:
        content = remove_copy_key(content, key)
    
    if content != original:
        write_file(page_path, content)
        return True
    return False

# ---------------------------------------------------------------------------
# 3. Contact page - remove left form
# ---------------------------------------------------------------------------

def fix_contact_page(page_path):
    """Remove left-side contact form, adjust layout to single column."""
    content = read_file(page_path)
    original = content
    
    # 3a. Remove the entire contact-form-wrap div
    # Strategy: find "<!-- Form -->" and "<!-- Info -->" comments, remove everything
    # from the Form comment up to (but not including) the Info comment.
    form_start = None
    info_start = None
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '<!-- Form -->' in line and form_start is None:
            form_start = i
        if '<!-- Info -->' in line and form_start is not None and info_start is None:
            info_start = i
            break
    
    if form_start is not None and info_start is not None:
        # Remove lines from form_start to info_start - 1 (inclusive)
        # But we also need to make sure we don't leave blank lines
        # Actually, let's find the last line of the form-wrap (the closing </div>)
        # The </div> before <!-- Info --> is the closing of contact-form-wrap
        new_lines = lines[:form_start] + lines[info_start:]
        content = '\n'.join(new_lines)
    else:
        # Fallback: try to find and remove the contact-form-wrap div
        print(f"  Warning: could not find Form/Info comments, using fallback removal")
        lines = content.split('\n')
        new_lines = []
        skipping = False
        depth = 0
        for line in lines:
            if not skipping and re.search(r'class="contact-form-wrap"', line):
                skipping = True
                opens = len(re.findall(r'<div[\s>]|<form[\s>]|<select[\s>]|<textarea[\s>]', line, re.IGNORECASE))
                closes = len(re.findall(r'</div>|</form>|</select>|</textarea>', line, re.IGNORECASE))
                depth = opens - closes
                if depth <= 0:
                    skipping = False
                continue
            
            if skipping:
                opens = len(re.findall(r'<div[\s>]|<form[\s>]|<select[\s>]|<textarea[\s>]', line, re.IGNORECASE))
                closes = len(re.findall(r'</div>|</form>|</select>|</textarea>', line, re.IGNORECASE))
                depth += opens - closes
                if depth <= 0:
                    skipping = False
                continue
            
            new_lines.append(line)
        content = '\n'.join(new_lines)
    
    # 3b. Change contact-layout grid from 1fr 1fr to single column
    # Main CSS - use \g<1> to avoid \11 being interpreted as group 11
    content = re.sub(
        r'(\.contact-layout\{[^{]*grid-template-columns:)1fr 1fr(;[^}]*\})',
        r'\g<1>1fr\g<2>',
        content
    )
    
    # Add max-width and margin:0 auto to center the info
    content = re.sub(
        r'(\.contact-layout\{[^}]*display:grid;)([^}]*\})',
        r'\g<1>max-width:600px;margin:0 auto;\g<2>',
        content
    )
    
    # 3c. Remove form-related CSS
    # Strategy: remove the entire "Contact Form" CSS section by finding its
    # comment marker and the next section's comment marker.
    lines = content.split('\n')
    form_section_start = None
    next_section_start = None
    for i, line in enumerate(lines):
        if '/* ---------- Contact Form ---------- */' in line:
            form_section_start = i
        elif form_section_start is not None and re.match(r'\s*/\* ----------', line):
            next_section_start = i
            break
    
    if form_section_start is not None and next_section_start is not None:
        # Remove lines from form_section_start to next_section_start - 1
        lines = lines[:form_section_start] + lines[next_section_start:]
        content = '\n'.join(lines)
    
    # Also remove responsive .form-row rule
    content = re.sub(r'[ \t]*\.form-row\{[^}]*\}[ \t]*\n?', '', content)
    
    # 3d. Remove contact form JS
    # Find the contactForm handler block
    lines = content.split('\n')
    new_lines = []
    skip_block = False
    brace_depth = 0
    found_contact_form = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if not skip_block and "const contactForm = document.getElementById('contact-form-el')" in line:
            skip_block = True
            brace_depth = 0
            found_contact_form = True
            i += 1
            continue
        
        if not skip_block and 'const contactForm = document.getElementById("contact-form-el")' in line:
            skip_block = True
            brace_depth = 0
            found_contact_form = True
            i += 1
            continue
        
        if skip_block:
            # Track braces to find end of the block
            brace_depth += line.count('{') - line.count('}')
            # The contactForm block structure:
            # const contactForm = ...;
            # if(contactForm){
            #   contactForm.addEventListener('submit', (e)=>{
            #     ...
            #   });
            # }
            # We need to skip until the closing } of the if(contactForm) block
            # Actually, let's just skip line by line until we see a line that looks
            # like the end of the contact form code (comment or next block)
            
            # Simple heuristic: skip until we find a line that's clearly not part
            # of the contact form handler, like "/* ===== Chatbot Widget ===== */"
            if 'Chatbot Widget' in line or '/* =====' in line:
                skip_block = False
                # Don't skip this line - it's the next section start
                new_lines.append(line)
                i += 1
                continue
            
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    content = '\n'.join(new_lines)
    
    # 3e. Remove copy keys for the form
    form_keys = [
        'contactFormTitle',
        'formName', 'formNamePlaceholder',
        'formEmail', 'formEmailPlaceholder',
        'formCompany', 'formCompanyPlaceholder',
        'formIndustry',
        'industrySelect', 'industryRestaurant', 'industryMedical',
        'industryLegal', 'industryRealEstate', 'industryRetail', 'industryOther',
        'formMessage', 'formMessagePlaceholder',
        'formSubmit',
    ]
    for key in form_keys:
        content = remove_copy_key(content, key)
    
    if content != original:
        write_file(page_path, content)
        return True
    return False

# ---------------------------------------------------------------------------
# 4. Pilot Apply FAQ - fix SVG sizing
# ---------------------------------------------------------------------------

def fix_pilot_faq(page_path):
    """Fix FAQ SVG sizing issue - add inline width/height to chevron SVGs."""
    content = read_file(page_path)
    original = content
    
    # Add width="20" height="20" to all .faq-question svg elements
    # Pattern: <svg viewBox="0 0 24 24" fill="none" ...><polyline points="6 9 12 15 18 9"></polyline></svg>
    # These are the chevron SVGs inside faq-question buttons
    
    # Strategy: find SVGs inside faq-question buttons that have the chevron polyline
    # More specifically: find <svg ...viewBox="0 0 24 24"...> that are followed by polyline points="6 9 12 15 18 9"
    # and add width="20" height="20" if not present
    
    # Simpler approach: in faq-question context, find svg that lacks width/height and add them
    # We look for svgs with the chevron polyline pattern
    
    # Match: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
    # And variants with just viewBox
    pattern = r'(<svg )(viewBox="0 0 24 24"[^>]*>)(<polyline points="6 9 12 15 18 9")'
    
    def add_svg_dimensions(match):
        prefix = match.group(1)
        attrs = match.group(2)
        rest = match.group(3)
        
        # Check if width or height already present
        if 'width=' in attrs and 'height=' in attrs:
            return match.group(0)
        
        # Add width="20" height="20" after the opening svg tag
        # Insert before viewBox
        new_attrs = 'width="20" height="20" ' + attrs
        return prefix + new_attrs + rest
    
    content = re.sub(pattern, add_svg_dimensions, content)
    
    # Also check: are there faq-answer ::before or ::after pseudo-elements?
    # If yes, remove them
    faq_answer_before = re.search(r'\.faq-answer::?before\s*\{', content)
    faq_answer_after = re.search(r'\.faq-answer::?after\s*\{', content)
    if faq_answer_before:
        content = remove_css_rule(content, '.faq-answer::before')
        content = remove_css_rule(content, '.faq-answer:before')
    if faq_answer_after:
        content = remove_css_rule(content, '.faq-answer::after')
        content = remove_css_rule(content, '.faq-answer:after')
    
    if content != original:
        write_file(page_path, content)
        return True
    return False

# ---------------------------------------------------------------------------
# 5. Syntax validation
# ---------------------------------------------------------------------------

def validate_syntax(page_path):
    """Run node --check on the script extracted from the HTML page.
    
    Since we can't easily run node on just the script, we extract all script
    content and write to a temp file, then run node --check.
    """
    content = read_file(page_path)
    
    # Extract content between <script> and </script> tags (non-inline scripts)
    # Also need to handle the fact that these are template literals with backticks etc.
    # Actually, node --check on the full file won't work since it's HTML.
    # Let's extract all <script>...</script> blocks and check them individually.
    
    script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    
    errors = []
    for i, script in enumerate(script_blocks):
        if not script.strip():
            continue
        tmp_path = f'/tmp/script_check_{Path(page_path).name}_{i}.js'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(script)
        try:
            result = subprocess.run(
                ['node', '--check', tmp_path],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                errors.append(f"Script block {i}: {result.stderr.strip()}")
        except Exception as e:
            errors.append(f"Script block {i}: validation error - {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    return errors

# ---------------------------------------------------------------------------
# 6. i18n consistency check
# ---------------------------------------------------------------------------

def check_i18n_consistency(page_path):
    """Check that all i18n keys in the HTML have EN/NL/FR translations.
    
    Returns list of issues.
    """
    content = read_file(page_path)
    
    # Find all data-i18n and data-i18n-placeholder keys in the HTML
    html_keys = set()
    
    # data-i18n="key"
    for match in re.finditer(r'data-i18n="([^"]+)"', content):
        html_keys.add(match.group(1))
    
    # data-i18n-placeholder="key"
    for match in re.finditer(r'data-i18n-placeholder="([^"]+)"', content):
        html_keys.add(match.group(1))
    
    if not html_keys:
        return []  # No i18n on this page (like 404.html maybe)
    
    # Extract copy objects for each language
    # This is tricky with regex. Let's use a simpler approach:
    # For each HTML key, check if it appears in all three language sections
    
    issues = []
    
    # Find all keys present in copy object
    # We'll just count occurrences of each key in the file
    # A fully consistent file should have each key appearing in EN, NL, and FR sections
    # But this is an approximation since keys can appear in other contexts too
    
    for key in sorted(html_keys):
        # Count how many times the key appears as a copy object key
        # Single-quoted: keyName:'
        single_count = len(re.findall(r"[\n\s,]" + re.escape(key) + r"\s*:\s*'", content))
        # Double-quoted: "keyName":
        double_count = len(re.findall(r'"' + re.escape(key) + r'"\s*:\s*"', content))
        
        total = single_count + double_count
        
        # We expect at least 3 (EN, NL, FR), but some pages might have duplicates
        if total < 3 and total > 0:
            issues.append(f"Key '{key}' appears only {total} times in copy (expected ≥3 for EN/NL/FR)")
    
    return issues

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Nexify AI Website Cleanup & Fix Script")
    print("=" * 60)
    
    # 1. Footer cleanup (all pages)
    print("\n[1/5] Fixing footers across all pages...")
    footer_changed = []
    for page in PAGES:
        page_path = BASE_DIR / page
        if page_path.exists():
            changed = fix_footer(page_path)
            if changed:
                footer_changed.append(page)
                print(f"  ✓ {page}")
    print(f"  Total: {len(footer_changed)} pages modified")
    
    # 2. About page
    print("\n[2/5] Fixing about page...")
    about_path = BASE_DIR / 'about.html'
    if about_path.exists():
        changed = fix_about_page(about_path)
        print(f"  ✓ about.html {'(modified)' if changed else '(no changes)'}")
    
    # 3. Contact page
    print("\n[3/5] Fixing contact page...")
    contact_path = BASE_DIR / 'contact.html'
    if contact_path.exists():
        changed = fix_contact_page(contact_path)
        print(f"  ✓ contact.html {'(modified)' if changed else '(no changes)'}")
    
    # 4. Pilot FAQ
    print("\n[4/5] Fixing pilot FAQ SVG sizing...")
    pilot_path = BASE_DIR / 'pilot-apply.html'
    if pilot_path.exists():
        changed = fix_pilot_faq(pilot_path)
        print(f"  ✓ pilot-apply.html {'(modified)' if changed else '(no changes)'}")
    
    # 5. Syntax validation
    print("\n[5/5] Validating JS syntax with node --check...")
    all_ok = True
    for page in PAGES:
        page_path = BASE_DIR / page
        if page_path.exists():
            errors = validate_syntax(page_path)
            if errors:
                all_ok = False
                print(f"  ✗ {page}:")
                for e in errors:
                    print(f"      - {e}")
            else:
                print(f"  ✓ {page}")
    
    # 6. i18n consistency check
    print("\n[Bonus] Checking i18n key consistency (EN/NL/FR)...")
    i18n_issues_found = False
    for page in PAGES:
        page_path = BASE_DIR / page
        if page_path.exists():
            issues = check_i18n_consistency(page_path)
            if issues:
                i18n_issues_found = True
                print(f"  ⚠ {page}:")
                for issue in issues:
                    print(f"      - {issue}")
    
    if not i18n_issues_found:
        print("  ✓ All pages pass i18n consistency check")
    
    print("\n" + "=" * 60)
    print("Done!")
    print(f"Syntax validation: {'PASSED' if all_ok else 'FAILED'}")
    print("=" * 60)
    
    if not all_ok:
        sys.exit(1)

if __name__ == '__main__':
    main()
