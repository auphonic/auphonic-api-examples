/*
  If you want to integrate Auphonic into your own web application,
  direct file uploads from your users to our servers are possible with
  cross-origin requests (CORS).
  For more details about CORS see
  http://www.html5rocks.com/en/tutorials/file/xhr2/ .

  This example shows you how to create, upload and start an Auphonic
  production using our Simple API (https://auphonic.com/api-docs/simple_api.html).

  In your HTML, you must have a corresponding file input form to make the above
  example working:
      <input type="file" id="files" name="files[]" multiple />

  For more details see:
  https://auphonic.com/api-docs/examples.html#simple-audio-file-upload-with-javascript-cors
*/

// Create the XHR object.
function createCORSRequest(method, url) {
  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr) {
    // XHR for Chrome/Firefox/Opera/Safari.
    xhr.open(method, url, true);
  } else if (typeof XDomainRequest != "undefined") {
    // XDomainRequest for IE.
    xhr = new XDomainRequest();
    xhr.open(method, url);
  } else {
    // CORS not supported.
    xhr = null;
  }
  return xhr;
}

function createProduction() {
  // create CORS request to Auphonic Simple API
  var xhr = new createCORSRequest("POST", "https://auphonic.com/api/simple/productions.json");
  // IMPORTANT: if you use OAuth, you must provide your bearer token here!
  //            otherwise you can also use HTTP Basic Authentication ...
  xhr.setRequestHeader("Authorization", "Bearer XXXXXXX");

  // production metadata and details
  var formData = new FormData();
  formData.append("title", "javascript upload test");
  formData.append("artist", "me");
  formData.append("loudnesstarget", -23);
  formData.append("action", "start");

  // add the media file which should be uploaded
  // the audio file must be selected in an HTML form with id files, e.g.:
  //   <input type="file" id="files" name="files[]" multiple />
  formData.append("input_file", document.querySelector('#files').files[0]);

  // submit request
  xhr.send(formData);
}

// event listener to trigger the upload when the user selects a new file
document.getElementById('files').addEventListener('change', createProduction, false);
