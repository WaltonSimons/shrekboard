function image_resolution(image_url) {
    var img = new Image();
    img.src = image_url;
    return img.width + "x" + img.height
}

function change_text(text) {
    var url = text.innerHTML.split('href="').pop().split('"').shift();
    var xhr = new XMLHttpRequest();
    xhr.open('HEAD', url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var size_in_bytes = xhr.getResponseHeader('Content-Length');
            text.innerHTML = text.innerHTML.replace('s r', formatBytes(size_in_bytes, 2) + ', ' + image_resolution(url));
        }
    };
    xhr.send(null);
}

function formatBytes(a, b) {
    if (0 == a) return "0 Bytes";
    var c = 1024, d = b || 2, e = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
        f = Math.floor(Math.log(a) / Math.log(c));
    return parseFloat((a / Math.pow(c, f)).toFixed(d)) + " " + e[f]
}

fileTexts = document.getElementsByClassName("fileText");

for (var i = 0; i < fileTexts.length; i++) {
    var text = fileTexts[i];
    change_text(text);
}