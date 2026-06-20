/**
 * Escape a string for inclusion in XML text or a double-quoted attribute. Escapes & < > and
 * the double-quote (attribute-safe). Single quotes are left as-is (legal in double-quoted
 * attributes and in text). Intentionally a superset of the add-on's installer.py
 * xml.sax.saxutils.escape (which escapes only & < >) so a value containing a double-quote
 * cannot break a generated attribute. Single source for both settings.xml and
 * playercorefactory.xml generation.
 */
export function xmlEscape(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
