# Reverse Engineering Ad Designs into the Keetrax Library

When your team spots a cool ad design, you can add it to the library so every future client brief can use it.

---

## Workflow

### 1. Show Claude the image

There are two ways to provide reference images:

**Option A — Direct image upload (best quality)**
Drag the screenshot or image directly into the Claude Code conversation and say:

> "Reverse engineer this into the Keetrax library"

**Option B — Instagram URLs**
Paste one or more Instagram post URLs and say the same. Claude will:
1. Extract `og:image` preview thumbnails via `curl` to get an initial read
2. Download the full-resolution originals via `instaloader` (see section 7)
3. Read the full-res files with the Read tool before writing the prompt

> ⚠️ Do not rely on text descriptions from web fetches — they are AI-generated summaries of content, not structural analyses. They miss font weights, exact layout proportions, colour values, and fine details. Always read the actual image file.

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

After adding the library.json entry, download the source images into a versioned subfolder so previews work offline and so Claude can read the actual images when refining the prompt.

**Folder structure:**
```
keetrax_library/
└── previews/
    └── [entry-id]/
        ├── ref_01_[label].jpg
        ├── ref_02_[label].jpg
        └── ref_03_[label].jpg
```

---

#### For Instagram sources — use instaloader (not curl)

The `og:image` curl approach only downloads a **cropped 640×640 thumbnail** — Instagram's CDN URLs have a signed `oh` parameter tied to the `stp` crop/resize transform. Removing `stp` to get the full image breaks the signature (returns 403). Use `instaloader` instead.

**Install:**
```bash
pip3 install instaloader browser-cookie3
```

**First-time download (loads session from Chrome):**
```bash
ID="keetrax-YYYYMMDD-NNNNN"
mkdir -p keetrax_library/previews/$ID
cd keetrax_library/previews/$ID

# Pass post shortcodes prefixed with -
instaloader --load-cookies chrome --no-metadata-json --no-captions --no-compress-json \
  -- -SHORTCODE1 -SHORTCODE2 -SHORTCODE3
```

The shortcode is the path segment from the URL: `https://www.instagram.com/p/DYCUjk-kwD0/` → shortcode is `DYCUjk-kwD0`.

After the first run, instaloader prints: `Next time use --login=USERNAME to reuse the same session.` Use that for subsequent downloads (do not combine `--load-cookies` and `--login`):
```bash
instaloader --login=USERNAME --no-metadata-json --no-captions --no-compress-json \
  -- -SHORTCODE
```

**What instaloader downloads:**
- Creates a subfolder per post named `-SHORTCODE/`
- Files named `YYYY-MM-DD_HH-MM-SS_UTC.jpg` (single posts) or `..._1.jpg`, `..._2.jpg` etc. (carousels)
- For carousels, pick the key frame(s) — usually `_1.jpg`

**Reorganise into clean names then delete subdirs:**
```bash
cp -- "-SHORTCODE1/YYYY-MM-DD_HH-MM-SS_UTC.jpg"   ref_01_[label].jpg
cp -- "-SHORTCODE2/YYYY-MM-DD_HH-MM-SS_UTC_1.jpg" ref_02_[label].jpg
cp -- "-SHORTCODE3/YYYY-MM-DD_HH-MM-SS_UTC.jpg"   ref_03_[label].jpg
rm -rf -- "-SHORTCODE1" "-SHORTCODE2" "-SHORTCODE3"
```

---

#### For other sources

Save screenshots or downloaded images directly into the folder with the same `ref_NN_[label].jpg` naming convention.

---

**Update `preview_images` in `library.json` to local relative paths:**
```json
"preview_images": [
  "previews/keetrax-20260514-00001/ref_01_comfycup.jpg",
  "previews/keetrax-20260514-00001/ref_02_edgars.jpg",
  "previews/keetrax-20260514-00001/ref_03_starbucks.jpg"
]
```

> Never store raw Instagram CDN URLs — they are signed and expire within hours. Always use local paths.

---

### 8. Refine the prompt by reading the actual images

After downloading, use the Read tool to view each image and audit the prompt against what's actually there. Common things that web-fetch text descriptions get wrong:

| What descriptions say | What the image actually shows |
|---|---|
| "label pills / badges" | Plain bold text headers — no background shape at all |
| "emoji-heavy Gen Z copy" | Often just 1 emoji, or a self-referential joke with no emoji |
| "serif font" | Heavy-weight sans-serif (almost always) |
| "off-white background" | Pure white #FFFFFF |
| "product centred in each panel" | Product in upper OR lower half — text fills the other half |
| "identical product size" | Slight size variation is acceptable if copy length differs |

**Check the prompt covers:**
- Exact text hierarchy (which line is larger, which is lighter weight)
- Whether the Gen Z panel has floating emojis around the product — and if so, how many and at what density
- Which element is the brand anchor: logo bar at bottom, OR brand colour applied to all text
- Portrait vs square format — both are valid, note what the references use
- Copy position relative to product (above or below) — consistent across both panels

Correct the prompt in `library.json` before marking the entry complete.

---

### 9. Verify it's searchable

After adding, test that the template surfaces correctly:

```bash
python3 peelgen.py select --query "your design description" --n 5
```

It should appear near the top. If it doesn't, add more specific tags.

---

### 10. Selecting from the library when given a brief

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
