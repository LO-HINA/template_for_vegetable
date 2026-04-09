function bindUploadPicture() {
    $("#image-upload").on("change", function(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("picture", file);

        $.post({
            url: "/upload/picture",
            data: formData,
            processData: false,
            contentType: false,
            success: function (result) {
                // const category = result['category'];
                const filename = result['filename'];

                console.log(category);
                console.log(filename);

                let imagePreview = $("#image-preview");
                imagePreview.attr("src", "/media/" + filename);
                imagePreview.removeClass("hidden");

                $("#image-placeholder").addClass("hidden");

                // $("#category").val(category.id);
                $("#picture").val("/media/" + filename);

            }
        });
    });
}

$(function () {
    bindUploadPicture();
});