
function status_update(_element){
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	$.ajax({
		method: 'POST',
		url:'set_like',
		headers: { 'X-CSRFToken': csrftoken },
		data: {
			id: $(_element).attr("value"),
			like_dislike: $(_element).text()
		},
	success: function (response) {
		var parent = $(_element).parent() // div containing buttons
		var like_button = $(parent).children("button.Like")
		var dislike_button = $(parent).children("button.Dislike") 

		// like_dislike_switch
		if ($(_element).hasClass("Like")) {
			like_dislike_switch($(like_button), 'to_like');
			like_dislike_switch($(dislike_button), 'to_dislike');
		} else {
			like_dislike_switch($(like_button), 'to_dislike');
			like_dislike_switch($(dislike_button), 'to_like');
		}
	}
	});
}

function like_dislike_switch(but, swit){
	remove_elem_class(but)
	if (swit == "to_like"){
		$(but).addClass("btn-success");
	} else{
		$(but).addClass("btn-secondary");
	}
}

function remove_elem_class(but){
	if ($(but).hasClass("btn-primary")) {
		$(but).removeClass("btn-primary");
	} else if ($(but).hasClass("btn-secondary")) {
		$(but).removeClass("btn-secondary");
	} else {
		$(but).removeClass("btn-success");
	}
	return
}