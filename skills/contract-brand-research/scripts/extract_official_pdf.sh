#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  extract_official_pdf.sh <official-pdf-url> <output-directory> [keyword-regex]

Downloads an official public PDF, extracts layout-preserving text, and prints matching
lines. Record the document title, publication date, source URL, and page context in the
evidence ledger before treating any result as evidence.
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -lt 2 ]]; then
  usage
  exit 0
fi

url="$1"
output_dir="$2"
keywords="${3:-turnover|revenue|sales|Umsatz|employees|export|production|warranty|spare part|repair|EPD|FSC|PEFC}"

if [[ ! "$url" =~ ^https:// ]]; then
  echo "Error: only HTTPS URLs are accepted." >&2
  exit 2
fi

command -v curl >/dev/null || { echo "Error: curl is required." >&2; exit 3; }
command -v pdftotext >/dev/null || { echo "Error: pdftotext is required." >&2; exit 3; }

mkdir -p "$output_dir"
pdf_path="$output_dir/official-report.pdf"
text_path="$output_dir/official-report.txt"
metadata_path="$output_dir/source-metadata.txt"

printf 'Source URL: %s\nRetrieved UTC: %s\n' "$url" "$(date -u +%FT%TZ)" > "$metadata_path"
curl --fail --location --silent --show-error --output "$pdf_path" "$url"
pdftotext -layout "$pdf_path" "$text_path"

printf '\nExtracted text: %s\nKeyword regex: %s\n\n' "$text_path" "$keywords"
grep --line-number --ignore-case --extended-regexp "$keywords" "$text_path" || true

echo "\nNext step: read surrounding paragraphs and capture the PDF page context before citing."
