# Newsletter Digest Skill

**name:** newsletter-digest  
**description:** Create a comprehensive, deduplicated daily digest from unread newsletters. Extracts essay content, follows non-sponsor links to referenced articles, and produces a MECE-categorized summary with proper citations. Use when the user wants a daily newsletter roundup or digest of their recent unread emails.

This skill creates a comprehensive daily digest from unread newsletters by extracting content, following reference links, deduplicating information, and producing a well-organized summary document.

---

## Core Workflow

**Important:** Complete each phase fully before moving to the next. Do not synthesize or write the digest until ALL newsletters have been collected, read, and their content extracted.

### Phase 1: Collect Unread Newsletters (Last 24 Hours)

1. Search Gmail for unread messages from the last 24 hours
2. **CRITICAL: Paginate through ALL results** — Gmail returns results in pages with a `nextPageToken`. Continue calling search_gmail_messages with the pageToken until no more results are returned. Do not stop after the first page.
3. Filter for newsletter-type content (exclude transactional emails, calendar invites, security alerts, notifications)
4. Identify newsletter sources by common patterns:
   - From addresses containing: "newsletter", "substack", "beehiiv", "ghost", "no-reply"
   - Subject lines indicating content: "Issue", "Edition", "Digest", "Weekly", "Daily"
   - Known newsletter platforms in headers
5. Exclude non-newsletter messages:
   - Security alerts (e.g., "Security alert" from Google)
   - System notifications (e.g., "Welcome to…" onboarding emails)
   - Live event notifications (e.g., "X is live now")
   - Calendar invites and meeting notifications
   - Transactional receipts and confirmations

### Phase 2: Extract Newsletter Content

For each newsletter identified:

1. **Read the full thread** to get complete context
2. **Extract essay/article content:**
   - Main body text (exclude headers/footers)
   - Author bylines and publication names
   - Headlines and subheadings
3. **Identify content links** (non-sponsor):
   - Links within article body that reference source material
   - Exclude: unsubscribe links, social media profile links, sponsor/advertising links
   - Prioritize: article links, research papers, primary sources, referenced posts
4. **Detect sponsor content** to exclude:
   - Sections marked "Sponsored", "Advertisement", "Partner Content"
   - Links to product pages or promotional landing pages
   - Content after phrases like "This post is brought to you by…"
5. **Store to memory:** Create a structured record with:
   - Newsletter name and sender
   - Message ID (for later marking as read)
   - Thread ID (for reference)
   - Publication date/time
   - Main content text
   - List of content links to investigate
   - Key topics/themes mentioned

### Phase 3: Follow Content Links

For each identified content link:

1. **Fetch the full content** using web_fetch
2. **Extract key information:**
   - Article title and author
   - Publication and date
   - Main arguments and key points
   - Supporting data or evidence
3. **Store to memory** with:
   - Full URL for citation
   - Summary of content
   - Which newsletter(s) referenced it
   - Key themes and topics
4. **Handle errors gracefully:**
   - If link is paywalled, note this and extract what's available
   - If link fails, record the URL and continue
   - Maximum 20 links to prevent overwhelming processing

### Phase 4: Deduplicate and Synthesize

**PREREQUISITE CHECK:** Before starting synthesis, verify:

- ✓ All pages of search results have been processed (no more nextPageToken)
- ✓ All identified newsletters have been read via read_gmail_thread
- ✓ Content from all newsletters is stored in memory
- ✓ All viable content links have been attempted (up to 20 max)

If any of these are incomplete, return to the appropriate phase before continuing.

**Now proceed with deduplication:**

1. **Identify duplicate coverage:**
   - Multiple newsletters covering the same story
   - Same underlying sources cited by different authors
   - Repeated facts or statistics across sources
2. **Extract unique insights:**
   - Different perspectives on the same topic
   - Unique analysis or commentary
   - Exclusive information from each source
3. **Build topic clusters:**
   - Group related content by theme
   - Identify causal relationships (X led to Y)
   - Note conflicting viewpoints or interpretations
4. **Create consolidated view:**
   - Merge duplicate information
   - Preserve attribution to all sources that mentioned it
   - Keep unique angles from each newsletter

### Phase 5: Categorize Using MECE Framework

Organize content into Mutually Exclusive, Collectively Exhaustive categories.

**Default category structure** (adjust based on content):

- **Technology & AI:** AI developments, software, hardware, tech companies
- **Business & Economics:** Markets, companies, economic policy, startups
- **Politics & Policy:** Government, elections, legislation, geopolitics
- **Science & Research:** Scientific discoveries, research findings, academic work
- **Culture & Society:** Social trends, media, arts, cultural commentary
- **Health & Medicine:** Medical news, public health, healthcare
- **Environment & Energy:** Climate, sustainability, energy policy
- **Other:** Items that don't fit above categories

**Category selection principles:**

- Each item appears in exactly ONE category (mutually exclusive)
- Every item fits into a category (collectively exhaustive)
- If many items fall into "Other", refine categories
- Aim for 5-8 major categories per digest

### Phase 6: Produce Summary Document

Create a well-structured HTML document with minimal, elegant styling.

**Document structure:** Use the HTML template from the skill (DOCTYPE, head with styles, body with h1, date, summary div, category sections with .story divs, Quick Hits, metadata).

**Hyperlink requirements:**

1. **Every source citation must be a clickable hyperlink:**
   - Newsletter names link to the original email or web archive
   - Referenced articles link to the original URL
   - Company/organization names link to their websites when first mentioned
   - Research papers link to arXiv, DOI, or publication page
2. **Link formats:**
   - For newsletters: Use web archive link if available (e.g., substack.com/p/article-slug)
   - For Gmail threads: Use mailto: links or note "Email source"
   - For external articles: Use full HTTPS URL
3. **Link placement:**
   - Include source links in the "Sources:" line at the top of each story
   - Add inline links throughout the body text for referenced materials
   - Create a "Quick Hits" section at the end with one-line items that are fully hyperlinked

**Citation requirements:**

1. Every fact or claim must cite the newsletter source with a hyperlink
2. When content comes from a linked article, cite both the newsletter AND the original article with hyperlinks
3. Distinguish between newsletter's own analysis vs. content they're summarizing from elsewhere

**Quality standards:**

- **Conciseness:** Each story summary should be scannable in 30 seconds
- **Clarity:** Use plain language, explain jargon on first use
- **Context:** Provide enough background for stories to make sense standalone
- **Objectivity:** Present multiple viewpoints when they exist
- **Accuracy:** Verify facts when multiple sources conflict
- **Aesthetics:** Keep styling minimal and elegant — focus on readability

### Phase 7: Redundancy Check and Refinement

**CRITICAL STEP:** Before delivering the digest, perform a comprehensive redundancy audit:

1. **Read the entire digest from start to finish**
2. **Identify redundancy patterns:**
   - Same story appearing in multiple categories
   - Same fact/statistic repeated in different sections
   - Overlapping narratives that could be consolidated
   - Related stories that should be merged under a single heading
3. **Refactor for MECE compliance:**
   - Each fact should appear exactly once in the most appropriate location
   - If a story spans multiple categories, choose the primary category and add a brief cross-reference if essential
   - Consolidate related items under umbrella headings
   - Remove duplicate attributions (don't cite the same source multiple times for the same fact)
4. **Conciseness pass:**
   - Eliminate redundant phrases
   - Combine related bullet points
   - Ensure no story is telling the reader the same thing twice
5. **Final verification:**
   - Each category contains mutually exclusive content
   - All major stories are collectively covered (nothing important missing)
   - No information appears in more than one place

**Example redundancy fix:**

- **BEFORE (redundant):** Same story in "AI Models" and again in "Infrastructure"
- **AFTER (MECE):** One combined story in "AI Models" covering both model launch and chip strategy

**Track token usage throughout execution:** Note input/output tokens, calculate cost (e.g. $3/MTok input, $15/MTok output), include in metadata.

### Phase 8: Mark Newsletters as Read in Gmail

**IMPORTANT FINAL STEP:** After successfully creating and delivering the digest, mark all processed newsletters as read to keep inbox organized.

**Current implementation:** Gmail tools may not include `modify_message` or `mark_as_read`. Available tools: read_gmail_profile, search_gmail_messages, read_gmail_message, read_gmail_thread.

**Workaround:** Include in the digest a "Processed Newsletters" section listing each newsletter and its Message ID, with a note that the user may want to mark them as read manually. Optionally suggest a Gmail filter (e.g. `from:(newsletter OR substack OR beehiiv) newer_than:1d` → Mark as read, apply label).

---

## Error Handling

- **No newsletters in last 24 hours:** Expand to 48 hours and inform user.
- **Pagination:** Always check for `nextPageToken`; continue until no more pages; report "Examined X messages, identified Y newsletters."
- **web_fetch fails:** Note link as "(link unavailable)" and continue.
- **Ambiguous content (news vs sponsor):** Err on the side of caution and exclude; document in footnote.
- **Difficult categorization:** Use best judgment for primary category; add "Also relates to: [other categories]".
- **Quality checks:** Verify all sources represented, no duplicate stories, all citations are working hyperlinks, reading time reasonable, token/cost in metadata.

---

## Output Location

Save the final digest to:

```
/mnt/user-data/outputs/newsletter-digest-[YYYY-MM-DD].html
```

Then present the file to the user using the present_files tool.

---

## Optimization Notes

- **Performance:** Process newsletters in parallel when possible; limit article fetches to most relevant links; cache article content if same URL appears in multiple newsletters.
- **Content quality:** Prioritize original reporting; weight thoughtful analysis; include data/research when available.
- **User experience:** Start with executive summary; use consistent formatting; provide links for deep dives.

---

## Example Scenarios

1. **Overlapping coverage:** Two tech newsletters cover same AI release → single story citing both and linking to official source once.
2. **Mixed content:** Newsletter has essay + research links + sponsor section → extract essay, follow research links, exclude sponsor.
3. **Newsletter cites newsletter:** A writes analysis, B summarizes and links to A → credit A as primary, note B also covered.
4. **Large volume:** Use pagination until no nextPageToken; report total examined vs newsletters identified.

---

## Extension Ideas

- Trend detection across days; follow-up tracking; priority flagging; personalization; searchable digest archive.

---

## Skill Evaluation

**Test prompts:** "Create my daily newsletter digest", "Summarize my unread newsletters from today", "What's in my newsletter inbox?"

**Quality indicators:** No duplicate information across categories; all major topics represented; working links; clear format; accurate categorization.

**Failure modes to avoid:** Including sponsored content; duplicate stories not merged; broken citations; unclear category boundaries; missing content; stopping pagination early; synthesizing before all content collected; redundant content in multiple sections; missing hyperlinks; not tracking token/cost.
