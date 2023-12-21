document.addEventListener("DOMContentLoaded", function () {
	// Add a listener to each of the buttons by querying the class
	var buttons = document.querySelectorAll(".jbtn")
	// Iterate over each button and add an event listener that will perform AJAX call
	buttons.forEach(function (button) {
		button.addEventListener("click", function () {
			var house_id = button.getAttribute("value")
			var option = button.getAttribute("name")
			fetchData(house_id, option);
		})
	})
});

function getCSRFToken() {
	var csrfTokenElement = document.getElementsByName("csrfmiddlewaretoken")[0];
	return csrfTokenElement ? csrfTokenElement.value : null;
}

function fetchData(houseID, option) {
	// Replace 'your_django_view_url/' with the actual URL of your Django view
	var url = "/scraper/set_like/";

	// Get the CSRF token
	var csrfToken = getCSRFToken();

	// Make sure the CSRF token is available
	if (!csrfToken) {
		console.error('CSRF token not found');
		return;
	}

	var postData = {
		"id": houseID,
		"option": option,
	}

	// Make an AJAX fetch request
	fetch(url, {
		method: 'POST', // or 'POST' if your Django view expects a POST request
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrfToken,
			// Add any additional headers if needed
		},
		body: JSON.stringify(postData),
	})
		.then(response => response.json())
		.then(data => {
			// Handle the JSON response data here
			console.log(data);
			console.log(data.result)

			// Change button class based on the response
			likeButton = document.getElementById(houseID + "_like")
			dislikeButton = document.getElementById(houseID + "_dislike")
			if (data.result == "success" && option == "like") {
				console.log("calling")
				likeButton.classList.remove('btn-primary');
				likeButton.classList.remove('btn-secondary');
				likeButton.classList.add('btn-success');
				dislikeButton.classList.remove('btn-danger');
				dislikeButton.classList.remove('btn-primary');
				dislikeButton.classList.add('btn-secondary');
			} else if (data.result == "success" && option == "dislike") {
				dislikeButton.classList.remove('btn-primary');
				dislikeButton.classList.remove('btn-secondary');
				dislikeButton.classList.add('btn-danger');
				likeButton.classList.remove('btn-success');
				likeButton.classList.remove('btn-primary');
				likeButton.classList.add('btn-secondary');
			}
		})
		.catch(error => {
			// Handle errors here
			console.error('Error:', error);
		});
}


// function status_update(_element){
// 	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
// 	$.ajax({
// 		method: 'POST',
// 		url:'set_like',
// 		headers: { 'X-CSRFToken': csrftoken },
// 		// Pass through all data for a given listing
// 		data: {
// 			id: $(_element).attr("value"),
// 			like_dislike: $(_element).text()
// 		},
// 	success: function (response) {
// 		var parent = $(_element).parent() // div containing buttons
// 		var like_button = $(parent).children("button.Like")
// 		var dislike_button = $(parent).children("button.Dislike") 

// 		// like_dislike_switch
// 		if ($(_element).hasClass("Like")) {
// 			like_dislike_switch($(like_button), 'to_like');
// 			like_dislike_switch($(dislike_button), 'to_dislike');
// 		} else {
// 			like_dislike_switch($(like_button), 'to_dislike');
// 			like_dislike_switch($(dislike_button), 'to_like');
// 		}
// 	}
// 	});
// }

// function like_dislike_switch(but, swit){
// 	remove_elem_class(but)
// 	if (swit == "to_like"){
// 		$(but).addClass("btn-success");
// 	} else{
// 		$(but).addClass("btn-secondary");
// 	}
// }

// function remove_elem_class(but){
// 	if ($(but).hasClass("btn-primary")) {
// 		$(but).removeClass("btn-primary");
// 	} else if ($(but).hasClass("btn-secondary")) {
// 		$(but).removeClass("btn-secondary");
// 	} else {
// 		$(but).removeClass("btn-success");
// 	}
// 	return
// }