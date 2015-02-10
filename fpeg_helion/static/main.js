$(document).ready(function () {

  function hexToBase64(str) {
    return btoa(String.fromCharCode.apply(null, str.replace(/\r|\n/g, "").replace(/([\da-fA-F]{2}) ?/g, "0x$1 ").replace(/ +$/, "").split(" ")));
  }

  $("#upload-button").click(function(e) {
  
    // get image data from form
    var form_data = new FormData($('form')[0]);
    
    // send async ajax request
    $.ajax({
      url: "/compress",
      type: "POST",
      data: form_data,
      cache: false,
      contentType: false,
      processData: false,
      
      complete: function(xhr, status) {
        console.log("request status: " + status);
        uid = xhr.getResponseHeader("X-Uploadid");
        console.log("ID: "+uid);
        
        $.ajax({
          url: "/get/"+uid,
          type: "GET",
          
          success: function(data, status, xhr) {
            console.log("get success");
            
            var img = document.createElement('img');
            img.src = 'data:image/jpeg;base64,' + data;
            
            $("#container").append(img);
          },
          
          complete: function(xhr, status) {
            console.log("get status: " + status);
          }
          
        });
      }
      
    });
    
  });

});
