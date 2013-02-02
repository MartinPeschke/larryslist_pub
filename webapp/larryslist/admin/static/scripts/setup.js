$(function(){
    var $el = $(".fixed-height"), $append = $(".fixed-appendix");
    if($el.length && $append.length){
        var res = function(e){
            $el.css({height: ($(window).height() - $el.position().top - $append.height() - 2)+"px"});
        };
        $(window).on({resize:res});
        res();
    }


    $(document).on({
        "click": function(e){
            var data=  $(e.currentTarget).data();
            require([data.customModule], function(V){V.init({el:e.currentTarget, data: data})});
        }
    },".js-link")
});