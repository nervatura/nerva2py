/*global PDFJS:false */
/*global report:false */
/*global document:false */
/*global window:false */
/*global Blob:false */

/*global json_temp:false */
/*global xml_temp:false */
/*global create_report:false */

PDFJS.disableWorker = true;
var pdfDoc = null,
    pageNum = 1,
    pageRendering = false,
    pageNumPending = null,
    scale = 1.3,
    canvas = document.getElementById('preview_box'),
    ctx = canvas.getContext('2d');

function renderPage(num) {
  pageRendering = true;
  pdfDoc.getPage(num).then(function(page) {
    var viewport = page.getViewport(scale);
    canvas.height = viewport.height;
    canvas.width = viewport.width;

    var renderContext = {
      canvasContext: ctx,
      viewport: viewport};
    var renderTask = page.render(renderContext);
    
    renderTask.promise.then(function () {
      pageRendering = false;
      if (pageNumPending !== null) {
        renderPage(pageNumPending);
        pageNumPending = null;}});});
  document.getElementById('page_num').textContent = pageNum;}

function queueRenderPage(num) {
  if (pageRendering) {
    pageNumPending = num;
  } else {
    renderPage(num);}}

function onPrevPage() {
  if (pageNum <= 1) {
    return;}
  pageNum--;
  queueRenderPage(pageNum);}
document.getElementById('prev').addEventListener('click', onPrevPage);

function onNextPage() {
  if (pageNum >= pdfDoc.numPages) {
    return;}
  pageNum++;
  queueRenderPage(pageNum);}
document.getElementById('next').addEventListener('click', onNextPage);

/*----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------*/
function show_report(rdoc) {
  pageNum = 1;
  PDFJS.getDocument(rdoc).then(function(pdfDoc_) {
    pdfDoc = pdfDoc_;
    document.getElementById('page_count').textContent = pdfDoc.numPages;
    renderPage(pageNum);});
}

function load_file(output) {
  var ctype = "xml";
  if (document.getElementById("dv_json_template").style.display === "block") {
    ctype = "json";}
  else if (document.getElementById("dv_js_template").style.display === "block") {
    ctype = "js";}
  var rpt = new report(document.getElementById("orientation").value);
  switch (ctype) {
    case "js":
      create_report(rpt);
      break;
    case "xml":
      var xml_str = document.getElementById("dv_xml_template").value;
      rpt.loadDefinition(xml_str);
      break;
    case "json":
      var json_str = document.getElementById("dv_json_template").value;
      rpt.loadJsonDefinition(json_str);
      break;}
  rpt.createReport();
  switch (output) {
    case "win":
      rpt.save2DataUrl();
      break;
    case "prev":
      show_report(rpt.save2Pdf());
      break;
    case "save":
      rpt.save2PdfFile("ReportTemplate.pdf");
      break;
    case "xml_data":
      var xdata = new Blob([rpt.save2Xml()], {type: 'text/xml'});
      window.URL.revokeObjectURL(xdata); xdata = window.URL.createObjectURL(xdata);
      window.open(xdata, '_blank');
      break;
    case "xml_temp":
      var xtdata = new Blob([rpt.getXmlTemplate()], {type: 'text/xml'});
      window.URL.revokeObjectURL(xtdata); xtdata = window.URL.createObjectURL(xtdata);
      window.open(xtdata, '_blank');
      break;
    case "json_temp":
      var jdata = new Blob([JSON.stringify(rpt.template.elements, null, " ")], {type: 'application/json'});
      window.URL.revokeObjectURL(jdata); jdata = window.URL.createObjectURL(jdata);
      window.open(jdata, '_blank');
      break;
  }}

document.getElementById('prev_report').addEventListener('click', function() {load_file('prev');});
document.getElementById('win_report').addEventListener('click', function() {load_file("win");});

document.getElementById('save_pdf_report').addEventListener('click', function() {load_file("save");});
document.getElementById('save_xml_data').addEventListener('click', function() {load_file("xml_data");});
document.getElementById('panel_state').addEventListener('click', function() {
  document.getElementById("temp_panel").style.display = 
    (document.getElementById("temp_panel").style.display==="none") ? "block" : "none";
});
document.getElementById('save_xml_temp').addEventListener('click', function() {load_file("xml_temp");});
document.getElementById('save_json_temp').addEventListener('click', function() {load_file("json_temp");});

function show_template(ttype) {
  document.getElementById("dv_xml_template").style.display = (ttype==="xml") ? "block" : "none";
  document.getElementById("dv_json_template").style.display = (ttype==="json") ? "block" : "none";
  document.getElementById("dv_js_template").style.display = (ttype==="js") ? "block" : "none";}
document.getElementById('set_xml_content').addEventListener('click', function() {
  show_template("xml");});
document.getElementById('set_json_content').addEventListener('click', function() {
  show_template("json");});
document.getElementById('set_js_content').addEventListener('click', function() {
  show_template("js");});

document.getElementById("dv_xml_template").value = xml_temp;
document.getElementById("dv_json_template").value = JSON.stringify(json_temp, null, " ");
document.getElementById("dv_js_template").value = create_report.toString();
