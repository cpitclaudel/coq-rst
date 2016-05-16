function annotateSup(marker) {
    switch (marker) {
    case "?":
        return "This block is optional.";
    case "*":
        return "This block is optional, and may be repeated.";
    case "+":
        return "This block may be repeated.";
    }
}

function annotateSub(separator) {
    return "Use “" + separator + "” to separate repetitions of this block.";
}

// function translatePunctuation(original) {
//     var mappings = { ",": "⸴" }; // ，
//     return mappings[original] || original;
// }

function annotateNotations () {
    $(".repeat-wrapper > sup")
        .attr("title", function(i, _attr) {
            return annotateSup($(this).text());
        });

    $(".repeat-wrapper > sub")
        .attr("title", function(i, _attr) {
            return annotateSub($(this).text());
        }); //.text(function(i, text) { return translatePunctuation(text); });
}

$(annotateNotations);
