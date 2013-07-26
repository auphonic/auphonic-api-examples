/*
  If you want to integrate Auphonic into your own web application,
  direct file uploads from your users to our servers are possible with
  cross-origin requests (CORS).
  For more details about CORS see
  http://www.html5rocks.com/en/tutorials/file/xhr2/ .

  For full controll, you can to use our JSON-based API.
  Here it's necessary to first create a production with all details and then
  upload a media file in a second request, see
  https://auphonic.com/api-docs/simple_usage.html#start-production-upload-file .

  In your HTML, you must have a corresponding file input form to make the above
  example working:
      <input type="file" id="files" name="files[]" multiple />

  For more details see:
  https://auphonic.com/api-docs/examples.html#complex-audio-file-upload-with-javascript-cors
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

function get_token() {
  // your OAuth2 bearer token
  return 'XXXXXXX';
}

function createProduction() {
  // create new production using the JSON API
  // NOTE: Content-type must be application/json!
  var xhr = new createCORSRequest("POST", "https://auphonic.com/api/productions.json");
  xhr.setRequestHeader("Content-type", "application/json");
  xhr.setRequestHeader("Authorization", "Bearer " + get_token());
  xhr.onload = function(e) {
    console.log("Production: created");

    // parse response of first request to get the production UUID
    var response = JSON.parse(e.target.response);
    var data = response.data;
    var production_uuid = data.uuid;

    // the audio file must be selected in an HTML form with id files, e.g.:
    //   <input type="file" id="files" name="files[]" multiple />
    var file = document.querySelector('#files').files[0];

    if (file) {
      console.log("File Upload: started");

      // second request to add audio file to the production
      // IMPORTANT: we must not set the Content Type to JSON here!
      var url = 'https://auphonic.com/api/production/{uuid}/upload.json'.replace('{uuid}', production_uuid);
      var xhr2 = new createCORSRequest("POST", url);
      xhr2.setRequestHeader("Authorization","Bearer " + get_token());

      // event listener to show upload progress
      xhr2.upload.addEventListener("progress", function(e) { console.log((e.loaded / e.total) * 100); }, false);

      // callback when upload finished
      xhr2.onload = function(e) {
        console.log("File Upload: Done");
      };

      // append file to our form and send second request
      var formData = new FormData();
      formData.append('input_file', file);
      xhr2.send(formData);
    }
  };

  // send first request and set some production details in JSON
  xhr.send(JSON.stringify({"metadata":{"title": "test upload 2"}}));
}

// event listener to trigger the upload when the user selects a new file
document.getElementById('files').addEventListener('change', createProduction, false);
