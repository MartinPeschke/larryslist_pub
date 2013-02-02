define(["tools/messaging", "tools/ajax", "text!templates/artist/artwork.html"], function(messaging, ajax, template){
    var
    formTempl = _.template(template)
    , init = function(opts){
        var
            $el = $(formTempl(opts.data)).appendTo("body")
            , $container = $(opts.el).closest(".tagsearch-container")
            , $result = $(opts.el).siblings(".artworks-list")
            , artTempl = _.template($container.find(".artwork-template").html())
            , success = function(resp, status, xhr, data){
                var work = _.clone(data.Artist[0].Artwork[0]);
                if(work.year.length)work.year = '('+work.year+')';

                var last = $result.find(".list-position").last();
                if(last.length)work.pos = parseInt(last.text(), 10) + 1;
                else work.pos = 1;
                $result.append(artTempl(work));
                $el.modal("hide").off().remove();
            };
        $el.modal("show");
        ajax.ifyForm({form: $el, url: "/api/0.0.1/admin/artist/artwork"
            , success: success
            , error: function(msg, resp, data){
                if(msg=='ALREADY_ASSIGNED'){
                    $el.validate().showErrors({'Artist-0\\.Artwork-0\\.title':'Already exists in another collection!'})
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