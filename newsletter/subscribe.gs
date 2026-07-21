/**
 * The Morning Bloom — subscriber collector (Google Apps Script).
 *
 * This turns a Google Sheet into the live subscriber list:
 *   • The website's Subscribe form POSTs an email here  -> a row is appended (deduped).
 *   • The daily send workflow GETs the list here (token-protected) -> emails go out.
 * Subscriber addresses stay private in your own Sheet; only the token-holding
 * workflow can read them back.
 *
 * ONE-TIME SETUP
 *   1. Create a Google Sheet (any name). Rename the first tab to "Subscribers".
 *   2. Extensions -> Apps Script. Delete the sample code, paste THIS file.
 *   3. Set TOKEN below to a long random string (e.g. mash the keyboard, 30+ chars).
 *   4. Deploy -> New deployment -> gear icon -> "Web app".
 *        Description: Morning Bloom subscribe
 *        Execute as:  Me
 *        Who has access: Anyone
 *      Click Deploy, authorize when prompted, and COPY the "Web app URL".
 *   5. In the GitHub repo -> Settings -> Secrets and variables -> Actions, add:
 *        SUBSCRIBE_ENDPOINT = the Web app URL from step 4
 *        SUBSCRIBE_TOKEN    = the same TOKEN string from step 3
 *   6. Send the Web app URL to Claude to wire the website form to it.
 */
var TOKEN = 'REPLACE_WITH_A_LONG_RANDOM_STRING';

function doPost(e) {
  var p = (e && e.parameter) || {};
  if ((p.company || '').trim() !== '') return _text('ok');      // honeypot: silently drop bots
  var email = (p.email || '').trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return _text('invalid');

  var sh = _sheet();
  var last = sh.getLastRow();
  var existing = last >= 1
    ? sh.getRange(1, 2, last, 1).getValues().map(function (r) { return String(r[0]).trim().toLowerCase(); })
    : [];
  if (existing.indexOf(email) === -1) sh.appendRow([new Date(), email]);
  return _text('ok');
}

function doGet(e) {
  var token = (e && e.parameter && e.parameter.token) || '';
  if (token !== TOKEN) return _text('forbidden');
  var sh = _sheet();
  var last = sh.getLastRow();
  if (last < 1) return _text('');
  var emails = sh.getRange(1, 2, last, 1).getValues()
    .map(function (r) { return String(r[0]).trim(); })
    .filter(function (v) { return v.indexOf('@') !== -1; });
  return _text(emails.join('\n'));
}

function _sheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName('Subscribers') || ss.getSheets()[0];
}

function _text(s) {
  return ContentService.createTextOutput(s).setMimeType(ContentService.MimeType.TEXT);
}
