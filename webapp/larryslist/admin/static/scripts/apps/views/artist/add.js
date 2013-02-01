define(["tools/ajax", "text!templates/artist/add.html"], function(ajax, templ){
    var template = _.template(templ)
        , init = function(success){
            return {'onCreate': function(term){
                var $el = $(template({term: term})).appendTo("body");
                $el.modal("show").find("input").first().focus();
                ajax.ifyForm({form: $el, url: "/api/0.0.1/admin/artist/create", success: function(resp, status, xhr, data){
                    success(data);
                    $el.modal("hide").off().remove();
                }});
            }}
        };
    return {init: init};
});