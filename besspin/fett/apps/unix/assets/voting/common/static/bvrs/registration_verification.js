
document.addEventListener('submit', e => {

	document.getElementById('outerDiv').style.visibility = 'hidden';
   
  // Store reference to form to make later code easier to read
  const form = e.target;

  // Post data using the Fetch API
  fetch('bvrs/voter_check_status', {
    method: 'POST',
    body: new FormData(form)
  })  
  .then(
	function(response) {
	  if (response.status !== 200) {
	    console.log('Looks like there was a problem. Status Code: ' +
	      response.status);
	    return;
	  }

	  // Examine the text in the response
	  response.json().then(function(data) {
	    console.log(data);
	  });
	}
  )

  // Prevent the default form submit
  e.preventDefault();

});


function fillVoterData (/*data*/){

	var data = '{"voter_q":[{"id":101,"lastname":"lastname","givennames":"firstname","resaddress":"1234 address","mailaddress":"1234 address","registeredparty":"whig","birthdate":507859200,"idinfo":"YmxvYjE=","status":0,"initialregtime":0,"lastupdatetime":0,"confidential":0}]}';

	jsonData = JSON.parse(data);

	var div = document.getElementById('voterDataInner');

	div.innerHTML += "<div class=voterDataItem>Given Name(s): " + jsonData['voter_q'][0]["givennames"] + "</div>";
	div.innerHTML += "<div class=voterDataItem>Last Name: " + jsonData['voter_q'][0]["lastname"] + "</div>";
	div.innerHTML += "<div class=voterDataItem>Residential Address: " + jsonData['voter_q'][0]["resaddress"] + "</div>";
	div.innerHTML += "<div class=voterDataItem>Mailing Address: " + jsonData['voter_q'][0]["mailaddress"] + "</div>";
	div.innerHTML += "<div class=voterDataItem>Registered Party: " + jsonData['voter_q'][0]["registeredparty"] + "</div>";
	div.innerHTML += "<div class=voterDataItem>Birthdate: " + jsonData['voter_q'][0]["birthdate"] + "</div>";
	
	if (jsonData['voter_q'][0]["status"] === '0'){
		div.innerHTML += "<div class=voterDataItem>Registration Status: Inactive" + "</div>";
	}
	else{
		div.innerHTML += "<div class=voterDataItem>Registration Status: Active" + "</div>";
	}
}