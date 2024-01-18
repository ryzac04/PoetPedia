
$(document).ready(function () {
    $("#toggle-poem-button").on("click", function (e) {
        e.preventDefault();

        const button = $(this);
        const poemId = button.data("id");
        const isFavorite = button.data("favorite");

        const poemData = {
            title: $("#poem-title").text(),
            author: $("#poem-author").text(),
            lines: $("#poem-lines").text(),
            id: poemId,
        };

        console.log("Poem Data:", poemData);
        console.log("Poem ID:", poemId);

        // The url for the ajax request is found in poems/show.html template //
        
        $.ajax({
            url: button.closest('form').attr('action'),
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(poemData),
            success: toggleButtonAppearance(button, !isFavorite)
        });
    });
});

function toggleButtonAppearance(button, isFavorite) {
    if (isFavorite) {
        button.removeClass("btn-secondary").addClass("btn-primary");
    } else {
        button.removeClass("btn-primary").addClass("btn-secondary");
    }

    button.data("favorite", isFavorite);
}
