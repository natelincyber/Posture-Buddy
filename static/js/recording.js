window.onload = function () {
    var sec = 3;
    document.getElementById("recorder").style.display = "none";
    document.getElementById("video").style.display = "none";
    setInterval(function () {
        document.getElementById("timer").innerHTML =
          sec--;
          if (sec < 0) {
            document.getElementById("time").style.display = "none";
            document.getElementById("video").style.display = "";
            document.getElementById("recorder").style.display = "";
          }
     }, 1000);
    
    // document.getElementById("recorder").innerHTML = ""
};