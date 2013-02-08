define(["require"]
    , function (require) {
        var
        initialize = function (router) {
                window.app_router = new router({});
                Backbone.history.start({ pushState: true });
                var last = 0, onTap = function(e){
                        var $t = $(e.currentTarget);
                        if($t.hasClass("stop")){
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        } else if($t.hasClass("history-back")){
                            window.history.back();
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        } else if($t.hasClass("external-link")) {
                            window.open($t.attr("href"), "_blank");
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        } else if(!(e.ctrlKey||e.metaKey)){
                            if(!$t.attr("disabled") && !$t.closest(".link-stop").length){
                                if((((new Date()).getTime()) - last) > 500){
                                    last = (new Date()).getTime();
                                    var href = $t.attr("href");
                                    if(href){
                                        if(!~_.indexOf(href, "http"))
                                            window.app_router.navigate(href, true);
                                        else
                                            window.location.hash = href;
                                    } else if($t.attr("hnc-loader")){
                                        require([$t.attr("hnc-loader")], function(View){
                                            View.init(window.__options__).render($t);
                                        });
                                    }
                                }
                            }
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }
                    }
                    , events = {click: function(e){
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }}, submitEvents = {};
                events[hnc.support.clickEvent] = onTap;
                $("body").on(events, ".js-link");
                return window.app_router;
            };
        return {initialize: initialize};
    }
);