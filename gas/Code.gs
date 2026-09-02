/**
 * 餃木 GYOZA WOOD — 線上點餐 Apps Script 後端
 *
 * 部署步驟請見同資料夾的 README.md。
 *
 * 這支腳本要「綁定」在你的訂單 Google 試算表上（試算表內
 * 「擴充功能 > Apps Script」建立），部署成 Web App 後，doPost()
 * 會接收官網結帳表單送出的訂單 JSON，驗證通過後寫入「Orders」
 * 工作表一列。金額一律由伺服器端依下方 PRICES 重新計算，不信任
 * 前端送來的價格，避免被竄改（例如改瀏覽器 devtools 送出假總額）。
 */

// ---------------------------------------------------------------------
// 設定
// ---------------------------------------------------------------------

var SHEET_NAME = 'Orders';

// 共用密鑰：必須與 index.html 裡的 ORDER_SHARED_SECRET 完全一致，
// 用來擋掉不知情亂打這個網址的機器人／爬蟲。這不是銀行等級的安全機制，
// 只是基本防護。
//
// 建議部署後改到「專案設定 > 指令碼屬性」新增一筆 ORDER_SECRET，
// 這樣密鑰就不會留在程式碼裡；沒設定的話就用下面這個預設值。
function getSharedSecret() {
  var fromProps = PropertiesService.getScriptProperties().getProperty('ORDER_SECRET');
  return fromProps || 'di-pU3LwVsB7fq_FDIZMRkIijjpetFSL';
}

// 商品價格表 — 必須手動與 index.html 裡 `products` 陣列的 id / price
// 保持一致。金額一律以這裡為準；前端送來的品項只帶 id 和數量，價格
// 由這裡查表算出，前端算的總額只作畫面顯示用、不會被採信。
//
// ⚠️ 之後在 index.html 增刪商品或改價，記得同步更新這裡。
var PRICES = {
  'gyoza-signature': { name: '招牌爆汁鍋貼', price: 95 },
  'gyoza-kimchi': { name: '韓式泡菜鍋貼', price: 105 },
  'gyoza-shrimp': { name: '鮮蝦韭黃鍋貼', price: 135 },
  'gyoza-veggie': { name: '田園蔬食鍋貼', price: 95 },
  'dumpling-cabbage': { name: '高麗菜鮮肉水餃', price: 90 },
  'dumpling-chive': { name: '韭菜鮮肉水餃', price: 95 },
  'dumpling-corn': { name: '玉米鮮肉水餃', price: 95 },
  'dumpling-hot': { name: '紅油抄手', price: 110 },
  'soup-sour': { name: '老派酸辣湯', price: 55 },
  'soup-radish': { name: '蘿蔔貢丸湯', price: 50 },
  'drink-tea': { name: '冷泡焙香烏龍', price: 45 },
  'drink-plum': { name: '桂花酸梅湯', price: 50 },
  'side-cucumber': { name: '蒜香拍黃瓜', price: 45 },
  'side-tofu': { name: '椒麻皮蛋豆腐', price: 60 },
  'side-kelp': { name: '滷香海帶豆干', price: 45 },
  'side-eggplant': { name: '胡麻茄子', price: 55 },
  'gift-fortune': { name: '招牌招財鍋貼禮盒 50 入', price: 699 }
};

var SERVICE_FEE = 10; // 與前端 serviceFee() 邏輯一致：購物車非空即收 $10。
var VALID_FULFILLMENTS = ['外帶', '內用', '宅配'];
var HEADERS = [
  '時間', '訂單編號', '取餐方式', '姓名', '手機', 'Email', '地址', '備註',
  '品項', '小計', '服務費', '總計', '品項明細(JSON)', '狀態', '來源'
];

// ---------------------------------------------------------------------
// Web App 進入點
// ---------------------------------------------------------------------

function doGet(e) {
  return ContentService.createTextOutput('餃木 GYOZA WOOD 訂單接收服務運作中。')
    .setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
  } catch (lockErr) {
    return jsonResponse({ ok: false, error: '系統忙碌，請稍後再試一次。' });
  }

  try {
    var payload = parsePayload(e);
    var result = handleOrder(payload);
    return jsonResponse(result);
  } catch (err) {
    return jsonResponse({ ok: false, error: (err && err.message) ? err.message : '未知錯誤' });
  } finally {
    lock.releaseLock();
  }
}

// ---------------------------------------------------------------------
// 核心邏輯
// ---------------------------------------------------------------------

function parsePayload(e) {
  if (!e || !e.postData || !e.postData.contents) {
    throw new Error('沒有收到訂單內容');
  }
  try {
    return JSON.parse(e.postData.contents);
  } catch (parseErr) {
    throw new Error('訂單格式錯誤');
  }
}

function handleOrder(payload) {
  if (!payload || payload.secret !== getSharedSecret()) {
    throw new Error('驗證失敗');
  }

  var fulfillment = String(payload.fulfillment || '').trim();
  var name = String(payload.name || '').trim();
  var phone = String(payload.phone || '').trim();
  var email = String(payload.email || '').trim();
  var address = String(payload.address || '').trim();
  var note = String(payload.note || '').trim();
  var items = Array.isArray(payload.items) ? payload.items : [];

  if (VALID_FULFILLMENTS.indexOf(fulfillment) === -1) throw new Error('取餐方式不正確');
  if (!name) throw new Error('請填寫姓名');
  if (!/^[0-9+\-\s]{8,}$/.test(phone)) throw new Error('手機格式不正確');
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('Email 格式不正確');
  if (fulfillment === '宅配' && !address) throw new Error('宅配需要填寫地址');
  if (name.length > 60 || note.length > 500 || address.length > 200) throw new Error('欄位內容過長');
  if (!items.length || items.length > 50) throw new Error('購物車內容不正確');

  var lines = [];
  var subtotal = 0;
  items.forEach(function (item) {
    var product = PRICES[item && item.id];
    var qty = Math.floor(Number(item && item.qty));
    if (!product || !(qty > 0) || qty > 99) throw new Error('購物車內容不正確');
    subtotal += product.price * qty;
    lines.push(product.name + ' x' + qty);
  });

  var serviceFee = SERVICE_FEE;
  var total = subtotal + serviceFee;
  var orderNo = buildOrderNumber();
  var sheet = ensureSheet();

  sheet.appendRow([
    new Date(),
    orderNo,
    fulfillment,
    name,
    phone,
    email,
    address,
    note,
    lines.join(', '),
    subtotal,
    serviceFee,
    total,
    JSON.stringify(items),
    '新訂單',
    payload.source || ''
  ]);

  return { ok: true, orderNo: orderNo, total: total };
}

function buildOrderNumber() {
  var now = new Date();
  var datePart = Utilities.formatDate(now, 'Asia/Taipei', 'yyMMdd');
  var randomPart = Math.floor(1000 + Math.random() * 9000);
  return 'GW' + datePart + randomPart;
}

function ensureSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// ---------------------------------------------------------------------
// 手動測試用：在 Apps Script 編輯器選這個函式按「執行」，
// 可以不透過網頁就測試訂單會不會正確寫進 Sheet。
// ---------------------------------------------------------------------
function testHandleOrder() {
  var result = handleOrder({
    secret: getSharedSecret(),
    fulfillment: '外帶',
    name: '測試訂單',
    phone: '0912345678',
    email: 'test@example.com',
    address: '',
    note: '這是手動測試，可以刪除這一列',
    items: [{ id: 'gyoza-signature', qty: 2 }, { id: 'soup-sour', qty: 1 }],
    source: 'testHandleOrder()'
  });
  Logger.log(result);
}
