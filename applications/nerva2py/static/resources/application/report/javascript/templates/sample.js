function create_report(rpt) {
  
  //default values
  rpt.template.document.title = "Nervatura Report";
  rpt.template.margins["left-margin"] = 15;
  rpt.template.margins["top-margin"] = 15;
  rpt.template.margins["right-margin"] = 15;
  rpt.template.style["font-family"] = "times";
  
  //header
  var header = rpt.template.elements.header;
  var row_data = rpt.insertElement(header, "row", -1, {height: 10});
  rpt.insertElement(row_data, "image",-1,{src:"logo"});
  rpt.insertElement(row_data, "cell",-1,{
    name:"label", value:"labels.title", "font-style": "bolditalic", "font-size": 26, color: "#D8DBDA"});
  rpt.insertElement(row_data, "cell",-1,{
    name:"label", value:"Javascript Sample", "font-style": "bold", align: "right"});
  rpt.insertElement(header, "vgap", -1, {height: 2});
  rpt.insertElement(header, "hline", -1, {"border-color": 218});
  rpt.insertElement(header, "vgap", -1, {height: 2});
  
  //details
  var details = rpt.template.elements.details;
  rpt.insertElement(details, "vgap", -1, {height: 2});
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", width: "50%", "font-style": "bold", value: "labels.left_text", border: "LT", 
    "border-color": 218, "background-color": 245});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", "font-style": "bold", value: "labels.left_text", border: "LTR", 
    "border-color": 218, "background-color": 245});
  
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", width: "50%", value: "head.short_text", border: "L", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", value: "head.short_text", border: "LR", "border-color": 218});
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", width: "50%", value: "head.short_text", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", value: "head.short_text", border: "LBR", "border-color": 218});
  
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", width: "40", "font-style": "bold", value: "labels.left_text", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", align: "center", width: "30", "font-style": "bold", value: "labels.center_text", 
    border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", align: "right", width: "40", "font-style": "bold", value: "labels.right_text", 
    border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", "font-style": "bold", value: "labels.left_text", border: "LBR", "border-color": 218});
  
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", width: "40", value: "head.short_text", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "date", align: "center", width: "30", value: "head.date", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "amount", align: "right", width: "40", value: "head.number", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", value: "head.short_text", border: "LBR", "border-color": 218});
  
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", "font-style": "bold", value: "labels.left_text", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", width: "50", value: "head.short_text", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", "font-style": "bold", value: "labels.left_text", border: "LB", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", value: "head.short_text", border: "LBR", "border-color": 218});
  
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "long_text", "multiline": "true", value: "head.long_text", border: "LBR", "border-color": 218});
  
  rpt.insertElement(details, "vgap", -1, {height: 2});
  row_data = rpt.insertElement(details, "row", -1, {hgap: 2});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", value: "labels.left_text", "font-style": "bold", border: "1", "border-color": 245, 
    "background-color": 245});
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", value: "head.short_text", border: "1", "border-color": 218});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", value: "labels.left_text", "font-style": "bold", border: "1", "border-color": 245, "background-color": 245});
  rpt.insertElement(row_data, "cell",-1,{
    name: "short_text", value: "head.short_text", border: "1", "border-color": 218});
  
  rpt.insertElement(details, "vgap", -1, {height: 2});
  row_data = rpt.insertElement(details, "row", -1, {hgap: 2});
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", value: "labels.long_text", "font-style": "bold", border: "1", "border-color": 245, "background-color": 245});
  rpt.insertElement(row_data, "cell",-1,{
    name: "long_text", "multiline": "true", value: "head.long_text", border: "1", "border-color": 218});
  
  rpt.insertElement(details, "vgap", -1, {height: 2});
  rpt.insertElement(details, "hline", -1, {"border-color": 218});
  rpt.insertElement(details, "vgap", -1, {height: 2});
  
  row_data = rpt.insertElement(details, "row", -1, {"hgap": 3});
  rpt.insertElement(row_data, "cell",-1,{
    "name": "label", "value": "Barcode (Interleaved 2of5)", "font-style": "bold", "font-size": 10,
    "border": "1", "border-color": 245, "background-color": 245});
  rpt.insertElement(row_data, "barcode",-1,{"code-type": "i2of5", "value": "1234567890", "visible-value":1});
  rpt.insertElement(row_data, "cell",-1,{
    "name": "label", "value": "Barcode (Code 39)", "font-style": "bold", "font-size": 10, 
    "border": "1", "border-color": 245, "background-color": 245});
  rpt.insertElement(row_data, "barcode",-1,{"code-type": "code39", "value": "1234567890ABCDEF", "visible-value":1});
  
  rpt.insertElement(details, "vgap", -1, {height: 3});
  
  row_data = rpt.insertElement(details, "row");
  rpt.insertElement(row_data, "cell",-1,{
    name: "label", value: "Datagrid Sample", align: "center", "font-style": "bold", 
    border: "1", "border-color": 245, "background-color": 245});
  rpt.insertElement(details, "vgap", -1, {height: 2});
  
  var grid_data = rpt.insertElement(details, "datagrid", -1, {
    name: "items", databind: "items", border: "1", "border-color": 218, "header-background": 245, "footer-background": 245});
  rpt.insertElement(grid_data, "column",-1,{
    width: "8%", fieldname: "counter", align: "right", label: "labels.counter", footer: "labels.total"});
  rpt.insertElement(grid_data, "column",-1,{
    width: "20%", fieldname: "date", align: "center", label: "labels.center_text"});
  rpt.insertElement(grid_data, "column",-1,{
    width: "15%", fieldname: "number", align: "right", label: "labels.right_text", 
    footer: "items_footer.items_total", "footer-align": "right"});
  rpt.insertElement(grid_data, "column",-1,{
    fieldname: "text", label: "labels.left_text"});
  
  rpt.insertElement(details, "vgap", -1, {height: 5});
  rpt.insertElement(details, "html", -1, {fieldname: "html_text", 
    html: "<i>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</i> ={{html_text}} Nulla a pretium nunc, in cursus quam."});
  
  //footer
  var footer = rpt.template.elements.footer;
  rpt.insertElement(footer, "vgap", -1, {height: 2});
  rpt.insertElement(footer, "hline", -1, {"border-color": 218});
  row_data = rpt.insertElement(footer, "row", -1, {height: 10});
  rpt.insertElement(row_data, "cell",-1,{value: "Nervatura Report Template", "font-style": "bolditalic"});
  rpt.insertElement(row_data, "cell",-1,{value: "{{page}}", align: "right", "font-style": "bold"});
  
  //data
  rpt.setData("labels", {"title": "REPORT TEMPLATE", "left_text": "Short text", "center_text": "Centered text", 
                                       "right_text": "Right text", "long_text": "Long text", "counter": "No.", "total": "Total"});
  rpt.setData("head", {"short_text": "Lorem ipsum dolor", "number": "123 456", "date": "2014.01.01", 
                                     "long_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque eu mattis diam, sed dapibus justo. In eget augue nisi. Cras eget odio vel mi vulputate interdum. Curabitur consequat sapien at lacus tincidunt, at sagittis felis lobortis. Aenean porta maximus quam eu porta. Fusce sed leo ut justo commodo facilisis. Vivamus vitae tempor erat, at ultrices enim. Nulla a pretium nunc, in cursus quam."});
  rpt.setData("html_text", "<p><b>Pellentesque eu mattis diam, sed dapibus justo. In eget augue nisi. Cras eget odio vel mi vulputate interdum. Curabitur consequat sapien at lacus tincidunt, at sagittis felis lobortis. Aenean porta maximus quam eu porta. Fusce sed leo ut justo commodo facilisis. Vivamus vitae tempor erat, at ultrices enim.</b></p>");
  rpt.setData("items_footer", {"items_total": "3 703 680"});
  var items = [];
  for(var i=0; i<30; i++) {
    items.push({"text": "Lorem ipsum dolor", "number": "123 456", "date": "2014.01.01"});}
  rpt.setData("items", items);
  rpt.setData("logo", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wIExQZM+QLBuYAAAQ5SURBVEjHtZVJbJRlGMd/77fM0ul0ykynLQPtjEOZWjptSisuJRorF6ocjEaDoDGSYKLiFmIMxoPGg0viRY0cNB6IUQ+YYCJEBLXQWqZgK6GU2taWLrS0dDrdO0vn+14PlYSlQAH9357L+89/eZ9HHDp0iP8TyqXDCV9Iuivvkf8lgXbp8JjPxUfHfseXs1yGs52sd+VgpueJqQYdPRE8sxniZgnElRbF8p1yXW6AgWgbDeeOoJgCu8PJtFbAc2W1tEeaxC0rADDTKVZmO+kxKwjawmwO5pJIGhzpP8je7m5KbycDgKnEDEnDYEO+G10xeT3Sxu6eIYJuP5OJffT5ihbNKD/klzckWLWuSibjUSyahZn5NBtXerkj0059dy+rPaUs1wvoiH3GXjkgIy6nbPV65PEMQzaNN0qLu+j6GZTfX5P+NPKjuqXIj8sV4vR0gv7ZJP2zCUpsEEdhW7GfztFOBqf6cQmV5ByUFpfxyr6veHpZpbhuBk/91qw+lGrDwIfXbqfGbkVXVQCiyRQvNZ5hY0EeIW+IkDfEm83dvL82wHRqAkOz3TiDXdqUeGLDLg73xfj5r4PoqopkwVa3RefFkkKeaWgDYHfXENV5LhRFRVMsZFvl0kLuP/aLCM+p4tfeLs4MtyEQgEQRgrs8Th70OtkeaefE2BQPeF1ICQ6Lk9WOOKMrlssltQjAavdwdqQbACkXrHXoOllWnWgiiVNApq4g/nV9+/pXaWrfw3Dh1Q1blCAr3kO5v5K0hPHUPHt6hinZf4JILE6R005CUTBNSJkmFxIp4qbG25veY3LyKJ9Pj8iGDIf0lFfIRT9aVjBHBsaK8Wb4qBuJMTyTpNTtoP2RdQD8PTXHjuOdfNwxiFWBHKsFj1WjPEvDJjIJOBXuCxQzdqpFLLoqJjwTsrbkYSyKBVPTsF6qUUpSpqRuOMaT9e0cq11LiSsTgLd+eheLq4YXKqtpra8Ti1o06ByQwYLVHB05yoHz+2mM1jGWGAPJQqOEoGsmzmvNnXxZHaL2yEKrvjv9LarmY2t4/WWPX6bAnm+TZ40kAlB0GDfO08dJptNxnl+xnYrcClrHZ9g7MMqOkI8PTvejaBo5Np253k/I879MaLBDXDPk+HBC5I9KkTcqhXdIitBIvtiau5Nszc3Xnd8A8GdsmnfKAnhtVnYW2iE1y8GhcbQZlUeDBSy5phdxobVNhPVnUdU0J893scXvITYbpbGvgVh6iIlUgiqPixbWcqb+sFjSur4Sued6hc0WkJIoX/zRQyI1icvhJG0YhA2DmJJDoxqgZoVXrhnsFjel4CIy5Ep+ONXKpjXVlKXconBcF8Epmyidd4hlFpU37vTxYccIuVX3ylsiUDNWse3ux+k4fvU181t1Nvu9pE3J9+eiNz6Zi8FfWSX7WpqveSoHg2EpgHC2g1hLk7hpgtvBP6lBrRsE+ni7AAAAAElFTkSuQmCC");
    
  return rpt;
}
