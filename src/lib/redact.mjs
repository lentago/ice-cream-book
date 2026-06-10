// Render-layer profanity redaction for icecreamtofightwith.com.
//
// The book swears on purpose — the linter (ice_cream_linter.py) *requires*
// 3-5 strategic profanities per recipe, so the markdown source must stay
// uncensored. This module bleeps the website at render time instead:
//
//   - redactHtml():  visible text → <span class="redacted"> hover-to-reveal
//                    black bars (CSS lives in Base.astro)
//   - redactPlain(): plain-text sinks (<title>, meta description, JSON-LD,
//                    RSS, pagefind metadata) → "F******" asterisk style,
//                    so crawlers and link previews never see the word
//   - rehypeRedact:  applies the span treatment to rendered markdown
//                    bodies (the 28 recipes), wired up in astro.config.mjs
//
// Plain .mjs (not .ts) so astro.config.mjs can import it too.

// Mirrors the linter's PROFANITY list (fuck, shit, damn, hell, ass) plus
// the compound/derived forms that actually appear in the corpus. Boundaries
// are tuned so class, molasses, grass, glass, mass, hello, and Hass (the
// avocado) survive unredacted.
const REDACT_SOURCE = [
  String.raw`\w*(?:fuck|shit|damn)\w*`, // fucking, bullshit, batshit, goddamn, ...
  String.raw`\bbastard\w*`, //              bastard, bastardizing, ...
  String.raw`\bbitch\w*`,
  String.raw`\bhell(?:fire|ish|hole|acious)?\b`, // hell, hellfire — not hello, shell
  String.raw`\b(?:dumb|jack|bad)?ass(?:hole)?(?:es|ed|s)?\b`, // ass(es), badass, half-assed
].join('|');

const redactRe = () => new RegExp(REDACT_SOURCE, 'gi');

const escapeHtml = (s) =>
  s.replace(/[&<>"']/g, (c) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[c]);

// data-pagefind-ignore keeps the hidden words out of the on-site search
// index — the black bars stay black even in search excerpts.
const SPAN_OPEN = '<span class="redacted" data-pagefind-ignore>';

/** Escape `text` and wrap each profanity in a hover-to-reveal span. */
export function redactHtml(text) {
  const re = redactRe();
  let out = '';
  let last = 0;
  let m;
  while ((m = re.exec(text))) {
    out += escapeHtml(text.slice(last, m.index));
    out += SPAN_OPEN + escapeHtml(m[0]) + '</span>';
    last = m.index + m[0].length;
  }
  return out + escapeHtml(text.slice(last));
}

/** Bowdlerize for plain-text contexts: "Fuck" → "F***". */
export function redactPlain(text) {
  return text.replace(redactRe(), (w) => w[0] + '*'.repeat(w.length - 1));
}

const SKIP_TAGS = new Set(['code', 'pre', 'script', 'style']);

function redactTextNode(value) {
  const re = redactRe();
  const nodes = [];
  let last = 0;
  let m;
  while ((m = re.exec(value))) {
    if (m.index > last) nodes.push({ type: 'text', value: value.slice(last, m.index) });
    nodes.push({
      type: 'element',
      tagName: 'span',
      properties: { className: ['redacted'], dataPagefindIgnore: '' },
      children: [{ type: 'text', value: m[0] }],
    });
    last = m.index + m[0].length;
  }
  if (last < value.length) nodes.push({ type: 'text', value: value.slice(last) });
  return nodes;
}

function walk(node) {
  if (!node.children) return;
  if (node.type === 'element' && SKIP_TAGS.has(node.tagName)) return;
  const out = [];
  for (const child of node.children) {
    if (child.type === 'text' && redactRe().test(child.value)) {
      out.push(...redactTextNode(child.value));
    } else {
      walk(child);
      out.push(child);
    }
  }
  node.children = out;
}

/** Rehype plugin: redact profanity in rendered markdown (recipe bodies). */
export function rehypeRedact() {
  return (tree) => walk(tree);
}
