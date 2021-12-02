var modal = document.getElementById("myModal");

var img = document.getElementById("myImg");
var modalImg = document.getElementById("img01");
var captionText = document.getElementById("caption");


window.onload = function() {
        var anchors = document.getElementsByClassName('brick');
        for(var i = 0; i < anchors.length; i++) {
            var anchor = anchors[i];
            anchor.onclick = function() {
                modal.style.display = "block";
                modalImg.src = this.children[0].src;
                captionText.innerHTML = this.alt;
            }
        }
    }

var span = document.getElementsByClassName("close")[0];

span.onclick = function() { 
  modal.style.display = "none";
}