console.log("functions") 

function redirect(path){
    path = path.replace(/ /g, '_');
    window.location.href = path;
}


