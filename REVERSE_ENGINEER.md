# Reverse Engineering Ad Designs into the Keetrax Library

When your team spots a cool ad design, you can add it to the library so every future client brief can use it.

---

## Workflow

### 1. Show Claude the image

Drag the screenshot or image directly into the Claude Code conversation and say:

> "Reverse engineer this into the Keetrax library"

Claude will analyse the design and produce a structured prompt entry ready to paste into `library.json`.

---

### 2. What Claude will extract

Claude examines the image across these dimensions and fills the schema below:

| Dimension | What to look for |
|---|---|
| **Layout** | `centered`, `split`, `grid`, `full-bleed`, `banner` |
| **Background** | Colour, gradient, texture, dark/light |
| **Typography** | Number of text blocks, size hierarchy, weight, colour |
| **Product placement** | Centre, corner, floating, in-hand, flat-lay |
| **Visual elements** | Hands, lifestyle scene, icons/badges, ingredients, comparison panels |
| **Mood** | `premium`, `clean`, `energetic`, `natural`, `dramatic`, `warm`, `trustworthy` |
| **Text density** | `low` (1–2 lines), `medium` (3–5), `high` (6+) |

---

### 3. The prompt Claude writes

The generated prompt follows this structure:

```
Create a [FORMAT] ad creative.

LAYOUT:
[Describe the overall composition — columns, whitespace, proportions]

BACKGROUND:
[Exact colour hex or description, texture if any]

PRODUCT:
[Where it sits, how it's presented — angle, shadow, glow, hands etc.]

TEXT BLOCKS:
- Headline: [INSERT HEADLINE] — [font style, size, colour]
- Sub-headline: [INSERT SUBHEADLINE] — [style]
- Supporting copy: [INSERT COPY] — [placement]
- CTA button: [INSERT CTA] — [colour, shape]
- Brand name: [INSERT BRAND NAME] — [placement]
[Add or remove blocks to match the original]

BRAND ELEMENTS:
[Logo placement, badge/seal positions, accent shapes]

COLOUR PALETTE:
- Background: [HEX or description]
- Primary text: [HEX]
- Accent: [HEX]

STYLE NOTES:
[Any specific lighting, grain, shadow style, photographic vs illustrated elements]

Output: single square 1:1 image, 2000×2000px, photorealistic studio quality.
```

---

### 4. The library.json entry Claude adds

> ⚠️ **`"prompt"` is required.** Without it, the entry appears in the HTML app and `select` results but cannot be used with `peelgen.py prompt`, `generate`, or `info` — the script will error and point you back here.

```json
{
  "id": "keetrax-YYYYMMDD-NNNNN",
  "source": "keetrax",
  "name": "Short Human-Readable Name",
  "description": "One sentence describing what makes this design distinctive.",
  "prompt": "...full prompt text (required — see section 3 for structure)...",
  "category": "product-photo",
  "product_types": ["health-beauty", "home-electronics"],
  "tags": ["dark-bg", "split-layout", "bold-type", "hands"],
  "mood": ["premium", "dramatic"],
  "use_cases": ["product-launch", "conversion"],
  "layout": "split",
  "text_density": "medium",
  "preview_images": ["https://...optional reference image URL..."],
  "reverse_engineered_from": "Brief description of the source (e.g. 'Apple product page hero, May 2026')",
  "added_at": "YYYY-MM-DD"
}
```

Append this entry to the `"templates"` array in `keetrax_library/library.json`.

---

### 5. ID convention for Keetrax templates

Format: `keetrax-YYYYMMDD-NNNNN` where NNNNN is a zero-padded sequential number within that day.

Examples:
- `keetrax-20260514-00001`
- `keetrax-20260514-00002`

---

### 6. Allowed category and tag values

**Categories** (match existing nanobanana categories):
- `product-photo` — clean product shot, no heavy copy
- `infographic` — multiple text blocks, benefit lists, icons
- `lifestyle` — product in context, people or scenes
- `ingredients` — callout of components or materials
- `social-proof` — testimonials, ratings, reviews
- `how-to-process` — step-by-step instructions
- `comparisons` — side-by-side or before/after

**Product types:**
- `health-beauty`, `pets`, `home-electronics`

**Tag vocabulary** (extend this list as needed):
`dark-bg`, `white-bg`, `gradient-bg`, `pastel-bg`, `split-layout`, `centered`, `grid`, `full-bleed`, `banner`, `hands`, `lifestyle`, `flat-lay`, `floating-product`, `bold-type`, `minimal-text`, `benefit-list`, `headline`, `social-proof`, `comparison`, `ingredients`, `badges`, `how-to`, `logo-featured`, `sale`, `luxury`, `playful`, `minimal`, `natural`, `clinical`, `warm`

---

### 7. Download reference images locally

After adding the library.json entry, download the source images into a versioned subfolder so previews work without a network connection.

**Folder structure:**
```
keetrax_library/
└── previews/
    └── [entry-id]/
        ├── ref_01_[label].jpg
        ├── ref_02_[label].jpg
        └── ref_03_[label].jpg
```

**For Instagram sources**, extract the `og:image` URL from the page HTML, then download:
```bash
# 1. Extract og:image URLs
curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://www.instagram.com/p/SHORTCODE/" \
  | grep -o 'og:image" content="[^"]*"'

# 2. Create folder and download (repeat for each image, label by brand/source)
ID="keetrax-YYYYMMDD-NNNNN"
mkdir -p keetrax_library/previews/$ID
curl -s -o "keetrax_library/previews/$ID/ref_01_[label].jpg" -A "Mozilla/5.0" "CDN_URL_HERE"
```

**For other sources** (web pages, uploaded screenshots), save the image directly into the folder with the same naming convention.

Once downloaded, update `preview_images` in `library.json` to use local relative paths:
```json
"preview_images": [
  "previews/keetrax-20260514-00001/ref_01_comfycup.jpg",
  "previews/keetrax-20260514-00001/ref_02_edgars.jpg"
]
```

> Note: Instagram CDN URLs are signed and expire within hours — always save to local paths, never store the raw CDN URL.

---

### 8. Verify it's searchable

After adding, test that the template surfaces correctly:

```bash
python3 peelgen.py select --query "your design description" --n 5
```

It should appear near the top. If it doesn't, add more specific tags.

---

### 9. Selecting from the library when given a brief

When you receive a client brief, run `select` before picking a template:

```bash
# General query
python3 peelgen.py select --query "premium skincare dark background minimal"

# Structured filters
python3 peelgen.py select \
  --type health-beauty \
  --mood premium \
  --use-case conversion \
  --n 6

# Combined
python3 peelgen.py select \
  --query "split layout bold headline" \
  --category infographic \
  --type home-electronics \
  --n 5
```

Review the top results, inspect with `peelgen.py info <id>`, then proceed with `peelgen.py prompt`.
