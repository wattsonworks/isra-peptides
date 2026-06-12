/**
 * Isra.Peptides - Lead / Order capture endpoint (Google Sheets)
 * ------------------------------------------------------------------
 * Deploy as a Web App, then paste the /exec URL into
 * index.html  ->  SHOP.SHEET_ENDPOINT.
 *
 * DEPLOY (one time, ~3 min):
 *  1. Create a Google Sheet. Note its tab name (default "Leads").
 *  2. Extensions -> Apps Script. Delete the sample, paste THIS file.
 *  3. Set SHEET_ID below to the id in your sheet URL
 *     (https://docs.google.com/spreadsheets/d/<THIS_PART>/edit).
 *  4. Deploy -> New deployment -> type "Web app".
 *       Execute as: Me   |   Who has access: Anyone
 *  5. Copy the Web app URL (ends with /exec) -> put it in index.html.
 *  6. Re-deploy after any edit (Deploy -> Manage deployments -> edit -> new version).
 *
 * The site POSTs form-encoded data (no-cors) so a slow/offline sheet
 * never blocks the customer - WhatsApp always opens.
 */

var SHEET_ID = 'PASTE_YOUR_SHEET_ID_HERE';
var SHEET_TAB = 'Leads';

var HEADERS = [
  'Date', 'Type', 'Name', 'Phone', 'Email', 'Address',
  'Coupon', 'Agent', 'Fulfillment', 'Discount %', 'Subtotal', 'Total',
  'Items', 'Source'
];

function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var sh = ss.getSheetByName(SHEET_TAB) || ss.insertSheet(SHEET_TAB);
    if (sh.getLastRow() === 0) {
      sh.appendRow(HEADERS);
      sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
      sh.setFrozenRows(1);
    }
    sh.appendRow([
      new Date(),
      p.type || '',          // "buy" | "ask"
      p.name || '',
      p.phone || '',
      p.email || '',
      p.address || '',
      p.coupon || '',
      p.agent || '',
      p.fulfillment || '',   // delivery | pickup | crypto
      p.discountPct || '',
      p.subtotal || '',
      p.total || '',
      p.items || '',
      p.source || 'isra-peptides'
    ]);
    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('isra-peptides lead endpoint is live');
}
