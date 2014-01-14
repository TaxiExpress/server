function drawImageOnCanvas(){
    var file = document.getElementById("archivo").files[0];     
    console.log(file);
    var fileReader = new FileReader();
    fileName = file.name;

    fileReader.onloadend = function(e) {
        var tempImg = new Image();
        var dataURL;
        tempImg.src = this.result;
        tempImg.onload = function() {
            var MAX_WIDTH = 120;
            var MAX_HEIGHT = 120;
            var tempW = tempImg.width;
            var tempH = tempImg.height;
            if (tempW > tempH) {
                if (tempW > MAX_WIDTH) {
                    tempH *= MAX_WIDTH / tempW;
                    tempW = MAX_WIDTH;
                }
            } else {
                if (tempH > MAX_HEIGHT) {
                    tempW *= MAX_HEIGHT / tempH;
                    tempH = MAX_HEIGHT;
                }
            }            
            var canvas = document.createElement("canvas");
            canvas.width = tempW;
            canvas.height = tempH;                  
            var ctx = canvas.getContext("2d");
            ctx.drawImage(this, 0, 0,tempW,tempH);
            var dataURL = canvas.toDataURL("image/jpeg")
            //Tenemos la foto en b64 en dataURL. Se la ponemos en el src de la foto.
            document.getElementById("foto").src = dataURL;
        }
    }
    fileReader.readAsDataURL(file); 
}

function mostrarEnBase64(){
    //Ya lo tenemos en base64 en el src de la foto. Con ello hacemos lo que se quiera.
    document.getElementById("URLdelafoto").innerText = document.getElementById("foto").src;
}
