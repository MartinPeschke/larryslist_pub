define(["tools/messaging", "tools/ajax", "text!ajax/templates/artwork_modal.html"], function(messaging, ajax, template){
    var
    formTempl = _.template(template)
    , init = function(opts){
        opts.$el = $(opts.event.target);
        var
            $el = $(formTempl(opts.data)).appendTo("body")
            , $container = opts.$el.closest(".tagsearch-container")
            , $result = opts.$el.siblings(".artworks-list")
            , success = function(resp, status, xhr, data){
                $result.append(resp.html).addClass("has-artworks");
                $el.modal("hide").off().remove();
            };
        $el.modal("show");
        ajax.ifyForm({form: $el, url: "/admin/collection/artwork/save"
            , success: success
            , error: function(msg, resp, data){
                if(msg=='ALREADY_ASSIGNED'){
                    $el.validate().showErrors({'Artwork\\.title':'Already exists in another collection!'})
                    $el.find(".btn-primary").hide();
                    $el.find(".btn-danger").fadeIn();
                } else {
                    messaging.addError({message: msg});
                    $el.modal("hide").off().remove();
                }
            }
        })
    };
    return {init:init};
});